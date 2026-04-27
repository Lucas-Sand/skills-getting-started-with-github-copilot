import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app, follow_redirects=False)

def test_root_redirect():
    # Arrange
    # No special setup needed
    
    # Act
    response = client.get("/")
    
    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    # Arrange
    # No special setup needed
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9
    assert "Chess Club" in data
    activity = data["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity

def test_signup_success():
    # Arrange
    email = "test@example.com"
    activity = "Chess Club"
    
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert f"Signed up {email} for {activity}" in data["message"]
    
    # Verify added
    response = client.get("/activities")
    data = response.json()
    assert email in data[activity]["participants"]

def test_signup_activity_not_found():
    # Arrange
    email = "test@example.com"
    activity = "Nonexistent"
    
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_signup_already_signed_up():
    # Arrange
    email = "duplicate@example.com"
    activity = "Programming Class"
    client.post(f"/activities/{activity}/signup?email={email}")
    
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up for this activity" in data["detail"]

def test_signup_activity_full():
    # Arrange
    activity = "Chess Club"
    max_participants = 12
    for i in range(max_participants):
        email = f"full{i}@example.com"
        client.post(f"/activities/{activity}/signup?email={email}")
    
    email = "overflow@example.com"
    
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "Activity is full" in data["detail"]

def test_delete_participant_success():
    # Arrange
    email = "remove@example.com"
    activity = "Gym Class"
    client.post(f"/activities/{activity}/signup?email={email}")
    
    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert f"Removed {email} from {activity}" in data["message"]
    
    # Verify removed
    response = client.get("/activities")
    data = response.json()
    assert email not in data[activity]["participants"]

def test_delete_activity_not_found():
    # Arrange
    email = "test@example.com"
    activity = "Nonexistent"
    
    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_delete_participant_not_found():
    # Arrange
    email = "nonexistent@example.com"
    activity = "Chess Club"
    
    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Participant not found" in data["detail"]
