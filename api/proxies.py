"""This module makes it easy to implement proxies by providing a class.."""

import os
import socket
import asyncio
import aiohttp
import aiohttp_socks

from dotenv import load_dotenv

load_dotenv()

class Proxy:
    """Represents a proxy. The type can be either http, https, socks4 or socks5."""

    def __init__(self,
        proxy_type: str='http',
        host_or_ip: str='127.0.0.1',
        port: int=8080,
        username: str=None,
        password: str=None
    ):
        self.proxy_type = proxy_type
        self.host_or_ip = host_or_ip
        self.ip_address = socket.gethostbyname(self.host_or_ip) if host_or_ip[0].isdigit() else host_or_ip
        self.host = self.host_or_ip
        self.port = port
        self.username = username
        self.password = password

        self.url = f'{self.proxy_type}://{self.username}:{self.password}@{self.host}:{self.port}'
        self.urls = {
            'http': self.url,
            'https': self.url
        }

        self.urls_httpx = {k + '://' :v for k, v in self.urls.items()}
        self.proxies = self.url

    async def initialize_connector(self, connector):
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=10),
            raise_for_status=True
        ) as session:
            async with session.request(
                method='get',
                url='https://checkip.amazonaws.com',
                headers={'Content-Type': 'application/json'}
            ) as response:
                detected_ip = await response.text()
                print(f'Detected IP: {detected_ip}')
                return detected_ip.strip()

    async def get_connector(self):
        proxy_types = {
            'http': aiohttp_socks.ProxyType.HTTP,
            'https': aiohttp_socks.ProxyType.HTTP,
            'socks4': aiohttp_socks.ProxyType.SOCKS4,
            'socks5': aiohttp_socks.ProxyType.SOCKS5
        }

        connector = aiohttp_socks.ProxyConnector(
            proxy_type=proxy_types[self.proxy_type],
            host=self.host,
            port=self.port,
            rdns=False,
            username=self.username,
            password=self.password
        )

        await self.initialize_connector(connector)

        return connector

default_proxy = Proxy(
    proxy_type=os.getenv('PROXY_TYPE', 'http'),
    host_or_ip=os.getenv('PROXY_HOST', '127.0.0.1'),
    port=int(os.getenv('PROXY_PORT', '8080')),
    username=os.getenv('PROXY_USER'),
    password=os.getenv('PROXY_PASS')
)

def test_requests():
    import requests

    # return requests.get(
    #     'https://checkip.amazonaws.com',
    #     timeout=5,
    #     proxies=default_proxy.urls
    # ).text.strip()


def test_httpx():
    import httpx

    print(default_proxy.proxies)

    with httpx.Client(proxies=default_proxy.proxies, headers={'Host': 'checkip.amazonaws.com'}) as client:
        return client.get(
        f'http://{socket.gethostbyname("checkip.amazonaws.com")}/',
    ).text.strip()

if __name__ == '__main__':
    print(test_requests())
    print(test_httpx())
