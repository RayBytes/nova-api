import os
import socks
import socket
import httpx

from rich import print

is_proxy_enabled = False

def enable_proxy():
    """Enables the SOCKS5 proxy."""

    global is_proxy_enabled

    if all([os.getenv('PROXY_PORT'), os.getenv('PROXY_IP'), os.getenv('PROXY_USER'), os.getenv('PROXY_PASS')]):
        proxy_type = socks.PROXY_TYPE_HTTP

        if '4' in os.getenv('PROXY_TYPE'):
            proxy_type = socks.PROXY_TYPE_SOCKS4

        if '5' in os.getenv('PROXY_TYPE'):
            proxy_type = socks.PROXY_TYPE_SOCKS5

        socks.set_default_proxy(
            proxy_type=proxy_type,
            addr=os.getenv('PROXY_HOST'),
            port=int(os.getenv('PROXY_PORT')),
            username=os.getenv('PROXY_USER'),
            password=os.getenv('PROXY_PASS')
        )
        socket.socket = socks.socksocket

        is_proxy_enabled = True

    else:
        print('[yellow]WARNING: PROXY_PORT, PROXY_IP, PROXY_USER, and PROXY_PASS are not set in the .env file or empty. \
Consider configuring a SOCKS5 proxy to improve the security.[/yellow]')

class InsecureIPError(Exception):
    """Raised when the IP address of the server is not secure."""

def ip_protection_check():
    """Makes sure that the actual server IP address is not exposed to the public."""

    actual_ips = os.getenv('ACTUAL_IPS', '').split()

    if actual_ips:
        detected_ip = httpx.get('https://checkip.amazonaws.com', timeout=5).text.strip()

        for actual_ip in actual_ips:
            if detected_ip.startswith(actual_ip):
                raise InsecureIPError(f'IP {detected_ip} is in the values of ACTUAL_IPS of the\
.env file. Enable a VPN or proxy to continue.')

        if is_proxy_enabled:
            print(f'[green]SUCCESS: The server IP {detected_ip} seems to be protected by a proxy.[/green]')

    else:
        print('[yellow]WARNING: ACTUAL_IPS is not set in the .env file or empty.\
This means that the real IP of the server could be exposed. If you\'re using something\
like Cloudflare or Repl.it, you can ignore this warning.[/yellow]')
