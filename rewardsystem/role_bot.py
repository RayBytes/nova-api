import nextcord
import aiohttp.web
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

client = nextcord.Client(intents=nextcord.Intents.all())

@client.event
async def on_ready():
    # start webserver using aiohttp
    app = aiohttp.web.Application()
    
    async def get_roles(request):
        return aiohttp.web.json_response(await get_userinfo())
    
    app.router.add_get('/get_roles', get_roles)

    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, 'localhost', 50000)
    await site.start()

    print('Bot is ready')


async def get_userinfo():
    guild = client.get_guild(int(GUILD_ID))
    members = guild.members

    user_roles = {member.id: [role.name for role in member.roles] for member in members}
    return user_roles

client.run(TOKEN)