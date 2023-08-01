"""FastAPI setup."""

import fastapi

from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

import core
import users
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

app.include_router(core.router)

@app.on_event('startup')
async def startup_event():
    await users.prepare()

@app.get('/')
async def root():
    """Returns the root endpoint."""

    return {
        'status': 'ok',
        'usage_docs': 'https://nova-oss.com',
        'core_api_docs_for_developers': '/docs',
        'github': 'https://github.com/novaoss/nova-api'
    }

app.add_route('/{path:path}', transfer.handle_api_request, ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
