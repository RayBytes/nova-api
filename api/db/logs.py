import os
import time

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from helpers import network

load_dotenv()

UA_SIMPLIFY = {
    'Windows NT': 'W',
    'Mozilla/5.0': 'M',
    'Win64; x64': '64',
    'Safari/537.36': 'S',
    'AppleWebKit/537.36 (KHTML, like Gecko)': 'K',
}

## MONGODB Setup

conn = AsyncIOMotorClient(os.getenv('MONGO_URI'))

async def _get_collection(collection_name: str):
    return conn['nova-core'][collection_name]

async def replacer(text: str, dict_: dict) -> str:
    for k, v in dict_.items():
        text = text.replace(k, v)
    return text

async def log_api_request(user: dict, incoming_request, target_url: str):
    db = await _get_collection('logs')
    payload = {}

    try:
        payload = await incoming_request.json()
    except Exception as exc:
        if 'JSONDecodeError' in str(exc):
            pass

    model = payload.get('model')
    ip_address = await network.get_ip(incoming_request)
    useragent = await replacer(incoming_request.headers.get('User-Agent'), UA_SIMPLIFY)

    new_log_item = {
        'timestamp': time.time(),
        'method': incoming_request.method,
        'path': incoming_request.url.path,
        'user_id': str(user['_id']),
        'security': {
            'ip': ip_address,
            'useragent': useragent,
        },
        'details': {
            'model': model,
            'target_url': target_url
        }
    }

    inserted = await db.insert_one(new_log_item)
    log_item = await db.find_one({'_id': inserted.inserted_id})
    return log_item

async def by_id(log_id: str):
    db = await _get_collection('logs')
    return await db.find_one({'_id': log_id})

async def by_user_id(user_id: str):
    db = await _get_collection('logs')
    return await db.find({'user_id': user_id})

async def delete_by_id(log_id: str):
    db = await _get_collection('logs')
    return await db.delete_one({'_id': log_id})

async def delete_by_user_id(user_id: str):
    db = await _get_collection('logs')
    return await db.delete_many({'user_id': user_id})

if __name__ == '__main__':
    pass
