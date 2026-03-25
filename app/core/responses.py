from typing import Any


def success_response(
    message: str,
    data: Any = None,
    status_code: int = 200,
) -> dict[str, Any]:
    return {
        "success": True,
        "message": message,
        "data": data,
        "status_code": status_code,
    }


def error_response(message: str, error: Any = None) -> dict[str, Any]:
    return {
        "success": False,
        "message": message,
        "error": error,
    }
