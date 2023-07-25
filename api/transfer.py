"""Module for transferring requests to ClosedAI API"""

import os
import json
import aiohttp
import logging
import starlette
import netclient

import proxies

from dotenv import load_dotenv

from starlette.background import StreamingResponse

load_dotenv()

# log to "api.log" file
logging.basicConfig(
    filename='api.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

logging.info('API started')

EXCLUDED_HEADERS = [
    'content-encoding',
    'content-length',
    'transfer-encoding',
    'connection'
]

async def handle_api_request(incoming_request, target_endpoint: str=''):
    """Transfer a streaming response from the incoming request to the target endpoint"""
    if not target_endpoint:
        target_endpoint = os.getenv('CLOSEDAI_ENDPOINT')

    target_url = f'{target_endpoint}{incoming_request.url.path}'.replace('/v1/v1', '/v1')
    logging.info('TRANSFER %s -> %s', incoming_request.url.path, target_url)

    if target_url.endswith('/v1'):
        return starlette.responses.Response(status_code=200, content='200. /v1 is the API endpoint root path.')

    if incoming_request.headers.get('Authorization') != f'Bearer {os.getenv("DEMO_AUTH")}':
        return starlette.responses.Response(status_code=403, content='Invalid API key')

    try:
        payload = await incoming_request.json()
    except json.decoder.JSONDecodeError:
        payload = {}

    target_provider = 'moe'

    if 'temperature' in payload or 'functions' in payload:
        target_provider = 'closed'

    return StreamingResponse(
        content=netclient.receive_target_stream()
    )
