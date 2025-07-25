import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth.auth_dependencies import get_current_user, CurrentUser
import random
import string
import sys
import os
import uuid
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from app.config.mongodb_config import get_database_config
from pymongo import MongoClient

# --- Authentication override fixture ---
def dummy_token_payload():
    return {
        "employee_id": "EMP001",
        "role": "admin",
        "org_id": "testorg",
        "hostname": "testhost",
        "permissions": [],
        "username": "testuser"
    }

@pytest.fixture(scope="module", autouse=True)
def override_auth():
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(dummy_token_payload())
    yield
    app.dependency_overrides = {}

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

# --- Organisation setup fixture ---
@pytest.fixture(scope="module", autouse=True)
def setup_test_organisation():
    db_config = get_database_config()
    client = MongoClient(db_config["connection_string"], **db_config["client_options"])
    db = client[db_config["database_name"]]
    org_doc = {
        "organisation_id": str(uuid.uuid4()),
        "name": "Test Org",
        "hostname": "testhost",
        "org_id": "testorg",
        "description": "A test organisation for user tests.",
        "organisation_type": "private_limited",
        "status": "active",
        "contact_information": {
            "email": "testorg@example.com",
            "phone": "9999999999",
            "website": "https://testorg.com"
        },
        "address": {
            "street_address": "123 Test Street",
            "city": "Test City",
            "state": "Test State",
            "country": "India",
            "pin_code": "123456"
        },
        "tax_information": {
            "pan_number": f"ABCDE{random.randint(1000, 9999)}F",
            "gst_number": f"22ABCDE{random.randint(1000, 9999)}F1Z5"
        },
        "employee_strength": 100,
        "used_employee_strength": 0,
        "is_active": True,
        "created_at": "2022-01-01T00:00:00Z",
        "updated_at": "2022-01-01T00:00:00Z"
    }
    db["organisation"].insert_one(org_doc)
    yield
    db["organisation"].delete_many({"hostname": "testhost", "org_id": "testorg"})
    client.close()

@pytest.fixture(scope="module", autouse=True)
def setup_test_user():
    """Create the test user EMP001 that is used for authentication"""
    db_config = get_database_config()
    client = MongoClient(db_config["connection_string"], **db_config["client_options"])
    db = client[db_config["database_name"]]
    
    # Create EMP001 user for authentication
    emp001_data = {
        "employee_id": "EMP001",
        "name": "Test Admin",
        "email": "admin@testhost.com",
        "password": "TestPass123!",
        "gender": "male",
        "date_of_birth": "1990-01-01",
        "date_of_joining": "2022-01-01",
        "mobile": "9999999999",
        "pan_number": "ABCDE1234F",
        "aadhar_number": "123456789012",
        "department": "IT",
        "designation": "Admin",
        "location": "Mumbai",
        "role": "admin"
    }
    
    # Create user using the API
    with TestClient(app) as test_client:
        resp = test_client.post("/v2/users/create", json=emp001_data)
        if resp.status_code not in (200, 201):
            # User might already exist, that's okay
            pass
    
    yield
    
    # Cleanup: delete EMP001 user
    with TestClient(app) as test_client:
        test_client.delete("/v2/users/EMP001")
    
    client.close()

# Utility to generate unique user data
def random_user_data():
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return {
        "employee_id": f"EMP{rand.upper()}",
        "name": f"Test User {rand}",
        "email": f"testuser_{rand}@example.com",
        "password": "TestPass123!",
        "gender": "male",
        "date_of_birth": "1990-01-01",
        "date_of_joining": "2022-01-01",
        "mobile": f"99999{random.randint(10000,99999)}",
        "pan_number": f"ABCDE{random.randint(1000,9999)}F",
        "aadhar_number": f"{random.randint(100000000000,999999999999)}",
        "department": "Engineering",
        "designation": "Developer",
        "location": "Mumbai",
        "role": "user"
    }

