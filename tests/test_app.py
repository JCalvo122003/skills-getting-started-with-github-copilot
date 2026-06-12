import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_success(self, client):
        """Test successfully fetching all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_has_required_fields(self, client):
        """Test that activities have all required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_get_activities_participants_is_list(self, client):
        """Test that participants field is a list"""
        response = client.get("/activities")
        data = response.json()
        for activity_name, activity_details in data.items():
            assert isinstance(activity_details["participants"], list)


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_duplicates_not_allowed(self, client):
        """Test that a student cannot sign up twice for the same activity"""
        email = "duplicate@mergington.edu"
        # First signup
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response1.status_code == 200

        # Second signup attempt
        response2 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_updates_participant_count(self, client):
        """Test that signup actually adds the participant"""
        email = "counter@mergington.edu"
        
        # Get initial count
        activities_before = client.get("/activities").json()
        initial_count = len(activities_before["Chess Club"]["participants"])

        # Signup
        client.post(f"/activities/Chess Club/signup?email={email}")

        # Get updated count
        activities_after = client.get("/activities").json()
        final_count = len(activities_after["Chess Club"]["participants"])

        assert final_count == initial_count + 1
        assert email in activities_after["Chess Club"]["participants"]

    def test_signup_multiple_different_activities(self, client):
        """Test that a student can sign up for multiple different activities"""
        email = "multi@mergington.edu"
        
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        response2 = client.post(
            f"/activities/Programming Class/signup?email={email}"
        )

        assert response1.status_code == 200
        assert response2.status_code == 200

        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        # First signup
        email = "unreg@mergington.edu"
        client.post(f"/activities/Chess Club/signup?email={email}")

        # Then unregister
        response = client.post(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant"""
        email = "remove@mergington.edu"
        
        # Signup
        client.post(f"/activities/Chess Club/signup?email={email}")
        activities_after_signup = client.get("/activities").json()
        assert email in activities_after_signup["Chess Club"]["participants"]

        # Unregister
        client.post(f"/activities/Chess Club/unregister?email={email}")
        activities_after_unregister = client.get("/activities").json()
        assert email not in activities_after_unregister["Chess Club"]["participants"]

    def test_unregister_nonexistent_participant(self, client):
        """Test unregistering a participant who is not signed up"""
        response = client.post(
            "/activities/Chess Club/unregister?email=notmember@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from an activity that doesn't exist"""
        response = client.post(
            "/activities/Fake Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_twice_fails(self, client):
        """Test that unregistering the same person twice fails the second time"""
        email = "double@mergington.edu"
        
        # Signup
        client.post(f"/activities/Chess Club/signup?email={email}")

        # First unregister should succeed
        response1 = client.post(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response1.status_code == 200

        # Second unregister should fail
        response2 = client.post(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response2.status_code == 404


class TestRootRedirect:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that root path redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
