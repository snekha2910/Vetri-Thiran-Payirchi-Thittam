class TestHomePlanner:
    def test_generate_home_plan(self, client, auth_headers):
        payload = {
            "title": "Living Room Redesign",
            "room_type": "living_room",
            "room_size_sqft": 250.0,
            "style": "Modern Minimalist",
            "total_budget": 50000.0,
            "currency": "INR",
            "budget_flexibility": "flexible",
            "key_priorities": ["Sofa", "Lighting"],
            "color_preferences": ["Grey", "Teal"]
        }
        resp = client.post("/api/v1/planner/home", json=payload, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "plan_id" in data
        assert "recommendations" in data
        assert "budget_summary" in data

    def test_home_plan_budget_structure(self, client, auth_headers):
        payload = {
            "title": "Bedroom Refresh",
            "room_type": "bedroom",
            "room_size_sqft": 180.0,
            "style": "Scandinavian",
            "total_budget": 40000.0,
            "currency": "INR",
            "budget_flexibility": "strict",
            "key_priorities": ["Bed frame", "Mattress"]
        }
        resp = client.post("/api/v1/planner/home", json=payload, headers=auth_headers)
        assert resp.status_code == 200
        summary = resp.json()["budget_summary"]
        assert summary["total_budget"] == 40000.0
        assert "remaining_budget" in summary

    def test_home_plan_requires_auth(self, client):
        resp = client.post("/api/v1/planner/home", json={
            "room_type": "living_room",
            "total_budget": 50000.0,
            "currency": "INR"
        })
        assert resp.status_code == 401

    def test_home_plan_low_budget_rejected(self, client, auth_headers):
        resp = client.post("/api/v1/planner/home", json={
            "room_type": "living_room",
            "total_budget": -100.0,
            "currency": "INR"
        }, headers=auth_headers)
        assert resp.status_code == 422

    def test_home_plan_appears_in_history(self, client, auth_headers):
        create_resp = client.post("/api/v1/planner/home", json={
            "title": "History Check Plan",
            "room_type": "kitchen",
            "total_budget": 30000.0,
            "currency": "INR"
        }, headers=auth_headers)
        plan_id = create_resp.json()["plan_id"]

        list_resp = client.get("/api/v1/plans", headers=auth_headers)
        assert list_resp.status_code == 200
        plan_ids = [p["id"] for p in list_resp.json()]
        assert plan_id in plan_ids


class TestPartyPlanner:
    def test_generate_party_plan(self, client, auth_headers):
        payload = {
            "title": "Birthday Party",
            "party_type": "birthday",
            "guest_count": 25,
            "theme": "Retro Disco",
            "total_budget": 35000.0,
            "currency": "INR",
            "venue_type": "indoor"
        }
        resp = client.post("/api/v1/planner/party", json=payload, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["planner_type"] == "party"
        assert len(data["recommendations"]) > 0

    def test_party_plan_requires_guest_count(self, client, auth_headers):
        resp = client.post("/api/v1/planner/party", json={
            "title": "No Guests Party",
            "party_type": "birthday",
            "total_budget": 20000.0,
            "currency": "INR"
        }, headers=auth_headers)
        assert resp.status_code == 422


class TestJewelryPlanner:
    def test_generate_jewelry_plan(self, client, auth_headers):
        payload = {
            "title": "Wedding Sangeet Jewelry",
            "occasion": "wedding",
            "jewelry_type": "set",
            "metal_preference": "gold",
            "style": "Traditional Heritage",
            "total_budget": 80000.0,
            "currency": "INR"
        }
        resp = client.post("/api/v1/planner/jewelry", json=payload, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["planner_type"] == "jewelry"

    def test_recommendation_shape(self, client, auth_headers):
        payload = {
            "title": "Festive Look",
            "occasion": "festival",
            "jewelry_type": "earrings",
            "total_budget": 15000.0,
            "currency": "INR"
        }
        resp = client.post("/api/v1/planner/jewelry", json=payload, headers=auth_headers)
        assert resp.status_code == 200
        recs = resp.json()["recommendations"]
        assert len(recs) > 0
        first = recs[0]
        assert "name" in first
        assert "price" in first
        assert "match_score" in first


class TestPlanCRUD:
    def test_list_plans_empty_for_new_user(self, client, other_user_headers):
        resp = client.get("/api/v1/plans", headers=other_user_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_plan_returns_full_plan(self, client, auth_headers):
        create_resp = client.post("/api/v1/planner/home", json={
            "title": "Full Plan Test",
            "room_type": "living_room",
            "total_budget": 25000.0,
            "currency": "INR"
        }, headers=auth_headers)
        plan_id = create_resp.json()["plan_id"]

        get_resp = client.get(f"/api/v1/plans/{plan_id}", headers=auth_headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == plan_id

    def test_delete_plan(self, client, auth_headers):
        create_resp = client.post("/api/v1/planner/home", json={
            "title": "To Be Deleted",
            "room_type": "bedroom",
            "total_budget": 20000.0,
            "currency": "INR"
        }, headers=auth_headers)
        plan_id = create_resp.json()["plan_id"]

        del_resp = client.delete(f"/api/v1/plans/{plan_id}", headers=auth_headers)
        assert del_resp.status_code in (200, 204)

    def test_cross_user_access_denied(self, client, auth_headers, other_user_headers):
        create_resp = client.post("/api/v1/planner/home", json={
            "title": "Private Plan",
            "room_type": "living_room",
            "total_budget": 30000.0,
            "currency": "INR"
        }, headers=auth_headers)
        plan_id = create_resp.json()["plan_id"]

        other_resp = client.get(f"/api/v1/plans/{plan_id}", headers=other_user_headers)
        assert other_resp.status_code in (403, 404)

    def test_recommendations_cross_user_access_denied(self, client, auth_headers, other_user_headers):
        create_resp = client.post("/api/v1/planner/home", json={
            "title": "Confidential Recommendations Plan",
            "room_type": "living_room",
            "total_budget": 35000.0,
            "currency": "INR"
        }, headers=auth_headers)
        plan_id = create_resp.json()["plan_id"]

        # Owner gets recommendations
        owner_resp = client.get(f"/api/v1/recommendations/{plan_id}", headers=auth_headers)
        assert owner_resp.status_code == 200

        # Non-owner cannot access recommendations
        other_resp = client.get(f"/api/v1/recommendations/{plan_id}", headers=other_user_headers)
        assert other_resp.status_code in (403, 404)

    def test_plans_pagination(self, client, auth_headers):
        # Create 3 plans
        for i in range(3):
            client.post("/api/v1/planner/home", json={
                "title": f"Pagination Plan {i}",
                "room_type": "bedroom",
                "total_budget": 20000.0 + i * 1000,
                "currency": "INR"
            }, headers=auth_headers)

        resp_limit_1 = client.get("/api/v1/plans?limit=1&offset=0", headers=auth_headers)
        assert resp_limit_1.status_code == 200
        items_1 = resp_limit_1.json()
        assert len(items_1) <= 1

        resp_history = client.get("/api/v1/history?limit=2&offset=0", headers=auth_headers)
        assert resp_history.status_code == 200
        assert len(resp_history.json()) <= 2

    def test_image_upload_invalid_type_rejected(self, client, auth_headers):
        import io
        fake_file = io.BytesIO(b"not an image text file")
        resp = client.post(
            "/api/v1/images/upload",
            files={"file": ("test.txt", fake_file, "text/plain")},
            headers=auth_headers
        )
        assert resp.status_code == 400
