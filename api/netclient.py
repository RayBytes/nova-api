import os
import httpx

import proxies

from dotenv import load_dotenv
from helpers.requesting import Request

load_dotenv()

async def stream_closedai_request(request: Request):
    async with httpx.AsyncClient(
        # proxies=proxies.default_proxy.urls_httpx,
        timeout=httpx.Timeout(request.timeout)
    ) as client:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {os.getenv("CLOSEDAI_KEY")}'
        }
        response = await client.request(
            method=request.method,
            url=request.url,
            json=request.payload,
            headers=headers
        )

        response.raise_for_status()

        async for chunk in response.aiter_bytes():
            chunk = f'{chunk.decode("utf8")}\n\n'
            yield chunk

if __name__ == '__main__':
    pass
