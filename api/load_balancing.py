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

async def _get_module_name(module) -> str:
    name = module.__name__
    if '.' in name:
        return name.split('.')[-1]
    return name

async def balance_chat_request(payload: dict) -> dict:
    """Load balance the chat completion request between chat providers."""

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
    
    module_name = await _get_module_name(provider)
    target['module'] = module_name

    return target

async def balance_organic_request(request: dict) -> dict:
    """Load balnace to non-chat completion request between other "organic" providers which respond in the desired format already."""

    providers_available = []

    if not request.get('headers'):
        request['headers'] = {
            'Content-Type': 'application/json'
        }

    for provider_module in provider_modules:
        if not provider_module.ORGANIC:
            continue

        if '/moderations' in request['path']:
            if not provider_module.MODERATIONS:
                continue

        providers_available.append(provider_module)

    provider = random.choice(providers_available)
    target = provider.organify(request)

    module_name = await _get_module_name(provider)
    target['module'] = module_name

    return target

if __name__ == '__main__':
    req = asyncio.run(balance_chat_request(payload={'model': 'gpt-3.5-turbo', 'stream': True}))
    print(req['url'])
