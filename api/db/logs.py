import os
import time

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

def _get_mongo(collection_name: str):
    return AsyncIOMotorClient(os.getenv('MONGO_URI'))['nova-core'][collection_name]

async def log_api_request(user, request, target_url):
    payload = await request.json()

    last_prompt = None
    if 'messages' in payload:
        last_prompt = payload['messages'][-1]['content']

    model = None
    if 'model' in payload:
        model = payload['model']

    new_log_item = {
        'timestamp': time.time(),
        'method': request.method,
        'path': request.url.path,
        'user_id': user['_id'],
        'security': {
            'ip': request.client.host,
            'useragent': request.headers.get('User-Agent')
        },
        'details': {
            'model': model,
            'last_prompt': last_prompt,
            'target_url': target_url
        }
    }

    inserted = await _get_mongo('logs').insert_one(new_log_item)
    log_item = await _get_mongo('logs').find_one({'_id': inserted.inserted_id})
    return log_item

async def by_id(log_id: str):
    return await _get_mongo('logs').find_one({'_id': log_id})

async def by_user_id(user_id: str):
    return await _get_mongo('logs').find({'user_id': user_id})

async def delete_by_id(log_id: str):
    return await _get_mongo('logs').delete_one({'_id': log_id})

async def delete_by_user_id(user_id: str):
    return await _get_mongo('logs').delete_many({'user_id': user_id})

if __name__ == '__main__':
    pass
