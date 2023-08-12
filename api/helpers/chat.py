import json
import string
import random
import asyncio

from rich import print

class CompletionStart:
    """Beinning of a chat"""

class CompletionStop:
    """End of a chat"""

async def create_chat_id() -> str:
    """Generates a random chat ID"""

    chars = string.ascii_letters + string.digits
    chat_id = ''.join(random.choices(chars, k=32))

    return f'chatcmpl-{chat_id}'

async def create_chat_chunk(chat_id: str, model: str, content=None) -> dict:
    """Creates the chunk for streaming chat.

    Args:
        chat_id (str): _description_
        model (str): _description_
        content (_type_, optional): _description_. Defaults to None.

    Returns:
        dict: _description_
    """
    content = content or {}

    delta = {}

    if content:
        delta = {
            'content': content
        }

    if content == CompletionStart:
        delta = {
            'role': 'assistant'
        }

    if content == CompletionStop:
        delta = {}

    chunk = {
        'id': chat_id,
        'object': 'chat.completion.chunk',
        'created': 0,
        'model': model,
        'choices': [
            {
                'delta': delta,
                'index': 0, 
                'finish_reason': 'stop' if content == CompletionStop else None
            }
        ],
    }

    return f'data: {json.dumps(chunk)}\n\n'