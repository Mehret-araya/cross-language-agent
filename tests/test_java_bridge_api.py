from fastapi.testclient import TestClient

from app.main import app

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
