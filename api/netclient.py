import os
import requests

from dotenv import load_dotenv

import proxies

from helpers import exceptions

load_dotenv()

async def stream(request: dict):
    headers = {
        'Content-Type': 'application/json'
    }

    for k, v in request.get('headers', {}).items():
        headers[k] = v

    for _ in range(3):
        response = requests.request(
            method=request.get('method', 'POST'),
            url=request['url'],
            json=request.get('payload', {}),
            headers=headers,
            timeout=int(os.getenv('TRANSFER_TIMEOUT', '120')),
            proxies=proxies.default_proxy.urls,
            stream=True
        )

        try:
            response.raise_for_status()
        except Exception as exc:
            if str(exc) == '429 Client Error: Too Many Requests for url: https://api.openai.com/v1/chat/completions':
                continue
        else:
            break

    for chunk in response.iter_lines():
        chunk = f'{chunk.decode("utf8")}\n\n'
        yield chunk

if __name__ == '__main__':
    pass
