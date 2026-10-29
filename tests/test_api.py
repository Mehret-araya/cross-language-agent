
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_frontend_and_assets_are_served():
    page = client.get("/")
    script = client.get("/assets/app.js")
    stylesheet = client.get("/assets/styles.css")
    root_script = client.get("/app.js")
    root_stylesheet = client.get("/styles.css")
    root_favicon = client.get("/favicon.svg")

    assert page.status_code == 200
    assert "Cross-Language Interoperability Agent" in page.text
    assert script.status_code == 200
    assert "analyze-with-execution" in script.text
    assert stylesheet.status_code == 200
    assert "package-grid" in stylesheet.text
    assert root_script.status_code == 200
    assert "analyze-with-execution" in root_script.text
    assert root_stylesheet.status_code == 200
    assert "package-grid" in root_stylesheet.text
    assert root_favicon.status_code == 200


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
    assert data["analysis"]["compatible"] is False
    assert "No matching export names" in data["analysis"]["risks"][1]
    assert data["strategy"]["name"] == "rest_api"
    assert data["adapter_plan"]["strategy"] == "rest_api"
    assert len(data["adapter_plan"]["steps"]) == 4
    assert len(data["adapter_plan"]["test_requirements"]) == 3


def test_analyze_normalizes_language_and_export_names():
    response = client.post(
        "/analyze",
        json={
            "source": {
                "name": "source",
                "language": " PYTHON ",
                "exports": [" calculate_total "],
            },
            "target": {
                "name": "target",
                "language": "python",
                "exports": ["calculate_total"],
            },
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["strategy"]["name"] == "direct_import"
    assert "Exports with matching names: calculate_total" in (
        data["analysis"]["evidence"]
    )
    assert any(
        "do not prove API compatibility" in risk
        for risk in data["analysis"]["risks"]
    )


def test_analyze_rejects_more_than_100_exports():
    response = client.post(
        "/analyze",
        json={
            "source": {
                "name": "source",
                "language": "Python",
                "exports": [f"export_{index}" for index in range(101)],
            },
            "target": {"name": "target", "language": "Java"},
        },
    )

    assert response.status_code == 422


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
