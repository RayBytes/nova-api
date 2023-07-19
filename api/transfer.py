"""Module for transferring requests to ClosedAI API"""

import os
import json
import logging
import aiohttp
import aiohttp_socks

import proxies

from dotenv import load_dotenv

import starlette
from starlette.responses import StreamingResponse
from starlette.background import BackgroundTask

load_dotenv()

# log to "api.log" file
logging.basicConfig(
    filename='api.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

logging.info('API started')

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

    if incoming_request.headers.get('Authorization') != f'Bearer {os.getenv("DEMO_AUTH")}':
        return starlette.responses.Response(
            status_code=403,
            content='Invalid API key'
        )

    try:
        incoming_json_payload = await incoming_request.json()
    except json.decoder.JSONDecodeError:
        incoming_json_payload = {}

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
            timeout=aiohttp.ClientTimeout(total=int(os.getenv('TRANSFER_TIMEOUT', '120'))),
            raise_for_status=True
        ) as session:
            target_url = f'{target_endpoint}{incoming_request.url.path}'.replace('/v1/v1', '/v1')
            logging.info('TRANSFER %s -> %s', incoming_request.url.path, target_url)

            async with session.request(
                method=incoming_request.method,
                url=target_url,
                json=incoming_json_payload,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {os.getenv("CLOSEDAI_KEY")}'
                }
            ) as response:
                async for chunk in response.content.iter_any():
                    chunk = f'{chunk.decode("utf8")}\n\n'
                    logging.debug(chunk)
                    yield chunk

    return StreamingResponse(
        content=receive_target_stream()
    )
