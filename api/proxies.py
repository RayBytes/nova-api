"""This module contains the Proxy class, which represents a proxy."""

import os
import httpx
import socket
import asyncio

from sockslib import socks
from rich import print
from dotenv import load_dotenv

load_dotenv()

class Proxy:
    """Represents a proxy. The type can be either http, https, socks4 or socks5."""

    def __init__(self,
        proxy_type: str='http',
        host: str='127.0.0.1',
        port: int=8080,
        username: str=None,
        password: str=None
    ):
        self.proxy_type = proxy_type
        self.ip_address = socket.gethostbyname(host)
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    @property
    def auth(self):
        """Returns the authentication part of the proxy URL, if the proxy has a username and password."""
        return f'{self.username}:{self.password}@' if all([self.username, self.password]) else ''

    @property
    def protocol(self):
        """Makes sure the hostnames are resolved correctly using the proxy.
        See https://stackoverflow.com/a/43266186
        """
        return self.proxy_type# + 'h' if self.proxy_type.startswith('socks') else self.proxy_type

    def proxies(self):
        """Returns a dictionary of proxies, ready to be used with the requests library or httpx.
        """

        url = f'{self.protocol}://{self.auth}{self.host}:{self.port}'

        proxies_dict = {
            'http://': url.replace('https', 'http') if self.proxy_type == 'https' else url,
            'https://': url.replace('http', 'https') if self.proxy_type == 'http' else url
        }

        return proxies_dict

    def __str__(self):
        return f'{self.proxy_type}://{len(self.auth) * "*"}{self.host}:{self.port}'

    def __repr__(self):
        return f'<Proxy type={self.proxy_type} host={self.host} port={self.port} username={self.username} password={len(self.password) * "*"}>'

active_proxy = Proxy(
    proxy_type=os.getenv('PROXY_TYPE', 'http'),
    host=os.getenv('PROXY_HOST', '127.0.0.1'),
    port=int(os.getenv('PROXY_PORT', 8080)),
    username=os.getenv('PROXY_USER'),
    password=os.getenv('PROXY_PASS')
)

def activate_proxy() -> None:
    socks.set_default_proxy(
        proxy_type=socks.PROXY_TYPES[active_proxy.proxy_type.upper()],
        addr=active_proxy.host,
        port=active_proxy.port,
        username=active_proxy.username,
        password=active_proxy.password
    )
    socket.socket = socks.socksocket

def check_proxy():
    """Checks if the proxy is working."""

    resp = httpx.get(
        url='https://echo.hoppscotch.io/',
        timeout=20,
        proxies=active_proxy.proxies()
    )
    resp.raise_for_status()

    return resp.ok

async def check_api():
    model = 'gpt-3.5-turbo'
    messages = [
        {
            'role': 'user',
            'content': 'Explain what a wormhole is.'
        },
    ]

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '  + os.getenv('CLOSEDAI_KEY')
    }

    json_data = {
        'model': model,
        'messages': messages,
        'stream': True
    }

    async with httpx.AsyncClient(timeout=20) as client:
        async with client.stream("POST", 'https://api.openai.com/v1/chat/completions', headers=headers, json=json_data) as response:
            response.raise_for_status()
            async for chunk in response.aiter_text():
                print(chunk.strip())

if __name__ == '__main__':
    asyncio.run(check_api())
