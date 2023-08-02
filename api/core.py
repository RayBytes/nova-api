"""User management."""

import os
import json
import fastapi

from db import users

from dotenv import load_dotenv

load_dotenv()
router = fastapi.APIRouter(tags=['core'])

async def check_core_auth(request):
    received_auth = request.headers.get('Authorization')

    if received_auth != os.getenv('CORE_API_KEY'):
        return fastapi.Response(status_code=403, content='Invalid or no API key given.')

@router.get('/users')
async def get_users(discord_id: int, incoming_request: fastapi.Request):
    auth_error = await check_core_auth(incoming_request)

    if auth_error:
        return auth_error

    user = await users.by_discord_id(discord_id)

    if not user:
        return fastapi.Response(status_code=404, content='User not found.')

    return user

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
    
    user = await users.create(discord_id)
    return user
