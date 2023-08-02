import os
import random
import string
import asyncio

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

def _get_mongo(collection_name: str):
    return AsyncIOMotorClient(os.getenv('MONGO_URI'))['nova-core'][collection_name]

async def create(discord_id: int=0) -> dict:
    """Adds a new user to the MongoDB collection."""
    chars = string.ascii_letters + string.digits

    infix = os.getenv('KEYGEN_INFIX')
    suffix = ''.join(random.choices(chars, k=20))
    prefix = ''.join(random.choices(chars, k=20))

    new_api_key = f'nv-{prefix}{infix}{suffix}'

    new_user = {
        'api_key': new_api_key,
        'credits': 1000,
        'role': '',
        'status': {
            'active': True,
            'ban_reason': '',
        },
        'auth': {
            'discord': discord_id,
            'github': None
        }
    }

    await _get_mongo('users').insert_one(new_user)

    user = await _get_mongo('users').find_one({'api_key': new_api_key})	
    return user

async def by_id(user_id: str):
    return await _get_mongo('users').find_one({'_id': user_id})

async def by_discord_id(discord_id: str):
    return await _get_mongo('users').find_one({'auth.discord': discord_id})

async def by_api_key(key: str):
    return await _get_mongo('users').find_one({'api_key': key})

async def update_by_id(user_id: str, update):
    return await _get_mongo('users').update_one({'_id': user_id}, update)

async def update_by_filter(obj_filter, update):
    return await _get_mongo('users').update_one(obj_filter, update)

async def delete(user_id: str):
    await _get_mongo('users').delete_one({'_id': user_id})


async def demo():
    user = await create(69420)
    print(user)

if __name__ == '__main__':
    asyncio.run(demo())
