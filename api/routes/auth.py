"""Optional account endpoints, separate from the existing anonymous application."""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

from api.auth import AUTH_COOKIE, FLOW_COOKIE, Identity, get_auth, get_identity

router = APIRouter()


def private(response):
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response


@router.get('/github/login')
def login(request: Request):
    service = get_auth(request)
    binding, url = service.start(request.cookies.get(FLOW_COOKIE))
    response = private(RedirectResponse(url, status_code=303))
    response.set_cookie(FLOW_COOKIE, binding, max_age=600, httponly=True,
                        secure=service.config.secure, samesite='lax', path='/api/auth')
    return response


@router.get('/github/callback')
def callback(request: Request, state: str = '', code: str = ''):
    service = get_auth(request)
    try:
        token = service.finish(request.cookies.get(FLOW_COOKIE), state, code,
                               request.cookies.get(AUTH_COOKIE))
        response = RedirectResponse(service.config.frontend_origin.rstrip('/') + '/', status_code=303)
        response.set_cookie(AUTH_COOKIE, token, httponly=True, secure=service.config.secure,
                            samesite='lax', path='/api', max_age=int(service.ttl))
    except HTTPException as exc:
        response = JSONResponse({'detail': exc.detail}, status_code=exc.status_code)
    response.delete_cookie(FLOW_COOKIE, path='/api/auth', secure=service.config.secure, httponly=True, samesite='lax')
    return private(response)


@router.get('/me')
def me(identity: Identity = Depends(get_identity)):
    return private(JSONResponse({'account_id': str(identity.owner)}))


@router.post('/logout')
def logout(request: Request):
    service = get_auth(request)
    if request.headers.get('origin') != service.config.frontend_origin.rstrip('/'):
        raise HTTPException(403, '退出请求来源无效')
    service.logout(request.cookies.get(AUTH_COOKIE), request.cookies.get(FLOW_COOKIE))
    response = private(JSONResponse({'success': True}))
    for name, path in ((AUTH_COOKIE, '/api'), (FLOW_COOKIE, '/api/auth')):
        response.delete_cookie(name, path=path, secure=service.config.secure, httponly=True, samesite='lax')
    return response
