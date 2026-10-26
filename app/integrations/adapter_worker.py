
import json
import sys

from app.integrations.billing_example import calculate_total
from app.integrations.json_adapter import handle_json_request


def main() -> None:
    request_json = sys.stdin.readline()

    if not request_json:
        return

    response = handle_json_request(request_json, calculate_total)
    print(response, flush=True)


if __name__ == "__main__":
    main()
