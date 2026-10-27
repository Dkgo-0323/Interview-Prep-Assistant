"""Account-record coordinator. No process-wide current record or model retry.

Only short storage transitions hold the auth lock, linearizing logout against
publication. Synchronous provider work runs outside both auth and DB locks.
"""
import asyncio
from dataclasses import dataclass, field

from fastapi import HTTPException
from pydantic import BaseModel

from api.auth import AUTH_COOKIE, get_auth
from api.routes.history import call
from models.schemas import GapAnalysis, JDInfo, QuestionList, ResumeInfo


MODELS = {'jd': JDInfo, 'resume': ResumeInfo, 'gap': GapAnalysis, 'questions': QuestionList}


def validated(key, value):
    # model_validate(instance) normally trusts that instance, including fields
    # mutated after construction. Round-trip its values to recheck constraints.
    return MODELS[key].model_validate(value.model_dump() if isinstance(value, BaseModel) else value)


@dataclass
class RecordAccess:
    auth: object
    token: str = field(repr=False)
    identity: object
    repository: object
    record: object

    @classmethod
    def capture(cls, request, identity, repository, record):
        return cls(get_auth(request), request.cookies.get(AUTH_COOKIE), identity, repository, record)

    def check(self):
        if self.auth.resolve(self.token) is not self.identity:
            raise HTTPException(401, '原登录会话已失效，请重新登录')

    def mutate(self, method, *args):
        with self.auth.lock:
            self.check()
            return call(self.repository, method, self.identity.owner, self.record, *args)

    def read(self):
        with self.auth.lock:
            self.check()
            return call(self.repository, 'get', self.identity.owner, self.record)


class RecordOperation:
    def __init__(self, access, revision, kind):
        self.access, self.revision, self.kind = access, revision, kind
        self.attempt = None
        self.pending = None
        self.done = False

    def begin(self):
        task = self.access.mutate('claim_task', self.revision, self.kind)
        self.attempt = task['attempt']
        snapshot = self.check()
        if self.kind == 'analysis':
            if any(not snapshot['inputs'].get(key) for key in ('jd_text', 'resume_text')):
                raise HTTPException(400, '请先上传职位描述 (JD) 文件和简历')
            return dict(snapshot['inputs'])
        if any(key not in snapshot['results'] for key in ('jd', 'resume', 'gap')):
            raise HTTPException(400, '请先完成智能分析')
        return {key: MODELS[key].model_validate(snapshot['results'][key]) for key in ('jd', 'resume', 'gap')}

    def check(self):
        row = self.access.read()
        tasks = call(self.access.repository, 'tasks', self.access.identity.owner, self.access.record)
        if row['revision'] != self.revision or not any(
            task['kind'] == self.kind and task['attempt'] == self.attempt
            and task['revision'] == self.revision and task['status'] == 'running' for task in tasks
        ):
            raise HTTPException(409, '资料或任务已变化，请刷新记录后重试')
        return row

    async def run(self, function, *args):
        self.check()
        task = asyncio.create_task(asyncio.to_thread(function, *args))
        self.pending = task
        # Keep a strong reference and consume a late exception on disconnect.
        task.add_done_callback(lambda completed: completed.exception() if not completed.cancelled() else None)
        result = await asyncio.shield(task)
        self.pending = None
        self.check()
        return result

    def publish(self, values):
        # Validate complete domain objects before any JSON reaches persistence.
        snapshot = {key: validated(key, value).model_dump(mode='json')
                    for key, value in values.items()}
        self.access.mutate('finish_task', self.revision, self.kind, self.attempt, snapshot)
        self.done = True

    def close(self, interrupted=False):
        if self.done or self.attempt is None:
            return
        self.done = True

        def cleanup(_=None):
            needs_interruption = interrupted
            if not needs_interruption:
                try:
                    # Failure is also an authorized transition; revoked sessions
                    # may only trigger exact-attempt lifecycle interruption below.
                    self.access.mutate('fail_task', self.revision, self.kind, self.attempt)
                except HTTPException as exc:
                    needs_interruption = exc.status_code == 401
                # Stale attempts never mutate newer work. No cleanup retry.
            if needs_interruption:
                try:
                    call(self.access.repository, 'interrupt_task', self.access.identity.owner,
                         self.access.record, self.revision, self.kind, self.attempt)
                except HTTPException:
                    pass  # Deleted/replaced/storage unavailable; startup is recovery.

        if self.pending is not None and not self.pending.done():
            self.pending.add_done_callback(cleanup)
        else:
            cleanup()
