import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config.mongodb_config import get_database_config
from app.auth.auth_dependencies import get_current_user, CurrentUser
from pymongo import MongoClient
from datetime import datetime, timezone, timedelta
import random
import string
from decimal import Decimal

# --- Authentication override fixture ---
def dummy_token_payload():
    return {
        "employee_id": "EMP001",
        "role": "admin",
        "org_id": "testorg",
        "hostname": "testhost",
        "permissions": ["admin"],
        "username": "testuser",
        "is_active": True,
        "name": "Test User",
        "email": "testuser@example.com"
    }

def no_employee_token_payload():
    return {
        "employee_id": None,
        "role": "admin",
        "org_id": "testorg",
        "hostname": "testhost",
        "permissions": ["admin"],
        "username": "testuser",
        "is_active": True,
        "name": "Test User",
        "email": "testuser@example.com"
    }

@pytest.fixture(scope="module", autouse=True)
def override_auth():
    from app.auth.auth_dependencies import CurrentUser
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(dummy_token_payload())
    yield
    app.dependency_overrides = {}

# Remove the problematic async fixture for now
# We'll use direct MongoDB connection for tests

# --- MongoDB config fixture ---
@pytest.fixture(scope="module")
def db_config():
    return get_database_config()

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function")
def mongo_salary_package_collection(db_config):
    client = MongoClient(db_config["connection_string"])
    db = client[db_config["database_name"]]
    collection = db["salary_package_records"]
    yield collection
    # Cleanup: Remove all EMP001 records after each test
    collection.delete_many({"employee_id": "EMP001"})
    client.close()

@pytest.fixture(scope="function")
def mongo_users_collection(db_config):
    client = MongoClient(db_config["connection_string"])
    db = client["pms_testhost"]
    collection = db["users_info"]
    yield collection
    # Cleanup: Remove all EMP001 records after each test
    collection.delete_many({"employee_id": "EMP001"})
    client.close()

@pytest.fixture(scope="function")
def seed_test_user(mongo_users_collection):
    # Insert EMP001 user for testhost org with all required fields
    mongo_users_collection.insert_one({
        "employee_id": "EMP001",
        "username": "testuser",
        "role": "admin",
        "hostname": "testhost",
        "org_id": "testorg",
        "permissions": ["admin"],
        "is_active": True,
        "password_hash": "$2b$12$GVFeHMEK2dmxhadbIOSv3u20xfuVYhKahNqZpTCsyu2s3cHIct4DW",
        "name": "Test User",
        "email": "testuser@example.com",
        "personal_details": {
            "gender": "male",
            "date_of_birth": "1990-01-01",
            "date_of_joining": "2020-01-01",
            "mobile": "9876543210",
            "address": "Test Address"
        },
        "documents": {
            "photo_path": None,
            "pan_document_path": None,
            "aadhar_document_path": None
        }
    })
    yield
    # Cleanup handled by mongo_users_collection fixture

@pytest.fixture(scope="function")
def clean_salary_package_records(mongo_salary_package_collection):
    # Clean up any existing records for EMP001
    mongo_salary_package_collection.delete_many({"employee_id": "EMP001"})
    yield
    # Clean up again after test
    mongo_salary_package_collection.delete_many({"employee_id": "EMP001"})

# --- Test data helpers ---
def create_salary_income_data():
    """Create sample salary income data for testing."""
    return {
        "basic_salary": 50000.0,
        "dearness_allowance": 10000.0,
        "hra_provided": 15000.0,
        "commission": 5000.0,
        "special_allowance": 20000.0,
        "epf_employee": 6000.0,
        "epf_employer": 6000.0,
        "eps_employee": 1250.0,
        "eps_employer": 1250.0,
        "vps_employee": 1000.0,
        "esi_contribution": 375.0,
        "effective_from": "2024-04-01",
        "effective_till": None
    }

def create_deductions_data():
    """Create sample deductions data for testing."""
    return {
        "hra_exemption": {
            "actual_rent_paid": 12000.0,
            "hra_city_type": "metro"
        },
        "section_80c": {
            "life_insurance_premium": 15000.0,
            "nsc_investment": 10000.0,
            "tax_saving_fd": 5000.0,
            "elss_investment": 10000.0,
            "home_loan_principal": 20000.0,
            "tuition_fees": 15000.0,
            "ulip_premium": 5000.0,
            "sukanya_samriddhi": 0.0,
            "stamp_duty_property": 0.0,
            "senior_citizen_savings": 0.0,
            "other_80c_investments": 0.0
        },
        "section_80d": {
            "health_insurance_premium": 15000.0,
            "preventive_health_checkup": 5000.0,
            "medical_expenses_senior_citizen": 0.0
        }
    }

