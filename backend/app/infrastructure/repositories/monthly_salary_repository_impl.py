import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from app.application.interfaces.repositories.monthly_salary_repository import MonthlySalaryRepository
from app.domain.entities.taxation.monthly_salary import MonthlySalary
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_year import TaxYear
from app.domain.value_objects.tax_regime import TaxRegime
from app.domain.entities.taxation.salary_income import SalaryIncome
from app.domain.entities.taxation.perquisites import Perquisites
from app.domain.entities.taxation.deductions import TaxDeductions
from app.domain.entities.taxation.retirement_benefits import RetirementBenefits
from app.domain.entities.taxation.lwp_details import LwpDetails

logger = logging.getLogger(__name__)

class MongoDBMonthlySalaryRepository(MonthlySalaryRepository):
    """MongoDB implementation of MonthlySalaryRepository."""
    
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
    
    async def save(self, monthly_salary: MonthlySalary, organisation_id: str) -> MonthlySalary:
        """Save a monthly salary record."""
        try:
            # Convert entity to document
            document = self._entity_to_document(monthly_salary, organisation_id)
            
            # Check if record already exists
            existing = await self.collection.find_one({
                "employee_id": monthly_salary.employee_id.value,
                "month": monthly_salary.month,
                "year": monthly_salary.year,
                "organisation_id": organisation_id
            })
            
            if existing:
                # Update existing record
                document["updated_at"] = datetime.utcnow()
                await self.collection.update_one(
                    {"_id": existing["_id"]},
                    {"$set": document}
                )
                logger.info(f"Updated monthly salary for employee {monthly_salary.employee_id.value}")
            else:
                # Insert new record
                document["created_at"] = datetime.utcnow()
                document["updated_at"] = datetime.utcnow()
                result = await self.collection.insert_one(document)
                logger.info(f"Created monthly salary for employee {monthly_salary.employee_id.value}")
            
            return monthly_salary
            
        except Exception as e:
            logger.error(f"Error saving monthly salary: {e}")
            raise
    
    async def get_by_employee_and_period(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int, 
        organisation_id: str
    ) -> Optional[MonthlySalary]:
        """Get monthly salary by employee and period."""
        try:
            document = await self.collection.find_one({
                "employee_id": employee_id.value,
                "month": month,
                "year": year,
                "organisation_id": organisation_id
            })
            
            if document:
                return self._document_to_entity(document)
            return None
            
        except Exception as e:
            logger.error(f"Error getting monthly salary: {e}")
            raise
    
    async def get_by_period(
        self, 
        month: int, 
        year: int, 
        organisation_id: str,
        status: Optional[str] = None,
        department: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[MonthlySalary]:
        """Get monthly salaries for a period with optional filtering."""
        try:
            query = {
                "month": month,
                "year": year,
                "organisation_id": organisation_id
            }
            
            if status:
                query["status"] = status
            
            if department:
                query["department"] = department
            
            cursor = self.collection.find(query).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting monthly salaries for period: {e}")
            raise
    
    async def get_summary_by_period(
        self, 
        month: int, 
        year: int, 
        organisation_id: str
    ) -> dict:
        """Get summary statistics for a period."""
        try:
            pipeline = [
                {
                    "$match": {
                        "month": month,
                        "year": year,
                        "organisation_id": organisation_id
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_employees": {"$sum": 1},
                        "computed_count": {
                            "$sum": {"$cond": [{"$eq": ["$status", "computed"]}, 1, 0]}
                        },
                        "pending_count": {
                            "$sum": {"$cond": [{"$eq": ["$status", "pending"]}, 1, 0]}
                        },
                        "approved_count": {
                            "$sum": {"$cond": [{"$eq": ["$status", "approved"]}, 1, 0]}
                        },
                        "paid_count": {
                            "$sum": {"$cond": [{"$eq": ["$status", "paid"]}, 1, 0]}
                        },
                        "total_gross_payroll": {"$sum": "$gross_salary.amount"},
                        "total_net_payroll": {"$sum": "$net_salary.amount"},
                        "total_deductions": {"$sum": "$total_deductions.amount"},
                        "total_tds": {"$sum": "$tax_amount.amount"},
                        "last_computed_at": {"$max": "$computation_date"}
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=1)
            
            if result:
                summary = result[0]
                total_employees = summary.get("total_employees", 0)
                computed_count = summary.get("computed_count", 0)
                
                return {
                    "month": month,
                    "year": year,
                    "total_employees": total_employees,
                    "computed_count": computed_count,
                    "pending_count": summary.get("pending_count", 0),
                    "approved_count": summary.get("approved_count", 0),
                    "paid_count": summary.get("paid_count", 0),
                    "total_gross_payroll": Decimal(str(summary.get("total_gross_payroll", 0))),
                    "total_net_payroll": Decimal(str(summary.get("total_net_payroll", 0))),
                    "total_deductions": Decimal(str(summary.get("total_deductions", 0))),
                    "total_tds": Decimal(str(summary.get("total_tds", 0))),
                    "computation_completion_rate": (
                        Decimal(str(computed_count)) / Decimal(str(total_employees)) * 100
                        if total_employees > 0 else Decimal('0')
                    ),
                    "last_computed_at": summary.get("last_computed_at"),
                    "next_processing_date": None  # Could be calculated based on business logic
                }
            
            return {
                "month": month,
                "year": year,
                "total_employees": 0,
                "computed_count": 0,
                "pending_count": 0,
                "approved_count": 0,
                "paid_count": 0,
                "total_gross_payroll": Decimal('0'),
                "total_net_payroll": Decimal('0'),
                "total_deductions": Decimal('0'),
                "total_tds": Decimal('0'),
                "computation_completion_rate": Decimal('0'),
                "last_computed_at": None,
                "next_processing_date": None
            }
            
        except Exception as e:
            logger.error(f"Error getting summary for period: {e}")
            raise
    
    async def get_all_employees_for_period(
        self, 
        month: int, 
        year: int, 
        organisation_id: str
    ) -> List[str]:
        """Get all employee IDs that should have salary records for a period."""
        try:
            cursor = self.collection.find(
                {
                    "month": month,
                    "year": year,
                    "organisation_id": organisation_id
                },
                {"employee_id": 1}
            )
            
            documents = await cursor.to_list(length=None)
            return [doc["employee_id"] for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting employee IDs for period: {e}")
            raise
    
    async def bulk_save(
        self, 
        monthly_salaries: List[MonthlySalary], 
        organisation_id: str
    ) -> List[MonthlySalary]:
        """Save multiple monthly salary records."""
        try:
            operations = []
            
            for salary in monthly_salaries:
                document = self._entity_to_document(salary, organisation_id)
                document["updated_at"] = datetime.utcnow()
                
                operations.append({
                    "updateOne": {
                        "filter": {
                            "employee_id": salary.employee_id.value,
                            "month": salary.month,
                            "year": salary.year,
                            "organisation_id": organisation_id
                        },
                        "update": {"$set": document},
                        "upsert": True
                    }
                })
            
            if operations:
                await self.collection.bulk_write(operations)
                logger.info(f"Bulk saved {len(monthly_salaries)} monthly salary records")
            
            return monthly_salaries
            
        except Exception as e:
            logger.error(f"Error bulk saving monthly salaries: {e}")
            raise
    
    async def update_status(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int, 
        status: str,
        notes: Optional[str] = None,
        updated_by: Optional[str] = None,
        organisation_id: str = None
    ) -> Optional[MonthlySalary]:
        """Update the status of a monthly salary record."""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            if notes is not None:
                update_data["notes"] = notes
            
            if updated_by:
                update_data["updated_by"] = updated_by
            
            result = await self.collection.find_one_and_update(
                {
                    "employee_id": employee_id.value,
                    "month": month,
                    "year": year,
                    "organisation_id": organisation_id
                },
                {"$set": update_data},
                return_document=True
            )
            
            if result:
                return self._document_to_entity(result)
            return None
            
        except Exception as e:
            logger.error(f"Error updating monthly salary status: {e}")
            raise
    
    async def mark_payment(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int, 
        payment_type: str,
        payment_reference: Optional[str] = None,
        payment_notes: Optional[str] = None,
        paid_by: Optional[str] = None,
        organisation_id: str = None
    ) -> Optional[MonthlySalary]:
        """Mark payment for a monthly salary record."""
        try:
            update_data = {
                "updated_at": datetime.utcnow()
            }
            
            if payment_type == "salary":
                update_data["salary_paid"] = True
                update_data["status"] = "salary_paid"
            elif payment_type == "tds":
                update_data["tds_paid"] = True
                update_data["status"] = "tds_paid"
            elif payment_type == "both":
                update_data["salary_paid"] = True
                update_data["tds_paid"] = True
                update_data["status"] = "paid"
            
            if payment_reference:
                update_data["payment_reference"] = payment_reference
            
            if payment_notes:
                update_data["payment_notes"] = payment_notes
            
            if paid_by:
                update_data["updated_by"] = paid_by
            
            result = await self.collection.find_one_and_update(
                {
                    "employee_id": employee_id.value,
                    "month": month,
                    "year": year,
                    "organisation_id": organisation_id
                },
                {"$set": update_data},
                return_document=True
            )
            
            if result:
                return self._document_to_entity(result)
            return None
            
        except Exception as e:
            logger.error(f"Error marking payment: {e}")
            raise
    
    async def delete(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int, 
        organisation_id: str
    ) -> bool:
        """Delete a monthly salary record."""
        try:
            result = await self.collection.delete_one({
                "employee_id": employee_id.value,
                "month": month,
                "year": year,
                "organisation_id": organisation_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting monthly salary: {e}")
            raise
    
    async def exists(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int, 
        organisation_id: str
    ) -> bool:
        """Check if a monthly salary record exists."""
        try:
            count = await self.collection.count_documents({
                "employee_id": employee_id.value,
                "month": month,
                "year": year,
                "organisation_id": organisation_id
            })
            
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking monthly salary existence: {e}")
            raise
    
    def _entity_to_document(self, entity: MonthlySalary, organisation_id: str) -> dict:
        """Convert MonthlySalary entity to MongoDB document."""
        return {
            "employee_id": entity.employee_id.value,
            "month": entity.month,
            "year": entity.year,
            "tax_year": entity.tax_year.value,
            "tax_regime": entity.tax_regime.value,
            
            # Salary components
            "basic_salary": {"amount": str(entity.salary.basic_salary.amount), "currency": "INR"},
            "da": {"amount": str(entity.salary.dearness_allowance.amount), "currency": "INR"},
            "hra": {"amount": str(entity.salary.hra_provided.amount), "currency": "INR"},
            "special_allowance": {"amount": str(entity.salary.special_allowance.amount), "currency": "INR"},
            "transport_allowance": {"amount": str(entity.transport_allowance.amount), "currency": "INR"},
            "medical_allowance": {"amount": str(entity.medical_allowance.amount), "currency": "INR"},
            "bonus": {"amount": str(entity.salary.bonus.amount), "currency": "INR"},
            "commission": {"amount": str(entity.salary.commission.amount), "currency": "INR"},
            "other_allowances": {"amount": str(entity.other_allowances.amount), "currency": "INR"},
            
            # Deductions
            "epf_employee": {"amount": str(entity.epf_employee.amount), "currency": "INR"},
            "esi_employee": {"amount": str(entity.esi_employee.amount), "currency": "INR"},
            "professional_tax": {"amount": str(entity.professional_tax.amount), "currency": "INR"},
            "tax_amount": {"amount": str(entity.tax_amount.amount), "currency": "INR"},
            "advance_deduction": {"amount": str(entity.advance_deduction.amount), "currency": "INR"},
            "loan_deduction": {"amount": str(entity.loan_deduction.amount), "currency": "INR"},
            "other_deductions": {"amount": str(entity.other_deductions.amount), "currency": "INR"},
            
            # Calculated totals
            "gross_salary": {"amount": str(entity.gross_salary.amount), "currency": "INR"},
            "total_deductions": {"amount": str(entity.total_deductions.amount), "currency": "INR"},
            "net_salary": {"amount": str(entity.net_salary.amount), "currency": "INR"},
            
            # Annual projections
            "annual_gross_salary": {"amount": str(entity.annual_gross_salary.amount), "currency": "INR"},
            "annual_tax_liability": {"amount": str(entity.annual_tax_liability.amount), "currency": "INR"},
            
            # Tax details
            "tax_exemptions": {"amount": str(entity.tax_exemptions.amount), "currency": "INR"},
            "standard_deduction": {"amount": str(entity.standard_deduction.amount), "currency": "INR"},
            
            # Working days and LWP
            "total_days_in_month": entity.total_days_in_month,
            "working_days_in_period": entity.working_days_in_period,
            "lwp_days": entity.lwp_days,
            "effective_working_days": entity.effective_working_days,
            
            # Status and payment tracking
            "status": entity.status,
            "salary_paid": entity.salary_paid,
            "tds_paid": entity.tds_paid,
            "payment_reference": entity.payment_reference,
            "payment_notes": entity.payment_notes,
            
            # Loan details
            "loan_principal_amount": {"amount": str(entity.loan_principal_amount.amount), "currency": "INR"},
            "loan_interest_amount": {"amount": str(entity.loan_interest_amount.amount), "currency": "INR"},
            "loan_outstanding_amount": {"amount": str(entity.loan_outstanding_amount.amount), "currency": "INR"},
            "loan_type": entity.loan_type,
            
            # Metadata
            "computation_date": entity.computation_date,
            "notes": entity.notes,
            "remarks": entity.remarks,
            "created_by": entity.created_by,
            "updated_by": entity.updated_by,
            
            # Multi-tenancy
            "organisation_id": organisation_id
        }
    
    def _document_to_entity(self, document: dict) -> MonthlySalary:
        """Convert MongoDB document to MonthlySalary entity."""
        # Create Money objects
        def create_money(money_dict: dict) -> Money:
            return Money(Decimal(money_dict.get("amount", "0")))
        
        # Create basic components (simplified for now)
        salary_income = SalaryIncome(
            basic_salary=create_money(document.get("basic_salary", {})),
            dearness_allowance=create_money(document.get("da", {})),
            hra_provided=create_money(document.get("hra", {})),
            special_allowance=create_money(document.get("special_allowance", {})),
            bonus=create_money(document.get("bonus", {})),
            commission=create_money(document.get("commission", {})),
            arrears=Money.zero(),
            gratuity=Money.zero(),
            leave_encashment=Money.zero(),
            professional_tax=create_money(document.get("professional_tax", {})),
            tds_deducted=create_money(document.get("tax_amount", {})),
            employer_pf=Money.zero(),
            employee_pf=create_money(document.get("epf_employee", {})),
            employer_esic=Money.zero(),
            employee_esic=create_money(document.get("esi_employee", {})),
            lta=Money.zero(),
            medical_allowance=create_money(document.get("medical_allowance", {})),
            conveyance_allowance=create_money(document.get("transport_allowance", {})),
            food_allowance=Money.zero(),
            telephone_allowance=Money.zero(),
            uniform_allowance=Money.zero(),
            educational_allowance=Money.zero()
        )
        
        # Create other components (simplified)
        perquisites = Perquisites()
        deductions = TaxDeductions()
        retirement = RetirementBenefits()
        lwp = LwpDetails()
        
        return MonthlySalary(
            employee_id=EmployeeId(document["employee_id"]),
            month=document["month"],
            year=document["year"],
            salary=salary_income,
            perquisites=perquisites,
            deductions=deductions,
            retirement=retirement,
            lwp=lwp,
            tax_year=TaxYear(document["tax_year"]),
            tax_regime=TaxRegime(document["tax_regime"]),
            tax_amount=create_money(document.get("tax_amount", {})),
            net_salary=create_money(document.get("net_salary", {})),
            
            # Additional components
            transport_allowance=create_money(document.get("transport_allowance", {})),
            medical_allowance=create_money(document.get("medical_allowance", {})),
            other_allowances=create_money(document.get("other_allowances", {})),
            
            epf_employee=create_money(document.get("epf_employee", {})),
            esi_employee=create_money(document.get("esi_employee", {})),
            professional_tax=create_money(document.get("professional_tax", {})),
            advance_deduction=create_money(document.get("advance_deduction", {})),
            loan_deduction=create_money(document.get("loan_deduction", {})),
            other_deductions=create_money(document.get("other_deductions", {})),
            
            gross_salary=create_money(document.get("gross_salary", {})),
            total_deductions=create_money(document.get("total_deductions", {})),
            
            annual_gross_salary=create_money(document.get("annual_gross_salary", {})),
            annual_tax_liability=create_money(document.get("annual_tax_liability", {})),
            
            tax_exemptions=create_money(document.get("tax_exemptions", {})),
            standard_deduction=create_money(document.get("standard_deduction", {})),
            
            total_days_in_month=document.get("total_days_in_month", 30),
            working_days_in_period=document.get("working_days_in_period", 30),
            lwp_days=document.get("lwp_days", 0),
            effective_working_days=document.get("effective_working_days", 30),
            
            status=document.get("status", "not_computed"),
            salary_paid=document.get("salary_paid", False),
            tds_paid=document.get("tds_paid", False),
            payment_reference=document.get("payment_reference"),
            payment_notes=document.get("payment_notes"),
            
            loan_principal_amount=create_money(document.get("loan_principal_amount", {})),
            loan_interest_amount=create_money(document.get("loan_interest_amount", {})),
            loan_outstanding_amount=create_money(document.get("loan_outstanding_amount", {})),
            loan_type=document.get("loan_type"),
            
            computation_date=document.get("computation_date"),
            notes=document.get("notes"),
            remarks=document.get("remarks"),
            created_at=document.get("created_at", datetime.utcnow()),
            updated_at=document.get("updated_at", datetime.utcnow()),
            created_by=document.get("created_by"),
            updated_by=document.get("updated_by")
        ) 