"""Manages web requests."""

import os

from dotenv import load_dotenv
from typing import Union, Optional

load_dotenv()

EXCLUDED_HEADERS = [
    'content-encoding',
    'content-length',
    'transfer-encoding',
    'connection'
]

class Request:
    def __init__(self,
        url: str,
        method: str='GET',
        payload: Optional[Union[dict, list]]=None,
        headers: dict={
            'Content-Type': 'application/json'
        }
    ):
        self.method = method.upper()
        self.url = url.replace('/v1/v1', '/v1')
        self.payload = payload
        self.headers = headers
        self.timeout = int(os.getenv('TRANSFER_TIMEOUT', '120'))

class HTTPXRequest(Request):
    def __init__(self, url: str, *args, **kwargs):
        super().__init__(url, *args, **kwargs)
        self.url += '?httpx=1'
