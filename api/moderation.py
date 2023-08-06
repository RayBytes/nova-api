import asyncio

import aiohttp
import proxies
import load_balancing

async def is_safe(inp) -> bool:
    text = inp

    if isinstance(inp, list):
        text = ''
        if isinstance(inp[0], dict):
            for msg in inp:
                text += msg['content'] + '\n'

        else:
            text = '\n'.join(inp)

    for _ in range(3):
        req = await load_balancing.balance_organic_request(
            {
                'path': '/v1/moderations',
                'payload': {'input': text}
            }
        )

        async with aiohttp.ClientSession(connector=proxies.default_proxy.connector) as session:
            try:
                async with session.request(
                    method=req.get('method', 'POST'),
                    url=req['url'],
                    data=req.get('data'),
                    json=req.get('payload'),
                    headers=req.get('headers'),
                    cookies=req.get('cookies'),
                    ssl=False,
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as res:
                    res.raise_for_status()

                    json_response = await res.json()

                    return not json_response['results'][0]['flagged']
            except Exception as exc:
                print('[!] moderation error:', type(exc), exc)
                continue

if __name__ == '__main__':
    print(asyncio.run(is_safe('I wanna kill myself')))
