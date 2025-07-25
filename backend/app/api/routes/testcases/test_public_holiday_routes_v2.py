import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from app.main import app
from datetime import date, datetime, timedelta
from app.application.dto.public_holiday_dto import CreatePublicHolidayRequestDTO
from app.auth.auth_dependencies import get_current_user, CurrentUser
from pymongo import MongoClient
import random

# Use a test database (set env var or patch config if needed)
# Example: os.environ['MONGODB_DB_NAME'] = 'test_db'

FUTURE_DATE = (datetime.now() + timedelta(days=30 + random.randint(1, 10000))).strftime("%Y-%m-%d")

# Clean up any existing test data before running tests
def pytest_configure(config):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["pms_testorg"]
    import datetime as dt
    date_obj = dt.datetime.strptime(FUTURE_DATE, "%Y-%m-%d").date()
    db["public_holidays"].delete_many({
        "$or": [
            {"holiday_date": FUTURE_DATE},
            {"holiday_date": date_obj},
            {"name": "Test Holiday"},
            {"name": "ImportTest"}
        ],
        "is_active": {"$in": [True, False]}
    })

class DummyUser(CurrentUser):
    def __init__(self):
        super().__init__(
            employee_id="testuser",
            hostname="testorg",
            username="testuser",
            permissions={},
            role="admin"
        )

def override_get_current_user():
    token_payload = {
        "employee_id": "testuser",
        "hostname": "testorg",
        "username": "testuser",
        "permissions": [],
        "role": "admin"
    }
    return CurrentUser(token_payload)

app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

# Helper: create a holiday
TEST_HOLIDAY = {
    "name": "Test Holiday",
    "holiday_date": FUTURE_DATE,
    "description": "A test holiday",
    "category": "national",
    "observance": "mandatory",
    "recurrence": "annual",
    "is_active": True,
    "location_specific": None
}

@pytest.fixture(scope="module")
def created_holiday_id(client):
    # Create a holiday and return its ID
    resp = client.post("/v2/public-holidays/", json=TEST_HOLIDAY)
    assert resp.status_code == 200
    return resp.json()["id"]

def test_health_check(client):
    resp = client.get("/v2/public-holidays/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

def test_create_public_holiday(client):
    import random
    from datetime import datetime, timedelta
    alt_date = (datetime.now() + timedelta(days=60 + random.randint(1, 10000))).strftime("%Y-%m-%d")
    alt_holiday = TEST_HOLIDAY.copy()
    alt_holiday["name"] = "Test Holiday 2"
    alt_holiday["holiday_date"] = alt_date
    resp = client.post("/v2/public-holidays/", json=alt_holiday)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == alt_holiday["name"]
    assert data["is_active"] is True

def test_list_public_holidays(client):
    resp = client.get("/v2/public-holidays/?limit=10")
    assert resp.status_code == 200
    data = resp.json()
    assert "holidays" in data
    assert isinstance(data["holidays"], list)

def test_get_public_holiday_by_id(client, created_holiday_id):
    resp = client.get(f"/v2/public-holidays/{created_holiday_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == created_holiday_id

def test_update_public_holiday(client, created_holiday_id):
    update = {"name": "Updated Holiday", "is_active": False}
    resp = client.put(f"/v2/public-holidays/{created_holiday_id}", json=update)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Updated Holiday"
    assert data["is_active"] is False

def test_delete_public_holiday(client, created_holiday_id):
    resp = client.delete(f"/v2/public-holidays/{created_holiday_id}")
    assert resp.status_code == 200
    assert "deleted" in resp.json()["message"].lower()

def test_import_public_holidays(client):
    # Create a temp CSV file
    content = f"name,date,category,observance,recurrence,is_active\nImportTest,{FUTURE_DATE},national,mandatory,annual,True\n"
    with tempfile.NamedTemporaryFile("w+b", suffix=".csv") as f:
        f.write(content.encode())
        f.seek(0)
        files = {"file": (os.path.basename(f.name), f, "text/csv")}
        resp = client.post("/v2/public-holidays/import", files=files)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert any(h["name"] == "ImportTest" for h in data)

def test_check_public_holiday(client):
    resp = client.get(f"/v2/public-holidays/check/{FUTURE_DATE}")
    assert resp.status_code == 200
    data = resp.json()
    assert "is_holiday" in data

def test_get_public_holidays_by_date_range(client):
    resp = client.get(f"/v2/public-holidays/range/{FUTURE_DATE}/{FUTURE_DATE}")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)

def test_get_public_holidays_by_month(client):
    resp = client.get(f"/v2/public-holidays/month/12/{FUTURE_DATE.split('-')[0]}")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list) 