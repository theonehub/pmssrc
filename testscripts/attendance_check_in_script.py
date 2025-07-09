import requests
from datetime import datetime, timedelta
import json
import uuid

def login(base_url, username, password):
    """Authenticate and get access token"""
    login_url = f"{base_url}/api/v2/auth/login"
    login_data = {
        "username": username,
        "password": password,
        "hostname": "theonetech"  # Added hostname parameter
    }
    response = requests.post(login_url, json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    raise Exception(f"Login failed: {response.text}")

def convert_date_format(date_str):
    """Convert DD-MM-YYYY to YYYY-MM-DD"""
    return datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d")

def generate_check_in_data(date_str, employee_id):
    """Generate check-in data for a specific date"""
    # Convert date string to datetime for manipulation
    date = datetime.strptime(date_str, "%Y-%m-%d")
    
    # Generate check-in time at 9:00 AM for the given date
    check_in_time = date.replace(hour=9, minute=0, second=0, microsecond=0)
    
    return {
        "attendance_id": str(uuid.uuid4()),
        "employee_id": employee_id,
        "attendance_date": date_str,
        "status": {
            "status": "present",
            "marking_type": "manual",
            "is_regularized": False,
            "regularization_reason": None
        },
        "working_hours": {
            "check_in_time": check_in_time.isoformat(),
            "check_out_time": None,
            "total_hours": 0,
            "break_hours": 0,
            "overtime_hours": 0,
            "shortage_hours": 8,
            "expected_hours": 8,
            "is_complete_day": False,
            "is_full_day": False,
            "is_half_day": False
        },
        "check_in_location": None,
        "check_out_location": None,
        "comments": None,
        "admin_notes": None,
        "created_at": datetime.utcnow().isoformat(),
        "created_by": employee_id,
        "updated_at": datetime.utcnow().isoformat(),
        "updated_by": employee_id
    }

def process_date_range(start_date, end_date, base_url, username, password):
    """Process check-ins for a date range"""
    # Convert dates to YYYY-MM-DD format
    start = datetime.strptime(convert_date_format(start_date), "%Y-%m-%d")
    end = datetime.strptime(convert_date_format(end_date), "%Y-%m-%d")
    
    # Get authentication token
    token = login(base_url, username, password)
    
    # Setup headers for authenticated requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Process each date in the range
    current_date = start
    while current_date <= end:
        date_str = current_date.strftime("%Y-%m-%d")
        check_in_data = generate_check_in_data(date_str, username.upper())
        
        # Make the check-in request
        check_in_url = f"{base_url}/api/v2/attendance/checkin"
        response = requests.post(check_in_url, headers=headers, json=check_in_data)
        
        if response.status_code == 200:
            print(f"Successfully checked in for {date_str}")
        else:
            print(f"Failed to check in for {date_str}: {response.text}")
        
        current_date += timedelta(days=1)

if __name__ == "__main__":
    # Configuration
    BASE_URL = "http://localhost:8000"
    USERNAME = "emp002"
    PASSWORD = "admin123"
    
    # Get date range from user
    start_date = input("Enter start date (DD-MM-YYYY): ")
    end_date = input("Enter end date (DD-MM-YYYY): ")
    
    try:
        process_date_range(start_date, end_date, BASE_URL, USERNAME, PASSWORD)
        print("Date range processing completed!")
    except Exception as e:
        print(f"Error occurred: {str(e)}") 