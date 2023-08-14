"""FastAPI setup."""

import fastapi

from rich import print
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import core
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
    # DATABASE FIX https://stackoverflow.com/questions/65970988/python-mongodb-motor-objectid-object-is-not-iterable-error-while-trying-to-f
    import pydantic, bson
    pydantic.json.ENCODERS_BY_TYPE[bson.objectid.ObjectId]=str

@app.get('/')
async def root():
    """
    Returns the root endpoint.
    """

    return {
        'status': 'ok',
        'usage_docs': 'https://nova-oss.com',
        'core_api_docs_for_developers': '/docs',
        'github': 'https://github.com/novaoss/nova-api'
    }

app.add_route('/{path:path}', transfer.handle, ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
