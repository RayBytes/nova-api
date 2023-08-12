import json
import starlette

async def error(code: int, message: str, tip: str) -> starlette.responses.Response:
    """Returns a starlette response JSON with the given error code, message and tip."""

    info = {'error': {
        'code': code,
        'message': message,
        'tip': tip,
        'website': 'https://nova-oss.com',
        'by': 'NovaOSS/Nova-API'
    }}

    return starlette.responses.Response(status_code=code, content=json.dumps(info))

async def yield_error(code: int, message: str, tip: str) -> str:
    """Returns a dumped JSON response with the given error code, message and tip."""

    return json.dumps({
        'code': code,
        'message': message,
        'tip': tip
    })
