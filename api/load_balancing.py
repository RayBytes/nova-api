import random
import asyncio

import chat_providers

provider_modules = [
    chat_providers.twa,
    chat_providers.quantum,
    chat_providers.churchless,
    chat_providers.closed,
    chat_providers.closed4
]

async def balance_chat_request(payload: dict) -> dict:
    providers_available = []

    for provider_module in provider_modules:
        if payload['stream'] and not provider_module.STREAMING:
            continue

        if payload['model'] not in provider_module.MODELS:
            continue

        providers_available.append(provider_module)

    provider = random.choice(providers_available)
    return provider.chat_completion(**payload)

async def balance_organic_request(request: dict) -> dict:
    providers_available = []

    for provider_module in provider_modules:
        if provider_module.ORGANIC:
            providers_available.append(provider_module)

    provider = random.choice(providers_available)

    return provider.organify(request)

if __name__ == '__main__':
    req = asyncio.run(balance_chat_request(payload={'model': 'gpt-3.5-turbo', 'stream': True}))
    print(req['url'])
