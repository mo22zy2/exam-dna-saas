from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def _rate_limit_key(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        return get_remote_address(request)
    from app.auth.utils import decode_access_token
    user_id = decode_access_token(token)
    if user_id:
        return str(user_id)
    return get_remote_address(request)


limiter = Limiter(key_func=_rate_limit_key, default_limits=["10/minute"])
