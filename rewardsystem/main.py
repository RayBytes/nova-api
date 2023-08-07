import asyncio
from settings import roles
import autocredits
import aiohttp
from dotenv import load_dotenv
import os
import pymongo

load_dotenv()

CONNECTION_STRING = os.getenv("MONGO_URI")


async def main():
    pymongo_client = pymongo.MongoClient(CONNECTION_STRING)

    await update_roles(pymongo_client)
    await autocredits.update_credits(pymongo_client, roles)


async def update_roles(pymongo_client):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('http://0.0.0.0:3224/get_roles') as response:
                data = await response.json()
        except aiohttp.ClientError as e:
            print(f"Error: {e}")
            return

    lvlroles = [f"lvl{lvl}" for lvl in range(10, 110, 10)]
    discord_users = data
    users = await autocredits.get_all_users(pymongo_client)

    for user in users.find():
        discord = str(user['auth']['discord'])

        for id_, roles in discord_users.items():
            if id_ == discord:
                for role in lvlroles:
                    if role in roles:
                        users.update_one({'auth.discord': int(discord)}, {
                                         '$set': {'level': role}})
                        print(f"Updated {discord} to {role}")

    return users

if __name__ == "__main__":
    asyncio.run(main())
