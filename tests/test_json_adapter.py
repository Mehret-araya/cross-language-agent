import json

from app.integrations.billing_example import calculate_total
from app.integrations.json_adapter import handle_json_request
from app.services.interoperability_service import run_adapter_example


def add(a, b):
    return a + b


def test_adapter_returns_function_result():
    response = handle_json_request(
        '{"arguments": {"a": 5, "b": 3}}',
        add,
    )

    data = json.loads(response)

    assert data["ok"] is True
    assert data["result"] == 8


def test_adapter_handles_invalid_json():
    response = handle_json_request(
        "not valid json",
        add,
    )

    data = json.loads(response)

    assert data["ok"] is False
    assert "error" in data


def fail_function():
    raise ValueError("Example function failure")


def test_adapter_handles_function_error():
    response = handle_json_request(
        '{"arguments": {}}',
        fail_function,
    )

    data = json.loads(response)

    assert data["ok"] is False
    assert data["error"] == "Example function failure"


def test_workflow_adapter_example_adds_two_numbers():
    result = run_adapter_example(5, 3)

    assert result == {"ok": True, "result": 8}


def test_adapter_calculates_billing_total():
    response = handle_json_request(
        '{"arguments": {"unit_price": "12.50", "quantity": 4}}',
        calculate_total,
    )

    data = json.loads(response)

    assert data["ok"] is True
    assert data["result"]["unit_price"] == "12.50"
    assert data["result"]["quantity"] == 4
    assert data["result"]["total"] == "50.00"


def test_adapter_handles_negative_billing_quantity():
    response = handle_json_request(
        '{"arguments": {"unit_price": "12.50", "quantity": -1}}',
        calculate_total,
    )

    data = json.loads(response)

    assert data["ok"] is False
    assert data["error"] == "Quantity cannot be negative."


def test_adapter_rejects_nonstandard_json_constants():
    response = handle_json_request(
        '{"arguments": {"a": NaN, "b": 1}}',
        add,
    )

    data = json.loads(response)

    assert data["ok"] is False
    assert "not a valid JSON constant" in data["error"]


def test_adapter_rejects_non_json_results():
    response = handle_json_request(
        '{"arguments": {}}',
        lambda: float("nan"),
    )

    data = json.loads(response)

    assert data["ok"] is False
    assert "Out of range float values" in data["error"]
