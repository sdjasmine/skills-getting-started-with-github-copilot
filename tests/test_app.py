import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

ORIGINAL_ACTIVITIES = copy.deepcopy(activities)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_root_redirect(client):
    # Arrange
    # Act
    response = client.get("/", allow_redirects=False)
    # Assert
    assert response.status_code in (301, 307)
    assert "/static/index.html" in response.headers["location"]


def test_get_activities(client):
    # Arrange
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    body = response.json()
    assert "Chess Club" in body
    assert body["Chess Club"]["max_participants"] == 12
    assert "michael@mergington.edu" in body["Chess Club"]["participants"]


def test_signup_for_activity(client):
    # Arrange
    email = "newstudent@mergington.edu"
    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_rejected(client):
    # Arrange
    email = "michael@mergington.edu"
    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})
    # Assert
    assert response.status_code == 400


def test_delete_participant(client):
    # Arrange
    email = "michael@mergington.edu"
    # Act
    response = client.delete("/activities/Chess Club/participants", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_delete_nonexistent_participant(client):
    # Arrange
    email = "nonexistent@mergington.edu"
    # Act
    response = client.delete("/activities/Chess Club/participants", params={"email": email})
    # Assert
    assert response.status_code == 404
