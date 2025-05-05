from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Dict, Any, Optional
from models.taxation import SalaryComponents, IncomeFromOtherSources, CapitalGains, DeductionComponents, Taxation, Perquisites
from services.taxation_service import calculate_total_tax, calculate_and_save_tax, get_or_create_taxation_by_emp_id
from database.taxation_database import get_taxation_by_emp_id, update_tax_payment, get_all_taxation, update_filing_status
from auth.auth import extract_hostname, role_checker, extract_emp_id
from pydantic import BaseModel

router = APIRouter()

class TaxCalculationRequest(BaseModel):
    emp_id: str
    tax_year: Optional[str] = None
    regime: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "emp_id": "EMP001",
                "tax_year": "2023-2024",
                "regime": "new"
            }
        }

class TaxPaymentRequest(BaseModel):
    emp_id: str
    amount_paid: float
    
    class Config:
        schema_extra = {
            "example": {
                "emp_id": "EMP001",
                "amount_paid": 50000
            }
        }

class FilingStatusRequest(BaseModel):
    emp_id: str
    status: str
    
    class Config:
        schema_extra = {
            "example": {
                "emp_id": "EMP001",
                "status": "filed"
            }
        }

class TaxationDataRequest(BaseModel):
    emp_id: str
    regime: str
    salary: Optional[Dict[str, Any]] = None
    other_sources: Optional[Dict[str, Any]] = None
    capital_gains: Optional[Dict[str, Any]] = None
    deductions: Optional[Dict[str, Any]] = None
    tax_year: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "emp_id": "EMP001",
                "regime": "old",
                "salary": {
                    "basic": 700000,
                    "hra": 350000,
                    "special_allowance": 200000,
                    "bonus": 150000
                },
                "other_sources": {
                    "interest_savings": 15000,
                    "interest_fd": 50000
                },
                "capital_gains": {
                    "stcg_111a": 50000,
                    "ltcg_112a": 200000
                },
                "deductions": {
                    "section_80c": 150000,
                    "section_80d": 25000
                },
                "tax_year": "2023-2024"
            }
        }

@router.post("/calculate-tax")
def calculate_tax_endpoint(
    request: TaxCalculationRequest,
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin", "user"]))
):
    """Calculate total tax for an employee"""
    try:
        tax = calculate_total_tax(request.emp_id, hostname)
        return {"emp_id": request.emp_id, "total_tax": tax}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating tax: {str(e)}")

@router.post("/save-taxation-data")
def save_taxation_data(
    request: TaxationDataRequest,
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin", "user"]))
):
    """Save taxation data and calculate tax"""
    try:
        # Convert dictionary to dataclass objects
        salary = SalaryComponents(**request.salary) if request.salary else None
        other_sources = IncomeFromOtherSources(**request.other_sources) if request.other_sources else None
        capital_gains = CapitalGains(**request.capital_gains) if request.capital_gains else None
        deductions = DeductionComponents(**request.deductions) if request.deductions else None
        
        # Calculate and save tax
        taxation = calculate_and_save_tax(
            emp_id=request.emp_id,
            hostname=hostname,
            tax_year=request.tax_year,
            regime=request.regime,
            salary=salary,
            other_sources=other_sources,
            capital_gains=capital_gains,
            deductions=deductions
        )
        
        return {"status": "success", "taxation": taxation}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving taxation data: {str(e)}")

@router.get("/taxation/{emp_id}")
def get_taxation_endpoint(
    emp_id: str,
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin", "user"]))
):
    """Get taxation data for an employee, creating defaults if not found"""
    try:
        # Use the service layer function that handles creation of default data if not found
        taxation = get_or_create_taxation_by_emp_id(emp_id, hostname)
        return taxation
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving taxation data: {str(e)}")

@router.post("/update-tax-payment")
def update_tax_payment_endpoint(
    request: TaxPaymentRequest,
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin"]))
):
    """Update tax payment for an employee"""
    try:
        updated_taxation = update_tax_payment(request.emp_id, hostname, request.amount_paid)
        return {"status": "success", "taxation": updated_taxation}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating tax payment: {str(e)}")

@router.post("/update-filing-status")
def update_filing_status_endpoint(
    request: FilingStatusRequest,
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin"]))
):
    """Update filing status for an employee's taxation"""
    try:
        updated_taxation = update_filing_status(request.emp_id, hostname, request.status)
        return {"status": "success", "taxation": updated_taxation}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating filing status: {str(e)}")

@router.get("/all-taxation")
def get_all_taxation_endpoint(
    tax_year: Optional[str] = Query(None, description="Filter by tax year"),
    filing_status: Optional[str] = Query(None, description="Filter by filing status"),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin"]))
):
    """Get all taxation records with optional filters including user information"""
    try:
        taxation_records = get_all_taxation(hostname, tax_year, filing_status)
        return {"total": len(taxation_records), "records": taxation_records}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving taxation records: {str(e)}")

@router.get("/my-taxation")
def get_my_taxation_endpoint(
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin", "user"]))
):
    """Get taxation data for the currently logged-in user, creating defaults if not found"""
    try:
        # Use the service layer function that handles creation of default data if not found
        taxation = get_or_create_taxation_by_emp_id(emp_id, hostname)
        return taxation
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving taxation data: {str(e)}")
