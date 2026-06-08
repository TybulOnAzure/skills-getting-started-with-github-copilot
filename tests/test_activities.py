"""
Test suite for Mergington High School Activities API using AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        # Arrange: No setup needed, activities are pre-loaded
        
        # Act: Make GET request to activities endpoint
        response = client.get("/activities")
        
        # Assert: Check response status and data structure
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "participants" in data["Chess Club"]
        assert "max_participants" in data["Chess Club"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_for_activity_success(self, client):
        # Arrange: Prepare test data
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act: Submit signup request
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert: Verify successful signup
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    def test_signup_duplicate_email_fails(self, client):
        # Arrange: Get an existing participant and activity
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act: Attempt to sign up with existing email
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert: Verify duplicate signup is rejected
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_for_nonexistent_activity_fails(self, client):
        # Arrange: Use a non-existent activity name
        activity_name = "Fake Club"
        email = "test@mergington.edu"
        
        # Act: Attempt signup for non-existent activity
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert: Verify 404 error
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_adds_participant_to_activity_list(self, client):
        # Arrange: Prepare new participant
        activity_name = "Drama Club"
        email = "newactor@mergington.edu"
        
        # Act: Sign up the participant
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act: Fetch activities to verify participant was added
        activities = client.get("/activities").json()
        
        # Assert: Verify participant appears in activity
        assert email in activities[activity_name]["participants"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint."""

    def test_remove_participant_success(self, client):
        # Arrange: First, sign up a participant
        activity_name = "Basketball Team"
        email = "tempplayer@mergington.edu"
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act: Remove the participant
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert: Verify successful removal
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"

    def test_remove_participant_verifies_removal(self, client):
        # Arrange: Sign up a participant first
        activity_name = "Art Studio"
        email = "tempartist@mergington.edu"
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act: Remove the participant and fetch activities
        client.delete(f"/activities/{activity_name}/participants/{email}")
        activities = client.get("/activities").json()
        
        # Assert: Verify participant is no longer in the list
        assert email not in activities[activity_name]["participants"]

    def test_remove_nonexistent_participant_fails(self, client):
        # Arrange: Use non-existent email for an activity
        activity_name = "Science Club"
        email = "noone@mergington.edu"
        
        # Act: Attempt to remove non-existent participant
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert: Verify 404 error
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    def test_remove_from_nonexistent_activity_fails(self, client):
        # Arrange: Use non-existent activity
        activity_name = "Nonexistent Club"
        email = "test@mergington.edu"
        
        # Act: Attempt to remove from non-existent activity
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert: Verify 404 error
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
