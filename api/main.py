import os
import fastapi

from starlette.responses import StreamingResponse
from starlette.requests import Request
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

import security
import transfer

load_dotenv()

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
        'discord': 'https://discord.gg/85gdcd57Xr',
        'github': 'https://github.com/Luna-OSS'
    }

async def _reverse_proxy(request: Request):
    headers = {
        name: value
        for name, value in target_response.headers.items()
        if name.lower() not in EXCLUDED_HEADERS
    }

    # ...

app.add_route('/{path:path}', _reverse_proxy, ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
