import os

from dotenv import load_dotenv

load_dotenv()

async def get_all_users(client):
    users = client[os.getenv('MONGO_NAME', 'nova-test')]['users']
    return users

async def update_credits(pymongo_client, settings=None):
    users = await get_all_users(pymongo_client)

    if not settings:
        users.update_many({}, {'$inc': {'credits': 2500}})

    else:
        for key, value in settings.items():
            users.update_many(
                {'level': key},
                {'$inc':
                    {'credits': int(value)}
                }
            )
