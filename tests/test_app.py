import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_get_activities_returns_activity_list():
    # Arrange
    with TestClient(app) as client:
        # Act
        response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert "participants" in data["Chess Club"]


def test_signup_for_activity_adds_new_participant():
    # Arrange
    email = "teststudent@mergington.edu"

    with TestClient(app) as client:
        # Act
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email},
        )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_existing_participant_returns_bad_request():
    # Arrange
    email = activities["Chess Club"]["participants"][0]

    with TestClient(app) as client:
        # Act
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email},
        )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_remove_from_activity_unregisters_participant():
    # Arrange
    email = activities["Chess Club"]["participants"][0]

    with TestClient(app) as client:
        # Act
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": email},
        )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_remove_unknown_participant_returns_not_found():
    # Arrange
    email = "missing@mergington.edu"

    with TestClient(app) as client:
        # Act
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": email},
        )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
