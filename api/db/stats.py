import os
import pytz
import asyncio
import datetime

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

## Statistics

class StatsManager:
    """
    ### The manager for all statistics tracking
    Stats tracked:
    - Dates
    - IPs
    - Target URLs
    - Tokens
    - Models
    - URL Paths
    """

    def __init__(self):
        self.conn = AsyncIOMotorClient(os.environ['MONGO_URI'])

    async def _get_collection(self, collection_name: str):
        return self.conn[os.getenv('MONGO_NAME', 'nova-test')][collection_name]
    
    async def add_date(self):
        date = datetime.datetime.now(pytz.timezone('GMT')).strftime('%Y.%m.%d')
        year, month, day = date.split('.')

        db = await self._get_collection('stats')
        await db.update_one({}, {'$inc': {f'dates.{year}.{month}.{day}': 1}}, upsert=True)

    async def add_ip_address(self, ip_address: str):
        ip_address = ip_address.replace('.', '_')
        db = await self._get_collection('stats')
        await db.update_one({}, {'$inc': {f'ips.{ip_address}': 1}}, upsert=True)

    async def add_target(self, url: str):
        db = await self._get_collection('stats')
        await db.update_one({}, {'$inc': {f'targets.{url}': 1}}, upsert=True)

    async def add_tokens(self, tokens: int, model: str):
        db = await self._get_collection('stats')
        await db.update_one({}, {'$inc': {f'tokens.{model}': tokens}}, upsert=True)

    async def add_model(self, model: str):
        db = await self._get_collection('stats')
        await db.update_one({}, {'$inc': {f'models.{model}': 1}}, upsert=True)

    async def add_path(self, path: str):
        path = path.replace('/', '_')
        db = await self._get_collection('stats')
        await db.update_one({}, {'$inc': {f'paths.{path}': 1}}, upsert=True)

    async def get_value(self, obj_filter):
        db = await self._get_collection('stats')
        return await db.find_one({obj_filter})

if __name__ == '__main__':
    stats = StatsManager()
    asyncio.run(stats.add_date())
    asyncio.run(stats.add_path('/__demo/test'))
