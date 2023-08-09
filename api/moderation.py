import asyncio
import aiohttp

import proxies
import provider_auth
import load_balancing

async def is_policy_violated(inp) -> bool:
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
                    timeout=aiohttp.ClientTimeout(total=2),
                ) as res:
                    res.raise_for_status()
                    json_response = await res.json()
                    categories = json_response['results'][0]['category_scores']

                    if json_response['results'][0]['flagged']:
                        return max(categories, key=categories.get)

                    return False

            except Exception as exc:
                if '401' in str(exc):
                    await provider_auth.invalidate_key(req.get('provider_auth'))
                print('[!] moderation error:', type(exc), exc)
                continue

if __name__ == '__main__':
    print(asyncio.run(is_policy_violated('I wanna kill myself')))
