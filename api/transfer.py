"""Does quite a few checks and prepares the incoming request for the target endpoint, so it can be streamed"""

import json
import yaml
import fastapi

from dotenv import load_dotenv

import streaming
import moderation

from db import users
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

    path = incoming_request.url.path.replace('v1/v1/', 'v1/')

    # METHOD
    if incoming_request.method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
        return await errors.error(405, f'Method "{incoming_request.method}" is not allowed.', 'Change the request method to the correct one.')

    # PAYLOAD
    try:
        payload = await incoming_request.json()
    except json.decoder.JSONDecodeError:
        payload = {}

    # Tokenise w/ tiktoken
    try:
        input_tokens = await tokens.count_for_messages(payload['messages'])
    except (KeyError, TypeError):
        input_tokens = 0

    # Check user auth
    received_key = incoming_request.headers.get('Authorization')

    if not received_key:
        return await errors.error(401, 'No NovaAI API key given!', 'Add "Authorization: Bearer nv-..." to your request headers.')

    if received_key.startswith('Bearer '):
        received_key = received_key.split('Bearer ')[1]

    user = await users.by_api_key(received_key.strip())

    if not user:
        return await errors.error(401, 'Invalid NovaAI API key!', 'Create a new NovaOSS API key.')

    ban_reason = user['status']['ban_reason']
    if ban_reason:
        return await errors.error(403, f'Your NovaAI account has been banned. Reason: "{ban_reason}".', 'Contact the staff for an appeal.')

    if not user['status']['active']:
        return await errors.error(418, 'Your NovaAI account is not active (paused).', 'Simply re-activate your account using a Discord command or the web panel.')

    if '/models' in path:
        return fastapi.responses.JSONResponse(content=models_list)

    # Calculate cost of tokens & check for nsfw prompts
    costs = credits_config['costs']
    cost = costs['other']

    policy_violation = False

    if 'chat/completions' in path:
        for model_name, model_cost in costs['chat-models'].items():
            if model_name in payload['model']:
                cost = model_cost

        policy_violation = await moderation.is_policy_violated(payload['messages'])

    elif '/moderations' in path:
        pass

    else:
        inp = payload.get('input', payload.get('prompt'))

        if inp:
            if len(inp) > 2 and not inp.isnumeric():
                policy_violation = await moderation.is_policy_violated(inp)

    if policy_violation:
        return await errors.error(400, f'The request contains content which violates this model\'s policies for "{policy_violation}".', 'We currently don\'t support any NSFW models.')


    role_cost_multiplier = credits_config['bonuses'].get(user['role'], 1)
    cost = round(cost * role_cost_multiplier)

    if user['credits'] < cost:
        return await errors.error(429, 'Not enough credits.', 'Wait or earn more credits. Learn more on our website or Discord server.')


    # Send the completion request

    if 'chat/completions' in path and not payload.get('stream') is True:
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
