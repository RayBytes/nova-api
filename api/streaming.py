import os
import yaml
import json
import asyncio
import aiohttp
import starlette

from rich import print
from dotenv import load_dotenv

import proxies
import load_balancing

from db import logs, users, stats
from helpers import network, chat

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

with open('config/credits.yml', encoding='utf8') as f:
    max_credits = yaml.safe_load(f)['max-credits']

async def stream(
    path: str='/v1/chat/completions',
    user: dict=None,
    payload: dict=None,
    credits_cost: int=0,
    demo_mode: bool=False,
    input_tokens: int=0,
    incoming_request: starlette.requests.Request=None,
):
    payload = payload or DEMO_PAYLOAD
    is_chat = False

    if 'chat/completions' in path:
        is_chat = True
        chat_id = await chat.create_chat_id()
        model = payload['model']

        chat_chunk = chat.create_chat_chunk(
            chat_id=chat_id,
            model=model,
            content=chat.CompletionStart
        )
        data = json.dumps(chat_chunk)

        chunk = f'data: {data}'

        yield chunk

    for _ in range(5):
        if is_chat:
            target_request = await load_balancing.balance_chat_request(payload)
        else:
            target_request = await load_balancing.balance_organic_request(payload)

        headers = {
            'Content-Type': 'application/json'
        }

        for k, v in target_request.get('headers', {}).items():
            headers[k] = v

        async with aiohttp.ClientSession(connector=proxies.random_proxy.connector) as session:
            async with session.request(
                method=target_request.get('method', 'POST'),
                url=target_request['url'],

                data=target_request.get('data'),
                json=target_request.get('payload'),

                headers=headers,
                cookies=target_request.get('cookies'),

                ssl=False,

                timeout=aiohttp.ClientTimeout(total=float(os.getenv('TRANSFER_TIMEOUT', '120'))),
            ) as response:
                try:
                    await response.raise_for_status()
                except Exception as exc:
                    continue
                    # if 'Too Many Requests' in str(exc):

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

                if not demo_mode:
                    ip_address = await network.get_ip(incoming_request)

                    await stats.add_date()
                    await stats.add_ip_address(ip_address)
                    await stats.add_path(path)
                    await stats.add_target(target_request['url'])

                    if is_chat:
                        await stats.add_model(model)
                        await stats.add_tokens(input_tokens, model)

                async for chunk in response.content.iter_any():
                    chunk = f'{chunk.decode("utf8")}\n\n'

                    if chunk.strip():
                        if is_chat:
                            if target_request['module'] == 'twa':
                                data = json.loads(chunk.split('data: ')[1])

                                if data.get('text'):
                                    chat_chunk = chat.create_chat_chunk(
                                        chat_id=chat_id,
                                        model=model,
                                        content=['text']
                                    )
                                    data = json.dumps(chat_chunk)

                                    chunk = f'data: {data}'

                        yield chunk
                break
    if is_chat:
        chat_chunk = chat.create_chat_chunk(
            chat_id=chat_id,
            model=model,
            content=chat.CompletionStop
        )
        data = json.dumps(chat_chunk)

        yield f'data: {data}'
        yield 'data: [DONE]'

if __name__ == '__main__':
    asyncio.run(stream())
