import asyncio
from settings import roles
import autocredits
import aiohttp
from dotenv import load_dotenv
import os
import pymongo

load_dotenv()

CONNECTION_STRING = os.getenv("CONNECTION_STRING")
pymongo_client = pymongo.MongoClient(CONNECTION_STRING)

async def main():
    users = await autocredits.get_all_users(pymongo_client)

    await update_roles(users)
    await autocredits.update_credits(users, roles)

async def update_roles(users):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('http://localhost:50000/get_roles') as response:
                data = await response.json()
        except aiohttp.ClientError as e:
            print(f"Error: {e}")
            return
    
    lvlroles = [f"lvl{lvl}" for lvl in range(10, 110, 10)] + ['']
    discord_users = data
    users = await autocredits.get_all_users(pymongo_client)

    filtered_users = users.find({'role': {'$in': lvlroles}})
    
    bulk_updates = []
    for user in filtered_users:
        discord = str(user['auth']['discord'])

        for id_, roles in discord_users.items():
            if id_ == discord:
                for role in lvlroles:
                    if role in roles:
                        bulk_updates.append(pymongo.UpdateOne({'auth.discord': int(discord)}, {'$set': {'role': role}}))
                        print(f"Updated {id_} to {role}")
                        break
    if bulk_updates:
        with pymongo_client:
            users.bulk_write(bulk_updates)

if __name__ == "__main__":
    asyncio.run(main())