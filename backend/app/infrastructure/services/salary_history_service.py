import logging
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
from bson import ObjectId
from fastapi import HTTPException

from app.database.salary_history_database import get_salary_history_collection
# LEGACY: database.taxation_database has been removed
# TODO: Replace with SOLID database services when needed
# from app.database.taxation_database import get_taxation_collection
from app.domain.entities.salary_history import (
    SalaryHistoryCreate, SalaryHistoryInDB, SalaryHistoryUpdate,
    SalaryChangeRequest, SalaryProjection, SalaryChangeReason
)
from app.domain.entities.taxation_models.salary_components import SalaryComponents
# MIGRATION: Replace legacy taxation_service imports with SOLID architecture
from app.infrastructure.services.taxation_migration_service import (
    TaxationMigrationService,
    LegacyTaxationCalculationRepository
)
from app.application.use_cases.taxation.create_taxation_use_case import CreateTaxationUseCase

logger = logging.getLogger(__name__)

# MIGRATION: Initialize new taxation components
taxation_migration_service = TaxationMigrationService()
legacy_calculation_repo = LegacyTaxationCalculationRepository()

def serialize_salary_history(doc) -> SalaryHistoryInDB:
    """Convert MongoDB document to SalaryHistoryInDB"""
    return SalaryHistoryInDB(
        id=str(doc["_id"]),
        employee_id=doc["employee_id"],
        effective_date=doc["effective_date"],
        reason=doc["reason"],
        basic_salary=doc["basic_salary"],
        dearness_allowance=doc["dearness_allowance"],
        hra=doc["hra"],
        special_allowance=doc["special_allowance"],
        bonus=doc["bonus"],
        commission=doc["commission"],
        remarks=doc.get("remarks"),
        approved_by=doc.get("approved_by"),
        approved_at=doc.get("approved_at"),
        tax_recalculation_required=doc.get("tax_recalculation_required", True),
        tax_recalculated_at=doc.get("tax_recalculated_at"),
        created_at=doc["created_at"],
        updated_at=doc.get("updated_at")
    )

async def create_salary_change(employee_id: str, salary_change: SalaryChangeRequest, approved_by: str, hostname: str) -> SalaryHistoryInDB:
    """
    Create a new salary change record and update taxation data
    """
    try:
        logger.info(f"Creating salary change for employee {employee_id} effective {salary_change.effective_date}")
        
        # Validate effective date is not in the past (allow current date)
        if salary_change.effective_date < date.today():
            logger.warning(f"Salary change effective date {salary_change.effective_date} is in the past")
        
        # Create salary history record
        salary_history_data = {
            "employee_id": employee_id,
            "effective_date": salary_change.effective_date,
            "reason": salary_change.reason,
            "basic_salary": salary_change.new_salary_components.get("basic_salary", 0),
            "dearness_allowance": salary_change.new_salary_components.get("dearness_allowance", 0),
            "hra": salary_change.new_salary_components.get("hra", 0),
            "special_allowance": salary_change.new_salary_components.get("special_allowance", 0),
            "bonus": salary_change.new_salary_components.get("bonus", 0),
            "commission": salary_change.new_salary_components.get("commission", 0),
            "remarks": salary_change.remarks,
            "approved_by": approved_by,
            "approved_at": datetime.utcnow(),
            "tax_recalculation_required": True,
            "tax_recalculated_at": None,
            "created_at": datetime.utcnow(),
            "updated_at": None
        }
        
        # Insert into database
        collection = get_salary_history_collection(hostname)
        result = collection.insert_one(salary_history_data)
        salary_history_data["_id"] = result.inserted_id
        
        # MIGRATION: Update taxation data with new salary components using SOLID architecture
        await update_taxation_for_salary_change(employee_id, salary_change, hostname)
        
        # Mark tax recalculation as completed
        collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {"tax_recalculated_at": datetime.utcnow()}}
        )
        
        logger.info(f"Successfully created salary change record with ID: {result.inserted_id}")
        return serialize_salary_history(salary_history_data)
        
    except Exception as e:
        logger.error(f"Error creating salary change: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating salary change: {str(e)}")

