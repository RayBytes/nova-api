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
            host=self.ip_address,
            port=self.port,
            rdns=False,
            username=self.username,
            password=self.password
        )

        await self.initialize_connector(connector)

        # Logging to check the connector state
        print("Connector: Is closed?", connector.closed)
        print("Connector: Is connected?", connector._connected)

        return connector


default_proxy = Proxy(
    proxy_type=os.getenv('PROXY_TYPE', 'http'),
    host=os.getenv('PROXY_HOST', '127.0.0.1'),
    port=int(os.getenv('PROXY_PORT', '8080')),
    username=os.getenv('PROXY_USER'),
    password=os.getenv('PROXY_PASS')
)
