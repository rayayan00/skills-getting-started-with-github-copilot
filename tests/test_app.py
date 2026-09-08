from src.app import activities


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_details(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_activity in response.json()
    assert {
        "description",
        "schedule",
        "max_participants",
        "participants",
    } <= response.json()[expected_activity].keys()


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    original_count = len(activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]
    assert len(activities[activity_name]["participants"]) == original_count + 1
    assert activities[activity_name]["participants"].count(email) == 1


def test_duplicate_signup_is_rejected(client):
    # Arrange
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]
    original_participants = activities[activity_name]["participants"].copy()

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities[activity_name]["participants"] == original_participants


def test_signup_for_unknown_activity_returns_not_found(client):
    # Arrange
    activity_name = "Unknown Activity"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_without_email_returns_validation_error(client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422


def test_unregister_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]
    other_participants = activities[activity_name]["participants"][1:].copy()

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert activities[activity_name]["participants"] == other_participants
    assert email in response.json()["message"]


def test_unregister_from_unknown_activity_returns_not_found(client):
    # Arrange
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_missing_participant_returns_not_found(client):
    # Arrange
    activity_name = "Chess Club"
    email = "missing.student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_repeated_unregister_returns_not_found(client):
    # Arrange
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]
    endpoint = f"/activities/{activity_name}/participants/{email}"

    # Act
    first_response = client.delete(endpoint)
    second_response = client.delete(endpoint)

    # Assert
    assert first_response.status_code == 200
    assert second_response.status_code == 404
    assert second_response.json()["detail"] == "Participant not found"