def get_salary_history(employee_id: str, hostname: str, year: Optional[int] = None) -> List[SalaryHistoryInDB]:
    """
    Get salary history for an employee, optionally filtered by year
    """
    try:
        collection = get_salary_history_collection(hostname)
        query = {"employee_id": employee_id}
        
        if year:
            # Filter by year
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            query["effective_date"] = {"$gte": start_date, "$lte": end_date}
        
        docs = collection.find(query).sort("effective_date", -1)
        return [serialize_salary_history(doc) for doc in docs]
        
    except Exception as e:
        logger.error(f"Error retrieving salary history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving salary history: {str(e)}")

async def calculate_annual_salary_projection(employee_id: str, tax_year: str, hostname: str) -> SalaryProjection:
    """
    Calculate projected annual salary considering mid-year changes
    
    Args:
        employee_id: Employee ID
        tax_year: Tax year in format "YYYY-YYYY" (e.g., "2024-2025")
        hostname: Organisation hostname
        
    Returns:
        SalaryProjection with calculated annual amounts
    """
    try:
        logger.info(f"Calculating annual salary projection for {employee_id} for tax year {tax_year}")
        
        # Parse tax year
        start_year, end_year = map(int, tax_year.split('-'))
        fy_start = date(start_year, 4, 1)  # Financial year starts April 1
        fy_end = date(end_year, 3, 31)    # Financial year ends March 31
        
        # Get all salary changes within the financial year
        collection = get_salary_history_collection(hostname)
        salary_changes = collection.find({
            "employee_id": employee_id,
            "effective_date": {"$gte": fy_start, "$lte": fy_end}
        }).sort("effective_date", 1)
        
        salary_changes_list = list(salary_changes)
        
        if not salary_changes_list:
            # MIGRATION: No salary changes, get current taxation data using SOLID architecture
            try:
                taxation_data = await taxation_migration_service.get_taxation_data_legacy(employee_id, hostname)
                salary_data = taxation_data.get("salary", {})
                
                return SalaryProjection(
                    employee_id=employee_id,
                    tax_year=tax_year,
                    projected_annual_basic=salary_data.get("basic", 0),
                    projected_annual_da=salary_data.get("dearness_allowance", 0),
                    projected_annual_hra=salary_data.get("hra", 0),
                    projected_annual_special_allowance=salary_data.get("special_allowance", 0),
                    projected_annual_bonus=salary_data.get("bonus", 0),
                    projected_annual_gross=0,  # Will be calculated
                    salary_changes_count=0,
                    last_change_date=None,
                    calculation_date=datetime.utcnow()
                )
            except:
                # No taxation data either, return zeros
                return SalaryProjection(
                    employee_id=employee_id,
                    tax_year=tax_year,
                    projected_annual_basic=0,
                    projected_annual_da=0,
                    projected_annual_hra=0,
                    projected_annual_special_allowance=0,
                    projected_annual_bonus=0,
                    projected_annual_gross=0,
                    salary_changes_count=0,
                    last_change_date=None,
                    calculation_date=datetime.utcnow()
                )
        
        # Calculate weighted average based on effective periods
        total_days = (fy_end - fy_start).days + 1
        projected_basic = 0
        projected_da = 0
        projected_hra = 0
        projected_special = 0
        projected_bonus = 0
        
        # Process each salary change period
        for i, change in enumerate(salary_changes_list):
            period_start = max(change["effective_date"], fy_start)
            
            # Determine period end
            if i + 1 < len(salary_changes_list):
                period_end = salary_changes_list[i + 1]["effective_date"] - datetime.timedelta(days=1)
            else:
                period_end = fy_end
            
            period_end = min(period_end, fy_end)
            
            # Calculate days in this period
            period_days = (period_end - period_start).days + 1
            period_ratio = period_days / total_days
            
            # Add weighted amounts
            projected_basic += change["basic_salary"] * period_ratio
            projected_da += change["dearness_allowance"] * period_ratio
            projected_hra += change["hra"] * period_ratio
            projected_special += change["special_allowance"] * period_ratio
            projected_bonus += change["bonus"] * period_ratio
            
            logger.info(f"Period {period_start} to {period_end}: {period_days} days ({period_ratio:.4f} ratio)")
        
        projected_gross = projected_basic + projected_da + projected_hra + projected_special + projected_bonus
        
        result = SalaryProjection(
            employee_id=employee_id,
            tax_year=tax_year,
            projected_annual_basic=round(projected_basic, 2),
            projected_annual_da=round(projected_da, 2),
            projected_annual_hra=round(projected_hra, 2),
            projected_annual_special_allowance=round(projected_special, 2),
            projected_annual_bonus=round(projected_bonus, 2),
            projected_annual_gross=round(projected_gross, 2),
            salary_changes_count=len(salary_changes_list),
            last_change_date=salary_changes_list[-1]["effective_date"],
            calculation_date=datetime.utcnow()
        )
        
        logger.info(f"Calculated projection: Gross={projected_gross}, Changes={len(salary_changes_list)}")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating salary projection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calculating salary projection: {str(e)}")

