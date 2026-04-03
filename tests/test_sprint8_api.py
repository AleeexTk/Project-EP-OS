import pytest
from fastapi.testclient import TestClient
from beta_pyramid_functional.D_Interface.evo_api import app

client = TestClient(app)

def test_api_architecture_map():
    response = client.get("/api/architecture/map")
    assert response.status_code == 200
    data = response.json()
    assert "modules" in data
    assert "routes" in data

def test_api_architecture_catalog():
    response = client.get("/api/architecture/catalog")
    assert response.status_code == 200
    data = response.json()
    assert "solutions" in data

def test_api_timeline():
    # Even if empty, it should return a list or an object
    response = client.get("/api/timeline")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
