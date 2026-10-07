import requests
import json
import uuid
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_full():
    # 1. Health check
    print("--- 1. Testing Health ---")
    r = requests.get(f"{BASE_URL}/health")
    print("Health Status:", r.status_code, r.json())
    assert r.status_code == 200
    health = r.json()
    assert health.get("supabase_connected") is True
    assert health.get("gemini_connected") is True

    # 2. Register new user
    email = f"audit_user_{int(time.time())}@pocketsmart.test"
    password = "AuditPassword123!"
    full_name = "Audit Test User"
    print(f"\n--- 2. Registering User: {email} ---")
    r = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "full_name": full_name
    })
    print("Register Status:", r.status_code, r.json())
    assert r.status_code in (200, 201)
    reg_data = r.json()
    access_token = reg_data["access_token"]
    user_id = reg_data["user"]["id"]
    print("Registered User ID:", user_id)

    # 3. Login with that user
    print("\n--- 3. Testing Login ---")
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    print("Login Status:", r.status_code, r.json())
    assert r.status_code == 200
    login_data = r.json()
    assert login_data["user"]["id"] == user_id
    token = login_data["access_token"]

    # 4. Auth me
    print("\n--- 4. Testing /auth/me ---")
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print("Me Status:", r.status_code, r.json())
    assert r.status_code == 200
    assert r.json()["id"] == user_id

    # 5. Home Planner
    print("\n--- 5. Testing Home Planner ---")
    home_payload = {
        "room_type": "living_room",
        "aesthetic_style": "minimalist",
        "budget": 50000.0,
        "currency": "INR",
        "special_requirements": "need compact sofa and wooden coffee table"
    }
    r = requests.post(f"{BASE_URL}/planner/home", json=home_payload, headers=headers)
    print("Home Planner Status:", r.status_code)
    assert r.status_code in (200, 201)
    home_plan = r.json()
    print("Plan ID:", home_plan.get("id"))
    print("Title:", home_plan.get("title"))
    print("Estimated Cost:", home_plan.get("estimated_cost"))
    print("Allocations:", len(home_plan.get("allocations", [])))
    print("Recommendations:", len(home_plan.get("recommendations", [])))
    assert home_plan.get("id") is not None

    # 6. Party Planner
    print("\n--- 6. Testing Party Planner ---")
    party_payload = {
        "event_type": "birthday",
        "guest_count": 20,
        "theme": "retro",
        "budget": 25000.0,
        "currency": "INR",
        "special_requests": "vegan options and retro lighting"
    }
    r = requests.post(f"{BASE_URL}/planner/party", json=party_payload, headers=headers)
    print("Party Planner Status:", r.status_code)
    assert r.status_code in (200, 201)
    party_plan = r.json()
    print("Party Plan ID:", party_plan.get("id"))
    print("Party Title:", party_plan.get("title"))

    # 7. Jewelry Planner
    print("\n--- 7. Testing Jewelry Planner ---")
    jewelry_payload = {
        "occasion": "wedding",
        "metal_preference": "gold",
        "budget": 80000.0,
        "currency": "INR",
        "style_notes": "traditional gold necklace set"
    }
    r = requests.post(f"{BASE_URL}/planner/jewelry", json=jewelry_payload, headers=headers)
    print("Jewelry Planner Status:", r.status_code)
    assert r.status_code in (200, 201)
    jewelry_plan = r.json()
    print("Jewelry Plan ID:", jewelry_plan.get("id"))
    print("Jewelry Title:", jewelry_plan.get("title"))

    # 8. List Plans
    print("\n--- 8. Testing List Plans ---")
    r = requests.get(f"{BASE_URL}/plans", headers=headers)
    print("List Plans Status:", r.status_code)
    assert r.status_code == 200
    plans_list = r.json()
    print("Total Plans for User:", len(plans_list))

    print("\n✅ ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_full()
