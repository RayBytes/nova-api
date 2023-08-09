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
    demo_mode: bool=False,
    input_tokens: int=0,
    incoming_request: starlette.requests.Request=None,
):
    is_chat = False
    is_stream = payload.get('stream', False)

    if 'chat/completions' in path:
        is_chat = True
        model = payload['model']

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

    for _ in range(5):
        headers = {
            'Content-Type': 'application/json'
        }

        try:
            if is_chat:
                target_request = await load_balancing.balance_chat_request(payload)
            else:
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
            error = await errors.yield_error(
                500,
                'Sorry, the API has no working keys anymore.',
                'The admins have been messaged automatically.'
            )
            yield error 
            return

        for k, v in target_request.get('headers', {}).items():
            target_request['headers'][k] = v

        if target_request['method'] == 'GET' and not payload:
            target_request['payload'] = None

        async with aiohttp.ClientSession(connector=proxies.default_proxy.connector) as session:
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

                        try:
                            async for chunk in response.content.iter_any():
                                send = False
                                chunk = f'{chunk.decode("utf8")}\n\n'
                                chunk = chunk.replace(os.getenv('MAGIC_WORD', 'novaOSScheckKeyword'), payload['model'])
                                chunk = chunk.replace(os.getenv('MAGIC_USER_WORD', 'novaOSSuserKeyword'), str(user['_id']))

                                if not chunk.strip():
                                    send = False

                                if is_chat and '{' in chunk:
                                    data = json.loads(chunk.split('data: ')[1])
                                    chunk = chunk.replace(data['id'], chat_id)
                                    send = True

                                    if target_request['module'] == 'twa' and data.get('text'):
                                        chunk = await chat.create_chat_chunk(
                                            chat_id=chat_id,
                                            model=model,
                                            content=['text']
                                        )
                                    if not data['choices'][0]['delta']:
                                        send = False

                                    if data['choices'][0]['delta'] == {'role': 'assistant'}:
                                        send = False
                                
                                if send:
                                    final_chunk = chunk.strip().replace('data: [DONE]', '') + '\n\n'
                                    yield final_chunk

                        except Exception as exc:
                            if 'Connection closed' in str(exc):
                                error = await errors.yield_error(
                                    500,
                                    'Sorry, there was an issue with the connection.',
                                    'Please first check if the issue on your end. If this error repeats, please don\'t heistate to contact the staff!.'
                                )
                                yield error 
                                return

                    break

            except ProxyError as exc:
                print('proxy error')
                continue

    if is_chat and is_stream:
        chunk = await chat.create_chat_chunk(
            chat_id=chat_id,
            model=model,
            content=chat.CompletionStop
        )
        yield chunk
        yield 'data: [DONE]\n\n'

    if not is_stream and json_response:
        yield json.dumps(json_response)

    # DONE =========================================================

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
