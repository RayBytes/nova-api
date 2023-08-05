"""Module for transferring requests to ClosedAI API"""

import os
import json
import yaml
import logging
import starlette

from dotenv import load_dotenv

import streaming

from db import logs, users
from helpers import tokens, errors, exceptions

load_dotenv()

# log to "api.log" file
logging.basicConfig(
    filename='api.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

with open('config/credits.yml', encoding='utf8') as f:
    credits_config = yaml.safe_load(f)

async def handle(incoming_request):
    """Transfer a streaming response from the incoming request to the target endpoint"""

    path = incoming_request.url.path

    # METHOD
    if incoming_request.method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
        return errors.error(405, f'Method "{incoming_request.method}" is not allowed.', 'Change the request method to the correct one.')

    # PAYLOAD
    try:
        payload = await incoming_request.json()
    except json.decoder.JSONDecodeError:
        payload = {}

    # TOKENS
    try:
        input_tokens = tokens.count_for_messages(payload['messages'])
    except (KeyError, TypeError):
        input_tokens = 0

    # AUTH
    received_key = incoming_request.headers.get('Authorization')

    if not received_key:
        return errors.error(401, 'No NovaAI API key given!', 'Add "Authorization: Bearer nv-..." to your request headers.')

    if received_key.startswith('Bearer '):
        received_key = received_key.split('Bearer ')[1]

    # USER
    user = await users.by_api_key(received_key.strip())

    if not user:
        return errors.error(401, 'Invalid NovaAI API key!', 'Create a new NovaOSS API key.')

    ban_reason = user['status']['ban_reason']
    if ban_reason:
        return errors.error(403, f'Your NovaAI account has been banned. Reason: "{ban_reason}".', 'Contact the staff for an appeal.')

    if not user['status']['active']:
        return errors.error(418, 'Your NovaAI account is not active (paused).', 'Simply re-activate your account using a Discord command or the web panel.')

    # COST
    costs = credits_config['costs']
    cost = costs['other']

    if 'chat/completions' in path:
        for model_name, model_cost in costs['chat-models'].items():
            if model_name in payload['model']:
                cost = model_cost

    role_cost_multiplier = credits_config['bonuses'].get(user['role'], 1)
    cost = round(cost * role_cost_multiplier)

    if user['credits'] < cost:
        return errors.error(429, 'Not enough credits.', 'Wait or earn more credits. Learn more on our website or Discord server.')

    # READY

    payload['user'] = str(user['_id'])

    if 'chat/completions' in path and not payload.get('stream') is True:
        payload['stream'] = False

    return starlette.responses.StreamingResponse(
        content=streaming.stream(
            user=user,
            path=path,
            payload=payload,
            credits_cost=cost,
            input_tokens=input_tokens,
            incoming_request=incoming_request,
        ),
        media_type='text/event-stream' if payload.get('stream', False) else 'application/json'
    )
