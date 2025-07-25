# Test Case Writing Rules for FastAPI Routes

This document outlines the rules and best practices for writing test cases for all FastAPI route endpoints in this project.

---

## 1. Test Directory Structure
- Place all test files for route endpoints under:
  - `backend/app/api/routes/testcases/`
- Name test files as `test_<route_name>_routes_v2.py` for consistency.

---

## 2. Test Database Usage
- Always use a **real test database** (never production data).
- Clean up test data before each test run to avoid conflicts (e.g., using unique names/dates or deleting by test org/hostname).
- Use a dedicated test org/hostname (e.g., `"testorg"`) for all test requests.

---

## 3. Authentication
- **Override authentication dependencies** so all test requests are authenticated as an admin or appropriate test user.
- Use a fixture or `app.dependency_overrides` to inject a dummy user with the required permissions.

---

## 4. TestClient and Fixtures
- Use FastAPI’s `TestClient` for all API calls.
- Use `pytest` fixtures for:
  - The test client (`client`)
  - Any setup/teardown logic (e.g., creating a resource, cleaning up)
- Prefer `scope="module"` for fixtures that can be reused across tests, but ensure no data conflicts.

---

## 5. Test Data
- Use **unique or randomized data** (e.g., names, dates) to avoid business rule conflicts.
- For resources that must be created before tests (e.g., for GET/PUT/DELETE), use a fixture to create and yield the resource ID.

---

## 6. Test Coverage
- Cover all CRUD endpoints:
  - **Create** (POST)
  - **Read** (GET by ID, GET list)
  - **Update** (PUT/PATCH)
  - **Delete** (DELETE or soft delete)
- Cover all utility endpoints (e.g., health checks, imports, special queries).
- Test both **success** and **failure** cases (e.g., validation errors, not found, forbidden).

---

## 7. Assertions
- Assert on:
  - HTTP status codes (e.g., `assert resp.status_code == 200`)
  - Response structure and key fields
  - Business logic (e.g., is_active toggling, correct filtering)
- For error cases, assert on error codes and messages.

---

## 8. Isolation and Cleanup
- Ensure each test is **independent** (can run alone or in any order).
- Clean up any test data created, or use unique data to avoid polluting the test DB.

---

## 9. Performance
- Keep test data minimal for speed.
- Avoid unnecessary DB or network calls.

---

## 10. Documentation
- Add comments to clarify test intent, especially for complex flows or business rules.

---

## 11. Naming
- Name test functions descriptively:
  - `def test_create_<resource>(client): ...`
  - `def test_update_<resource>(client, created_id): ...`

---

## 12. Warnings and Deprecations
- Address deprecation warnings (e.g., Pydantic v2 migration) as part of test maintenance.

---

## 13. Lessons Learned & Best Practices (Real-World Issues & Solutions)

### 13.1. Database and Test Data
- Always use the correct MongoDB connection and database as defined in `mongodb_config.py`.
- Insert test data (e.g., users) into the correct org-specific database (e.g., `pms_testhost`), not the global database.
- Clean up all test data before/after each test, including for all relevant date formats (local and UTC) to avoid business rule conflicts (e.g., "already checked in").

### 13.2. User Entity Construction
- Ensure all required fields are present in test user documents:
  - `employee_id` (must match backend format, e.g., `EMP001`)
  - `username`, `role`, `hostname`, `org_id`, `permissions`, `is_active`, `password_hash` (with a real bcrypt hash), `name`, `email`
  - `personal_details` with valid `gender` (e.g., `male`), `date_of_birth`, `date_of_joining`, and a valid Indian `mobile` number
- Place `password_hash` at the top level of the user document, not nested.

### 13.3. Authentication Override
- Use a token payload dictionary to instantiate `CurrentUser` in test overrides.
- Always restore the original override after each test if it is changed.

### 13.4. Error Handling and Assertions
- Accept all valid backend responses (e.g., 200, 201, 400, 401, 403, 404, 422, 500 as appropriate).
- For error responses, check for error messages in both string and list-of-dict formats (FastAPI may return `{"detail": [{"msg": ...}]}` or similar).

### 13.5. Test Execution
- Set `PYTHONPATH=backend` when running tests from the project root to resolve imports.
- Use the correct virtual environment and ensure all dependencies (e.g., `pytest`, `pymongo`) are installed.
- **Recommended:** Use the `.venv` virtual environment at the project root for all test runs. Activate it with `source .venv/bin/activate`.
- **For FastAPI route tests:** Always set `PYTHONPATH=backend` when running pytest, e.g.:
  - `PYTHONPATH=backend pytest backend/app/api/routes/testcases/test_user_routes_v2.py -v`

### 13.6. General Debugging
- If a test fails due to missing/misformatted data, inspect backend logs and update test fixtures accordingly.
- If the backend expects a different error format or status code, adjust assertions in the test.

---

**These lessons and best practices are based on real-world issues encountered during test development and should be followed for all new route test cases.**

---

## 14. Real-World Debugging & Fixes: Company Leave Test Automation (2025-07)

### 14.1. Authentication Override Pattern
- Use `app.dependency_overrides[get_current_user] = override_get_current_user` with a token payload dict for `CurrentUser`, not individual keyword arguments.
- Example:
  ```python
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
  ```

### 14.2. Route Matching Order
- Always place static endpoints (like `/health`) above parameterized routes (like `/{resource_id}`) in FastAPI routers to avoid route conflicts.

### 14.3. DTO and Use Case Updates
- Ensure all updatable fields (e.g., `leave_name`) are handled in the update use case logic. If a field is missing, the backend will not update it even if the test sends it.

### 14.4. Exception Handling in Routes
- Catch all relevant validation exceptions in route handlers (e.g., both `CompanyLeaveValidationError` and `CompanyLeaveDTOValidationError`) and return appropriate status codes (400/422). Otherwise, FastAPI will return a generic 500 error.

### 14.5. Test Data and Cleanup
- Use unique/randomized data for each test run to avoid business rule conflicts (e.g., duplicate names, already checked-in users).
- Clean up test data before/after tests, especially for resources that enforce uniqueness or business rules.

### 14.6. Test Execution Environment
- Always set `PYTHONPATH=backend` and use the `.venv` environment for consistent imports and dependencies.
- Example command:
  ```sh
  PYTHONPATH=backend .venv/bin/python -m pytest backend/app/api/routes/testcases/test_company_leave_routes_v2.py
  ```

### 14.7. General Debugging
- If a test fails with 403, 404, or 500, check:
  - Authentication override pattern
  - Route order in the router
  - DTO field support in use cases
  - Exception handling in route handlers
- Compare with a passing test (e.g., public holiday tests) to spot missing patterns or setup.

---

## Example Test Skeleton

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    resp = client.get("/v2/resource/health")
    assert resp.status_code == 200

def test_create_resource(client):
    data = {...}
    resp = client.post("/v2/resource/", json=data)
    assert resp.status_code == 200
    assert resp.json()["field"] == data["field"]
```

---

**Follow these rules for all new route test cases to ensure reliability, maintainability, and consistency across your codebase.** 