"""This module makes it easy to implement proxies by providing a class.."""

import os
import socket
import asyncio

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

active_proxy = Proxy(
    proxy_type=os.getenv('PROXY_TYPE', 'http'),
    host=os.getenv('PROXY_HOST', '127.0.0.1'),
    port=int(os.getenv('PROXY_PORT', 8080)),
    username=os.getenv('PROXY_USER'),
    password=os.getenv('PROXY_PASS')
)
