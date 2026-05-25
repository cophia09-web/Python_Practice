from functools import wraps
from typing import Callable, Dict, Any, List

transaction_log: List[Dict[str, Any]] = []


def audit_log(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(request: Dict[str, Any]) -> Dict[str, Any]:
        log_entry = {
            "method": request.get("method"),
            "path": request.get("path"),
            "user_id": request.get("session", {}).get("user_id"),
            "status_code": None
        }
        transaction_log.append(log_entry)
        response = func(request)
        log_entry["status_code"] = response.get("status_code")
        return response
    return wrapper


def login_required(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(request: Dict[str, Any]) -> Dict[str, Any]:
        if not request.get("session", {}).get("user_id"):
            return {"status_code": 401, "body": "Unauthorized", "headers": {}}
        return func(request)
    return wrapper


def role_required(required_role: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request: Dict[str, Any]) -> Dict[str, Any]:
            session = request.get("session", {})
            if session.get("role") != required_role:
                return {"status_code": 403, "body": "Forbidden", "headers": {}}
            return func(request)
        return wrapper
    return decorator
