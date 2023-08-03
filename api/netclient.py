import os
import aiohttp
import asyncio
import aiohttp_socks

from dotenv import load_dotenv

import proxies

from helpers import exceptions

load_dotenv()

async def stream(request: dict, demo_mode: bool=False):
    headers = {
        'Content-Type': 'application/json'
    }

    for k, v in request.get('headers', {}).items():
        headers[k] = v

    for _ in range(3):
        async with aiohttp.ClientSession(connector=proxies.default_proxy.connector) as session:
            async with session.get(
                # 'GET',
                'https://checkip.amazonaws.com/'
            ) as response:
                print(response.content)
                print(type(response.content))

                # html = await response.text()
                # print(html)

                    # async with session.get(
                        # method='GET',
                        # url='https://checkip.amazonaws.com',
                        # method=request.get('method', 'POST'),
                        # url=request['url'],
                        # json=request.get('payload', {}),
                        # headers=headers,
                        # timeout=aiohttp.ClientTimeout(total=float(os.getenv('TRANSFER_TIMEOUT', '120'))),
                    # ) as response:
                        # try:
                            # await response.raise_for_status()
                        # except Exception as exc:
                            # if 'Too Many Requests' in str(exc):
                                # continue
                        # else:
                            # break

                async for chunk in response.content.iter_chunks():
                    # chunk = f'{chunk.decode("utf8")}\n\n'
                
                    if demo_mode:
                        print(chunk)

                    yield chunk

if __name__ == '__main__':
    asyncio.run(stream({'method': 'GET', 'url': 'https://checkip.amazonaws.com'}, True))

