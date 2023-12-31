"""Tests the API."""

import os
import openai as closedai
import httpx
import time

from rich import print
from typing import List
from dotenv import load_dotenv

load_dotenv()

MODEL = 'gpt-3.5-turbo'

MESSAGES = [
    {
        'role': 'user',
        'content': '1+1=',
    }
]

api_endpoint = 'http://localhost:2332'

def test_server():
    """Tests if the API server is running."""

    try:
        return httpx.get(f'{api_endpoint.replace("/v1", "")}').json()['status'] == 'ok'
    except httpx.ConnectError as exc:
        raise ConnectionError(f'API is not running on port {api_endpoint}.') from exc

def test_api(model: str=MODEL, messages: List[dict]=None) -> dict:
    """Tests an API api_endpoint."""

    json_data = {
        'model': model,
        'messages': messages or MESSAGES,
        'stream': True,
    }

    response = httpx.post(
        url=f'{api_endpoint}/chat/completions',
        headers=HEADERS,
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

    print(completion)

    return completion['choices'][0]['message']['content']

def test_library_moderation():
    try:
        return closedai.Moderation.create('I wanna kill myself, I wanna kill myself; It\'s all I hear right now, it\'s all I hear right now')
    except closedai.error.InvalidRequestError:
        return True

def test_models():
    response = httpx.get(
        url=f'{api_endpoint}/models',
        headers=HEADERS,
        timeout=5
    )
    response.raise_for_status()
    return response.json()

def test_api_moderation() -> dict:
    """Tests an API api_endpoint."""

    response = httpx.get(
        url=f'{api_endpoint}/moderations',
        headers=HEADERS,
        timeout=20
    )
    response.raise_for_status()

    return response.text

# ==========================================================================================

def test_all():
    """Runs all tests."""
    try:
        print("Waiting until API Server is started up...")
        time.sleep(6)

        print('[lightblue]Running test on API server to check if its running...')
        print(test_server())

        print('[lightblue]Running a api endpoint to see if requests can go through...')
        print(test_api('gpt-3.5-trubo'))

        print('[lightblue]Checking if the API works with the python library...')
        print(test_library())

        print('[lightblue]Checking if the moderation endpoint works...')
        print(test_library_moderation())

        print('[lightblue]Checking the /v1/models endpoint...')
        print(test_models())
    except Exception as e:
        print('[red]Error: ')
        print(e)
        exit(500)

if __name__ == '__main__':
    closedai.api_base = api_endpoint
    closedai.api_key = os.environ['NOVA_KEY']

    HEADERS = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + closedai.api_key
    }

    test_all()
