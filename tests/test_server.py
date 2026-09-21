"""
Unit and Integration Tests for FastAPI Server and Frontend Routes.
"""

import pytest
from fastapi.testclient import TestClient
from src.server import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_status_endpoint(client):
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["indexed_chunks"] > 0
    assert data["steps_count"] == 7

def test_list_shlokas_endpoint(client):
    response = client.get("/api/shlokas")
    assert response.status_code == 200
    shlokas = response.json()
    assert len(shlokas) == 9
    first = shlokas[0]
    assert "id" in first
    assert "text" in first
    assert first["shloka_number"] == 1

def test_shloka_detail_by_id_and_number(client):
    # Test by full ID
    res1 = client.get("/api/shlokas/sushruta_nidana_ch1_shloka_001_002")
    assert res1.status_code == 200
    assert res1.json()["shloka"]["shloka_number"] == 1

    # Test by numeric shloka number
    res2 = client.get("/api/shlokas/1")
    assert res2.status_code == 200
    assert res2.json()["shloka"]["shloka_number"] == 1

    # Test by non-existent
    res_404 = client.get("/api/shlokas/9999")
    assert res_404.status_code == 404

def test_semantic_search_endpoint(client):
    response = client.get("/api/search?q=Prana+Vayu&top_k=3")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert "text" in results[0]
    assert "similarity_score" in results[0]

def test_grounded_chat_endpoint(client):
    payload = {
        "shloka_id": "1",
        "message": "What is the subject of this verse?"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 0
    assert "sources" in data
    assert len(data["sources"]) > 0

def test_static_index_serving(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Ayurvidya" in response.text
    assert "btnRunAnalysis" in response.text

def test_run_analysis_and_cache_cycle(client):
    # Run analysis for shloka 1
    resp = client.post("/api/shlokas/1/analyze?force_refresh=false")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["steps"]) == 7
    assert "1" in data["steps"]

    # Clear cache
    del_resp = client.delete("/api/shlokas/1/cache")
    assert del_resp.status_code == 200
    assert "Cache cleared" in del_resp.json()["message"]
