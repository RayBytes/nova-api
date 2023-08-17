import sys
# Weird hack because PYTHON IS GOOD LANGUAGE :))))
sys.path.append('../')
from api.db.users import UserManager


async def update_credits(pymongo_client, settings=None):
    manager = UserManager()
    users = await manager.get_all_users(pymongo_client)

    if not settings:
        users.update_many({}, {'$inc': {'credits': 2500}})

    else:
        for key, value in settings.items():
            users.update_many(
                {'level': key}, {'$inc': {'credits': int(value)}})
