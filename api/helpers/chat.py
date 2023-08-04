import string
import random
import asyncio

from rich import print

class CompletionStart:
    """Beinning of a chat"""

class CompletionStop:
    """End of a chat"""

async def create_chat_id() -> str:
    chars = string.ascii_letters + string.digits
    chat_id = ''.join(random.choices(chars, k=32))

    return f'chatcmpl-{chat_id}'

def create_chat_chunk(chat_id: str, model: str, content=None) -> dict:
    content = content or {}

    delta = {}

    if content:
        delta = {
            'content': content
        }

    if not isinstance(content, str):
        delta = {
            'role': 'assistant'
        }

    chunk = {
        'id': chat_id,
        'object': 'chat.completion.chunk',
        'created': 0,
        'model': model,
        'choices': [
            {
                'delta': delta,
                'index': 0, 
                'finish_reason': None if not(isinstance(content, str)) else 'stop'
            }
        ],
    }
    print(chunk)

    return chunk

if __name__ == '__main__':
    demo_chat_id = asyncio.run(create_chat_id())
    print(demo_chat_id)
    print(asyncio.run(create_chat_chunk(
        model='gpt-4',
        content='Hello',
        chat_id=demo_chat_id,
    )))
