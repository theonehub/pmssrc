import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth.auth_dependencies import get_current_user, CurrentUser
import uuid

# --- Fixtures ---

# Override authentication globally for all tests (like public holiday tests)
def override_get_current_user():
    token_payload = {
        "employee_id": "TESTADMIN001",
        "username": "testadmin",
        "role": "admin",
        "hostname": "testorg",
        "org_id": "testorgid",
        "permissions": ["admin"],
        "is_active": True,
        "name": "Test Admin",
        "email": "testadmin@test.com"
    }
    return CurrentUser(token_payload)

app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

# --- Helper for unique data ---
def unique_leave_name():
    return f"TestLeave_{uuid.uuid4().hex[:8]}"

# --- Tests ---

def test_health_check(client):
    resp = client.get("/v2/company-leaves/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

def test_create_company_leave(client):
    data = {
        "leave_name": unique_leave_name(),
        "accrual_type": "annually",
        "annual_allocation": 10,
        "description": "Test leave policy",
        "encashable": True
    }
    resp = client.post("/v2/company-leaves/", json=data)
    assert resp.status_code == 200
    result = resp.json()
    assert result["leave_name"] == data["leave_name"]
    assert result["annual_allocation"] == data["annual_allocation"]
    # Save for later tests
    client._last_created_id = result["company_leave_id"]

def test_get_company_leave_by_id(client):
    leave_id = getattr(client, "_last_created_id", None)
    assert leave_id, "No leave_id from previous test"
    resp = client.get(f"/v2/company-leaves/{leave_id}")
    assert resp.status_code == 200
    result = resp.json()
    assert result["company_leave_id"] == leave_id

def test_update_company_leave(client):
    leave_id = getattr(client, "_last_created_id", None)
    assert leave_id, "No leave_id from previous test"
    update_data = {
        "leave_name": unique_leave_name(),
        "accrual_type": "monthly",
        "annual_allocation": 12,
        "description": "Updated description",
        "encashable": False,
        "is_active": True,
        "updated_by": "TESTADMIN001"
    }
    resp = client.put(f"/v2/company-leaves/{leave_id}", json=update_data)
    assert resp.status_code == 200
    result = resp.json()
    assert result["leave_name"] == update_data["leave_name"]
    assert result["annual_allocation"] == update_data["annual_allocation"]

def test_list_company_leaves(client):
    resp = client.get("/v2/company-leaves/")
    assert resp.status_code == 200
    result = resp.json()
    assert "items" in result

def test_delete_company_leave(client):
    leave_id = getattr(client, "_last_created_id", None)
    assert leave_id, "No leave_id from previous test"
    resp = client.delete(f"/v2/company-leaves/{leave_id}")
    assert resp.status_code == 200
    assert "deleted" in resp.text or "success" in resp.text.lower()

def test_get_company_leave_not_found(client):
    resp = client.get("/v2/company-leaves/nonexistentid")
    assert resp.status_code == 404

def test_update_company_leave_validation_error(client):
    # Try to update with invalid data (e.g., negative allocation)
    data = {
        "leave_name": unique_leave_name(),
        "accrual_type": "annually",
        "annual_allocation": 10,
        "description": "Test leave policy",
        "encashable": True
    }
    resp = client.post("/v2/company-leaves/", json=data)
    leave_id = resp.json()["company_leave_id"]
    update_data = {
        "annual_allocation": -5,
        "updated_by": "TESTADMIN001"
    }
    resp = client.put(f"/v2/company-leaves/{leave_id}", json=update_data)
    assert resp.status_code in (400, 422)
    # Cleanup
    client.delete(f"/v2/company-leaves/{leave_id}") 