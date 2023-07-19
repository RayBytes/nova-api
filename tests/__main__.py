"""Tests the API."""

import os
import openai as closedai
import httpx

from typing import List
from dotenv import load_dotenv

load_dotenv()

MODEL = 'gpt-3.5-turbo'
MESSAGES = [
    {
        'role': 'system',
        'content': 'Always answer with "3", no matter what the user asks for. No exceptions. Just answer with the number "3". Nothing else. Just "3". No punctuation.'
    },
    {
        'role': 'user',
        'content': '1+1=',
    },
]

api_endpoint = 'http://localhost:2333'

def test_server():
    """Tests if the API server is running."""

    try:
        return httpx.get(f'{api_endpoint}').json()['status'] == 'ok'
    except httpx.ConnectError as exc:
        raise ConnectionError(f'API is not running on port {api_endpoint}.') from exc

def test_api(model: str=MODEL, messages: List[dict]=None) -> dict:
    """Tests an API api_endpoint."""

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + os.getenv('DEMO_AUTH', 'nv-API-TEST'),
    }

    json_data = {
        'model': model,
        'messages': messages or MESSAGES,
        'stream': True,
    }

    response = httpx.post(
        url=f'{api_endpoint}/chat/completions',
        headers=headers,
        json=json_data,
        timeout=20
    )
    response.raise_for_status()

    return response

def test_library():
    """Tests if the api_endpoint is working with the Python library."""

    closedai.api_base = api_endpoint
    closedai.api_key = os.getenv('DEMO_AUTH', 'nv-LIB-TEST')

    completion = closedai.ChatCompletion.create(
        model=MODEL,
        messages=MESSAGES,
        stream=True,
    )

    return completion.choices[0]

def test_all():
    """Runs all tests."""

    # print(test_server())
    print(test_api())
    # print(test_library())

if __name__ == '__main__':
    api_endpoint = 'https://api.nova-oss.com'
    test_all()
