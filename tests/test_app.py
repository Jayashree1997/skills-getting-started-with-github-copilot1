from fastapi.testclient import TestClient
from src.app import app, activities
import copy

client = TestClient(app)


def setup_function():
    # backup activities state before each test
    global _orig_activities
    _orig_activities = copy.deepcopy(activities)


def teardown_function():
    # restore original state after each test
    activities.clear()
    activities.update(copy.deepcopy(_orig_activities))


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Basketball Team" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "newstudent@example.com"

    # Ensure email not already registered
    assert email not in activities[activity]["participants"]

    # Sign up
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert f"Signed up {email}" in resp.json().get("message", "")

    # Verify participant present in activities listing
    resp2 = client.get("/activities")
    assert resp2.status_code == 200
    assert email in resp2.json()[activity]["participants"]

    # Unregister
    resp3 = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert resp3.status_code == 200
    assert f"Unregistered {email}" in resp3.json().get("message", "")

    # Verify participant removed
    resp4 = client.get("/activities")
    assert resp4.status_code == 200
    assert email not in resp4.json()[activity]["participants"]


def test_unregister_nonexistent_participant():
    activity = "Chess Club"
    email = "doesnotexist@example.com"

    # Ensure email not present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    resp = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 404


def test_activity_not_found():
    resp = client.post("/activities/NoSuchActivity/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404
    resp2 = client.post("/activities/NoSuchActivity/unregister", params={"email": "a@b.com"})
    assert resp2.status_code == 404
