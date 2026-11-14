import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def test_activity():
    return {
        "description": "A test activity",
        "schedule": "Mondays, 3:00 PM",
        "max_participants": 3,
        "participants": ["existing@mergington.edu"],
    }


@pytest.fixture
def client(monkeypatch, test_activity):
    monkeypatch.setattr(app_module, "activities", {"Chess Club": test_activity})
    return TestClient(app_module.app)


def test_get_activities_returns_activity_details(client, test_activity):
    # Arrange
    expected_activity = test_activity

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"Chess Club": expected_activity}


def test_signup_adds_participant(client, test_activity):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in test_activity["participants"]


def test_signup_rejects_duplicate_participant(client, test_activity):
    # Arrange
    email = test_activity["participants"][0]

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }
    assert test_activity["participants"] == [email]


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client, test_activity):
    # Arrange
    email = test_activity["participants"][0]

    # Act
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in test_activity["participants"]


def test_unregister_returns_not_found_for_missing_participant(client, test_activity):
    # Arrange
    email = "missing@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert test_activity["participants"] == ["existing@mergington.edu"]


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Unknown%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
