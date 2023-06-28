import os
import httpx

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

async def stream_api_response(request, target_endpoint: str='https://api.openai.com/v1'):
    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream(
            method=request.method,
            url=f'{target_endpoint}/{request.url.path}',
            headers={
                'Authorization': 'Bearer ' + os.getenv('CLOSEDAI_KEY'),
                'Content-Type': 'application/json'
            },
            data=await request.body(),
        ) as target_response:
            target_response.raise_for_status()

