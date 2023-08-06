import json
import starlette

async def error(code: int, message: str, tip: str) -> starlette.responses.Response: 
    info = {'error': {
        'code': code,
        'message': message,
        'tip': tip,
        'website': 'https://nova-oss.com',
        'by': 'NovaOSS/Nova-API'
    }}

    return starlette.responses.Response(status_code=code, content=json.dumps(info))

async def yield_error(code: int, message: str, tip: str) -> str:
    return json.dumps({
        'code': code,
        'message': message,
        'tip': tip
    })
