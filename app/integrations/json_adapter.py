
import json
from typing import Any, Callable


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"{value} is not a valid JSON constant.")


def handle_json_request(
    request_json: str,
    function: Callable[..., Any],
) -> str:
    """Call a Python function using JSON input and return JSON output."""
    try:
        request = json.loads(request_json, parse_constant=_reject_json_constant)

        if not isinstance(request, dict):
            raise ValueError("Request must be a JSON object.")

        arguments = request.get("arguments", {})

        if not isinstance(arguments, dict):
            raise ValueError("'arguments' must be a JSON object.")

        result = function(**arguments)

        return json.dumps({
            "ok": True,
            "result": result,
        }, allow_nan=False)

    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        return json.dumps({
            "ok": False,
            "error": str(exc),
        })
