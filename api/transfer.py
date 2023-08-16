"""Does quite a few checks and prepares the incoming request for the target endpoint, so it can be streamed"""

import json
import yaml
import fastapi

from dotenv import load_dotenv

import streaming
import moderation

from db.users import UserManager
from helpers import tokens, errors

load_dotenv()

models_list = json.load(open('models.json'))

with open('config/credits.yml', encoding='utf8') as f:
    credits_config = yaml.safe_load(f)

async def handle(incoming_request):
    """
    ### Transfer a streaming response 
    Takes the request from the incoming request to the target endpoint.
    Checks method, token amount, auth and cost along with if request is NSFW.
    """
    users = UserManager()
    path = incoming_request.url.path.replace('v1/v1/', 'v1/')

    allowed_methods = {'GET', 'POST', 'PUT', 'DELETE', 'PATCH'}
    method = incoming_request.method

    if method not in allowed_methods:
        return await errors.error(405, f'Method "{method}" is not allowed.', 'Change the request method to the correct one.')

    try:
        payload = await incoming_request.json()
    except json.decoder.JSONDecodeError:
        payload = {}

    try:
        input_tokens = await tokens.count_for_messages(payload.get('messages', []))
    except (KeyError, TypeError):
        input_tokens = 0

    received_key = incoming_request.headers.get('Authorization')

    if not received_key or not received_key.startswith('Bearer '):
        return await errors.error(401, 'No NovaAI API key given!', 'Add "Authorization: Bearer nv-..." to your request headers.')

    user = await users.user_by_api_key(received_key.split('Bearer ')[1].strip())

    if not user or not user['status']['active']:
        return await errors.error(401, 'Invalid or inactive NovaAI API key!', 'Create a new NovaOSS API key or reactivate your account.')

    ban_reason = user['status']['ban_reason']
    if ban_reason:
        return await errors.error(403, f'Your NovaAI account has been banned. Reason: "{ban_reason}".', 'Contact the staff for an appeal.')

    path_contains_models = '/models' in path
    if path_contains_models:
        return fastapi.responses.JSONResponse(content=models_list)

    costs = credits_config['costs']
    cost = costs['other']

    if 'chat/completions' in path:
        cost = costs['chat-models'].get(payload.get('model'), cost)

    policy_violation = False
    if 'chat/completions' in path or ('input' in payload or 'prompt' in payload):
        inp = payload.get('input', payload.get('prompt', ''))
        if inp and len(inp) > 2 and not inp.isnumeric():
            policy_violation = await moderation.is_policy_violated(inp)

    if policy_violation:
        return await errors.error(400, f'The request contains content which violates this model\'s policies for "{policy_violation}".', 'We currently don\'t support any NSFW models.')

    role_cost_multiplier = credits_config['bonuses'].get(user['role'], 1)
    cost = round(cost * role_cost_multiplier)

    if user['credits'] < cost:
        return await errors.error(429, 'Not enough credits.', 'Wait or earn more credits. Learn more on our website or Discord server.')

    if 'chat/completions' in path and not payload.get('stream', False):
        payload['stream'] = False

    media_type = 'text/event-stream' if payload.get('stream', False) else 'application/json'

    return fastapi.responses.StreamingResponse(
        content=streaming.stream(
            user=user,
            path=path,
            payload=payload,
            credits_cost=cost,
            input_tokens=input_tokens,
            incoming_request=incoming_request,
        ),
        media_type=media_type
    )
