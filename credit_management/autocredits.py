async def get_all_users(client):
    users = client['nova-core']['users']
    return users
        
async def update_credits(users, settings = None):
    if not settings:
        users.update_many({}, {"$inc": {"credits": 250}})

    else:
        for key, value in settings.items():
            users.update_many({'role': key}, {"$inc": {"credits": int(value)}})
            print(f"Updated {key} to {value}")