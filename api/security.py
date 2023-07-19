"""Security checks for the API. Checks if the IP is masked etc."""

import os
import asyncio

from rich import print
from tests import check_proxy
from dotenv import load_dotenv

load_dotenv()
is_proxy_enabled = bool(os.getenv('PROXY_HOST', None))

class InsecureIPError(Exception):
    """Raised when the IP address of the server is not secure."""

async def ip_protection_check():
    """Makes sure that the actual server IP address is not exposed to the public."""

    if not is_proxy_enabled:
        print('[yellow]WARN:     The proxy is not enabled. \
Skipping IP protection check.[/yellow]')
        return True

    actual_ips = os.getenv('ACTUAL_IPS', '').split()

    if actual_ips:
        # run the async function check_proxy() and get its result
        response_ip = await check_proxy()

        for actual_ip in actual_ips:
            if actual_ip in response_ip:
                raise InsecureIPError(f'IP pattern "{actual_ip}" is in the values of ACTUAL_IPS of the\
.env file. Enable a VPN or proxy to continue.')

        if is_proxy_enabled:
            print(f'[green]GOOD:     The IP "{response_ip}" was detected, which seems to be a proxy. Great![/green]')
            return True

    else:
        print('[yellow]WARN:     ACTUAL_IPS is not set in the .env file or empty.\
This means that the real IP of the server could be exposed. If you\'re using something\
like Cloudflare or Repl.it, you can ignore this warning.[/yellow]')

if __name__ == '__main__':
    ip_protection_check()
