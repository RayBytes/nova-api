import os
import pytz
import asyncio
import datetime

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

def _get_mongo(collection_name: str):
    return AsyncIOMotorClient(os.getenv('MONGO_URI'))['nova-core'][collection_name]

async def add_date():
    date = datetime.datetime.now(pytz.timezone('GMT')).strftime('%Y.%m.%d')
    year, month, day = date.split('.')

    await _get_mongo('stats').update_one({}, {'$inc': {f'dates.{year}.{month}.{day}': 1}}, upsert=True)

async def add_ip_address(ip_address: str):
    ip_address = ip_address.replace('.', '_')
    await _get_mongo('stats').update_one({}, {'$inc': {f'ips.{ip_address}': 1}}, upsert=True)

async def add_target(url: str):
    await _get_mongo('stats').update_one({}, {'$inc': {f'targets.{url}': 1}}, upsert=True)

async def add_tokens(tokens: int, model: str):
    await _get_mongo('stats').update_one({}, {'$inc': {f'tokens.{model}': tokens}}, upsert=True)

async def add_model(model: str):
    await _get_mongo('stats').update_one({}, {'$inc': {f'models.{model}': 1}}, upsert=True)

async def add_path(path: str):
    path = path.replace('/', '_')
    await _get_mongo('stats').update_one({}, {'$inc': {f'paths.{path}': 1}}, upsert=True)

async def get_value(obj_filter):
    return await _get_mongo('stats').find_one({obj_filter})

if __name__ == '__main__':
    asyncio.run(add_date())
    asyncio.run(add_path('/__demo/test'))
