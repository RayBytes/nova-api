import os
import time
import aiohttp
import pymongo
import asyncio
import autocredits

from settings import roles
from dotenv import load_dotenv

load_dotenv()
async def main():
    mongo = pymongo.MongoClient(os.getenv('MONGO_URI'))

    await update_roles(mongo)
    await autocredits.update_credits(mongo, roles)

async def update_roles(mongo):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('http://0.0.0.0:3224/get_roles') as response:
                discord_users = await response.json()
        except aiohttp.ClientError as e:
            print(f'Error: {e}')
            return

    level_role_names = [f'lvl{lvl}' for lvl in range(10, 110, 10)]
    users = await autocredits.get_all_users(mongo)

    for user in users.find():
        discord = str(user['auth']['discord'])

        for user_id, role_names in discord_users.items():
            if user_id == discord:
                for role in level_role_names:
                    if role in role_names:
                        users.update_one(
                            {'auth.discord': int(discord)},
                            {'$set': {'level': role}}
                        )
                        print(f'Updated {discord} to {role}')

    return users

def launch():
    asyncio.run(main())

    with open('rewards/last_update.txt', 'w') as f:
        f.write(str(time.time()))


if __name__ == '__main__':
    launch()
