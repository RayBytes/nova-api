import os
import asyncio
import aiohttp
import pymongo

import autocredits

from dotenv import load_dotenv

from settings import roles

load_dotenv()

pymongo_client = pymongo.MongoClient(os.getenv('MONGO_URI'))

async def main():
    users = await autocredits.get_all_users(pymongo_client)

    await update_roles(users)
    await autocredits.update_credits(users, roles)

async def update_roles(users):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('http://localhost:3224/get_roles') as response:
                discord_users = await response.json()
        except aiohttp.ClientError as e:
            raise ValueError('Could not get roles.') from exc

    lvlroles = [f'lvl{lvl}' for lvl in range(10, 110, 10)] + ['']

    users = await autocredits.get_all_users(pymongo_client)

    filtered_users = users.find({'role': {'$in': lvlroles}})
    
    bulk_updates = []
    for user in filtered_users:
        discord = str(user['auth']['discord'])

        for id_, roles in discord_users.items():
            if id_ == discord:
                for role in lvlroles:
                    print(2, id_)
                    if role in roles:
                        print(0, id_)
                        bulk_updates.append(pymongo.UpdateOne(
                            {'auth.discord': int(discord)},
                            {'$set': {'role': role}})
                        )
                        print(1, id_)
                        print(f'Updated {id_} to {role}')
                        break

    if bulk_updates:
        with pymongo_client:
            users.bulk_write(bulk_updates)

if __name__ == "__main__":
    asyncio.run(main())