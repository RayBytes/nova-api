import os

from dotenv import load_dotenv

load_dotenv()

async def receive_target_stream():
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=int(os.getenv('TRANSFER_TIMEOUT', '120'))),
        raise_for_status=False
    ) as session:     
        async with session.request(
            method=incoming_request.method,
            url=target_url,
            json=incoming_json_payload,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {os.getenv("CLOSEDAI_KEY")}'
            }
        ) as response:
            async for chunk in response.content.iter_any():
                chunk = f'{chunk.decode("utf8")}\n\n'

                yield chunk
