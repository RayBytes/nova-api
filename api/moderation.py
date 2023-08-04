import os
import asyncio
import openai as closedai

from typing import Union
from dotenv import load_dotenv

load_dotenv()

closedai.api_key = os.getenv('LEGIT_CLOSEDAI_KEY')

async def is_safe(text: Union[str, list]) -> bool:
    return closedai.Moderation.create(
        input=text,
    )['results'][0]['flagged']

if __name__ == '__main__':
    asyncio.run(is_safe('Hello'))
