"""
MongoDB Monthly Salary Repository
MongoDB implementation of the monthly salary repository
"""

from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from bson import ObjectId
from app.utils.logger import get_logger

from app.application.interfaces.repositories.monthly_salary_repository import MonthlySalaryRepository
from app.domain.entities.taxation.monthly_salary import MonthlySalary
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.tax_year import TaxYear
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
from app.domain.value_objects.money import Money
from app.domain.entities.taxation.salary_income import SalaryIncome, SpecificAllowances
from app.domain.entities.taxation.perquisites import Perquisites
from app.domain.entities.taxation.deductions import TaxDeductions
from app.domain.entities.taxation.retirement_benefits import RetirementBenefits
from app.domain.entities.taxation.lwp_details import LWPDetails
from app.infrastructure.database.database_connector import DatabaseConnector


class MongoDBMonthlySalaryRepository(MonthlySalaryRepository):
    """
    MongoDB implementation of the monthly salary repository.
    
    Handles persistence operations for monthly salary records with multi-tenancy support.
    """
    
    def __init__(self, database_connector: DatabaseConnector):
        """
        Initialize the repository.
        
        Args:
            database_connector: Database connector for MongoDB operations
        """
        self.database_connector = database_connector
        self.logger = get_logger(__name__)
        self._connection_string = None
        self._client_options = None
    
    def set_connection_config(self, connection_string: str, client_options: dict):
        """Set MongoDB connection configuration."""
        self._connection_string = connection_string
        self._client_options = client_options
    
    async def _get_collection(self, organization_id: str):
        """Get MongoDB collection for the organization."""
        # Fix database name logic - if organisation_id is None or global, use global database directly
        if organization_id and organization_id not in ["global", "pms_global_database"]:
            # For specific organisation, use pms_organisationid format
            db_name = f"pms_{organization_id}"
        else:
            # For global or None, use the global database name directly
            db_name = "pms_global_database"
        
        # Ensure database is connected in the current event loop
        if not self.database_connector.is_connected:
            self.logger.info("Database not connected, establishing connection...")
            
            try:
                # Use stored connection configuration or fallback to config functions
                if self._connection_string and self._client_options:
                    self.logger.info("Using stored connection parameters from repository configuration")
                    connection_string = self._connection_string
                    options = self._client_options
                else:
                    # Fallback to config functions if connection config not set
                    self.logger.info("Loading connection parameters from mongodb_config")
                    from app.config.mongodb_config import get_mongodb_connection_string, get_mongodb_client_options
                    connection_string = get_mongodb_connection_string()
                    options = get_mongodb_client_options()
                
                await self.database_connector.connect(connection_string, **options)
                self.logger.info("MongoDB connection established successfully in current event loop")
                
            except Exception as e:
                self.logger.error(f"Failed to establish database connection: {e}")
                raise RuntimeError(f"Database connection failed: {e}")
        
        # Verify connection and get collection
        try:
            database = self.database_connector.get_database(db_name)
            collection = database["monthly_salary"]
            self.logger.info(f"Successfully retrieved collection: monthly_salary from database: {db_name}")
            return collection
            
        except Exception as e:
            self.logger.error(f"Failed to get collection monthly_salary: {e}")
            # Reset connection state to force reconnection on next call
            if hasattr(self.database_connector, '_client'):
                self.database_connector._client = None
            raise RuntimeError(f"Collection access failed: {e}")
    
    async def save(self, monthly_salary: MonthlySalary, organization_id: str) -> MonthlySalary:
        """Save or update a monthly salary record."""
        try:
            collection = await self._get_collection(organization_id)
            
            # Convert entity to document
            document = self._convert_to_document(monthly_salary)
            
            # Check if record exists
            existing_doc = await collection.find_one({
                "employee_id": str(monthly_salary.employee_id),
                "month": monthly_salary.month,
                "year": monthly_salary.year
            })
            
            if existing_doc:
                # Update existing record
                document["updated_at"] = datetime.utcnow()
                document["version"] = existing_doc.get("version", 1) + 1
                
                result = await collection.replace_one(
                    {"_id": existing_doc["_id"]},
                    document
                )
                
                if result.modified_count == 0:
                    raise Exception("Failed to update monthly salary record")
                
                self.logger.info(f"Updated monthly salary record for employee {monthly_salary.employee_id}, month {monthly_salary.month}, year {monthly_salary.year}")
            else:
                # Insert new record
                document["created_at"] = datetime.utcnow()
                document["updated_at"] = datetime.utcnow()
                document["version"] = 1
                
                result = await collection.insert_one(document)
                
                if not result.inserted_id:
                    raise Exception("Failed to insert monthly salary record")
                
                self.logger.info(f"Created monthly salary record for employee {monthly_salary.employee_id}, month {monthly_salary.month}, year {monthly_salary.year}")
            
            return monthly_salary
            
        except Exception as e:
            self.logger.error(f"Error saving monthly salary record: {str(e)}")
            raise
    
    async def get_by_id(self, monthly_salary_id: str, organization_id: str) -> Optional[MonthlySalary]:
        """Get monthly salary record by ID."""
        try:
            collection = await self._get_collection(organization_id)
            document = await collection.find_one({"_id": ObjectId(monthly_salary_id)})
            
            if document:
                return self._convert_to_entity(document)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting monthly salary record by ID: {str(e)}")
            raise
    
    async def get_by_employee_month_year(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int, 
        organization_id: str
    ) -> Optional[MonthlySalary]:
        """Get monthly salary record by employee ID, month, and year."""
        try:
            collection = await self._get_collection(organization_id)
            document = await collection.find_one({
                "employee_id": str(employee_id),
                "month": month,
                "year": year
            })
            
            if document:
                return self._convert_to_entity(document)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting monthly salary record by employee/month/year: {str(e)}")
            raise
    
    async def get_by_employee(
        self, 
        employee_id: EmployeeId, 
        organization_id: str,
        limit: int = 12,
        offset: int = 0
    ) -> List[MonthlySalary]:
        """Get all monthly salary records for an employee."""
        try:
            collection = await self._get_collection(organization_id)
            cursor = collection.find({"employee_id": str(employee_id)}).skip(offset).limit(limit).sort([("year", -1), ("month", -1)])
            
            documents = await cursor.to_list(length=None)
            return [self._convert_to_entity(doc) for doc in documents]
            
        except Exception as e:
            self.logger.error(f"Error getting monthly salary records by employee: {str(e)}")
            raise
    
    async def get_by_month_year(
        self, 
        month: int, 
        year: int, 
        organization_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[MonthlySalary]:
        """Get all monthly salary records for a specific month and year."""
        try:
            collection = await self._get_collection(organization_id)
            cursor = collection.find({
                "month": month,
                "year": year
            }).skip(offset).limit(limit)
            
            documents = await cursor.to_list(length=None)
            return [self._convert_to_entity(doc) for doc in documents]
            
        except Exception as e:
            self.logger.error(f"Error getting monthly salary records by month/year: {str(e)}")
            raise
    
    async def get_by_tax_year(
        self, 
        tax_year: TaxYear,
        organization_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[MonthlySalary]:
        """Get all monthly salary records for a tax year."""
        try:
            collection = await self._get_collection(organization_id)
            cursor = collection.find({
                "tax_year": str(tax_year)
            }).skip(offset).limit(limit)
            
            documents = await cursor.to_list(length=None)
            return [self._convert_to_entity(doc) for doc in documents]
            
        except Exception as e:
            self.logger.error(f"Error getting monthly salary records by tax year: {str(e)}")
            raise
    
    async def search(
        self, 
        organization_id: str,
        employee_id: Optional[EmployeeId] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        tax_year: Optional[TaxYear] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[MonthlySalary]:
        """Search monthly salary records with filters."""
        try:
            collection = await self._get_collection(organization_id)
            
            # Build query
            query = {}
            if employee_id:
                query["employee_id"] = str(employee_id)
            if month is not None:
                query["month"] = month
            if year is not None:
                query["year"] = year
            if tax_year:
                query["tax_year"] = str(tax_year)
            
            cursor = collection.find(query).skip(offset).limit(limit).sort([("year", -1), ("month", -1)])
            documents = await cursor.to_list(length=None)
            
            return [self._convert_to_entity(doc) for doc in documents]
            
        except Exception as e:
            self.logger.error(f"Error searching monthly salary records: {str(e)}")
            raise
    
    async def count(
        self, 
        organization_id: str,
        employee_id: Optional[EmployeeId] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        tax_year: Optional[TaxYear] = None
    ) -> int:
        """Count monthly salary records with filters."""
        try:
            collection = await self._get_collection(organization_id)
            
            # Build query
            query = {}
            if employee_id:
                query["employee_id"] = str(employee_id)
            if month is not None:
                query["month"] = month
            if year is not None:
                query["year"] = year
            if tax_year:
                query["tax_year"] = str(tax_year)
            
            return await collection.count_documents(query)
            
        except Exception as e:
            self.logger.error(f"Error counting monthly salary records: {str(e)}")
            raise
    
    async def delete(self, monthly_salary_id: str, organization_id: str) -> bool:
        """Delete a monthly salary record."""
        try:
            collection = await self._get_collection(organization_id)
            result = await collection.delete_one({"_id": ObjectId(monthly_salary_id)})
            return result.deleted_count > 0
            
        except Exception as e:
            self.logger.error(f"Error deleting monthly salary record: {str(e)}")
            raise
    
    async def exists(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int,
        organization_id: str
    ) -> bool:
        """Check if a monthly salary record exists."""
        try:
            collection = await self._get_collection(organization_id)
            document = await collection.find_one({
                "employee_id": str(employee_id),
                "month": month,
                "year": year
            })
            return document is not None
            
        except Exception as e:
            self.logger.error(f"Error checking monthly salary record existence: {str(e)}")
            raise
    
    async def get_by_employee_and_period(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int, 
        organisation_id: str
    ) -> Optional[MonthlySalary]:
        """Get monthly salary record by employee and period."""
        return await self.get_by_employee_month_year(employee_id, month, year, organisation_id)
    
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
        """Get monthly salary records for a period with filters."""
        try:
            collection = await self._get_collection(organisation_id)
            
            # Build query
            query = {"month": month, "year": year}
            if status:
                query["status"] = status
            if department:
                query["salary.employee_department"] = department
            
            cursor = collection.find(query).skip(skip).limit(limit)
            documents = await cursor.to_list(length=None)
            return [self._convert_to_entity(doc) for doc in documents]
            
        except Exception as e:
            self.logger.error(f"Error getting monthly salary records by period: {str(e)}")
            raise
    
    async def get_summary_by_period(
        self, 
        month: int, 
        year: int, 
        organisation_id: str
    ) -> dict:
        """Get summary statistics for a period."""
        try:
            collection = await self._get_collection(organisation_id)
            
            # Pipeline for aggregation
            pipeline = [
                {"$match": {"month": month, "year": year}},
                {"$group": {
                    "_id": None,
                    "total_records": {"$sum": 1},
                    "total_gross_salary": {"$sum": "$gross_salary.amount"},
                    "total_net_salary": {"$sum": "$net_salary.amount"},
                    "total_tax_amount": {"$sum": "$tax_amount.amount"},
                    "total_deductions": {"$sum": "$total_deductions.amount"},
                    "computed_count": {"$sum": {"$cond": [{"$eq": ["$status", "computed"]}, 1, 0]}},
                    "approved_count": {"$sum": {"$cond": [{"$eq": ["$status", "approved"]}, 1, 0]}},
                    "paid_count": {"$sum": {"$cond": [{"$eq": ["$status", "paid"]}, 1, 0]}},
                    "rejected_count": {"$sum": {"$cond": [{"$eq": ["$status", "rejected"]}, 1, 0]}}
                }}
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=None)
            
            if result:
                summary = result[0]
                return {
                    "total_records": summary["total_records"],
                    "total_gross_salary": float(summary["total_gross_salary"]),
                    "total_net_salary": float(summary["total_net_salary"]),
                    "total_tax_amount": float(summary["total_tax_amount"]),
                    "total_deductions": float(summary["total_deductions"]),
                    "status_breakdown": {
                        "computed": summary["computed_count"],
                        "approved": summary["approved_count"],
                        "paid": summary["paid_count"],
                        "rejected": summary["rejected_count"]
                    }
                }
            else:
                return {
                    "total_records": 0,
                    "total_gross_salary": 0.0,
                    "total_net_salary": 0.0,
                    "total_tax_amount": 0.0,
                    "total_deductions": 0.0,
                    "status_breakdown": {
                        "computed": 0,
                        "approved": 0,
                        "paid": 0,
                        "rejected": 0
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Error getting monthly salary summary: {str(e)}")
            raise

    async def get_all_employees_for_period(
        self, 
        month: int, 
        year: int, 
        organisation_id: str
    ) -> List[str]:
        """Get all employee IDs for a period."""
        try:
            collection = await self._get_collection(organisation_id)
            cursor = collection.find(
                {"month": month, "year": year},
                {"employee_id": 1}
            )
            documents = await cursor.to_list(length=None)
            return [doc["employee_id"] for doc in documents]
            
        except Exception as e:
            self.logger.error(f"Error getting employee IDs for period: {str(e)}")
            raise

    async def bulk_save(
        self, 
        monthly_salaries: List[MonthlySalary], 
        organisation_id: str
    ) -> List[MonthlySalary]:
        """Bulk save monthly salary records."""
        try:
            collection = await self._get_collection(organisation_id)
            
            # Convert entities to documents
            documents = [self._convert_to_document(salary) for salary in monthly_salaries]
            
            # Add timestamps and version
            for doc in documents:
                doc["created_at"] = datetime.utcnow()
                doc["updated_at"] = datetime.utcnow()
                doc["version"] = 1
            
            # Insert documents
            result = await collection.insert_many(documents)
            
            if len(result.inserted_ids) != len(monthly_salaries):
                raise Exception("Failed to insert all monthly salary records")
            
            self.logger.info(f"Bulk saved {len(monthly_salaries)} monthly salary records")
            return monthly_salaries
            
        except Exception as e:
            self.logger.error(f"Error bulk saving monthly salary records: {str(e)}")
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
        """Update monthly salary status."""
        try:
            collection = await self._get_collection(organisation_id)
            
            # Build update document
            update_doc = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            if notes:
                update_doc["notes"] = notes
            if updated_by:
                update_doc["updated_by"] = updated_by
            
            result = await collection.update_one(
                {
                    "employee_id": str(employee_id),
                    "month": month,
                    "year": year
                },
                {"$set": update_doc}
            )
            
            if result.modified_count > 0:
                # Return updated record
                return await self.get_by_employee_and_period(employee_id, month, year, organisation_id)
            return None
            
        except Exception as e:
            self.logger.error(f"Error updating monthly salary status: {str(e)}")
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
        """Mark salary payment."""
        try:
            collection = await self._get_collection(organisation_id)
            
            # Build update document
            update_doc = {
                "updated_at": datetime.utcnow()
            }
            
            if payment_type == "salary":
                update_doc["salary_paid"] = True
                update_doc["status"] = "salary_paid"
            elif payment_type == "tds":
                update_doc["tds_paid"] = True
                update_doc["status"] = "tds_paid"
            elif payment_type == "both":
                update_doc["salary_paid"] = True
                update_doc["tds_paid"] = True
                update_doc["status"] = "paid"
            
            if payment_reference:
                update_doc["payment_reference"] = payment_reference
            if payment_notes:
                update_doc["payment_notes"] = payment_notes
            if paid_by:
                update_doc["updated_by"] = paid_by
            
            result = await collection.update_one(
                {
                    "employee_id": str(employee_id),
                    "month": month,
                    "year": year
                },
                {"$set": update_doc}
            )
            
            if result.modified_count > 0:
                # Return updated record
                return await self.get_by_employee_and_period(employee_id, month, year, organisation_id)
            return None
            
        except Exception as e:
            self.logger.error(f"Error marking salary payment: {str(e)}")
            raise

    async def delete(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int, 
        organisation_id: str
    ) -> bool:
        """Delete monthly salary record by employee and period."""
        try:
            collection = await self._get_collection(organisation_id)
            result = await collection.delete_one({
                "employee_id": str(employee_id),
                "month": month,
                "year": year
            })
            return result.deleted_count > 0
            
        except Exception as e:
            self.logger.error(f"Error deleting monthly salary record: {str(e)}")
            raise
    
    def _convert_to_document(self, monthly_salary: MonthlySalary) -> dict:
        """Convert MonthlySalary entity to MongoDB document."""
        return {
            "employee_id": str(monthly_salary.employee_id),
            "month": monthly_salary.month,
            "year": monthly_salary.year,
            "salary": self._serialize_salary_income(monthly_salary.salary),
            "perquisites": self._serialize_perquisites(monthly_salary.perquisites),
            "deductions": self._serialize_deductions(monthly_salary.deductions),
            "retirement": self._serialize_retirement_benefits(monthly_salary.retirement),
            "lwp": self._serialize_lwp_details(monthly_salary.lwp),
            "tax_year": str(monthly_salary.tax_year),
            "tax_regime": {
                "regime_type": monthly_salary.tax_regime.regime_type.value
            },
            "tax_amount": {
                "amount": str(monthly_salary.tax_amount.amount),
                "currency": monthly_salary.tax_amount.currency
            },
            "net_salary": {
                "amount": str(monthly_salary.net_salary.amount),
                "currency": monthly_salary.net_salary.currency
            }
        }
    
    def _convert_to_entity(self, document: dict) -> MonthlySalary:
        """Convert MongoDB document to MonthlySalary entity."""
        return MonthlySalary(
            employee_id=EmployeeId(document["employee_id"]),
            month=document["month"],
            year=document["year"],
            salary=self._deserialize_salary_income(document["salary"]),
            perquisites=self._deserialize_perquisites(document.get("perquisites")),
            deductions=self._deserialize_deductions(document["deductions"]),
            retirement=self._deserialize_retirement_benefits(document.get("retirement")),
            lwp=self._deserialize_lwp_details(document.get("lwp")),
            tax_year=TaxYear.from_string(document["tax_year"]),
            tax_regime=TaxRegime(TaxRegimeType(document["tax_regime"]["regime_type"])),
            tax_amount=Money(
                amount=Decimal(document["tax_amount"]["amount"]),
                currency=document["tax_amount"]["currency"]
            ),
            net_salary=Money(
                amount=Decimal(document["net_salary"]["amount"]),
                currency=document["net_salary"]["currency"]
            )
        )
    
    def _serialize_salary_income(self, salary_income: SalaryIncome) -> dict:
        """Serialize salary income to document format."""
        if not salary_income:
            return {}
        
        return {
            "basic_salary": {
                "amount": str(salary_income.basic_salary.amount),
                "currency": salary_income.basic_salary.currency
            },
            "dearness_allowance": {
                "amount": str(salary_income.dearness_allowance.amount),
                "currency": salary_income.dearness_allowance.currency
            },
            "hra_provided": {
                "amount": str(salary_income.hra_provided.amount),
                "currency": salary_income.hra_provided.currency
            },
            "special_allowance": {
                "amount": str(salary_income.special_allowance.amount),
                "currency": salary_income.special_allowance.currency
            },
            "bonus": {
                "amount": str(salary_income.bonus.amount),
                "currency": salary_income.bonus.currency
            },
            "commission": {
                "amount": str(salary_income.commission.amount),
                "currency": salary_income.commission.currency
            },
            "arrears": {
                "amount": str(salary_income.arrears.amount),
                "currency": salary_income.arrears.currency
            },
            "specific_allowances": self._serialize_specific_allowances(salary_income.specific_allowances) if salary_income.specific_allowances else None
        }
    
    def _deserialize_salary_income(self, document: dict) -> SalaryIncome:
        """Deserialize salary income from document format."""
        if not document:
            return SalaryIncome()
        
        return SalaryIncome(
            basic_salary=Money(
                amount=Decimal(document["basic_salary"]["amount"]),
                currency=document["basic_salary"]["currency"]
            ),
            dearness_allowance=Money(
                amount=Decimal(document["dearness_allowance"]["amount"]),
                currency=document["dearness_allowance"]["currency"]
            ),
            hra_provided=Money(
                amount=Decimal(document["hra_provided"]["amount"]),
                currency=document["hra_provided"]["currency"]
            ),
            special_allowance=Money(
                amount=Decimal(document["special_allowance"]["amount"]),
                currency=document["special_allowance"]["currency"]
            ),
            bonus=Money(
                amount=Decimal(document["bonus"]["amount"]),
                currency=document["bonus"]["currency"]
            ),
            commission=Money(
                amount=Decimal(document["commission"]["amount"]),
                currency=document["commission"]["currency"]
            ),
            arrears=Money(
                amount=Decimal(document["arrears"]["amount"]),
                currency=document["arrears"]["currency"]
            ),
            specific_allowances=self._deserialize_specific_allowances(document.get("specific_allowances")) if document.get("specific_allowances") else None
        )
    
    def _serialize_specific_allowances(self, specific_allowances: SpecificAllowances) -> dict:
        """Serialize specific allowances to document format."""
        if not specific_allowances:
            return {}
        
        # This is a simplified serialization - you may need to add more fields based on your SpecificAllowances structure
        return {
            "hills_allowance": {
                "amount": str(specific_allowances.hills_allowance.amount),
                "currency": specific_allowances.hills_allowance.currency
            } if specific_allowances.hills_allowance else None,
            # Add other specific allowances as needed
        }
    
    def _deserialize_specific_allowances(self, document: dict) -> SpecificAllowances:
        """Deserialize specific allowances from document format."""
        if not document:
            return SpecificAllowances()
        
        # This is a simplified deserialization - you may need to add more fields
        allowances = SpecificAllowances()
        if document.get("hills_allowance"):
            allowances.hills_allowance = Money(
                amount=Decimal(document["hills_allowance"]["amount"]),
                currency=document["hills_allowance"]["currency"]
            )
        # Add other specific allowances as needed
        
        return allowances
    
    def _serialize_perquisites(self, perquisites: Perquisites) -> dict:
        """Serialize perquisites to document format."""
        if not perquisites:
            return {}
        
        # Simplified serialization - you may need to add more fields based on your Perquisites structure
        return {
            "has_perquisites": True,
            # Add specific perquisite fields as needed
        }
    
    def _deserialize_perquisites(self, document: dict) -> Perquisites:
        """Deserialize perquisites from document format."""
        if not document:
            return Perquisites()
        
        # Simplified deserialization - you may need to add more fields
        return Perquisites()
    
    def _serialize_deductions(self, deductions: TaxDeductions) -> dict:
        """Serialize deductions to document format."""
        if not deductions:
            return {}
        
        # Simplified serialization - you may need to add more fields based on your TaxDeductions structure
        return {
            "has_deductions": True,
            # Add specific deduction fields as needed
        }
    
    def _deserialize_deductions(self, document: dict) -> TaxDeductions:
        """Deserialize deductions from document format."""
        if not document:
            return TaxDeductions()
        
        # Simplified deserialization - you may need to add more fields
        return TaxDeductions()
    
    def _serialize_retirement_benefits(self, retirement: RetirementBenefits) -> dict:
        """Serialize retirement benefits to document format."""
        if not retirement:
            return {}
        
        # Simplified serialization - you may need to add more fields based on your RetirementBenefits structure
        return {
            "has_retirement_benefits": True,
            # Add specific retirement benefit fields as needed
        }
    
    def _deserialize_retirement_benefits(self, document: dict) -> RetirementBenefits:
        """Deserialize retirement benefits from document format."""
        if not document:
            return RetirementBenefits()
        
        # Simplified deserialization - you may need to add more fields
        return RetirementBenefits()
    
    def _serialize_lwp_details(self, lwp: LWPDetails) -> dict:
        """Serialize LWP details to document format."""
        if not lwp:
            return {}
        
        # Simplified serialization - you may need to add more fields based on your LwpDetails structure
        return {
            "has_lwp": True,
            # Add specific LWP fields as needed
        }
    
    def _deserialize_lwp_details(self, document: dict) -> LWPDetails:
        """Deserialize LWP details from document format."""
        if not document:
            return LWPDetails()
        
        # Simplified deserialization - you may need to add more fields
        return LWPDetails() 