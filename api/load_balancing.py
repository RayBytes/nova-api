import random
import asyncio

import providers

provider_modules = [
    # providers.twa,
    # providers.quantum,
    providers.churchless,
    providers.closed,
    providers.closed4
]

def _get_module_name(module) -> str:
    name = module.__name__
    if '.' in name:
        return name.split('.')[-1]
    return name

async def balance_chat_request(payload: dict) -> dict:
    providers_available = []

    for provider_module in provider_modules:
        if payload['stream'] and not provider_module.STREAMING:
            continue

        if payload['model'] not in provider_module.MODELS:
            continue

        providers_available.append(provider_module)

    if not providers_available:
        raise NotImplementedError('This model does not exist.')

    provider = random.choice(providers_available)
    target = provider.chat_completion(**payload)
    target['module'] = _get_module_name(provider)

    return target

async def balance_organic_request(request: dict) -> dict:
    providers_available = []

    for provider_module in provider_modules:
        if provider_module.ORGANIC:
            providers_available.append(provider_module)

    provider = random.choice(providers_available)
    target = provider.organify(request)
    target['module'] = _get_module_name(provider)

    return target

if __name__ == '__main__':
    req = asyncio.run(balance_chat_request(payload={'model': 'gpt-3.5-turbo', 'stream': True}))
    print(req['url'])
