import os
import httpx

from rich import print

import proxies

from dotenv import load_dotenv

load_dotenv()
is_proxy_enabled = False

def enable_proxy():
    """Enables the proxy."""

    global is_proxy_enabled

    proxies.activate_proxy()

    print(f'[green]SUCCESS: Proxy enabled: {proxies.active_proxy}[/green]')

    is_proxy_enabled = True

class InsecureIPError(Exception):
    """Raised when the IP address of the server is not secure."""

def ip_protection_check():
    """Makes sure that the actual server IP address is not exposed to the public."""

    actual_ips = os.getenv('ACTUAL_IPS', '').split()

    if actual_ips:
        echo_response = httpx.get(
            url='https://echo.hoppscotch.io/',
            timeout=15
        )

        response_data = echo_response.json()
        response_ip = response_data['headers']['x-forwarded-for']

        for actual_ip in actual_ips:
            if actual_ip in response_data:
                raise InsecureIPError(f'IP pattern "{actual_ip}" is in the values of ACTUAL_IPS of the\
.env file. Enable a VPN or proxy to continue.')

        if is_proxy_enabled:
            print(f'[green]SUCCESS: The IP "{response_ip}" was detected, which seems to be a proxy. Great![/green]')

    else:
        print('[yellow]WARNING: ACTUAL_IPS is not set in the .env file or empty.\
This means that the real IP of the server could be exposed. If you\'re using something\
like Cloudflare or Repl.it, you can ignore this warning.[/yellow]')

if __name__ == '__main__':
    enable_proxy()
    ip_protection_check()
