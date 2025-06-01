import logging
from datetime import datetime, date
from typing import List, Dict, Optional
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING

from database.database_connector import connect_to_database
from app.domain.entities.salary_history import SalaryHistoryInDB

logger = logging.getLogger(__name__)

def get_salary_history_collection(hostname: str):
    """
    Returns the salary history collection for the specified company.
    """
    db = connect_to_database(hostname)
    return db["salary_history"]

def ensure_salary_history_indexes(hostname: str):
    """
    Ensure necessary indexes for optimal query performance
    """
    try:
        collection = get_salary_history_collection(hostname)
        
        # Index for employee and effective date queries
        collection.create_index([
            ("employee_id", ASCENDING),
            ("effective_date", DESCENDING)
        ])
        
        # Index for tax recalculation queries
        collection.create_index([
            ("tax_recalculation_required", ASCENDING),
            ("tax_recalculated_at", ASCENDING)
        ])
        
        # Index for date range queries
        collection.create_index([
            ("effective_date", ASCENDING)
        ])
        
        logger.info("Salary history indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating salary history indexes: {str(e)}")

# Export the collection for direct import
def get_salary_history_collection_direct(hostname: str):
    """Direct collection access for imports"""
    return get_salary_history_collection(hostname) 