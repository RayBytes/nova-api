"""This module contains the streaming logic for the API."""

import os
import json
import dhooks
import asyncio
import aiohttp
import starlette
import datetime

from rich import print
from dotenv import load_dotenv
from python_socks._errors import ProxyError

import proxies
import provider_auth
import load_balancing

from db import logs
from db.users import UserManager
from db.stats import StatsManager
from helpers import network, chat, errors
import yaml


load_dotenv()

## Loads config which contains rate limits
with open('config/config.yml', encoding='utf8') as f:
    config = yaml.safe_load(f)

## Where all rate limit requested data will be stored.
# Rate limit data is **not persistent** (It will be deleted on server stop/restart).
user_last_request_time = {}

DEMO_PAYLOAD = {
    'model': 'gpt-3.5-turbo',
    'messages': [
        {
            'role': 'user',
            'content': '1+1='
        }
    ]
}

async def process_response(response, is_chat, chat_id, model, target_request):
    """Proccesses chunks from streaming

    Args:
        response (_type_): The response
        is_chat (bool): If there is 'chat/completions' in path
        chat_id (_type_): ID of chat with bot
        model (_type_): What AI model it is
    """
    async for chunk in response.content.iter_any():
        chunk = chunk.decode("utf8").strip()
        send = False

        if is_chat and '{' in chunk:
            data = json.loads(chunk.split('data: ')[1])
            chunk = chunk.replace(data['id'], chat_id)
            send = True

            if target_request['module'] == 'twa' and data.get('text'):
                chunk = await chat.create_chat_chunk(chat_id=chat_id, model=model, content=['text'])

            if (not data['choices'][0]['delta']) or data['choices'][0]['delta'] == {'role': 'assistant'}:
                send = False

        if send and chunk:
            yield chunk + '\n\n'

async def stream(
    path: str='/v1/chat/completions',
    user: dict=None,
    payload: dict=None,
    credits_cost: int=0,
    input_tokens: int=0,
    incoming_request: starlette.requests.Request=None,
):
    """Stream the completions request. Sends data in chunks
    If not streaming, it sends the result in its entirety.

    Args:
        path (str, optional): URL Path. Defaults to '/v1/chat/completions'.
        user (dict, optional): User object (dict) Defaults to None.
        payload (dict, optional): Payload. Defaults to None.
        credits_cost (int, optional): Cost of the credits of the request. Defaults to 0.
        input_tokens (int, optional): Total tokens calculated with tokenizer. Defaults to 0.
        incoming_request (starlette.requests.Request, optional): Incoming request. Defaults to None.
    """

    ## Rate limits user.
    # If rate limit is exceeded, error code 429. Otherwise, lets the user pass but notes down
    # last request time for future requests.
    if user:
        role = user.get('role', 'default')
        rate_limit = config['roles'][role]['rate_limit'].get(payload['model'], 10)

        last_request_time = user_last_request_time.get(user['api_key'])
        time_since_last_request = datetime.now() - last_request_time

        if time_since_last_request < datetime.timedelta(seconds=rate_limit):
            yield await errors.yield_error(429, "Rate limit exceeded', 'You are making requests too quickly. Please wait and try again later. Ask a administrator if you think this shouldn't happen. ")
            return
        else:
            user_last_request_time[user['_id']] = datetime.now()

    ## Setup managers
    db = UserManager()
    stats = StatsManager()

    is_chat = False
    is_stream = payload.get('stream', False)

    if 'chat/completions' in path:
        is_chat = True
        model = payload['model']

    if is_chat and is_stream:
        chat_id = await chat.create_chat_id()
        yield await chat.create_chat_chunk(chat_id=chat_id, model=model, content=chat.CompletionStart)
        yield await chat.create_chat_chunk(chat_id=chat_id, model=model, content=None)

    json_response = {'error': 'No JSON response could be received'}

    for _ in range(5):
        headers = {'Content-Type': 'application/json'}


        # Load balancing
        # If the request is a chat completion, then we need to load balance between chat providers
        # If the request is an organic request, then we need to load balance between organic providers

        try:
            if is_chat:
                target_request = await load_balancing.balance_chat_request(payload)
            else:
                
                # In this case we are doing a organic request. "organic" means that it's not using a reverse engineered front-end, but rather ClosedAI's API directly
                # churchless.tech is an example of an organic provider, because it redirects the request to ClosedAI.
                target_request = await load_balancing.balance_organic_request({
                    'method': incoming_request.method,
                    'path': path,
                    'payload': payload,
                    'headers': headers,
                    'cookies': incoming_request.cookies
                })
        except ValueError as exc:
            webhook = dhooks.Webhook(os.getenv('DISCORD_WEBHOOK__API_ISSUE'))
            webhook.send(content=f'API Issue: **`{exc}`**\nhttps://i.imgflip.com/7uv122.jpg')
            yield await errors.yield_error(500, 'Sorry, the API has no working keys anymore.', 'The admins have been messaged automatically.')
            return

        target_request['headers'].update(target_request.get('headers', {}))

        if target_request['method'] == 'GET' and not payload:
            target_request['payload'] = None

        # We haven't done any requests as of right now, everything until now was just preparation
        # Here, we process the request
        async with aiohttp.ClientSession(connector=proxies.get_proxy().connector) as session:
            try:
                async with session.request(
                    method=target_request.get('method', 'POST'),
                    url=target_request['url'],
                    data=target_request.get('data'),
                    json=target_request.get('payload'),
                    headers=target_request.get('headers', {}),
                    cookies=target_request.get('cookies'),
                    ssl=False,
                    timeout=aiohttp.ClientTimeout(total=float(os.getenv('TRANSFER_TIMEOUT', '120'))),
                ) as response:
                    if response.content_type == 'application/json':
                        data = await response.json()

                        if data.get('code') == 'invalid_api_key':
                            await provider_auth.invalidate_key(target_request.get('provider_auth'))
                            continue

                        if response.ok:
                            json_response = data

                    if is_stream:
                        try:
                            response.raise_for_status()
                        except Exception as exc:
                            if 'Too Many Requests' in str(exc):
                                continue

                        async for chunk in process_response(response, is_chat, chat_id, model, target_request):
                            yield chunk

                    break

            except ProxyError as exc:
                print('[!] Proxy error:', exc)
                continue

    if is_chat and is_stream:
        yield await chat.create_chat_chunk(chat_id=chat_id, model=model, content=chat.CompletionStop)
        yield 'data: [DONE]\n\n'

    if not is_stream and json_response:
        yield json.dumps(json_response)

    if user and incoming_request:
        await logs.log_api_request(user=user, incoming_request=incoming_request, target_url=target_request['url'])

    if credits_cost and user:
        await db.update_by_id(user['_id'], {'$inc': {'credits': -credits_cost}})

    ip_address = await network.get_ip(incoming_request)
    await stats.add_date()
    await stats.add_ip_address(ip_address)
    await stats.add_path(path)
    await stats.add_target(target_request['url'])
    if is_chat:
        await stats.add_model(model)
        await stats.add_tokens(input_tokens, model)

if __name__ == '__main__':
    asyncio.run(stream())
