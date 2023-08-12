import base64
import asyncio

async def get_ip(request) -> str:
    """Get the IP address of the incoming request."""

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
