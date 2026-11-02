"""Integration tests for OpenRFP FastAPI REST endpoints."""

import pytest
from fastapi.testclient import TestClient
from openrfp.api.server import create_app
from openrfp.models import RequirementCategory


@pytest.fixture
def client(temp_storage_dir, monkeypatch):
    """Provide a TestClient with storage directed to temporary directory."""
    monkeypatch.setattr("openrfp.api.routes.storage.base_dir", temp_storage_dir)
    monkeypatch.setattr("openrfp.api.routes.storage.rfp_dir", temp_storage_dir / "rfps")
    monkeypatch.setattr("openrfp.api.routes.storage.kb_dir", temp_storage_dir / "knowledge")
    monkeypatch.setattr("openrfp.api.routes.storage.proposal_dir", temp_storage_dir / "proposals")
    monkeypatch.setattr("openrfp.storage.settings.data_dir", temp_storage_dir)
    app = create_app()
    return TestClient(app)


def test_should_return_healthy_status_on_health_check(client):
    """Verify /api/v1/health returns 200 OK and status."""
    # Act
    response = client.get("/api/v1/health")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"


def test_should_serve_ui_dashboard_on_root(client):
    """Verify GET / returns HTML dashboard."""
    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "OpenRFP Agent" in response.text


def test_should_parse_rfp_via_api(client):
    """Verify POST /api/v1/rfp/parse extracts compliance matrix."""
    # Arrange
    payload = {
        "title": "Cloud Banking RFP",
        "buyer_name": "Apex Bank",
        "raw_text": "# Section: Security\n- Must support AES-256 and SOC 2.\n- Must provide 99.99% uptime."
    }

    # Act
    response = client.post("/api/v1/rfp/parse", json=payload)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Cloud Banking RFP"
    assert len(data["requirements"]) == 2


def test_should_add_and_search_knowledge_via_api(client):
    """Verify knowledge item creation and hybrid search."""
    # Arrange
    kb_item = {
        "id": "KB-TEST-001",
        "title": "SOC 2 Report",
        "category": RequirementCategory.SECURITY_COMPLIANCE.value,
        "content": "We maintain an active annual SOC 2 Type II attestation report.",
        "tags": ["SOC 2", "Compliance"]
    }

    # Act - Add
    add_res = client.post("/api/v1/knowledge", json=kb_item)
    assert add_res.status_code == 200

    # Act - Search
    search_res = client.post(
        "/api/v1/knowledge/search",
        json={"query": "SOC 2 Type II attestation", "category": RequirementCategory.SECURITY_COMPLIANCE.value}
    )

    # Assert
    assert search_res.status_code == 200
    results = search_res.json()
    assert len(results) > 0
    assert results[0]["item"]["id"] == "KB-TEST-001"


def test_should_parse_and_draft_end_to_end_via_api(client):
    """Verify full pipeline: shredding, matching, drafting, and export."""
    # Arrange
    client.post("/api/v1/knowledge", json={
        "id": "KB-SLA-01",
        "title": "High Availability SLA",
        "category": RequirementCategory.SLA_SUPPORT.value,
        "content": "Guaranteed 99.99% uptime with SLA financial credits.",
        "tags": ["SLA", "Uptime"]
    })
    payload = {
        "title": "FinTech Tender",
        "buyer_name": "FinTech Corp",
        "raw_text": "# Requirements\n- Vendor must guarantee 99.99% uptime.\n- Must support quantum physics."
    }

    # Act
    res = client.post("/api/v1/rfp/parse-and-draft", json=payload)

    # Assert
    assert res.status_code == 200
    data = res.json()
    assert len(data["drafts"]) == 2
    rfp_id = data["rfp_id"]

    # Act - Export markdown
    export_res = client.get(f"/api/v1/proposal/{rfp_id}/export/markdown")
    assert export_res.status_code == 200
    assert "Proposal Response for FinTech Corp" in export_res.text


def test_should_return_404_when_rfp_not_found(client):
    """Verify non-existent RFP returns 404."""
    # Act
    response = client.get("/api/v1/rfp/non-existent-id")

    # Assert
    assert response.status_code == 404
