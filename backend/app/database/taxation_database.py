from fastapi import HTTPException
from models.taxation import Taxation, SalaryComponents, IncomeFromOtherSources, CapitalGains, DeductionComponents, Perquisites
import logging
from database.database_connector import connect_to_database
from database.user_database import get_all_users
from typing import List, Dict, Any, Optional
import datetime

logger = logging.getLogger(__name__)


def get_taxation_collection(company_id: str):
    db = connect_to_database(company_id)
    return db["taxation"]

def get_taxation_by_emp_id(emp_id: str, hostname: str) -> Dict[str, Any]:
    collection = get_taxation_collection(hostname)
    taxation = collection.find_one({"emp_id": emp_id})
    if not taxation:
        raise HTTPException(status_code=404, detail=f"Taxation not found for employee {emp_id}")
    
    # Convert ObjectId to string before returning
    return _convert_objectid(taxation)

def save_taxation(taxation: Taxation, hostname: str) -> Dict[str, Any]:
    """Save taxation data to the database"""
    collection = get_taxation_collection(hostname)
    
    # Convert to dictionary for MongoDB storage
    taxation_dict = taxation.to_dict()
    taxation_dict["updated_at"] = datetime.datetime.utcnow()
    
    # Check if record exists
    existing = collection.find_one({"emp_id": taxation.emp_id})
    if existing:
        # Update existing record
        collection.update_one(
            {"emp_id": taxation.emp_id},
            {"$set": taxation_dict}
        )
    else:
        # Create new record
        taxation_dict["created_at"] = datetime.datetime.utcnow()
        collection.insert_one(taxation_dict)
    
    return get_taxation_by_emp_id(taxation.emp_id, hostname)

def update_tax_payment(emp_id: str, hostname: str, amount_paid: float) -> Dict[str, Any]:
    """Update tax payment for an employee"""
    taxation_data = get_taxation_by_emp_id(emp_id, hostname)
    taxation = Taxation.from_dict(taxation_data)
    
    # Update tax paid and recalculate due/refundable amounts
    taxation.tax_paid += amount_paid
    taxation.tax_due = max(0, taxation.tax_payable - taxation.tax_paid)
    taxation.tax_refundable = max(0, taxation.tax_paid - taxation.tax_payable)
    taxation.tax_pending = taxation.tax_due
    
    # Save updates to database
    return save_taxation(taxation, hostname)

def _convert_objectid(data):
    """Convert MongoDB ObjectId to string in dictionaries"""
    if isinstance(data, dict):
        # Create a new dict to avoid modifying the original during iteration
        converted = {}
        for key, value in data.items():
            if key == '_id':
                # Convert ObjectId to string
                converted[key] = str(value)
            else:
                # Recursively process nested dictionaries/lists
                converted[key] = _convert_objectid(value)
        return converted
    elif isinstance(data, list):
        # Process each item in a list
        return [_convert_objectid(item) for item in data]
    else:
        # Return other types unchanged
        return data

def get_all_taxation(hostname: str, tax_year: Optional[str] = None, filing_status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all taxation records with optional filters and include user information"""
    collection = get_taxation_collection(hostname)
    
    # First, get all users to get their names
    users = get_all_users(hostname)
    
    # Create a dictionary mapping emp_id to user details
    user_map = {}
    for user in users:
        user_map[user.get('emp_id')] = {
            'name': user.get('name', 'Unknown'),
            'email': user.get('email', ''),
            'role': user.get('role', '')
        }
    
    # Build query based on filters for taxation data
    query = {}
    if tax_year:
        query["tax_year"] = tax_year
    if filing_status:
        query["filing_status"] = filing_status
    
    # Execute query to get taxation data
    taxation_results = list(collection.find(query))
    
    # Create a set of all employee IDs from taxation data
    taxation_emp_ids = {record.get('emp_id') for record in taxation_results}
    
    # Prepare final results list
    results = []
    
    # Add users with taxation data
    for record in taxation_results:
        # Convert ObjectId to string
        record = _convert_objectid(record)
        
        emp_id = record.get('emp_id')
        user_info = user_map.get(emp_id, {'name': 'Unknown', 'email': '', 'role': ''})
        
        # Combine user info with taxation record
        results.append({
            **record,
            'user_name': user_info['name'],
            'user_email': user_info['email'],
            'user_role': user_info['role']
        })
    
    # Add users without taxation data if they exist
    for emp_id, user_info in user_map.items():
        if emp_id not in taxation_emp_ids:
            # Create an empty taxation record with user info
            results.append({
                'emp_id': emp_id,
                'user_name': user_info['name'],
                'user_email': user_info['email'],
                'user_role': user_info['role'],
                'tax_year': tax_year or '',
                'filing_status': 'Not Filed',
                'total_tax': 0,
                'regime': 'old'
            })
    
    return results

def update_filing_status(emp_id: str, hostname: str, status: str) -> Dict[str, Any]:
    """Update filing status of taxation"""
    valid_statuses = ["draft", "filed", "approved", "rejected", "pending"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")
    
    taxation_data = get_taxation_by_emp_id(emp_id, hostname)
    taxation = Taxation.from_dict(taxation_data)
    
    # Update filing status
    taxation.filing_status = status
    
    # Save updates to database and return with ObjectId converted to string
    return save_taxation(taxation, hostname)

def _object_to_dict(obj) -> Dict:
    """Convert an object to dictionary for MongoDB storage"""
    if hasattr(obj, "__dict__"):
        result = {}
        for key, value in obj.__dict__.items():
            if key.startswith("_"):
                continue
            result[key] = _object_to_dict(value) if hasattr(value, "__dict__") else value
        return result
    return obj
