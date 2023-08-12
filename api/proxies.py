"""This module makes it easy to implement proxies by providing a class.."""

import os
import socket
import random
import asyncio
import aiohttp
import aiohttp_socks

from rich import print
from dotenv import load_dotenv

load_dotenv()

USE_PROXY_LIST = os.getenv('USE_PROXY_LIST', 'False').lower() == 'true'

class Proxy:
    """Represents a proxy. The type can be either http, https, socks4 or socks5.
You can also pass a url, which will be parsed into the other attributes.
URL format:
    [type]://[username:password@]host:port
"""

    def __init__(self,
        url: str=None,
        proxy_type: str='http',
        host_or_ip: str='127.0.0.1',
        port: int=8080,
        username: str=None,
        password: str=None
    ):
        if url:
            proxy_type = url.split('://')[0]
            url = url.split('://')[1]

            if '@' in url:
                username = url.split('@')[1].split(':')[0]
                password = url.split('@')[1].split(':')[1]

            host_or_ip = url.split(':')[0]
            port = url.split(':')[1]

        self.proxy_type = proxy_type
        self.host_or_ip = host_or_ip
        self.ip_address = socket.gethostbyname(self.host_or_ip) # get ip address from host
        self.host = self.host_or_ip
        self.port = port
        self.username = username
        self.password = password

        self.url = f'{self.proxy_type}://{self.username}:{self.password}@{self.host}:{self.port}'
        self.url_ip = f'{self.proxy_type}://{self.username}:{self.password}@{self.ip_address}:{self.port}'
        self.urls = {
            'http': self.url,
            'https': self.url
        }

        self.urls_httpx = {k + '://' :v for k, v in self.urls.items()}
        self.proxies = self.url

    @property
    def connector(self):
        """Returns an aiohttp_socks.ProxyConnector object. Which can be used in aiohttp.ClientSession."""

        proxy_types = {
            'http': aiohttp_socks.ProxyType.HTTP,
            'https': aiohttp_socks.ProxyType.HTTP,
            'socks4': aiohttp_socks.ProxyType.SOCKS4,
            'socks5': aiohttp_socks.ProxyType.SOCKS5
        }

        return aiohttp_socks.ProxyConnector(
            proxy_type=proxy_types[self.proxy_type],
            host=self.ip_address,
            port=self.port,
            rdns=False, # remote DNS
            username=self.username,
            password=self.password
        )

# load proxies from files

proxies_in_files = []

try:
    for proxy_type in ['http', 'socks4', 'socks5']:
        with open(f'secret/proxies/{proxy_type}.txt') as f:
            for line in f.readlines():
                if line.strip() and not line.strip().startswith('#'):
                    if '#' in line:
                        line = line.split('#')[0]

                    proxies_in_files.append(f'{proxy_type}://{line.strip()}')
except FileNotFoundError:
    pass

# Proxy lists support

class ProxyLists:
    def __init__(self):
        random_proxy = random.choice(proxies_in_files)

        self.get_random = Proxy(url=random_proxy)
        self.connector = aiohttp_socks.ChainProxyConnector.from_urls(proxies_in_files)

# ================================================================================================================================ #

# Proxy tests
# Can be useful if you want to troubleshoot your proxies

def test_httpx_workaround():
    import httpx

    print(default_proxy.proxies)

    # this workaround solves the RNDS issue, but fails for Cloudflare protected websites
    with httpx.Client(proxies=default_proxy.proxies, headers={'Host': 'checkip.amazonaws.com'}) as client:
        return client.get(
        f'http://{socket.gethostbyname("checkip.amazonaws.com")}/',
    ).text.strip()

def test_requests():
    import requests

    print(default_proxy.proxies)

    return requests.get(
        timeout=5,
        url='https://checkip.amazonaws.com/',
        proxies=default_proxy.urls
    ).text.strip()

async def test_aiohttp_socks():
    async with aiohttp.ClientSession(connector=default_proxy.connector) as session:
        async with session.get('https://checkip.amazonaws.com/') as response:
            html = await response.text()
            return html.strip()

async def streaming_aiohttp_socks():
    async with aiohttp.ClientSession(connector=default_proxy.connector) as session:
        async with session.get('https://httpbin.org/get', headers={
            'Authorization': 'x'
        }) as response:
            json = await response.json()
            return json

async def text_httpx_socks():
    import httpx
    from httpx_socks import AsyncProxyTransport

    print(default_proxy.url_ip)

    transport = AsyncProxyTransport.from_url(default_proxy.url_ip)
    async with httpx.AsyncClient(transport=transport) as client:
        res = await client.get('https://checkip.amazonaws.com')
        return res.text

# ================================================================================================================================ #

def get_proxy() -> Proxy:
    """Returns a Proxy object. The proxy is either from the proxy list or from the environment variables.
"""
    if USE_PROXY_LIST:
        return ProxyLists().get_random

    return Proxy(
        proxy_type=os.getenv('PROXY_TYPE', 'http'),
        host_or_ip=os.getenv('PROXY_HOST', '127.0.0.1'),
        port=int(os.getenv('PROXY_PORT', '8080')),
        username=os.getenv('PROXY_USER'),
        password=os.getenv('PROXY_PASS')
    )

if __name__ == '__main__':
    # print(test_httpx())
    # print(test_requests())
    # print(asyncio.run(test_aiohttp_socks()))
    print(asyncio.run(streaming_aiohttp_socks()))
    # print(asyncio.run(text_httpx_socks()))
