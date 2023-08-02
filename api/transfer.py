"""Module for transferring requests to ClosedAI API"""

import os
import json
import logging
import starlette

from dotenv import load_dotenv

import netclient
import chat_balancing

from db import logs, users
from helpers import tokens, errors, exceptions

load_dotenv()

# log to "api.log" file
logging.basicConfig(
    filename='api.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

logging.info('API started')

async def handle(incoming_request):
    """Transfer a streaming response from the incoming request to the target endpoint"""

    path = incoming_request.url.path

    if incoming_request.method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
        return errors.error(405, f'Method "{incoming_request.method}" is not allowed.', 'Change the request method to the correct one.')

    try:
        payload = await incoming_request.json()
    except json.decoder.JSONDecodeError:
        payload = {}

    try:
        input_tokens = tokens.count_for_messages(payload['messages'])
    except (KeyError, TypeError):
        input_tokens = 0

    auth_header = incoming_request.headers.get('Authorization')

    if not auth_header:
        return errors.error(401, 'No NovaAI API key given!', 'Add "Authorization: Bearer nv-..." to your request headers.')

    received_key = auth_header

    if auth_header.startswith('Bearer '):
        received_key = auth_header.split('Bearer ')[1]

    user = await users.by_api_key(received_key)

    if not user:
        return errors.error(401, 'Invalid NovaAI API key!', 'Create a new NovaOSS API key.')

    ban_reason = user['status']['ban_reason']
    if ban_reason:
        return errors.error(403, f'Your NovaAI account has been banned. Reason: "{ban_reason}".', 'Contact the staff for an appeal.')

    if not user['status']['active']:
        return errors.error(418, 'Your NovaAI account is not active (paused).', 'Simply re-activate your account using a Discord command or the web panel.')

    payload['user'] = str(user['_id'])

    cost = 1

    if '/chat/completions' in path:
        cost = 5

        if 'gpt-4' in payload['model']:
            cost = 10

    else:
        return errors.error(404, f'Sorry, we don\'t support "{path}" yet. We\'re working on it.', 'Contact our team.')

    if not payload.get('stream') is True:
        payload['stream'] = False

    if user['credits'] < cost:
        return errors.error(429, 'Not enough credits.', 'You do not have enough credits to complete this request.')

    await users.update_by_id(user['_id'], {'$inc': {'credits': -cost}})

    target_request = await chat_balancing.balance(payload)

    print(target_request['url'])

    return starlette.responses.StreamingResponse(netclient.stream(target_request))
