"""
SWYNEX Final AI Application - Test Suite: Flask Web API Endpoints
Tests root route, analysis POST endpoint, sample presets, and evaluation endpoints.
"""

import pytest
from web_app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Student Announcement Intelligence System" in response.data


def test_api_analyze_valid_text(client):
    payload = {
        "text": "The End-Semester Examination timetable for B.Tech Semester 5 is officially released. Admit cards before Friday 5:00 PM."
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["classification"]["category"] == "Exam"
    assert data["priority"]["priority"] == "High"
    assert len(data["extraction"]["dates"]) > 0


def test_api_analyze_empty_text(client):
    payload = {"text": ""}
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is False
    assert "empty" in data["error"]


def test_api_samples_endpoint(client):
    response = client.get("/api/samples")
    assert response.status_code == 200
    data = response.get_json()
    assert "exam" in data
    assert "assignment" in data


def test_api_evaluate_endpoint(client):
    response = client.get("/api/evaluate")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "category_accuracy" in data
    assert len(data["cases"]) == 18
