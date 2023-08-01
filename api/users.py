import os
import uuid
import time
import string
import random
import asyncio

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from rich import print

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB_NAME = 'users'

def get_mongo(collection_name):
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    return db[collection_name]

async def prepare() -> None:
    """Create the MongoDB collection."""

    collection = get_mongo('users')

    await collection.create_index('id', unique=True)
    await collection.create_index('discord_id', unique=True)
    await collection.create_index('api_key', unique=True)

async def add_user(discord_id: int = 0, tags: list = None) -> dict:
    """Adds a new user to the MongoDB collection."""

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
        'ban_reason': '',
        'active': True,
        'discord_id': discord_id,
        'credit': 0,
        'tags': '/'.join(tags),
        'usage': {
            'events': [],
            'num_tokens': 0
        }
    }

    collection = get_mongo('users')
    await collection.insert_one(new_user)

    return new_user

async def get_user(by_id: str = '', by_discord_id: int = 0, by_api_key: str = ''):
    """Retrieve a user from the MongoDB collection."""

    collection = get_mongo('users')
    query = {
        '$or': [
            {'id': by_id},
            {'discord_id': by_discord_id},
            {'api_key': by_api_key},
        ]
    }
    return await collection.find_one(query)

async def get_all_users():
    """Retrieve all users from the MongoDB collection."""

    collection = get_mongo('users')
    return list(await collection.find())

async def user_used_api(user_id: str, num_tokens: int = 0, model='', ip_address: str = '', user_agent: str = '') -> None:
    """Update the stats of a user."""

    collection = get_mongo('users')
    user = await get_user(by_id=user_id)

    if not user:
        raise ValueError('User not found.')

    usage = user['usage']
    usage['events'].append({
        'timestamp': time.time(),
        'ip_address': ip_address,
        'user_agent': user_agent,
        'model': model,
        'num_tokens': num_tokens
    })

    usage['num_tokens'] += num_tokens

    await collection.update_one({'id': user_id}, {'$set': {'usage': usage}})

async def demo():
    await prepare()

    example_id = 133769420
    user = await get_user(by_discord_id=example_id)
    print(user)
    uid = await user['id']

    await user_used_api(uid, model='gpt-5', num_tokens=42, ip_address='9.9.9.9', user_agent='Mozilla/5.0')
    # print(user)

if __name__ == '__main__':
    asyncio.run(demo())
