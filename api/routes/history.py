"""Account-owned record management; no model calls or anonymous data migration."""
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, field_validator

from api.auth import Identity, get_auth, get_identity
from api.history_errors import HistoryConflict, HistoryFull, HistoryMissing

router = APIRouter()


class RecordTitle(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    title: str

    @field_validator('title')
    @classmethod
    def valid_title(cls, value):
        value = value.strip()
        if not 1 <= len(value) <= 100:
            raise ValueError('title must contain 1–100 characters')
        return value


class RecordSummary(BaseModel):
    id: UUID
    title: str
    revision: int
    created_at: datetime
    updated_at: datetime


class RecordDetail(RecordSummary):
    inputs: dict
    results: dict


def writer(request: Request, identity: Identity = Depends(get_identity)) -> Identity:
    # SameSite is defense in depth; every cookie-authenticated write also checks
    # the exact configured frontend origin, including loopback development.
    if request.headers.get('origin') != get_auth(request).config.frontend_origin.rstrip('/'):
        raise HTTPException(403, '记录修改请求来源无效')
    return identity


def store(request: Request):
    repository = getattr(request.app.state, 'history_store', None)
    if repository is None:
        raise HTTPException(503, '历史存储尚未配置')
    return repository


def call(repository, method, *args):
    try:
        return getattr(repository, method)(*args)
    except HistoryMissing:
        raise HTTPException(404, '记录不存在') from None
    except HistoryFull:
        raise HTTPException(409, '历史记录已达20份，请先删除不需要的记录') from None
    except HistoryConflict:
        raise HTTPException(409, '资料版本已变化或任务仍在运行，请刷新记录后重试') from None
    except Exception:
        # Never expose SQL, DSNs, input text or provider payloads. Do not retry a
        # mutation automatically: a lost connection may follow a committed write.
        raise HTTPException(503, '历史存储暂不可用，请刷新记录后重试') from None


@router.get('', response_model=list[RecordSummary])
def list_records(identity: Identity = Depends(get_identity), repository=Depends(store)):
    return call(repository, 'list', identity.owner)


@router.post('', response_model=RecordDetail, status_code=201)
def create_record(body: RecordTitle, identity: Identity = Depends(writer), repository=Depends(store)):
    return call(repository, 'create', identity.owner, body.title)


@router.get('/{record_id}', response_model=RecordDetail)
def read_record(record_id: UUID, identity: Identity = Depends(get_identity), repository=Depends(store)):
    return call(repository, 'get', identity.owner, record_id)


@router.patch('/{record_id}', response_model=RecordDetail)
def rename_record(record_id: UUID, body: RecordTitle, identity: Identity = Depends(writer), repository=Depends(store)):
    return call(repository, 'rename', identity.owner, record_id, body.title)


@router.delete('/{record_id}', status_code=204)
def delete_record(record_id: UUID, identity: Identity = Depends(writer), repository=Depends(store)):
    call(repository, 'delete', identity.owner, record_id)
    return Response(status_code=204)
