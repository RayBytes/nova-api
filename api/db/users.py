import os
import yaml
import random
import string
import asyncio

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

with open('config/config.yml', encoding='utf8') as f:
    credits_config = yaml.safe_load(f)

## MONGODB Setup

class UserManager:
    """
    ### Manager of all users in the database.
    Following methods are available:

    - `_get_collection(collection_name)`
    - `create(discord_id)`
    - `user_by_id(user_id)`
    - `user_by_discord_id(discord_id)`
    - `user_by_api_key(api_key)`
    - `update_by_id(user_id, new_obj)`
    - `update_by_filter(filter_object, new_obj)`
    - `delete(user_id)`
    """

    def __init__(self):
        self.conn = AsyncIOMotorClient(os.getenv('MONGO_URI'))

    async def _get_collection(self, collection_name: str):
        return self.conn['nova-core'][collection_name]
    
    async def get_all_users(self):
        return self.conn['nova-core']['users']

    async def create(self, discord_id: str = '') -> dict:
        chars = string.ascii_letters + string.digits

        infix = os.getenv('KEYGEN_INFIX')
        suffix = ''.join(random.choices(chars, k=20))
        prefix = ''.join(random.choices(chars, k=20))

        new_api_key = f'nv-{prefix}{infix}{suffix}'

        new_user = {
            'api_key': new_api_key,
            'credits': credits_config['start-credits'],
            'role': '',
            'level': '',
            'status': {
                'active': True,
                'ban_reason': '',
            },
            'auth': {
                'discord': str(discord_id),
                'github': None
            }
        }

        db = await self._get_collection('users')
        await db.insert_one(new_user)
        user = await db.find_one({'api_key': new_api_key})
        return user

    async def user_by_id(self, user_id: str):
        db = await self._get_collection('users')
        return await db.find_one({'_id': user_id})

    async def user_by_discord_id(self, discord_id: str):
        db = await self._get_collection('users')
        return await db.find_one({'auth.discord': str(int(discord_id))})

    async def user_by_api_key(self, key: str):
        db = await self._get_collection('users')
        return await db.find_one({'api_key': key})

    async def update_by_id(self, user_id: str, update):
        db = await self._get_collection('users')
        return await db.update_one({'_id': user_id}, update)

    async def update_by_filter(self, obj_filter, update):
        db = await self._get_collection('users')
        return await db.update_one(obj_filter, update)

    async def delete(self, user_id: str):
        db = await self._get_collection('users')
        await db.delete_one({'_id': user_id})

async def demo():
    user = await UserManager().create(69420)
    print(user)

if __name__ == '__main__':
    asyncio.run(demo())
