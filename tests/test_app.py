from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


def test_get_activities_returns_available_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    activities_data = response.json()
    assert "Chess Club" in activities_data
    assert isinstance(activities_data["Chess Club"]["participants"], list)


def test_signup_adds_participant_to_activity():
    activity_name = "Chess Club"
    email = "test_student@mergington.edu"
    encoded_activity = quote(activity_name, safe="")

    # Ensure test participant is not already present before signup
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    response = client.post(
        f"/activities/{encoded_activity}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    activities[activity_name]["participants"].remove(email)


def test_remove_participant_deletes_an_existing_participant():
    activity_name = "Programming Class"
    email = "remove_test@mergington.edu"
    encoded_activity = quote(activity_name, safe="")

    if email not in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].append(email)

    response = client.delete(
        f"/activities/{encoded_activity}/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Successfully removed {email} from {activity_name}"


def test_signup_duplicate_returns_400():
    activity_name = "Chess Club"
    email = "duplicate_test@mergington.edu"
    encoded_activity = quote(activity_name, safe="")

    if email not in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].append(email)

    response = client.post(
        f"/activities/{encoded_activity}/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"

    activities[activity_name]["participants"].remove(email)


def test_remove_nonexistent_participant_returns_404():
    activity_name = "Programming Class"
    email = "missing_test@mergington.edu"
    encoded_activity = quote(activity_name, safe="")

    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    response = client.delete(
        f"/activities/{encoded_activity}/participants",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
