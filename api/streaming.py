import os
import yaml
import asyncio
import aiohttp
import starlette

from dotenv import load_dotenv

import proxies
import load_balancing

from db import logs, users, stats
from rich import print
from helpers import network

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

    if 'chat/completions' in path: # is a chat endpoint
        target_request = await load_balancing.balance_chat_request(payload)
    else:
        target_request = await load_balancing.balance_organic_request(payload)

    headers = {
        'Content-Type': 'application/json'
    }

    for k, v in target_request.get('headers', {}).items():
        headers[k] = v

    for _ in range(5):
        async with aiohttp.ClientSession(connector=proxies.default_proxy.connector) as session:
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
                    if 'Too Many Requests' in str(exc):
                        continue
                else:
                    break

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
            await stats.add_date()
            await stats.add_ip_address(network.get_ip(incoming_request))
            await stats.add_model(payload.get('model', '_non-chat'))
            await stats.add_path(path)
            await stats.add_target(target_request['url'])
            await stats.add_tokens(input_tokens)

        async for chunk in response.content.iter_chunks():
            # chunk = f'{chunk.decode("utf8")}\n\n'

            if demo_mode:
                print(chunk)

            yield chunk

if __name__ == '__main__':
    asyncio.run(stream())
