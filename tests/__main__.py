"""Tests the API."""

from typing import List

import openai as closedai
import httpx

PORT = 8000

MODEL = 'gpt-3.5-turbo'
MESSAGES = [
    {
        'role': 'user',
        'content': 'Hello!',
    },
]
ENDPOINT = f'http://localhost:{PORT}'

def test_server():
    """Tests if the API is running."""

    try:
        return httpx.get(f'{ENDPOINT}').json()['status'] == 'ok'
    except httpx.ConnectError as exc:
        raise ConnectionError(f'API is not running on port {PORT}.') from exc

def test_api(model: str=MODEL, messages: List[dict]=None) -> dict:
    """Tests an API endpoint."""

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'nv-API-TEST',
    }

    json_data = {
        'model': model,
        'messages': messages or MESSAGES,
    }

    response = httpx.post(f'{ENDPOINT}/chat/completions', headers=headers, json=json_data, timeout=20)
    response.raise_for_status()

    return response.json()['choices'][0]

def test_library():
    """Tests if the endpoint is working with the "Closed"AI library."""

    closedai.api_base = ENDPOINT
    closedai.api_key = 'nv-LIBRARY-TEST'

    completion = closedai.ChatCompletion.create(
        model=MODEL,
        messages=MESSAGES,
    )

    return completion.choices[0]

def test_all():
    """Runs all tests."""

    print(test_server())
    print(test_api())
    print(test_library())

if __name__ == '__main__':
    test_all()
