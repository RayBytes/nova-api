async def get_ip(request) -> str:
    return request.client.host
