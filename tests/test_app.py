import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities before each test to avoid cross-test pollution."""
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = original


def test_root_redirects_to_index():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Mergington High School" in resp.text


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success():
    activity = "Chess Club"
    email = "test.student@mergington.edu"
    # quote the activity name for URL safety
    path = f"/activities/{quote(activity)}/signup"
    resp = client.post(path, params={"email": email})
    assert resp.status_code == 200
    assert email in app_module.activities[activity]["participants"]
    assert email in resp.json().get("message", "")


def test_signup_already_signed():
    activity = "Chess Club"
    # pick one of the existing participants
    existing = app_module.activities[activity]["participants"][0]
    path = f"/activities/{quote(activity)}/signup"
    resp = client.post(path, params={"email": existing})
    assert resp.status_code == 400


def test_signup_activity_not_found():
    activity = "Nonexistent Club"
    path = f"/activities/{quote(activity)}/signup"
    resp = client.post(path, params={"email": "x@x.com"})
    assert resp.status_code == 404
