"""PostgreSQL history repository; callers must supply a VERIFIED account identity.

Record management HTTP uses this repository through the GitHub identity boundary.
Each call owns a short transaction; never hold a DB lock during a model request.
"""
from pathlib import Path
from uuid import UUID, uuid4

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb


from api.history_errors import HistoryConflict, HistoryFull, HistoryMissing


class HistoryStore:
    def __init__(self, connect):
        self.connect = connect

    @classmethod
    def from_dsn(cls, dsn):
        return cls(lambda: psycopg.connect(dsn, row_factory=dict_row, connect_timeout=5))

    def migrate(self):
        directory = Path(__file__).resolve().parents[1] / 'db/migrations'
        with self.connect() as conn:
            # Serialize concurrent initializers. Versioned migrations are explicit,
            # never executed as a side effect of importing the application.
            conn.execute('SELECT pg_advisory_xact_lock(712649001)')
            for name in ('001_history.sql', '002_history_tasks.sql'):
                conn.execute((directory / name).read_text(encoding='utf-8-sig'))

    def account_for_github(self, github_id: int) -> UUID:
        """Only call with id returned by GitHub's authenticated user endpoint."""
        if type(github_id) is not int or github_id <= 0:
            raise ValueError('invalid GitHub identity')
        with self.connect() as conn:
            return conn.execute(
                'INSERT INTO accounts(id, github_id) VALUES (%s,%s) '
                'ON CONFLICT(github_id) DO UPDATE SET github_id=EXCLUDED.github_id '
                'RETURNING id', (uuid4(), github_id),
            ).fetchone()['id']

    @staticmethod
    def _title(title):
        title = title.strip()
        if not 1 <= len(title) <= 100:
            raise ValueError('title must contain 1–100 characters')
        return title

    def create(self, owner, title):
        title = self._title(title)
        with self.connect() as conn:
            # All creates by this owner serialize before COUNT, including from
            # another device/process. A per-process Python lock is insufficient.
            if not conn.execute('SELECT id FROM accounts WHERE id=%s FOR UPDATE', (owner,)).fetchone():
                raise HistoryMissing()
            count = conn.execute('SELECT count(*) AS n FROM preparations WHERE owner_id=%s', (owner,)).fetchone()['n']
            if count >= 20:
                raise HistoryFull()
            return conn.execute(
                'INSERT INTO preparations(id,owner_id,title) VALUES (%s,%s,%s) RETURNING *',
                (uuid4(), owner, title),
            ).fetchone()

    def list(self, owner):
        with self.connect() as conn:
            # Listing never loads private text/results for every history item.
            return conn.execute(
                'SELECT id,title,revision,created_at,updated_at FROM preparations '
                'WHERE owner_id=%s ORDER BY updated_at DESC,id', (owner,),
            ).fetchall()

    def get(self, owner, record):
        with self.connect() as conn:
            row = conn.execute('SELECT * FROM preparations WHERE id=%s AND owner_id=%s', (record, owner)).fetchone()
            if row is None:
                raise HistoryMissing()
            return row

    def rename(self, owner, record, title):
        with self.connect() as conn:
            row = conn.execute(
                'UPDATE preparations SET title=%s,updated_at=now() WHERE id=%s AND owner_id=%s RETURNING *',
                (self._title(title), record, owner),
            ).fetchone()
            if row is None:
                raise HistoryMissing()
            return row

    def delete(self, owner, record):
        with self.connect() as conn:
            if not conn.execute('DELETE FROM preparations WHERE id=%s AND owner_id=%s RETURNING id', (record, owner)).fetchone():
                raise HistoryMissing()

    def replace_inputs(self, owner, record, revision, inputs):
        if not isinstance(inputs, dict) or not set(inputs) <= {'jd_text', 'resume_text'}:
            raise ValueError('only parsed JD/resume text may be stored')
        if any(not isinstance(value, str) for value in inputs.values()):
            raise ValueError('inputs must be text')
        with self.connect() as conn:
            row = conn.execute(
                "UPDATE preparations SET inputs=%s,results='{}'::jsonb,revision=revision+1,updated_at=now() "
                'WHERE id=%s AND owner_id=%s AND revision=%s RETURNING *',
                (Jsonb(inputs), record, owner, revision),
            ).fetchone()
            if row is None:
                raise HistoryConflict()
            conn.execute(
                "UPDATE preparation_tasks SET status='interrupted',updated_at=now() "
                "WHERE record_id=%s AND status='running'", (record,),
            )
            return row

    @staticmethod
    def _kind(kind):
        if kind not in {'analysis', 'questions'}:
            raise ValueError('unknown task kind')

    @staticmethod
    def _lock_record(conn, owner, record, revision=None):
        row = conn.execute(
            'SELECT revision FROM preparations WHERE id=%s AND owner_id=%s FOR UPDATE',
            (record, owner),
        ).fetchone()
        if row is None:
            raise HistoryMissing()
        if revision is not None and row['revision'] != revision:
            raise HistoryConflict()

    def tasks(self, owner, record):
        with self.connect() as conn:
            self._lock_record(conn, owner, record)
            return conn.execute(
                'SELECT kind,revision,attempt,status,updated_at FROM preparation_tasks '
                'WHERE record_id=%s ORDER BY kind', (record,),
            ).fetchall()

    def claim_task(self, owner, record, revision, kind):
        """Explicit request only. No model invocation/retry occurs in this store."""
        self._kind(kind)
        with self.connect() as conn:
            self._lock_record(conn, owner, record, revision)
            if conn.execute(
                "SELECT 1 FROM preparation_tasks WHERE record_id=%s AND status='running'",
                (record,),
            ).fetchone():
                raise HistoryConflict()
            return conn.execute(
                'INSERT INTO preparation_tasks(record_id,kind,revision,attempt,status) '
                "VALUES (%s,%s,%s,%s,'running') ON CONFLICT(record_id,kind) DO UPDATE SET "
                "revision=EXCLUDED.revision,attempt=EXCLUDED.attempt,status='running',updated_at=now() "
                'RETURNING *', (record, kind, revision, uuid4()),
            ).fetchone()

    def finish_task(self, owner, record, revision, kind, attempt, results):
        """Atomically publish a whole task snapshot and finish its exact attempt.

        The HTTP coordinator MUST revalidate the originating account session
        before calling this; repository ownership is not session revocation.
        """
        self._kind(kind)
        expected = {'jd', 'resume', 'gap'} if kind == 'analysis' else {'questions'}
        if not isinstance(results, dict) or set(results) != expected:
            raise ValueError('task requires a complete result snapshot')
        with self.connect() as conn:
            self._lock_record(conn, owner, record, revision)
            self._transition_task(conn, record, revision, kind, attempt, 'completed')
            # A regenerated analysis invalidates questions derived from the old
            # report, even when its input revision has not changed.
            expression = "results - 'questions'" if kind == 'analysis' else 'results'
            conn.execute(
                f'UPDATE preparations SET results=({expression}) || %s,updated_at=now() WHERE id=%s',
                (Jsonb(results), record),
            )
            if kind == 'analysis':
                conn.execute("DELETE FROM preparation_tasks WHERE record_id=%s AND kind='questions'", (record,))

    @staticmethod
    def _transition_task(conn, record, revision, kind, attempt, status):
        if not conn.execute(
            'UPDATE preparation_tasks SET status=%s,updated_at=now() '
            "WHERE record_id=%s AND revision=%s AND kind=%s AND attempt=%s AND status='running' RETURNING attempt",
            (status, record, revision, kind, attempt),
        ).fetchone():
            raise HistoryConflict()

    def fail_task(self, owner, record, revision, kind, attempt):
        self._kind(kind)
        with self.connect() as conn:
            self._lock_record(conn, owner, record, revision)
            self._transition_task(conn, record, revision, kind, attempt, 'failed')

    def interrupt_tasks_on_startup(self):
        """Only after the old sole worker has stopped, BEFORE accepting requests.

        Never call during live traffic or when merely opening another repository
        connection. Does not resume or invoke models. HTTP startup wiring pending.
        """
        with self.connect() as conn:
            return conn.execute(
                "UPDATE preparation_tasks SET status='interrupted',updated_at=now() "
                "WHERE status='running'",
            ).rowcount

    def publish(self, owner, record, revision, key, result):
        if key not in {'jd', 'resume', 'gap', 'questions'}:
            raise ValueError('unknown result kind')
        with self.connect() as conn:
            row = conn.execute(
                'UPDATE preparations SET results=results || %s,updated_at=now() '
                'WHERE id=%s AND owner_id=%s AND revision=%s RETURNING id',
                (Jsonb({key: result}), record, owner, revision),
            ).fetchone()
            if row is None:
                raise HistoryConflict()