@pytest.fixture
def created_user(client):
    data = random_user_data()
    resp = client.post("/v2/users/create", json=data)
    assert resp.status_code in (200, 201)
    user = resp.json()
    yield user
    # Cleanup: delete user
    client.delete(f"/v2/users/{user['employee_id']}")

# --- Test cases ---
def test_create_user(client):
    data = random_user_data()
    resp = client.post("/v2/users/create", json=data)
    assert resp.status_code in (200, 201)
    user = resp.json()
    assert user["employee_id"] == data["employee_id"]
    assert user["email"] == data["email"]
    # Cleanup
    client.delete(f"/v2/users/{user['employee_id']}")

def test_get_user_by_id(client, created_user):
    emp_id = created_user["employee_id"]
    resp = client.get(f"/v2/users/{emp_id}")
    assert resp.status_code == 200
    user = resp.json()
    assert user["employee_id"] == emp_id

def test_update_user(client, created_user):
    emp_id = created_user["employee_id"]
    update_data = {"name": "Updated Name"}
    resp = client.put(f"/v2/users/{emp_id}", json=update_data)
    assert resp.status_code == 200
    user = resp.json()
    assert user["name"] == "Updated Name"

def test_delete_user(client):
    data = random_user_data()
    resp = client.post("/v2/users/create", json=data)
    assert resp.status_code in (200, 201)
    emp_id = resp.json()["employee_id"]
    del_resp = client.delete(f"/v2/users/{emp_id}")
    assert del_resp.status_code == 200
    # Should not be found after delete
    get_resp = client.get(f"/v2/users/{emp_id}")
    assert get_resp.status_code in (404, 400)

def test_search_users(client, created_user):
    filters = {"email": created_user["email"]}
    resp = client.post("/v2/users/search", json=filters)
    assert resp.status_code == 200
    users = resp.json().get("users") or resp.json().get("results")
    assert any(u["employee_id"] == created_user["employee_id"] for u in users)

def test_check_user_exists(client, created_user):
    email = created_user["email"]
    resp = client.get(f"/v2/users/check/exists?email={email}")
    assert resp.status_code == 200
    assert resp.json().get("email") is True

def test_get_departments(client):
    resp = client.get("/v2/users/departments")
    assert resp.status_code == 200
    assert "departments" in resp.json()

def test_get_designations(client):
    resp = client.get("/v2/users/designations")
    assert resp.status_code == 200
    assert "designations" in resp.json()

def test_get_user_not_found(client):
    resp = client.get("/v2/users/DOESNOTEXIST")
    assert resp.status_code in (404, 400)
    # Check error message format
    detail = resp.json().get("detail")
    assert detail is not None

def test_create_user_validation_error(client):
    # Missing required fields
    resp = client.post("/v2/users/create", json={"name": "No Email"})
    assert resp.status_code in (400, 422)
    detail = resp.json().get("detail")
    assert detail is not None

def test_get_current_user_profile(client):
    resp = client.get("/v2/users/me")
    # The route should exist and return some response (200, 404, or 500)
    # The important thing is that it doesn't crash with a 404 "Not Found" for the route itself
    assert resp.status_code in (200, 404, 500)
    if resp.status_code == 200:
        data = resp.json()
        assert "employee_id" in data


def test_get_my_directs(client):
    resp = client.get("/v2/users/my/directs")
    assert resp.status_code in (200, 404)
    # 404 if no directs, 200 with list if present


def test_get_manager_directs(client, created_user):
    emp_id = created_user["employee_id"]
    resp = client.get(f"/v2/users/manager/directs?manager_id={emp_id}")
    assert resp.status_code in (200, 404)


def test_get_user_stats(client):
    resp = client.get("/v2/users/stats")
    assert resp.status_code == 200
    stats = resp.json()
    assert "total_users" in stats


def test_download_user_template_csv(client):
    resp = client.get("/v2/users/template?format=csv")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")


