"""
Monthly Salary Repository Implementation
MongoDB implementation of monthly salary repository interfaces
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.application.interfaces.repositories.monthly_salary_repository import (
    MonthlySalaryRepository, MonthlySalaryQueryRepository
)
from app.application.dto.monthly_salary_dto import MonthlySalaryFilterDTO
from app.domain.entities.monthly_salary import MonthlySalary, ProcessingStatus
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.money import Money
from app.infrastructure.database.database_connector import DatabaseConnector
from app.config.mongodb_config import get_mongodb_connection_string, get_mongodb_client_options

logger = logging.getLogger(__name__)


class MongoDBMonthlySalaryRepository(MonthlySalaryRepository, MonthlySalaryQueryRepository):
    """MongoDB implementation of monthly salary repository."""
    
    def __init__(self, database_connector: DatabaseConnector):
        """
        Initialize repository with database connector.
        
        Args:
            database_connector: Database connector for MongoDB operations
        """
        self.db_connector = database_connector
        self._collection_name = "monthly_salary"
        self._logger = logging.getLogger(__name__)
        
        # Connection configuration (will be set by dependency container)
        self._connection_string = None
        self._client_options = None
    
    def set_connection_config(self, connection_string: str, client_options: Dict[str, Any]):
        """
        Set MongoDB connection configuration.
        
        Args:
            connection_string: MongoDB connection string
            client_options: MongoDB client options
        """
        self._connection_string = connection_string
        self._client_options = client_options
        
    async def _get_collection(self, organisation_id: str):
        """
        Get monthly salary collection for specific organisation.
        
        Ensures database connection is established in the correct event loop.
        """
        db_name = "pms_"+organisation_id
        
        # Ensure database is connected in the current event loop
        if not self.db_connector.is_connected:
            logger.info("Database not connected, establishing connection...")
            
            try:
                # Use stored connection configuration or fallback to config functions
                if self._connection_string and self._client_options:
                    logger.info("Using stored connection parameters from repository configuration")
                    connection_string = self._connection_string
                    options = self._client_options
                else:
                    # Fallback to config functions if connection config not set
                    logger.info("Loading connection parameters from mongodb_config")
                    connection_string = get_mongodb_connection_string()
                    options = get_mongodb_client_options()
                
                await self.db_connector.connect(connection_string, **options)
                logger.info("MongoDB connection established successfully in current event loop")
                
            except Exception as e:
                logger.error(f"Failed to establish database connection: {e}")
                raise RuntimeError(f"Database connection failed: {e}")
        
        # Verify connection and get collection
        try:
            db = self.db_connector.get_database(db_name)
            collection = db[self._collection_name]
            logger.info(f"Successfully retrieved collection: {self._collection_name} from database: {db_name}")
            return collection
            
        except Exception as e:
            logger.error(f"Failed to get collection {self._collection_name}: {e}")
            # Reset connection state to force reconnection on next call
            if hasattr(self.db_connector, '_client'):
                self.db_connector._client = None
            raise RuntimeError(f"Collection access failed: {e}")
    
    async def save(self, monthly_salary: MonthlySalary, hostname: str) -> MonthlySalary:
        """Save or update monthly salary record."""
        try:
            collection = await self._get_collection(hostname)
            
            # Convert entity to document
            document = self._entity_to_document(monthly_salary)
            
            # Upsert based on employee_id, month, year
            filter_query = {
                "employee_id": document["employee_id"],
                "month": document["month"],
                "year": document["year"]
            }
            
            # Update timestamps
            document["updated_at"] = datetime.utcnow()
            
            result = await collection.replace_one(
                filter_query,
                document,
                upsert=True
            )
            
            logger.info(f"Saved monthly salary for {monthly_salary.employee_id}, {monthly_salary.month}/{monthly_salary.year}")
            return monthly_salary
            
        except Exception as e:
            logger.error(f"Error saving monthly salary: {e}")
            raise
    
    async def get_by_employee_month_year(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int, 
        hostname: str
    ) -> Optional[MonthlySalary]:
        """Get monthly salary by employee, month, and year."""
        try:
            collection = await self._get_collection(hostname)
            
            document = await collection.find_one({
                "employee_id": str(employee_id),
                "month": month,
                "year": year
            })
            
            if document:
                return self._document_to_entity(document)
            return None
            
        except Exception as e:
            logger.error(f"Error getting monthly salary: {e}")
            raise
    
    async def get_by_employee_tax_year(
        self, 
        employee_id: EmployeeId, 
        tax_year: str, 
        hostname: str
    ) -> List[MonthlySalary]:
        """Get all monthly salaries for an employee in a tax year."""
        try:
            collection = await self._get_collection(hostname)
            
            cursor = collection.find({
                "employee_id": str(employee_id),
                "tax_year": tax_year
            }).sort("month", 1)
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting monthly salaries by tax year: {e}")
            raise
    
    async def get_by_month_year(
        self, 
        month: int, 
        year: int, 
        hostname: str,
        filters: Optional[MonthlySalaryFilterDTO] = None
    ) -> List[MonthlySalary]:
        """Get all monthly salaries for a specific month/year."""
        try:
            collection = await self._get_collection(hostname)
            
            # Build query
            query = {"month": month, "year": year}
            
            if filters:
                if filters.status:
                    query["status"] = filters.status
                if filters.tax_year:
                    query["tax_year"] = filters.tax_year
            
            # Apply pagination
            skip = filters.skip if filters else 0
            limit = filters.limit if filters else 50
            
            cursor = collection.find(query).skip(skip).limit(limit).sort("employee_id", 1)
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting monthly salaries by month/year: {e}")
            raise
    
    async def get_by_status(
        self, 
        status: str, 
        hostname: str,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> List[MonthlySalary]:
        """Get monthly salaries by status."""
        try:
            collection = await self._get_collection(hostname)
            
            query = {"status": status}
            if month:
                query["month"] = month
            if year:
                query["year"] = year
            
            cursor = collection.find(query).sort("updated_at", -1)
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting monthly salaries by status: {e}")
            raise
    
    async def get_summary_by_month_year(
        self, 
        month: int, 
        year: int, 
        hostname: str
    ) -> Dict[str, Any]:
        """Get summary statistics for a month/year."""
        try:
            collection = await self._get_collection(hostname)
            
            # Aggregation pipeline for summary
            pipeline = [
                {"$match": {"month": month, "year": year}},
                {
                    "$group": {
                        "_id": None,
                        "total_employees": {"$sum": 1},
                        "total_gross_payroll": {"$sum": "$gross_salary"},
                        "total_net_payroll": {"$sum": "$net_salary"},
                        "total_deductions": {"$sum": "$total_deductions"},
                        "total_tds": {"$sum": "$tds"},
                        "status_counts": {
                            "$push": "$status"
                        }
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=1)
            
            if result:
                summary = result[0]
                
                # Count by status
                status_counts = {}
                for status in summary["status_counts"]:
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                return {
                    "month": month,
                    "year": year,
                    "total_employees": summary["total_employees"],
                    "computed_count": status_counts.get("computed", 0),
                    "pending_count": status_counts.get("pending", 0),
                    "approved_count": status_counts.get("approved", 0),
                    "paid_count": status_counts.get("paid", 0),
                    "total_gross_payroll": summary["total_gross_payroll"],
                    "total_net_payroll": summary["total_net_payroll"],
                    "total_deductions": summary["total_deductions"],
                    "total_tds": summary["total_tds"],
                    "computation_completion_rate": (status_counts.get("computed", 0) / summary["total_employees"] * 100) if summary["total_employees"] > 0 else 0
                }
            
            return {
                "month": month,
                "year": year,
                "total_employees": 0,
                "computed_count": 0,
                "pending_count": 0,
                "approved_count": 0,
                "paid_count": 0,
                "total_gross_payroll": 0.0,
                "total_net_payroll": 0.0,
                "total_deductions": 0.0,
                "total_tds": 0.0,
                "computation_completion_rate": 0.0
            }
            
        except Exception as e:
            logger.error(f"Error getting summary: {e}")
            raise
    
    async def delete_by_employee_month_year(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int, 
        hostname: str
    ) -> bool:
        """Delete monthly salary record."""
        try:
            collection = await self._get_collection(hostname)
            
            result = await collection.delete_one({
                "employee_id": str(employee_id),
                "month": month,
                "year": year
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
        hostname: str
    ) -> bool:
        """Check if monthly salary record exists."""
        try:
            collection = await self._get_collection(hostname)
            
            count = await collection.count_documents({
                "employee_id": str(employee_id),
                "month": month,
                "year": year
            })
            
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking existence: {e}")
            raise
    
    async def count_by_filters(
        self, 
        filters: MonthlySalaryFilterDTO, 
        hostname: str
    ) -> int:
        """Count monthly salary records by filters."""
        try:
            collection = await self._get_collection(hostname)
            
            query = {}
            if filters.month:
                query["month"] = filters.month
            if filters.year:
                query["year"] = filters.year
            if filters.tax_year:
                query["tax_year"] = filters.tax_year
            if filters.status:
                query["status"] = filters.status
            
            return await collection.count_documents(query)
            
        except Exception as e:
            logger.error(f"Error counting records: {e}")
            raise
    
    async def get_employees_without_salary(
        self, 
        month: int, 
        year: int, 
        hostname: str
    ) -> List[str]:
        """Get list of employee IDs without monthly salary for given month/year."""
        try:
            # This would require joining with user collection
            # For now, return empty list - can be enhanced later
            return []
            
        except Exception as e:
            logger.error(f"Error getting employees without salary: {e}")
            raise
    
    # Query repository methods
    async def get_monthly_salary_with_employee_details(
        self, 
        employee_id: EmployeeId, 
        month: int, 
        year: int, 
        hostname: str
    ) -> Optional[Dict[str, Any]]:
        """Get monthly salary with employee details."""
        try:
            # This would require aggregation with user collection
            # For now, just return the monthly salary
            monthly_salary = await self.get_by_employee_month_year(employee_id, month, year, hostname)
            if monthly_salary:
                return self._entity_to_document(monthly_salary)
            return None
            
        except Exception as e:
            logger.error(f"Error getting monthly salary with employee details: {e}")
            raise
    
    async def get_payroll_summary_by_department(
        self, 
        month: int, 
        year: int, 
        hostname: str
    ) -> List[Dict[str, Any]]:
        """Get payroll summary grouped by department."""
        try:
            # This would require aggregation with user collection for department info
            # For now, return empty list - can be enhanced later
            return []
            
        except Exception as e:
            logger.error(f"Error getting payroll summary by department: {e}")
            raise
    
    async def get_monthly_salary_trends(
        self, 
        employee_id: EmployeeId, 
        months: int, 
        hostname: str
    ) -> List[Dict[str, Any]]:
        """Get monthly salary trends for an employee."""
        try:
            collection = await self._get_collection(hostname)
            
            cursor = collection.find({
                "employee_id": str(employee_id)
            }).sort("year", -1).sort("month", -1).limit(months)
            
            documents = await cursor.to_list(length=None)
            return documents
            
        except Exception as e:
            logger.error(f"Error getting salary trends: {e}")
            raise
    
    def _entity_to_document(self, entity: MonthlySalary) -> Dict[str, Any]:
        """Convert monthly salary entity to MongoDB document."""
        return {
            "employee_id": str(entity.employee_id),
            "month": entity.month,
            "year": entity.year,
            "tax_year": entity.tax_year,
            
            # Salary components
            "basic_salary": entity.basic_salary.to_float(),
            "da": entity.da.to_float(),
            "hra": entity.hra.to_float(),
            "special_allowance": entity.special_allowance.to_float(),
            "bonus": entity.bonus.to_float(),
            "commission": entity.commission.to_float(),
            "overtime": entity.overtime.to_float(),
            "arrears": entity.arrears.to_float(),
            
            # Deductions
            "epf_employee": entity.epf_employee.to_float(),
            "esi_employee": entity.esi_employee.to_float(),
            "professional_tax": entity.professional_tax.to_float(),
            "tds": entity.tds.to_float(),
            "advance_deduction": entity.advance_deduction.to_float(),
            "loan_deduction": entity.loan_deduction.to_float(),
            "other_deductions": entity.other_deductions.to_float(),
            
            # Calculated totals
            "gross_salary": entity.gross_salary.to_float(),
            "total_deductions": entity.total_deductions.to_float(),
            "net_salary": entity.net_salary.to_float(),
            
            # Annual projections
            "annual_gross_salary": entity.annual_gross_salary.to_float(),
            "annual_tax_liability": entity.annual_tax_liability.to_float(),
            
            # Tax details
            "tax_regime": entity.tax_regime,
            "tax_exemptions": entity.tax_exemptions.to_float(),
            "standard_deduction": entity.standard_deduction.to_float(),
            
            # Working days
            "total_days_in_month": entity.total_days_in_month,
            "working_days_in_period": entity.working_days_in_period,
            "lwp_days": entity.lwp_days,
            "effective_working_days": entity.effective_working_days,
            
            # Processing details
            "status": entity.status.value,
            "computation_date": entity.computation_date,
            "notes": entity.notes,
            "remarks": entity.remarks,
            
            # Audit fields
            "organization_id": entity.organization_id,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
            "created_by": entity.created_by,
            "updated_by": entity.updated_by
        }
    
    def _document_to_entity(self, document: Dict[str, Any]) -> MonthlySalary:
        """Convert MongoDB document to monthly salary entity."""
        return MonthlySalary(
            employee_id=EmployeeId(document["employee_id"]),
            month=document["month"],
            year=document["year"],
            tax_year=document["tax_year"],
            
            # Salary components
            basic_salary=Money.from_float(document.get("basic_salary", 0.0)),
            da=Money.from_float(document.get("da", 0.0)),
            hra=Money.from_float(document.get("hra", 0.0)),
            special_allowance=Money.from_float(document.get("special_allowance", 0.0)),
            bonus=Money.from_float(document.get("bonus", 0.0)),
            commission=Money.from_float(document.get("commission", 0.0)),
            overtime=Money.from_float(document.get("overtime", 0.0)),
            arrears=Money.from_float(document.get("arrears", 0.0)),
            
            # Deductions
            epf_employee=Money.from_float(document.get("epf_employee", 0.0)),
            esi_employee=Money.from_float(document.get("esi_employee", 0.0)),
            professional_tax=Money.from_float(document.get("professional_tax", 0.0)),
            tds=Money.from_float(document.get("tds", 0.0)),
            advance_deduction=Money.from_float(document.get("advance_deduction", 0.0)),
            loan_deduction=Money.from_float(document.get("loan_deduction", 0.0)),
            other_deductions=Money.from_float(document.get("other_deductions", 0.0)),
            
            # Calculated totals
            gross_salary=Money.from_float(document.get("gross_salary", 0.0)),
            total_deductions=Money.from_float(document.get("total_deductions", 0.0)),
            net_salary=Money.from_float(document.get("net_salary", 0.0)),
            
            # Annual projections
            annual_gross_salary=Money.from_float(document.get("annual_gross_salary", 0.0)),
            annual_tax_liability=Money.from_float(document.get("annual_tax_liability", 0.0)),
            
            # Tax details
            tax_regime=document.get("tax_regime", "new"),
            tax_exemptions=Money.from_float(document.get("tax_exemptions", 0.0)),
            standard_deduction=Money.from_float(document.get("standard_deduction", 0.0)),
            
            # Working days
            total_days_in_month=document.get("total_days_in_month", 30),
            working_days_in_period=document.get("working_days_in_period", 22),
            lwp_days=document.get("lwp_days", 0),
            effective_working_days=document.get("effective_working_days", 22),
            
            # Processing details
            status=ProcessingStatus(document.get("status", ProcessingStatus.NOT_COMPUTED)),
            computation_date=document.get("computation_date"),
            notes=document.get("notes"),
            remarks=document.get("remarks"),
            
            # Audit fields
            organization_id=document.get("organization_id", ""),
            created_at=document.get("created_at", datetime.utcnow()),
            updated_at=document.get("updated_at", datetime.utcnow()),
            created_by=document.get("created_by"),
            updated_by=document.get("updated_by")
        ) 