"""Explicit account-record upload, POST SSE analysis and question generation."""
import asyncio
from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

from api.auth import Identity, get_identity
from api.events import _sse
from api.files import _read_and_parse
from api.record_workflow import MODELS, RecordAccess, RecordOperation
from api.routes.history import RecordDetail, call, store, writer
from api.schemas import QuestionResponse
from core.analyzers.jd_analyzer import analyze_jd
from core.analyzers.resume_analyzer import analyze_resume
from core.analyzers.gap_analyzer import analyze_gap
from core.generators.question_generator import generate_questions
from services.llm_service import LLMService

router = APIRouter()


class Version(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    revision: int = Field(ge=0)


class QuestionsVersion(Version):
    num_questions: int = Field(default=10, ge=10, le=50)


class TaskStatus(BaseModel):
    kind: Literal['analysis', 'questions']
    revision: int
    attempt: UUID
    status: Literal['running', 'completed', 'failed', 'interrupted']
    updated_at: datetime


def access(request, identity, repository, record_id):
    return RecordAccess.capture(request, identity, repository, record_id)


@router.post('/{record_id}/upload/{kind}', response_model=RecordDetail)
async def upload(record_id: UUID, kind: Literal['jd', 'resume'], request: Request,
                 revision: int = Query(ge=0), file: UploadFile = File(...),
                 identity: Identity = Depends(writer), repository=Depends(store)):
    current = access(request, identity, repository, record_id)
    row = current.read()
    if row['revision'] != revision:
        raise HTTPException(409, '资料版本已变化，请刷新记录后重试')
    # Reuse actual parser/tempfile cleanup. No filenames/binary are persisted.
    try:
        text = await _read_and_parse(file)
    except HTTPException as exc:
        if exc.status_code >= 500:
            raise HTTPException(500, '文件解析失败，请检查文件后重试') from None
        raise
    inputs = dict(row['inputs'])
    inputs[kind + '_text'] = text
    return current.mutate('replace_inputs', revision, inputs)


@router.delete('/{record_id}/inputs', response_model=RecordDetail)
def clear(record_id: UUID, body: Version, request: Request,
          identity: Identity = Depends(writer), repository=Depends(store)):
    current = access(request, identity, repository, record_id)
    current.read()  # Uniform foreign/missing 404 before revision mutation.
    return current.mutate('replace_inputs', body.revision, {})


@router.get('/{record_id}/tasks', response_model=list[TaskStatus])
def tasks(record_id: UUID, identity: Identity = Depends(get_identity), repository=Depends(store)):
    return call(repository, 'tasks', identity.owner, record_id)


async def stream(operation):
    cancelled = False
    try:
        inputs = operation.begin()
        llm = await operation.run(LLMService)
        yield _sse('jd_start', '正在解析职位描述... (1/3)')
        jd = MODELS['jd'].model_validate(await operation.run(analyze_jd, inputs['jd_text'], llm))
        yield _sse('jd_done', '职位描述解析完成', {'job_title': jd.job_title})
        yield _sse('resume_start', '正在解析简历... (2/3)')
        resume = MODELS['resume'].model_validate(await operation.run(analyze_resume, inputs['resume_text'], llm))
        yield _sse('resume_done', '简历解析完成')
        yield _sse('gap_start', '正在计算匹配度... (3/3)')
        gap = MODELS['gap'].model_validate(await operation.run(analyze_gap, jd, resume, llm))
        operation.publish({'jd': jd, 'resume': resume, 'gap': gap})
        yield _sse('complete', '分析完成！', gap.model_dump(mode='json'))
    except asyncio.CancelledError:
        cancelled = True
        raise
    except HTTPException as exc:
        yield _sse('error', exc.detail, {'status': exc.status_code})
    except Exception:
        yield _sse('error', '分析失败，请检查服务配置后明确重试', {'status': 500})
    finally:
        operation.close(interrupted=cancelled)


@router.post('/{record_id}/analysis/stream')
async def analysis(record_id: UUID, body: Version, request: Request,
                   identity: Identity = Depends(writer), repository=Depends(store)):
    current = access(request, identity, repository, record_id)
    current.read()
    return StreamingResponse(stream(RecordOperation(current, body.revision, 'analysis')),
        media_type='text/event-stream', headers={'Cache-Control': 'no-store', 'X-Accel-Buffering': 'no'})


@router.get('/{record_id}/analysis/result')
def result(record_id: UUID, identity: Identity = Depends(get_identity), repository=Depends(store)):
    row = call(repository, 'get', identity.owner, record_id)
    if 'gap' not in row['results']:
        raise HTTPException(404, '暂无分析结果，请先进行分析')
    try:
        data = MODELS['gap'].model_validate(row['results']['gap']).model_dump(mode='json')
    except Exception:
        raise HTTPException(503, '已存分析结果不可用，请重新分析') from None
    return {'success': True, 'data': data}


@router.post('/{record_id}/questions/generate', response_model=QuestionResponse)
async def generate(record_id: UUID, body: QuestionsVersion, request: Request,
                   identity: Identity = Depends(writer), repository=Depends(store)):
    current = access(request, identity, repository, record_id)
    current.read()
    operation = RecordOperation(current, body.revision, 'questions')
    cancelled = False
    try:
        inputs = operation.begin()
        llm = await operation.run(LLMService)
        questions = MODELS['questions'].model_validate(await operation.run(generate_questions,
            inputs['gap'], inputs['resume'], inputs['jd'], llm, body.num_questions))
        operation.publish({'questions': questions})
        return QuestionResponse(total=len(questions.questions), questions=questions.model_dump(mode='json')['questions'])
    except asyncio.CancelledError:
        cancelled = True
        raise
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(500, '题目生成失败，请检查服务配置后明确重试') from None
    finally:
        operation.close(interrupted=cancelled)


@router.get('/{record_id}/questions/cached', response_model=QuestionResponse)
def cached(record_id: UUID, identity: Identity = Depends(get_identity), repository=Depends(store)):
    row = call(repository, 'get', identity.owner, record_id)
    if 'questions' not in row['results']:
        raise HTTPException(404, '暂无题目，请先生成')
    try:
        questions = MODELS['questions'].model_validate(row['results']['questions'])
    except Exception:
        raise HTTPException(503, '已存题目不可用，请重新生成') from None
    return QuestionResponse(total=len(questions.questions), questions=questions.model_dump(mode='json')['questions'])