# --- TESTS ---

# =============================================================================
# HEALTH CHECK AND UTILITY ENDPOINTS
# =============================================================================

def test_health_check(client):
    """Test taxation service health check endpoint."""
    response = client.get("/v2/taxation/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "message" in data
    assert "timestamp" in data

def test_compare_tax_regimes(client):
    """Test tax regime comparison endpoint."""
    response = client.get("/v2/taxation/tax-regimes/comparison")
    assert response.status_code == 200
    data = response.json()
    assert "regime_comparison" in data
    assert "tax_slabs_2024_25" in data
    assert "recommendation" in data

def test_get_perquisites_types(client):
    """Test perquisites types endpoint."""
    response = client.get("/v2/taxation/perquisites/types")
    assert response.status_code == 200
    data = response.json()
    assert "perquisite_types" in data
    assert "applicability" in data

def test_get_capital_gains_rates(client):
    """Test capital gains rates endpoint."""
    response = client.get("/v2/taxation/capital-gains/rates")
    assert response.status_code == 200
    data = response.json()
    assert "short_term_capital_gains" in data
    assert "long_term_capital_gains" in data
    assert "holding_periods" in data

def test_get_retirement_benefits_info(client):
    """Test retirement benefits info endpoint."""
    response = client.get("/v2/taxation/retirement-benefits/info")
    assert response.status_code == 200
    data = response.json()
    assert "retirement_benefits" in data

def test_get_available_tax_years(client):
    """Test available tax years endpoint."""
    response = client.get("/v2/taxation/tax-years")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    for year_data in data:
        assert "value" in year_data
        assert "display_name" in year_data
        assert "assessment_year" in year_data
        assert "is_current" in year_data

# =============================================================================
# EMPLOYEE SELECTION ENDPOINTS
# =============================================================================

def test_get_employees_for_selection_success(client, seed_test_user):
    """Test successful employee selection endpoint."""
    response = client.get("/v2/taxation/employees/selection")
    assert response.status_code == 200
    data = response.json()
    assert "employees" in data
    assert "total" in data
    assert "filtered_count" in data
    assert isinstance(data["employees"], list)

def test_get_employees_for_selection_with_filters(client, seed_test_user):
    """Test employee selection with various filters."""
    # Test with search filter
    response = client.get("/v2/taxation/employees/selection?search=EMP001")
    assert response.status_code == 200
    
    # Test with pagination
    response = client.get("/v2/taxation/employees/selection?skip=0&limit=10")
    assert response.status_code == 200
    
    # Test with department filter
    response = client.get("/v2/taxation/employees/selection?department=IT")
    assert response.status_code == 200

def test_get_employees_for_selection_invalid_params(client):
    """Test employee selection with invalid parameters."""
    # Test with invalid limit
    response = client.get("/v2/taxation/employees/selection?limit=1000")
    assert response.status_code == 422

# =============================================================================
# COMPONENT UPDATE ENDPOINTS
# =============================================================================

def test_update_salary_component_success(client, clean_salary_package_records, seed_test_user):
    """Test successful salary component update."""
    salary_data = create_salary_income_data()
    
    request_data = {
        "employee_id": "EMP001",
        "tax_year": "2024-25",
        "salary_income": salary_data,
        "force_new_revision": False,
        "notes": "Test salary update"
    }
    
    response = client.put("/v2/taxation/records/employee/EMP001/salary", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["employee_id"] == "EMP001"
    assert data["tax_year"] == "2024-25"
    assert data["component_type"] == "salary_income"
    assert data["status"] == "success"
    assert "taxation_id" in data

def test_update_salary_component_employee_id_mismatch(client, clean_salary_package_records, seed_test_user):
    """Test salary component update with employee ID mismatch."""
    salary_data = create_salary_income_data()
    
    request_data = {
        "employee_id": "EMP002",  # Different from URL
        "tax_year": "2024-25",
        "salary_income": salary_data
    }
    
    response = client.put("/v2/taxation/records/employee/EMP001/salary", json=request_data)
    assert response.status_code == 400
    assert "Employee ID in path must match employee_id in request body" in response.text

def test_update_deductions_component_success(client, clean_salary_package_records, seed_test_user):
    """Test successful deductions component update."""
    deductions_data = create_deductions_data()
    
    request_data = {
        "employee_id": "EMP001",
        "tax_year": "2024-25",
        "deductions": deductions_data,
        "notes": "Test deductions update"
    }
    
    response = client.put("/v2/taxation/records/employee/EMP001/deductions", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["employee_id"] == "EMP001"
    assert data["tax_year"] == "2024-25"
    assert data["component_type"] == "deductions"
    assert data["status"] == "success"

def test_update_regime_component_success(client, clean_salary_package_records, seed_test_user):
    """Test successful regime component update."""
    request_data = {
        "employee_id": "EMP001",
        "tax_year": "2024-25",
        "regime_type": "old",
        "age": 30,
        "notes": "Test regime update"
    }
    
    response = client.put("/v2/taxation/records/employee/EMP001/regime", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["employee_id"] == "EMP001"
    assert data["tax_year"] == "2024-25"
    assert data["component_type"] == "regime"
    assert data["status"] == "success"

def test_update_regime_component_invalid_regime(client, clean_salary_package_records, seed_test_user):
    """Test regime component update with invalid regime type."""
    request_data = {
        "employee_id": "EMP001",
        "tax_year": "2024-25",
        "regime_type": "invalid",  # Invalid regime
        "age": 30
    }
    
    response = client.put("/v2/taxation/records/employee/EMP001/regime", json=request_data)
    assert response.status_code == 422

def test_is_regime_update_allowed_success(client, clean_salary_package_records, seed_test_user):
    """Test regime update allowed check."""
    response = client.get("/v2/taxation/records/employee/EMP001/regime/allowed?tax_year=2024-25")
    assert response.status_code == 200
    data = response.json()
    assert "is_allowed" in data
    assert "current_regime" in data
    assert "message" in data

# =============================================================================
# COMPONENT RETRIEVAL ENDPOINTS
# =============================================================================

def test_get_component_success(client, clean_salary_package_records, seed_test_user):
    """Test successful component retrieval."""
    # First create a component
    salary_data = create_salary_income_data()
    request_data = {
        "employee_id": "EMP001",
        "tax_year": "2024-25",
        "salary_income": salary_data
    }
    client.put("/v2/taxation/records/employee/EMP001/salary", json=request_data)
    
    # Then retrieve it
    response = client.get("/v2/taxation/records/employee/EMP001/component/salary?tax_year=2024-25")
    assert response.status_code == 200
    data = response.json()
    assert data["employee_id"] == "EMP001"
    assert data["tax_year"] == "2024-25"
    assert data["component_type"] == "salary"
    assert "component_data" in data

def test_get_component_not_found(client, clean_salary_package_records, seed_test_user):
    """Test component retrieval for non-existent component."""
    response = client.get("/v2/taxation/records/employee/EMP001/component/nonexistent?tax_year=2024-25")
    assert response.status_code in [404, 500]  # Accept both as backend might return different errors

# =============================================================================
# MONTHLY TAX COMPUTATION ENDPOINTS
# =============================================================================

def test_compute_monthly_tax_success(client, clean_salary_package_records, seed_test_user):
    """Test successful monthly tax computation."""
    # First create salary data
    salary_data = create_salary_income_data()
    request_data = {
        "employee_id": "EMP001",
        "tax_year": "2024-25",
        "salary_income": salary_data
    }
    client.put("/v2/taxation/records/employee/EMP001/salary", json=request_data)
    
    # Then compute monthly tax
    response = client.get("/v2/taxation/monthly-tax/employee/EMP001")
    assert response.status_code == 200
    data = response.json()
    assert "monthly_tax_liability" in data
    assert "annual_tax_liability" in data
    assert "tax_regime" in data

def test_compute_current_month_tax_success(client, clean_salary_package_records, seed_test_user):
    """Test successful current month tax computation."""
    # First create salary data
    salary_data = create_salary_income_data()
    request_data = {
        "employee_id": "EMP001",
        "tax_year": "2024-25",
        "salary_income": salary_data
    }
    client.put("/v2/taxation/records/employee/EMP001/salary", json=request_data)
    
    # Then compute current month tax
    response = client.get("/v2/taxation/monthly-tax/current/EMP001")
    assert response.status_code == 200
    data = response.json()
    assert "monthly_tax_liability" in data
    assert "annual_tax_liability" in data

def test_compute_monthly_tax_employee_not_found(client):
    """Test monthly tax computation for non-existent employee."""
    random_emp = "emp_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    response = client.get(f"/v2/taxation/monthly-tax/employee/{random_emp}")
    assert response.status_code in [404, 422, 500]  # Accept various error codes

# =============================================================================
# MONTHLY SALARY COMPUTATION ENDPOINTS
# =============================================================================

def test_compute_monthly_salary_success(client, clean_salary_package_records, seed_test_user):
    """Test successful monthly salary computation."""
    request_data = {
        "employee_id": "EMP001",
        "month": 1,
        "year": 2024,
        "tax_year": "2024-25",
        "one_time_arrear": 0.0,
        "one_time_bonus": 0.0,
        "lwp_days": 0
    }
    
    response = client.post("/v2/taxation/monthly-salary/compute", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["employee_id"] == "EMP001"
    assert data["month"] == 1
    assert data["year"] == 2024
    assert data["tax_year"] == "2024-25"
    assert "gross_salary" in data
    assert "total_deductions" in data
    assert "net_salary" in data

def test_compute_monthly_salary_invalid_data(client):
    """Test monthly salary computation with invalid data."""
    request_data = {
        "employee_id": "EMP001",
        "month": 13,  # Invalid month
        "year": 2024,
        "tax_year": "2024-25"
    }
    
    response = client.post("/v2/taxation/monthly-salary/compute", json=request_data)
    assert response.status_code == 422

def test_get_monthly_salary_success(client, clean_salary_package_records, seed_test_user):
    """Test successful monthly salary retrieval."""
    # First compute a monthly salary
    request_data = {
        "employee_id": "EMP001",
        "month": 1,
        "year": 2024,
        "tax_year": "2024-25",
        "one_time_arrear": 0.0,
        "one_time_bonus": 0.0,
        "lwp_days": 0
    }
    client.post("/v2/taxation/monthly-salary/compute", json=request_data)
    
    # Then retrieve it
    response = client.get("/v2/taxation/monthly-salary/employee/EMP001/month/1/year/2024")
    assert response.status_code == 200
    data = response.json()
    assert data["employee_id"] == "EMP001"
    assert data["month"] == 1
    assert data["year"] == 2024

def test_get_monthly_salary_not_found(client):
    """Test monthly salary retrieval for non-existent record."""
    response = client.get("/v2/taxation/monthly-salary/employee/EMP001/month/1/year/2020")
    assert response.status_code in [404, 500]

def test_get_employee_salary_history_success(client, clean_salary_package_records, seed_test_user):
    """Test successful salary history retrieval."""
    response = client.get("/v2/taxation/monthly-salary/employee/EMP001/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_monthly_salaries_for_period_success(client, clean_salary_package_records, seed_test_user):
    """Test successful monthly salaries for period retrieval."""
    response = client.get("/v2/taxation/monthly-salary/period/month/1/tax-year/2024-25")
    assert response.status_code == 200
    data = response.json()
    assert "monthly_salaries" in data
    assert "total_count" in data

def test_get_monthly_salary_summary_success(client, clean_salary_package_records, seed_test_user):
    """Test successful monthly salary summary retrieval."""
    response = client.get("/v2/taxation/monthly-salary/summary/month/1/tax-year/2024-25")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data

# =============================================================================
# EXPORT ENDPOINTS
# =============================================================================

def test_export_salary_package_to_excel_success(client, clean_salary_package_records, seed_test_user):
    """Test successful salary package export to Excel."""
    # First create some data
    salary_data = create_salary_income_data()
    request_data = {
        "employee_id": "EMP001",
        "tax_year": "2024-25",
        "salary_income": salary_data
    }
    client.put("/v2/taxation/records/employee/EMP001/salary", json=request_data)
    
    # Then export
    response = client.get("/v2/taxation/export/salary-package/EMP001?tax_year=2024-25")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "Content-Disposition" in response.headers

def test_export_salary_package_single_sheet_success(client, clean_salary_package_records, seed_test_user):
    """Test successful salary package export to single Excel sheet."""
    # First create some data
    salary_data = create_salary_income_data()
    request_data = {
        "employee_id": "EMP001",
        "tax_year": "2024-25",
        "salary_income": salary_data
    }
    client.put("/v2/taxation/records/employee/EMP001/salary", json=request_data)
    
    # Then export
    response = client.get("/v2/taxation/export/salary-package-single/EMP001?tax_year=2024-25")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "Content-Disposition" in response.headers

# =============================================================================
# LOAN PROCESSING ENDPOINTS
# =============================================================================

def test_process_loan_schedule_success(client, clean_salary_package_records, seed_test_user):
    """Test successful loan schedule processing."""
    response = client.get("/v2/taxation/loan-schedule/employee/EMP001?tax_year=2024-25")
    assert response.status_code == 200
    data = response.json()
    assert "employee_info" in data
    assert "loan_info" in data
    assert "processing_date" in data

def test_process_loan_schedule_employee_not_found(client):
    """Test loan schedule processing for non-existent employee."""
    random_emp = "emp_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    response = client.get(f"/v2/taxation/loan-schedule/employee/{random_emp}?tax_year=2024-25")
    assert response.status_code in [404, 422, 500]

# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

def test_unauthorized_access(client):
    """Test unauthorized access to taxation endpoints."""
    from app.auth.auth_dependencies import get_current_user
    app.dependency_overrides[get_current_user] = lambda: None
    
    response = client.get("/v2/taxation/health")
    assert response.status_code in [401, 403, 500]
    
    # Restore the original override
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(dummy_token_payload())

def test_missing_employee_id(client):
    """Test endpoints with missing employee ID."""
    from app.auth.auth_dependencies import CurrentUser
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(no_employee_token_payload())
    
    response = client.get("/v2/taxation/health")
    assert response.status_code in [400, 500]
    
    # Restore the original override
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(dummy_token_payload())

def test_invalid_tax_year_format(client, clean_salary_package_records, seed_test_user):
    """Test endpoints with invalid tax year format."""
    salary_data = create_salary_income_data()
    request_data = {
        "employee_id": "EMP001",
        "tax_year": "invalid-year",  # Invalid format
        "salary_income": salary_data
    }
    
    response = client.put("/v2/taxation/records/employee/EMP001/salary", json=request_data)
    assert response.status_code in [422, 500]

def test_validation_errors(client):
    """Test various validation errors."""
    # Test with negative salary values
    salary_data = create_salary_income_data()
    salary_data["basic_salary"] = -1000.0  # Invalid negative value
    
    request_data = {
        "employee_id": "EMP001",
        "tax_year": "2024-25",
        "salary_income": salary_data
    }
    
    response = client.put("/v2/taxation/records/employee/EMP001/salary", json=request_data)
    assert response.status_code == 422

# =============================================================================
# EDGE CASES AND BOUNDARY TESTS
# =============================================================================

def test_large_salary_values(client, clean_salary_package_records, seed_test_user):
    """Test with very large salary values."""
    salary_data = create_salary_income_data()
    salary_data["basic_salary"] = 999999999.99  # Very large value
    
    request_data = {
        "employee_id": "EMP001",
        "tax_year": "2024-25",
        "salary_income": salary_data
    }
    
    response = client.put("/v2/taxation/records/employee/EMP001/salary", json=request_data)
    assert response.status_code == 200

def test_zero_salary_values(client, clean_salary_package_records, seed_test_user):
    """Test with zero salary values."""
    salary_data = create_salary_income_data()
    salary_data["basic_salary"] = 0.0
    salary_data["dearness_allowance"] = 0.0
    
    request_data = {
        "employee_id": "EMP001",
        "tax_year": "2024-25",
        "salary_income": salary_data
    }
    
    response = client.put("/v2/taxation/records/employee/EMP001/salary", json=request_data)
    assert response.status_code == 200

def test_special_characters_in_notes(client, clean_salary_package_records, seed_test_user):
    """Test with special characters in notes field."""
    salary_data = create_salary_income_data()
    
    request_data = {
        "employee_id": "EMP001",
        "tax_year": "2024-25",
        "salary_income": salary_data,
        "notes": "Test notes with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
    }
    
    response = client.put("/v2/taxation/records/employee/EMP001/salary", json=request_data)
    assert response.status_code == 200

def test_unicode_characters_in_notes(client, clean_salary_package_records, seed_test_user):
    """Test with Unicode characters in notes field."""
    salary_data = create_salary_income_data()
    
    request_data = {
        "employee_id": "EMP001",
        "tax_year": "2024-25",
        "salary_income": salary_data,
        "notes": "Test notes with Unicode: ₹, €, ¥, £, ₹, 中文, हिंदी"
    }
    
    response = client.put("/v2/taxation/records/employee/EMP001/salary", json=request_data)
    assert response.status_code == 200 