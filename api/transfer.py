"""Module for transferring requests to ClosedAI API"""

import os
import json
import tokens
import logging
import starlette

from dotenv import load_dotenv
from helpers import requesting, tokens, errors

load_dotenv()

# log to "api.log" file
logging.basicConfig(
    filename='api.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

logging.info('API started')

DEFAULT_ENDPOINT = os.getenv('CLOSEDAI_ENDPOINT')

async def handle_api_request(incoming_request, target_endpoint: str=DEFAULT_ENDPOINT):
    """Transfer a streaming response from the incoming request to the target endpoint"""

    target_url = f'{target_endpoint}{incoming_request.url.path}'

    if incoming_request.method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
        return errors.error(405, f'Method "{incoming_request.method}" is not allowed.', 'Change the request method to the correct one.')

    try:
        payload = await incoming_request.json()
    except json.decoder.JSONDecodeError:
        payload = {}

    try:
        input_tokens = tokens.count_for_messages(payload['messages'])
    except:
        input_tokens = 0

    auth_header = incoming_request.headers.get('Authorization')

    if not auth_header:
        return errors.error(401, 'No NovaOSS API key given!', 'Add "Authorization: Bearer nv-..." to your request headers.')

    received_key = auth_header

    if auth_header.startswith('Bearer '):
        received_key = auth_header.split('Bearer ')[1]

    user = users.get_user(by_api_key=received_key)

    if not user:
        return errors.error(401, 'Invalid NovaOSS API key!', 'Create a new NovaOSS API key.')

    if not user['active']:
        return errors.error(403, 'Your account is not active.', 'Activate your account.')

    logging.info(f'[%s] %s -> %s', incoming_request.method, incoming_request.url.path, target_url)

    request = requesting.Request(
        url=target_url,
        payload=payload,
        method=incoming_request.method,
    )

    return starlette.responses.StreamingResponse(
        content=netclient.stream_closedai_request(request)
    )
