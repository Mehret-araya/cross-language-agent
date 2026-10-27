
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_analyze_endpoint_returns_workflow_result():
    response = client.post(
        "/analyze",
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
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert "analysis" in data
    assert "strategy" in data
    assert "adapter_plan" in data
    assert data["strategy"]["name"]
    assert data["adapter_plan"]["steps"]


def test_analyze_rejects_blank_package_metadata():
    response = client.post(
        "/analyze",
        json={
            "source": {"name": " ", "language": "Python"},
            "target": {"name": "target", "language": "Java"},
        },
    )

    assert response.status_code == 422


def test_analyze_rejects_blank_export_names():
    response = client.post(
        "/analyze",
        json={
            "source": {
                "name": "source",
                "language": "Python",
                "exports": [" "],
            },
            "target": {"name": "target", "language": "Java"},
        },
    )

    assert response.status_code == 422


def test_analyze_rejects_unknown_package_fields():
    response = client.post(
        "/analyze",
        json={
            "source": {
                "name": "source",
                "language": "Python",
                "unexpected": True,
            },
            "target": {"name": "target", "language": "Java"},
        },
    )

    assert response.status_code == 422
