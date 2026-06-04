from typing import Any


def success_response(data: Any = None, msg: str = "success") -> dict:
    return {"code": 200, "data": data, "msg": msg}
