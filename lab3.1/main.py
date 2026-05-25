from typing import Dict, Any

import framework
import views  # noqa: F401 — registers all routes via decorators


def dispatch(request: Dict[str, Any]) -> Dict[str, Any]:
    method = request.get("method", "").upper()
    path = request.get("path", "")
    handler = framework._routes.get((method, path))
    if handler is None:
        return {"status_code": 404, "body": "Not Found", "headers": {}}
    return handler(request)
