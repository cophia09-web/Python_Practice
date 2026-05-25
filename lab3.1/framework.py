from types import SimpleNamespace
from typing import Dict, Callable, Tuple

_routes: Dict[Tuple[str, str], Callable] = {}


def register_route(method: str, path: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        _routes[(method, path)] = func
        return func
    return decorator


def get(path: str) -> Callable:
    return register_route("GET", path)


def post(path: str) -> Callable:
    return register_route("POST", path)


app = SimpleNamespace(get=get, post=post)
