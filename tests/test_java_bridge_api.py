import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.integrations.java_bridge import (
    JavaBridgeError,
    JavaBridgeTimeout,
    JavaToolchainUnavailable,
    run_java_billing_example,
)

client = TestClient(app)


def test_execute_billing_example_endpoint():
    response = client.post(
        "/execute-billing-example",
        json={
            "unit_price": "20.00",
            "quantity": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["ok"] is True
    assert data["result"]["unit_price"] == "20.00"
    assert data["result"]["quantity"] == 3
    assert data["result"]["total"] == "60.00"


def test_java_bridge_surfaces_worker_errors():
    with pytest.raises(
        JavaBridgeError,
        match="Java billing example failed: Unit price must be a valid number.",
    ):
        run_java_billing_example("not-a-price", 3)


def test_analyze_with_execution_endpoint():
    response = client.post(
        "/analyze-with-execution",
        json={
            "source": {
                "name": "billing-python",
                "language": "Python",
                "version": "1.0",
                "runtime": "Python 3.12",
                "exports": ["calculate_total"],
            },
            "target": {
                "name": "billing-java",
                "language": "Java",
                "version": "1.0",
                "runtime": "JVM",
                "exports": ["calculateTotal"],
            },
            "execute_example": True,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert "analysis" in data
    assert "strategy" in data
    assert "adapter_plan" in data
    assert data["execution_example"]["ok"] is True
    assert data["execution_example"]["result"]["total"] == "60.00"


def test_execute_billing_example_rejects_invalid_price():
    response = client.post(
        "/execute-billing-example",
        json={
            "unit_price": "abc",
            "quantity": 3,
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize("price", ["NaN", "Infinity", "-Infinity", "-0.01"])
def test_execute_billing_example_rejects_invalid_decimal_values(price):
    response = client.post(
        "/execute-billing-example",
        json={"unit_price": price, "quantity": 3},
    )

    assert response.status_code == 422


def test_execute_billing_example_rejects_negative_quantity():
    response = client.post(
        "/execute-billing-example",
        json={
            "unit_price": "12.50",
            "quantity": -1,
        },
    )

    assert response.status_code == 422


def test_execute_billing_example_rejects_boolean_quantity():
    response = client.post(
        "/execute-billing-example",
        json={"unit_price": "12.50", "quantity": True},
    )

    assert response.status_code == 422


def test_execute_billing_example_rejects_unknown_fields():
    response = client.post(
        "/execute-billing-example",
        json={
            "unit_price": "12.50",
            "quantity": 3,
            "unexpected": True,
        },
    )

    assert response.status_code == 422


def test_execute_billing_example_reports_missing_java_toolchain(monkeypatch):
    def fail_with_missing_toolchain(**kwargs):
        raise JavaToolchainUnavailable("Java runtime was not found.")

    monkeypatch.setattr(
        "app.api.routes.analysis.run_java_billing_example",
        fail_with_missing_toolchain,
    )

    response = client.post(
        "/execute-billing-example",
        json={"unit_price": "12.50", "quantity": 3},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Java runtime was not found."


def test_execute_billing_example_reports_bridge_failures(monkeypatch):
    def fail_bridge(**kwargs):
        raise JavaBridgeError("Java bridge failed.")

    monkeypatch.setattr(
        "app.api.routes.analysis.run_java_billing_example",
        fail_bridge,
    )

    response = client.post(
        "/execute-billing-example",
        json={"unit_price": "12.50", "quantity": 3},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Java bridge failed."


def test_execute_billing_example_reports_bridge_timeouts(monkeypatch):
    def timeout_bridge(**kwargs):
        raise JavaBridgeTimeout("Java billing example timed out.")

    monkeypatch.setattr(
        "app.api.routes.analysis.run_java_billing_example",
        timeout_bridge,
    )

    response = client.post(
        "/execute-billing-example",
        json={"unit_price": "12.50", "quantity": 3},
    )

    assert response.status_code == 504
    assert response.json()["detail"] == "Java billing example timed out."


def test_analyze_with_execution_reports_bridge_failures(monkeypatch):
    def fail_bridge(**kwargs):
        raise JavaBridgeError("Java bridge failed.")

    monkeypatch.setattr(
        "app.services.interoperability_service.run_java_billing_example",
        fail_bridge,
    )

    response = client.post(
        "/analyze-with-execution",
        json={
            "source": {"name": "billing-python", "language": "Python"},
            "target": {"name": "billing-java", "language": "Java"},
            "execute_example": True,
        },
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Java bridge failed."
