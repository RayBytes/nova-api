"""ClosedAI key manager."""

import os
import uuid
import time
import asyncio

from rich import print
from helpers import databases

async def prepare() -> None:
    """Creates the database tables"""

    keys_db = await databases.connect('closed_keys')
    await keys_db.execute(
        """
        CREATE TABLE IF NOT EXISTS closed_keys (
            id TEXT PRIMARY KEY,
            key TEXT,
            source TEXT DEFAULT 'unknown',
            created_at INTEGER,
            last_used INTEGER,
            uses_count INTEGER DEFAULT 0,
            tokens_generated INTEGER DEFAULT 0,
            active BOOLEAN,
            working BOOLEAN,
            tags TEXT DEFAULT ''
        )
        """
    )
    await keys_db.commit()

async def add_key(
    key: str,
    source: str='unknown',
    tags: list=None
) -> None:
    """Adds a new key to the database"""

    tags = tags or []

    new_key = {
        'id': str(uuid.uuid4()),
        'key': key,
        'source': source,
        'created_at': int(time.time()),
        'last_used': -1,
        'uses_count': 0,
        'tokens_generated': 0,
        'active': True,
        'working': True,
        'tags': '/'.join(tags),
    }

    await databases.insert_dict(new_key, 'closed_keys', 'closed_keys')

async def get_working_key() -> dict:
    """Returns a working key"""

    keys_db = await databases.connect('closed_keys')

    async with keys_db.execute('SELECT * FROM closed_keys WHERE working = 1') as cursor:
        async for row in cursor:
            return await databases.row_to_dict(row, cursor)

    return None

asyncio.run(prepare())

async def key_stopped_working(key: str) -> None:
    """Marks a key as stopped working"""

    keys_db = await databases.connect('closed_keys')

    await keys_db.execute(
        """
        UPDATE closed_keys
        SET working = 0
        WHERE key = :key
        """,
        {'key': key}
    )
    await keys_db.commit()

async def key_was_used(key: str, num_tokens: int) -> None:
    """Updates the stats of a key"""

    keys_db = await databases.connect('closed_keys')

    # set last_used to int of time.time(), adds one to uses_count and adds num_tokens to tokens_generated
    await keys_db.execute(
        """
        UPDATE closed_keys
        SET last_used = :last_used, uses_count = uses_count + 1, tokens_generated = tokens_generated + :tokens_generated
        WHERE key = :key
        """,
        {
            'key': key,
            'last_used': int(time.time()),
            'tokens_generated': num_tokens
        }
    )
    await keys_db.commit()

async def demo():
    await add_key('sk-non-working-key')
    await key_stopped_working('sk-non-working-key')
    await add_key('sk-working-key')
    key = await get_working_key()
    print(key)

if __name__ == '__main__':
    asyncio.run(demo())
    os.system(f'pkill -f {os.path.basename(__file__)}')
