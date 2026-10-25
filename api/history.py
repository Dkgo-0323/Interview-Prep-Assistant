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
        source = Path(__file__).resolve().parents[1] / 'db/migrations/001_history.sql'
        with self.connect() as conn:
            # Serialize concurrent initializers. Versioned migrations are explicit,
            # never executed as a side effect of importing the application.
            conn.execute('SELECT pg_advisory_xact_lock(712649001)')
            conn.execute(source.read_text(encoding='utf-8-sig'))

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
            return row

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
