
import json
from typing import Any, Callable


def handle_json_request(
    request_json: str,
    function: Callable[..., Any],
) -> str:
    """Call a Python function using JSON input and return JSON output."""
    try:
        request = json.loads(request_json)

        if not isinstance(request, dict):
            raise ValueError("Request must be a JSON object.")

        arguments = request.get("arguments", {})

        if not isinstance(arguments, dict):
            raise ValueError("'arguments' must be a JSON object.")

        result = function(**arguments)

        return json.dumps({
            "ok": True,
            "result": result,
        })

    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        return json.dumps({
            "ok": False,
            "error": str(exc),
        })
