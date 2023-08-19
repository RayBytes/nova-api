import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from api.db.users import UserManager

manager = UserManager()

async def update_credits(settings=None):
    users = await manager.get_all_users()

    if not settings:
        await users.update_many({}, {'$inc': {'credits': 2500}})

    else:
        for key, value in settings.items():
            await users.update_many(
                {'level': key}, {'$inc': {'credits': int(value)}})

get_all_users = manager.get_all_users
