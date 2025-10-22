"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    assert response.json() == activities
    
    # Verify specific activity details
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)

def test_signup_success():
    response = client.post("/activities/Chess Club/signup?email=new.student@mergington.edu")
    assert response.status_code == 200
    assert "new.student@mergington.edu" in activities["Chess Club"]["participants"]
    assert response.json() == {"message": "Signed up new.student@mergington.edu for Chess Club"}

def test_signup_nonexistent_activity():
    response = client.post("/activities/Nonexistent Club/signup?email=student@mergington.edu")
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}

def test_signup_duplicate_student():
    # First signup
    client.post("/activities/Programming Class/signup?email=test.student@mergington.edu")
    
    # Try to sign up the same student again
    response = client.post("/activities/Chess Club/signup?email=test.student@mergington.edu")
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for an activity"}

@pytest.fixture(autouse=True)
def cleanup():
    # Store original participants
    original_participants = {
        activity: list(details["participants"])
        for activity, details in activities.items()
    }
    
    yield
    
    # Restore original participants after each test
    for activity, participants in original_participants.items():
        activities[activity]["participants"] = participants