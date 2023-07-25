import os
import aiohttp

import proxies

from dotenv import load_dotenv
from request_manager import Request

load_dotenv()

async def stream_closedai_request(request: Request):
    async with aiohttp.ClientSession(
        connector=await proxies.default_proxy.get_connector(),
        timeout=aiohttp.ClientTimeout(total=request.timeout),
        raise_for_status=False
    ) as session:
        async with session.request(
            method=request.method,
            url=request.url,
            json=request.payload,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {os.getenv("CLOSEDAI_KEY")}'
            }
        ) as response:
            async for chunk in response.content.iter_any():
                chunk = f'{chunk.decode("utf8")}\n\n'
                yield chunk

if __name__ == '__main__':
    pass
