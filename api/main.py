"""FastAPI setup."""

import fastapi
import asyncio

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
    # await security.ip_protection_check()

@app.get('/')
async def root():
    """Returns the root endpoint."""

    return {
        'status': 'ok',
        'readme': 'https://nova-oss.com'
    }

@app.route('/v1')
async def api_root():
    """Returns the API root endpoint."""

    return {
        'status': 'ok',
    }

app.add_route('/{path:path}', transfer.transfer_streaming_response, ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
