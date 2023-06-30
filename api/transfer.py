"""Module for transferring requests to ClosedAI API"""

import os
import aiohttp
import aiohttp_socks

import proxies

from dotenv import load_dotenv

from starlette.responses import StreamingResponse
from starlette.background import BackgroundTask

load_dotenv()

EXCLUDED_HEADERS = [
    'content-encoding',
    'content-length',
    'transfer-encoding',
    'connection'
]

proxy = proxies.active_proxy
proxy_connector = aiohttp_socks.ProxyConnector(
    proxy_type=aiohttp_socks.ProxyType.SOCKS5,
    host=proxy.ip_address,
    port=proxy.port,
    rdns=False,
    username=proxy.username,
    password=proxy.password
)

async def transfer_streaming_response(incoming_request, target_endpoint: str='https://api.openai.com/v1'):
    """Transfer a streaming response from the incoming request to the target endpoint"""

    incoming_json_payload = await incoming_request.json()

    async def receive_target_stream():
        connector = aiohttp_socks.ProxyConnector(
            proxy_type=aiohttp_socks.ProxyType.SOCKS5,
            host=proxy.ip_address,
            port=proxy.port,
            rdns=False,
            username=proxy.username,
            password=proxy.password
        )
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=120),
            raise_for_status=True
        ) as session:
            async with session.request(
                method=incoming_request.method,
                url=f'{target_endpoint}/{incoming_request.url.path}',
                json=incoming_json_payload,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {os.getenv("CLOSEDAI_KEY")}'
                }
            ) as response:
                async for chunk in response.content.iter_any():
                    chunk = f'{chunk.decode("utf8")}\n\n'
                    yield chunk

    return StreamingResponse(
        content=receive_target_stream()
    )
