"""User management."""

import os
import json
import fastapi

from db.users import UserManager

from dhooks import Webhook, Embed
from dotenv import load_dotenv

load_dotenv()
router = fastapi.APIRouter(tags=['core'])

async def check_core_auth(request):
    """
    
    ### Checks the request's auth
    Auth is taken from environment variable `CORE_API_KEY`

    """
    received_auth = request.headers.get('Authorization')

    if received_auth != os.getenv('CORE_API_KEY'):
        return fastapi.Response(status_code=403, content='Invalid or no API key given.')

@router.get('/users')
async def get_users(discord_id: int, incoming_request: fastapi.Request):
    auth = await check_core_auth(incoming_request)
    if auth:
        return auth

    # Get user by discord ID
    manager = UserManager()
    user = await manager.user_by_discord_id(discord_id)
    if not user:
        return fastapi.Response(status_code=404, content='User not found.')

    return user

async def new_user_webhook(user: dict) -> None:    
    dhook = Webhook(os.getenv('DISCORD_WEBHOOK__USER_CREATED'))

    embed = Embed(
        description='New User',
        color=0x90ee90,
    )

    embed.add_field(name='ID', value=str(user['_id']), inline=False)
    embed.add_field(name='Discord', value=user['auth']['discord'] or '-')
    embed.add_field(name='Github', value=user['auth']['github'] or '-')

    dhook.send(embed=embed)

@router.post('/users')
async def create_user(incoming_request: fastapi.Request):
    auth_error = await check_core_auth(incoming_request)

    if auth_error:
        return auth_error

    try:
        payload = await incoming_request.json()
        discord_id = payload.get('discord_id')
    except (json.decoder.JSONDecodeError, AttributeError):
        return fastapi.Response(status_code=400, content='Invalid or no payload received.')
    
    # Create the user 
    manager = UserManager()
    user = await manager.create(discord_id)
    await new_user_webhook(user)

    return user

@router.put('/users')
async def update_user(incoming_request: fastapi.Request):
    auth_error = await check_core_auth(incoming_request)

    if auth_error:
        return auth_error

    try:
        payload = await incoming_request.json()
        discord_id = payload.get('discord_id')
        updates = payload.get('updates')
    except (json.decoder.JSONDecodeError, AttributeError):
        return fastapi.Response(status_code=400, content='Invalid or no payload received.')
    
    # Update the user 
    manager = UserManager()
    user = await manager.update_by_discord_id(discord_id, updates)

    return user