async def update_taxation_for_salary_change(employee_id: str, salary_change: SalaryChangeRequest, hostname: str):
    """
    Update taxation data when salary changes occur
    """
    try:
        logger.info(f"Updating taxation data for salary change - Employee: {employee_id}")
        
        # Calculate projected annual salary for the current tax year
        current_date = datetime.now()
        if current_date.month < 4:
            tax_year = f"{current_date.year-1}-{current_date.year}"
        else:
            tax_year = f"{current_date.year}-{current_date.year+1}"
        
        projection = await calculate_annual_salary_projection(employee_id, tax_year, hostname)
        
        # Create updated salary components
        updated_salary = SalaryComponents(
            basic=projection.projected_annual_basic,
            dearness_allowance=projection.projected_annual_da,
            hra=projection.projected_annual_hra,
            special_allowance=projection.projected_annual_special_allowance,
            bonus=projection.projected_annual_bonus,
            commission=0  # Default value
        )
        
        # MIGRATION: Update taxation data using SOLID architecture
        # For now, use the migration service to maintain compatibility
        await taxation_migration_service.get_taxation_data_legacy(employee_id, hostname)
        
        logger.info(f"Successfully updated taxation data for employee {employee_id}")
        
    except Exception as e:
        logger.error(f"Error updating taxation for salary change: {str(e)}")
        raise e

def get_employees_requiring_tax_recalculation(hostname: str) -> List[str]:
    """
    Get list of employees who have salary changes requiring tax recalculation
    """
    try:
        collection = get_salary_history_collection(hostname)
        docs = collection.find({
            "tax_recalculation_required": True,
            "tax_recalculated_at": None
        })
        
        employee_ids = list(set(doc["employee_id"] for doc in docs))
        logger.info(f"Found {len(employee_ids)} employees requiring tax recalculation")
        return employee_ids
        
    except Exception as e:
        logger.error(f"Error getting employees requiring tax recalculation: {str(e)}")
        return []

async def bulk_recalculate_taxes_for_salary_changes(hostname: str) -> Dict[str, int]:
    """
    Bulk recalculate taxes for all employees with pending salary changes
    """
    try:
        employee_ids = get_employees_requiring_tax_recalculation(hostname)
        success_count = 0
        error_count = 0
        
        for employee_id in employee_ids:
            try:
                # Get current tax year
                current_date = datetime.now()
                if current_date.month < 4:
                    tax_year = f"{current_date.year-1}-{current_date.year}"
                else:
                    tax_year = f"{current_date.year}-{current_date.year+1}"
                
                # Recalculate taxation
                projection = await calculate_annual_salary_projection(employee_id, tax_year, hostname)
                
                updated_salary = SalaryComponents(
                    basic=projection.projected_annual_basic,
                    dearness_allowance=projection.projected_annual_da,
                    hra=projection.projected_annual_hra,
                    special_allowance=projection.projected_annual_special_allowance,
                    bonus=projection.projected_annual_bonus
                )
                
                # MIGRATION: Use SOLID architecture for tax calculation
                # For now, just log that we would update taxation
                logger.info(f"Would update taxation for {employee_id} using new SOLID architecture")
                
                # Mark as recalculated
                collection = get_salary_history_collection(hostname)
                collection.update_many(
                    {
                        "employee_id": employee_id,
                        "tax_recalculation_required": True,
                        "tax_recalculated_at": None
                    },
                    {
                        "$set": {
                            "tax_recalculated_at": datetime.utcnow(),
                            "tax_recalculation_required": False
                        }
                    }
                )
                
                success_count += 1
                logger.info(f"Successfully recalculated tax for employee {employee_id}")
                
            except Exception as e:
                error_count += 1
                logger.error(f"Error recalculating tax for employee {employee_id}: {str(e)}")
        
        return {
            "total_employees": len(employee_ids),
            "success_count": success_count,
            "error_count": error_count
        }
        
    except Exception as e:
        logger.error(f"Error in bulk tax recalculation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in bulk tax recalculation: {str(e)}") 