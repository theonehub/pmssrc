import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth.auth_dependencies import get_current_user, CurrentUser
import mongomock
import json

# --- Fixtures ---
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module", autouse=True)
def override_auth():
    app.dependency_overrides[get_current_user] = lambda: CurrentUser({
        "employee_id": "EMP_TEST_ADMIN",
        "username": "testadmin",
        "role": "admin",
        "hostname": "testhost",
        "org_id": "testorg",
        "permissions": ["*"],
        "is_active": True,
        "password_hash": "$2b$12$testhash",
        "name": "Test Admin",
        "email": "testadmin@example.com",
        "personal_details": {
            "gender": "male",
            "date_of_birth": "1990-01-01",
            "date_of_joining": "2020-01-01",
            "mobile": "9999999999"
        }
    })
    yield
    app.dependency_overrides = {}

# --- Test Data ---
def make_org_data(unique_str="001"):
    return {
        "name": f"Test Org {unique_str}",
        "description": "A test organisation.",
        "hostname": f"testhost{unique_str}",
        "organisation_type": "private_limited",
        "bank_name": "Test Bank",
        "account_number": f"123456789{unique_str}",
        "ifsc_code": "TEST0001",
        "account_holder_name": "Test Holder",
        "branch_name": "Test Branch",
        "branch_address": "123 Test St",
        "account_type": "savings",
        "employee_strength": 10,
        "email": f"org{unique_str}@example.com",
        "phone": "1234567890",
        "website": "https://test.org",
        "fax": "123456",
        "street_address": "123 Test St",
        "city": "Testville",
        "state": "Teststate",
        "country": "Testland",
        "pin_code": "123456",
        "pan_number": f"PAN{unique_str}",
        "gst_number": f"GST{unique_str}",
        "tan_number": f"TAN{unique_str}",
        "esi_establishment_id": f"ESI{unique_str}",
        "pf_establishment_id": f"PF{unique_str}"
    }

# --- CRUD Tests ---
def test_create_organisation(client):
    data = make_org_data("create")
    resp = client.post(
        "/v2/organisations/",
        data={"organisation_data": json.dumps(data)},
        files={}
    )
    assert resp.status_code in (200, 201)
    assert resp.json()["name"] == data["name"]
    # Save org_id for later tests if needed


def test_list_organisations(client):
    resp = client.get("/v2/organisations/?skip=0&limit=10")
    assert resp.status_code == 200
    assert "organisations" in resp.json()


def test_get_organisation_by_id(client):
    # Create first
    data = make_org_data("getid")
    create_resp = client.post(
        "/v2/organisations/",
        data={"organisation_data": json.dumps(data)},
        files={}
    )
    org_id = create_resp.json().get("id")
    resp = client.get(f"/v2/organisations/{org_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == org_id


def test_update_organisation(client):
    # Create first
    data = make_org_data("update")
    create_resp = client.post(
        "/v2/organisations/",
        data={"organisation_data": json.dumps(data)},
        files={}
    )
    org_id = create_resp.json().get("id")
    update_data = {"name": "Updated Org Name"}
    resp = client.put(f"/v2/organisations/{org_id}", json=update_data)
    assert resp.status_code in (200, 201)
    assert resp.json()["name"] == "Updated Org Name"


def test_delete_organisation(client):
    # Create first
    data = make_org_data("delete")
    create_resp = client.post(
        "/v2/organisations/",
        data={"organisation_data": json.dumps(data)},
        files={}
    )
    org_id = create_resp.json().get("id")
    resp = client.delete(f"/v2/organisations/{org_id}")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Organisation deleted successfully"

# --- Analytics & Utility Endpoints ---
def test_organisation_statistics(client):
    resp = client.get("/v2/organisations/analytics/statistics")
    assert resp.status_code == 200
    assert "status" in resp.json() or "total_organisations" in resp.json()

def test_organisation_health(client):
    resp = client.get("/v2/organisations/analytics/health")
    assert resp.status_code == 200
    assert "status" in resp.json()

def test_validate_organisation_data(client):
    data = make_org_data("validate")
    resp = client.post("/v2/organisations/validate", json=data)
    assert resp.status_code == 200
    assert "valid" in resp.json()

def test_check_name_availability(client):
    resp = client.get("/v2/organisations/check-availability/name/TestOrgUnique")
    assert resp.status_code == 200
    assert "available" in resp.json()

def test_check_hostname_availability(client):
    resp = client.get("/v2/organisations/check-availability/hostname/testhostunique")
    assert resp.status_code == 200
    assert "available" in resp.json()

def test_check_pan_availability(client):
    resp = client.get("/v2/organisations/check-availability/pan/PANUNIQUE")
    assert resp.status_code == 200
    assert "available" in resp.json()

def test_get_current_organisation(client):
    resp = client.get("/v2/organisations/current/organisation")
    # Accept 200 or 404 (if not found for test user)
    assert resp.status_code in (200, 404)


def test_organisation_health_check(client):
    resp = client.get("/v2/organisations/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

# --- American spelling endpoints (minimal, as they alias British) ---
def test_create_organization_american(client):
    data = make_org_data("us")
    resp = client.post(
        "/v2/organizations/",
        data={"organisation_data": json.dumps(data)},
        files={}
    )
    assert resp.status_code in (200, 201)
    assert resp.json()["name"] == data["name"]


def test_organization_health_check(client):
    resp = client.get("/v2/organizations/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

# Add more tests for edge/failure cases, validation errors, and business rules as needed. 