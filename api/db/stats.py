import os
import pytz
import asyncio
import datetime

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

## MONGODB Setup

conn = AsyncIOMotorClient(os.getenv('MONGO_URI'))

async def _get_collection(collection_name: str):
    return conn['nova-core'][collection_name]

## Statistics

async def add_date():
    date = datetime.datetime.now(pytz.timezone('GMT')).strftime('%Y.%m.%d')
    year, month, day = date.split('.')

    db = await _get_collection('stats')
    await db.update_one({}, {'$inc': {f'dates.{year}.{month}.{day}': 1}}, upsert=True)

async def add_ip_address(ip_address: str):
    ip_address = ip_address.replace('.', '_')
    db = await _get_collection('stats')
    await db.update_one({}, {'$inc': {f'ips.{ip_address}': 1}}, upsert=True)

async def add_target(url: str):
    db = await _get_collection('stats')
    await db.update_one({}, {'$inc': {f'targets.{url}': 1}}, upsert=True)

async def add_tokens(tokens: int, model: str):
    db = await _get_collection('stats')
    await db.update_one({}, {'$inc': {f'tokens.{model}': tokens}}, upsert=True)

async def add_model(model: str):
    db = await _get_collection('stats')
    await db.update_one({}, {'$inc': {f'models.{model}': 1}}, upsert=True)

async def add_path(path: str):
    path = path.replace('/', '_')
    db = await _get_collection('stats')
    await db.update_one({}, {'$inc': {f'paths.{path}': 1}}, upsert=True)

async def get_value(obj_filter):
    db = await _get_collection('stats')
    return await db.find_one({obj_filter})

if __name__ == '__main__':
    asyncio.run(add_date())
    asyncio.run(add_path('/__demo/test'))
