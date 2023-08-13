"""This module contains the streaming logic for the API."""

import os
import json
import dhooks
import asyncio
import aiohttp
import starlette

from rich import print
from dotenv import load_dotenv
from python_socks._errors import ProxyError

import proxies
import provider_auth
import load_balancing

from db import logs, users, stats
from helpers import network, chat, errors

load_dotenv()

DEMO_PAYLOAD = {
    'model': 'gpt-3.5-turbo',
    'messages': [
        {
            'role': 'user',
            'content': '1+1='
        }
    ]
}

async def stream(
    path: str='/v1/chat/completions',
    user: dict=None,
    payload: dict=None,
    credits_cost: int=0,
    input_tokens: int=0,
    incoming_request: starlette.requests.Request=None,
):
    """Stream the completions request. Sends data in chunks

    Args:
        path (str, optional): URL Path. Defaults to '/v1/chat/completions'.
        user (dict, optional): User object (dict) Defaults to None.
        payload (dict, optional): Payload. Defaults to None.
        credits_cost (int, optional): Cost of the credits of the request. Defaults to 0.
        input_tokens (int, optional): Total tokens calculated with tokenizer. Defaults to 0.
        incoming_request (starlette.requests.Request, optional): Incoming request. Defaults to None.
    """
    is_chat = False
    is_stream = payload.get('stream', False)

    if 'chat/completions' in path:
        is_chat = True
        model = payload['model']

    # Chat completions always have the same beginning
    if is_chat and is_stream:
        chat_id = await chat.create_chat_id()

        chunk = await chat.create_chat_chunk(
            chat_id=chat_id,
            model=model,
            content=chat.CompletionStart
        )
        yield chunk

        chunk = await chat.create_chat_chunk(
            chat_id=chat_id,
            model=model,
            content=None
        )

        yield chunk

    json_response = {
        'error': 'No JSON response could be received'
    }

    # Try to get a response from the API
    for _ in range(5):
        headers = {
            'Content-Type': 'application/json'
        }

        # Load balancing
        # If the request is a chat completion, then we need to load balance between chat providers
        # If the request is an organic request, then we need to load balance between organic providers

        try:
            if is_chat:
                target_request = await load_balancing.balance_chat_request(payload)
            else:
                # "organic" means that it's not using a reverse engineered front-end, but rather ClosedAI's API directly
                # churchless.tech is an example of an organic provider, because it redirects the request to ClosedAI.
                target_request = await load_balancing.balance_organic_request({
                    'method': incoming_request.method,
                    'path': path,
                    'payload': payload,
                    'headers': headers,
                    'cookies': incoming_request.cookies
                })
        except ValueError as exc:
            # Error load balancing? Send a webhook to the admins
            webhook = dhooks.Webhook(os.getenv('DISCORD_WEBHOOK__API_ISSUE'))
            webhook.send(content=f'API Issue: **`{exc}`**\nhttps://i.imgflip.com/7uv122.jpg')

            yield await errors.yield_error(
                500,
                'Sorry, the API has no working keys anymore.',
                'The admins have been messaged automatically.'
            )
            return

        for k, v in target_request.get('headers', {}).items():
            target_request['headers'][k] = v

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
                    # if the answer is JSON
                    if response.content_type == 'application/json':
                        data = await response.json()

                        # Invalidate the key if it's not working
                        if data.get('code') == 'invalid_api_key':
                            await provider_auth.invalidate_key(target_request.get('provider_auth'))
                            continue

                        if response.ok:
                            json_response = data

                    # if the answer is a stream
                    if is_stream:
                        try:
                            response.raise_for_status()
                        except Exception as exc:
                            # Rate limit? Balance again
                            if 'Too Many Requests' in str(exc):
                                continue

                        try:
                            # process the response chunks
                            async for chunk in response.content.iter_any():
                                send = False
                                chunk = f'{chunk.decode("utf8")}\n\n'

                                if is_chat and '{' in chunk:
                                    # parse the JSON
                                    data = json.loads(chunk.split('data: ')[1])
                                    chunk = chunk.replace(data['id'], chat_id)
                                    send = True

                                    # create a custom chunk if we're using specific providers
                                    if target_request['module'] == 'twa' and data.get('text'):
                                        chunk = await chat.create_chat_chunk(
                                            chat_id=chat_id,
                                            model=model,
                                            content=['text']
                                        )

                                    # don't send empty/unnecessary messages
                                    if (not data['choices'][0]['delta']) or data['choices'][0]['delta'] == {'role': 'assistant'}:
                                        send = False

                                # send the chunk
                                if send and chunk.strip():
                                    final_chunk = chunk.strip().replace('data: [DONE]', '') + '\n\n'
                                    yield final_chunk

                        except Exception as exc:
                            if 'Connection closed' in str(exc):
                                yield await errors.yield_error(
                                    500,
                                    'Sorry, there was an issue with the connection.',
                                    'Please first check if the issue on your end. If this error repeats, please don\'t heistate to contact the staff!.'
                                )
                                return

                    break

            except ProxyError as exc:
                print('[!] Proxy error:', exc)
                continue

    # Chat completions always have the same ending
    if is_chat and is_stream:
        chunk = await chat.create_chat_chunk(
            chat_id=chat_id,
            model=model,
            content=chat.CompletionStop
        )
        yield chunk
        yield 'data: [DONE]\n\n'

    # If the response is JSON, then we need to yield it like this
    if not is_stream and json_response:
        yield json.dumps(json_response)

    # DONE WITH REQUEST, NOW LOGGING ETC.

    if user and incoming_request:
        await logs.log_api_request(
            user=user,
            incoming_request=incoming_request,
            target_url=target_request['url']
        )

    if credits_cost and user:
        await users.update_by_id(user['_id'], {
            '$inc': {'credits': -credits_cost}
        })

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
