import os
import httpx
import proxies
import asyncio
import aiohttp
import aiohttp_socks

from rich import print
from dotenv import load_dotenv

load_dotenv()

async def check_proxy():
    """Checks if the proxy is working."""

    proxy = proxies.active_proxy

    connector = aiohttp_socks.ProxyConnector(
        proxy_type=aiohttp_socks.ProxyType.SOCKS5,
        host=proxy.ip_address,
        port=proxy.port,
        rdns=False,
        username=proxy.username,
        password=proxy.password
    )

    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get('https://echo.hoppscotch.io/') as response:
            json_data = await response.json()
            return json_data['headers']['x-forwarded-for']

async def check_api():
    """Checks if the API is working."""

    model = 'gpt-3.5-turbo'
    messages = [
        {
            'role': 'user',
            'content': '2+2='
        },
    ]

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '  + os.getenv('CLOSEDAI_KEY')
    }

    json_data = {
        'model': model,
        'messages': messages,
        'stream': True
    }

    async with httpx.AsyncClient(timeout=20) as client:
        async with client.stream('POST', 'https://api.openai.com/v1/chat/completions', headers=headers, json=json_data) as response:
            response.raise_for_status()
            async for chunk in response.aiter_text():
                print(chunk.strip())

if __name__ == '__main__':
    # asyncio.run(check_api())
    asyncio.run(check_proxy())
