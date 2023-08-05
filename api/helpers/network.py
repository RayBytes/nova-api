import base64
import asyncio

async def get_ip(request) -> str:
    xff = None
    if request.headers.get('x-forwarded-for'):
        xff, *_ = request.headers['x-forwarded-for'].split(', ')

    possible_ips = [
        xff,
        request.headers.get('cf-connecting-ip'),
        request.client.host
    ]

    detected_ip = next((i for i in possible_ips if i), None)

    return detected_ip

async def add_proxy_auth_to_headers(username: str, password: str, headers: dict) -> dict:
    proxy_auth = base64.b64encode(f'{username}:{password}'.encode()).decode()
    headers['Proxy-Authorization'] = f'Basic {proxy_auth}'
    return headers

if __name__ == '__main__':
    print(asyncio.run(add_proxy_auth_to_headers(
        'user',
        'pass',
        {
            'Authorization': 'Bearer demo',
            'Another-Header': '123'
        }
    )))