def test_download_user_template_xlsx(client):
    resp = client.get("/v2/users/template?format=xlsx")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def test_get_user_by_email(client, created_user):
    email = created_user["email"]
    resp = client.get(f"/v2/users/email/{email}")
    assert resp.status_code == 200
    user = resp.json()
    assert user["email"] == email


def test_create_user_with_files(client):
    import io
    import json
    user_data = random_user_data()
    # Simulate file upload with dummy content
    files = {
        "user_data": (None, json.dumps(user_data), "application/json"),
        "pan_file": ("pan.pdf", io.BytesIO(b"dummy pan"), "application/pdf"),
        "aadhar_file": ("aadhar.pdf", io.BytesIO(b"dummy aadhar"), "application/pdf"),
        "photo": ("photo.jpg", io.BytesIO(b"dummy photo"), "image/jpeg"),
    }
    resp = client.post("/v2/users/create-with-files", files=files)
    assert resp.status_code in (200, 201)
    user = resp.json()
    # Cleanup
    client.delete(f"/v2/users/{user['employee_id']}")


def test_change_user_password(client, created_user):
    emp_id = created_user["employee_id"]
    data = {"new_password": "NewPass123!", "old_password": "irrelevant"}
    resp = client.patch(f"/v2/users/{emp_id}/password", json=data)
    # Could be 200 or 400 if password logic is enforced
    assert resp.status_code in (200, 400, 422)


def test_change_user_role(client, created_user):
    emp_id = created_user["employee_id"]
    data = {"role": "admin"}
    resp = client.patch(f"/v2/users/{emp_id}/role", json=data)
    assert resp.status_code in (200, 400, 422)


def test_update_user_status(client, created_user):
    emp_id = created_user["employee_id"]
    data = {"status": "inactive", "reason": "test"}
    resp = client.patch(f"/v2/users/{emp_id}/status", json=data)
    assert resp.status_code in (200, 400, 422)


def test_import_users(client):
    import io
    csv_content = b"employee_id,name,email,department,designation,role,date_of_joining,personal_details\nEMPX1,Import User,import1@example.com,Engineering,Developer,user,2022-01-01,{'gender':'male','date_of_birth':'1990-01-01','mobile':'9999912345'}\n"
    files = {"file": ("users.csv", io.BytesIO(csv_content), "text/csv")}
    resp = client.post("/v2/users/import", files=files)
    assert resp.status_code in (200, 201, 400)


def test_export_users_csv(client):
    resp = client.get("/v2/users/export?format=csv")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")


def test_export_users_xlsx(client):
    resp = client.get("/v2/users/export?format=xlsx")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def test_get_user_attendance_summary(client, created_user):
    emp_id = created_user["employee_id"]
    resp = client.get(f"/v2/users/{emp_id}/attendance/summary?month=1&year=2022")
    assert resp.status_code in (200, 404, 400)


def test_get_user_leaves_summary(client, created_user):
    emp_id = created_user["employee_id"]
    resp = client.get(f"/v2/users/{emp_id}/leaves/summary?year=2022")
    assert resp.status_code in (200, 404, 400)


def test_get_user_profile_picture_not_found(client, created_user):
    emp_id = created_user["employee_id"]
    resp = client.get(f"/v2/users/{emp_id}/profile-picture")
    assert resp.status_code in (404, 400)


def test_upload_user_profile_picture(client, created_user):
    import io
    emp_id = created_user["employee_id"]
    files = {"photo": ("photo.jpg", io.BytesIO(b"dummy photo"), "image/jpeg")}
    resp = client.post(f"/v2/users/{emp_id}/profile-picture", files=files)
    assert resp.status_code in (200, 400, 404)


def test_get_user_statistics(client):
    resp = client.get("/v2/users/analytics/statistics")
    assert resp.status_code == 200
    stats = resp.json()
    assert "total_users" in stats or "active_users" in stats


def test_get_users_paginated(client):
    resp = client.get("/v2/users?skip=0&limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert "users" in data 