import os
import httpx
import fastapi

from starlette.requests import Request
from starlette.responses import StreamingResponse
from starlette.background import BackgroundTask
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

import security

load_dotenv()
target_api_client = httpx.AsyncClient(base_url='https://api.openai.com/')

app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

@app.on_event('startup')
async def startup_event():
    """Read up the API server."""

    security.enable_proxy()
    security.ip_protection_check()

@app.get('/')
async def root():
    """Returns the root endpoint."""

    return {
        'status': 'ok',
        'discord': 'https://discord.gg/mX9BYdFeQF',
        'github': 'https://github.com/Luna-OSS'
    }

async def _reverse_proxy(request: Request):
    target_url = f'https://api.openai.com/v1/{request.url.path}'

    request_to_api = target_api_client.build_request(
        method=request.method,
        url=target_url,
        headers={
            'Authorization': 'Bearer ' + os.getenv('OPENAI_KEY'),
            'Content-Type': 'application/json'
        },
        content=await request.body(),
    )

    api_response = await target_api_client.send(request_to_api, stream=True)

    print(f'[{request.method}] {request.url.path} {api_response.status_code}')

    return StreamingResponse(
        api_response.aiter_raw(),
        status_code=api_response.status_code,
        headers=api_response.headers,
        background=BackgroundTask(api_response.aclose)
    )

app.add_route('/{path:path}', _reverse_proxy, ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
