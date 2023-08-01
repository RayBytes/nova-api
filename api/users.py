"""User system."""

import os
import uuid
import time
import string
import random
import asyncio

from helpers import databases
from dotenv import load_dotenv

load_dotenv()

async def prepare() -> None:
    """Creates the database tables"""

    users_db = await databases.connect('users')
    await users_db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            api_key TEXT,
            active BOOLEAN,
            created_at INTEGER,
            last_used INTEGER DEFAULT 0,
            uses_count INTEGER DEFAULT 0,
            tokens_generated INTEGER DEFAULT 0,
            discord_id INTEGER DEFAULT 0,
            credit INTEGER DEFAULT 0,
            tags TEXT DEFAULT ''
        )
        """
    )
    await users_db.commit()

async def add_user(
    discord_id: int=0,
    tags: list=None,
) -> dict:
    """Adds a new key to the database"""

    chars = string.ascii_letters + string.digits

    infix = os.getenv('KEYGEN_INFIX')
    suffix = ''.join(random.choices(chars, k=20))
    prefix = ''.join(random.choices(chars, k=20))

    key = f'nv-{prefix}{infix}{suffix}'

    tags = tags or []    
    new_user = {
        'id': str(uuid.uuid4()),
        'api_key': key,
        'created_at': int(time.time()),
        'last_used': 0,
        'uses_count': 0,
        'tokens_generated': 0,
        'active': True,
        'discord_id': discord_id,
        'credit': 0,
        'tags': '/'.join(tags)
    }

    await databases.insert_dict(new_user, 'users', 'users')
    return new_user

async def get_user(
    by_id: str='',
    by_discord_id: int=0,
):
    users_db = await databases.connect('users')

    async with users_db.execute(
        'SELECT * FROM users WHERE id = :id OR discord_id = :discord_id',
        {'id': by_id, 'discord_id': by_discord_id}
    ) as cursor:
        async for row in cursor:
            result = await databases.row_to_dict(row, cursor)
            return result

    return None

async def get_all_users():
    users_db = await databases.connect('users')
    results = []

    async with users_db.execute(
        'SELECT * FROM users'
    ) as cursor:
        async for row in cursor:
            result = await databases.row_to_dict(row, cursor)
            results.append(result)

    return results

async def demo():
    await prepare()

    users = await get_all_users()
    print(users)

    example_id = 133769420
    user = await add_user(discord_id=example_id)
    print(user)

    del user
    print('Fetching user...')

    user = await get_user(by_discord_id=example_id) 
    print(user['api_key'])

if __name__ == '__main__':
    asyncio.run(demo())
    os.system(f'pkill -f {os.path.basename(__file__)}')
