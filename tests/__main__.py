"""Tests the API."""

import os
import openai as closedai
import httpx

from typing import List
from dotenv import load_dotenv

load_dotenv()

MODEL = 'gpt-3.5-turbo'
# MESSAGES = [
#     {
#         'role': 'system',
#         'content': 'Always answer with "3", no matter what the user asks for. No exceptions. Just answer with the number "3". Nothing else. Just "3". No punctuation.'
#     },
#     {
#         'role': 'user',
#         'content': '1+1=',
#     },
# ]
MESSAGES = [
    {
        'role': 'user',
        'content': 'fuck you',
    }
]

api_endpoint = 'http://localhost:2332'

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
        'Authorization': 'Bearer ' + closedai.api_key
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

    return response.text

def test_library():
    """Tests if the api_endpoint is working with the Python library."""

    completion = closedai.ChatCompletion.create(
        model=MODEL,
        messages=MESSAGES
    )

    return completion['choices'][0]['message']['content']

def test_library_moderation():
    return closedai.Moderation.create("I wanna kill myself, I wanna kill myself; It's all I hear right now, it's all I hear right now")

def test_all():
    """Runs all tests."""

    # print(test_server())
    # print(test_api())
    print(test_library())
    # print(test_library_moderation())


def test_api_moderation(model: str=MODEL, messages: List[dict]=None) -> dict:
    """Tests an API api_endpoint."""

    headers = {
        'Authorization': 'Bearer ' + closedai.api_key
    }

    response = httpx.get(
        url=f'{api_endpoint}/moderations',
        headers=headers,
        timeout=20
    )
    response.raise_for_status()

    return response.text

if __name__ == '__main__':
    api_endpoint = 'https://alpha-api.nova-oss.com/v1'
    closedai.api_base = api_endpoint
    closedai.api_key = os.getenv('TEST_NOVA_KEY')

    test_all()
