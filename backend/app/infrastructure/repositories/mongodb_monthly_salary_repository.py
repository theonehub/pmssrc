"""
MongoDB Monthly Salary Repository Implementation
MongoDB implementation of monthly salary repository interface
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from bson import ObjectId

from app.application.interfaces.repositories.monthly_salary_repository import (
    MonthlySalaryRepository
)
from app.domain.entities.monthly_salary import MonthlySalary
from app.infrastructure.database.database_connector import DatabaseConnector
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.tax_year import TaxYear
from app.domain.value_objects.tax_regime import TaxRegime
from app.domain.value_objects.money import Money
from app.domain.entities.taxation.salary_income import SalaryIncome, SpecificAllowances
from app.domain.entities.taxation.perquisites import (
    Perquisites, AccommodationPerquisite, CarPerquisite, LTAPerquisite,
    InterestFreeConcessionalLoan, ESOPPerquisite, UtilitiesPerquisite,
    FreeEducationPerquisite, LunchRefreshmentPerquisite, DomesticHelpPerquisite,
    MovableAssetUsage, MovableAssetTransfer, GiftVoucherPerquisite,
    MonetaryBenefitsPerquisite, ClubExpensesPerquisite, MonthlyPerquisitesPayouts,
    MonthlyPerquisitesComponents
)
from app.domain.entities.taxation.deductions import (
    TaxDeductions, DeductionSection80C, DeductionSection80CCC, DeductionSection80CCD,
    DeductionSection80D, DeductionSection80DD, DeductionSection80DDB,
    DeductionSection80E, DeductionSection80EEB, DeductionSection80G,
    DeductionSection80GGC, DeductionSection80U, DeductionSection80TTA_TTB,
    HRAExemption, OtherDeductions, RelationType, DisabilityPercentage
)
from app.domain.entities.taxation.retirement_benefits import (
    RetirementBenefits, LeaveEncashment, Gratuity, VRS, Pension, RetrenchmentCompensation
)
from app.domain.entities.taxation.lwp_details import LWPDetails
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MongoDBMonthlySalaryRepository(MonthlySalaryRepository):
    """
    MongoDB implementation of monthly salary repository.
    
    Follows SOLID principles and DDD patterns:
    - SRP: Only handles monthly salary persistence
    - OCP: Can be extended without modification
    - LSP: Substitutable for repository interface
    - ISP: Implements focused interfaces
    - DIP: Depends on DatabaseConnector abstraction
    """
    
    def __init__(self, database_connector: DatabaseConnector):
        """
        Initialize repository with database connector.
        
        Args:
            database_connector: Database connection abstraction
        """
        self.db_connector = database_connector
        self._collection_name = "salaries-computed"
        
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
    
    async def _get_collection(self, organisation_id: str = None):
        """
        Get monthly salary collection for specific organisation or global.
        
        Ensures database connection is established in the correct event loop.
        """
        
        db_name = organisation_id if organisation_id else "pms_global_database"
        logger.debug(f"_get_collection: Getting collection for db_name: {db_name}, organisation_id: {organisation_id}")
        
        # Ensure database is connected in the current event loop
        if not self.db_connector.is_connected:
            logger.debug("_get_collection: Database not connected, attempting to connect")
            try:
                # Use stored connection configuration or fallback to config functions
                if self._connection_string and self._client_options:
                    connection_string = self._connection_string
                    options = self._client_options
                    logger.debug("_get_collection: Using stored connection configuration")
                else:
                    # Fallback to config functions if connection config not set
                    logger.debug("_get_collection: Falling back to config functions for connection")
                    from app.config.mongodb_config import get_mongodb_connection_string, get_mongodb_client_options
                    connection_string = get_mongodb_connection_string()
                    options = get_mongodb_client_options()
                
                logger.debug(f"_get_collection: Connecting to database with connection_string length: {len(connection_string) if connection_string else 0}")
                await self.db_connector.connect(connection_string, **options)
                logger.debug("_get_collection: Database connection successful")
                
            except Exception as e:
                logger.error(f"_get_collection: Database connection failed: {e}", exc_info=True)
                raise RuntimeError(f"Database connection failed: {e}")
        else:
            logger.debug("_get_collection: Database already connected")
        
        # Get collection
        try:
            final_db_name = 'pms_'+db_name
            logger.debug(f"_get_collection: Getting database: {final_db_name}")
            db = self.db_connector.get_database(final_db_name)
            
            logger.debug(f"_get_collection: Getting collection: {self._collection_name}")
            collection = db[self._collection_name]
            
            logger.debug(f"_get_collection: Successfully got collection {self._collection_name} from database {final_db_name}")
            return collection
            
        except Exception as e:
            logger.error(f"_get_collection: Collection access failed: {e}", exc_info=True)
            raise RuntimeError(f"Collection access failed: {e}")
    
    async def save(self, monthly_salary: MonthlySalary, organization_id: str) -> MonthlySalary:
        """
        Save monthly salary to organisation-specific database.
        
        Args:
            monthly_salary: Monthly salary entity to save
            organization_id: Organization ID for database selection
            
        Returns:
            Saved monthly salary entity
        """
        try:
            # Get collection for organization
            collection = await self._get_collection(organization_id)
            
            # Convert entity to document
            document = self._entity_to_document(monthly_salary, organization_id)
            
            # Check if record already exists
            existing_filter = {
                "employee_id": str(monthly_salary.employee_id),
                "month": monthly_salary.month,
                "year": monthly_salary.year,
                "organization_id": organization_id
            }
            
            existing_doc = await collection.find_one(existing_filter)
            
            if existing_doc:
                # Update existing record
                document["updated_at"] = datetime.utcnow()
                document["version"] = existing_doc.get("version", 1) + 1
                
                result = await collection.replace_one(
                    {"_id": existing_doc["_id"]}, document
                )
                
                if result.modified_count == 0:
                    raise Exception("Failed to update monthly salary record")
                
                logger.info(f"Updated monthly salary for employee {monthly_salary.employee_id}, month {monthly_salary.month}/{monthly_salary.year}")
            else:
                # Insert new record
                document["created_at"] = datetime.utcnow()
                document["updated_at"] = datetime.utcnow()
                document["version"] = 1
                
                result = await collection.insert_one(document)
                
                if not result.inserted_id:
                    raise Exception("Failed to insert monthly salary record")
                
                logger.info(f"Created monthly salary for employee {monthly_salary.employee_id}, month {monthly_salary.month}/{monthly_salary.year}")
            
            # Return the saved entity
            return monthly_salary
            
        except Exception as e:
            logger.error(f"Error saving monthly salary: {str(e)}")
            raise
    
    async def save_batch(self, monthly_salaries: List[MonthlySalary], organization_id: str) -> List[MonthlySalary]:
        """
        Save multiple monthly salaries in a batch operation.
        
        Args:
            monthly_salaries: List of monthly salary entities to save
            organization_id: Organization ID for database selection
            
        Returns:
            List of saved monthly salary entities
        """
        try:
            # Get collection for organization
            collection = await self._get_collection(organization_id)
            
            # Convert entities to documents
            documents = []
            for monthly_salary in monthly_salaries:
                document = self._entity_to_document(monthly_salary, organization_id)
                document["created_at"] = datetime.utcnow()
                document["updated_at"] = datetime.utcnow()
                document["version"] = 1
                documents.append(document)
            
            # Insert documents in batch
            if documents:
                result = await collection.insert_many(documents)
                
                if len(result.inserted_ids) != len(documents):
                    raise Exception("Batch insert failed - not all documents were inserted")
                
                logger.info(f"Batch saved {len(documents)} monthly salary records")
            
            return monthly_salaries
            
        except Exception as e:
            logger.error(f"Error in batch save: {str(e)}")
            raise
    
    async def update(self, monthly_salary: MonthlySalary, organization_id: str) -> MonthlySalary:
        """
        Update existing monthly salary.
        
        Args:
            monthly_salary: Monthly salary entity to update
            organization_id: Organization ID for database selection
            
        Returns:
            Updated monthly salary entity
        """
        try:
            # Get collection for organization
            collection = await self._get_collection(organization_id)
            
            # Convert entity to document
            document = self._entity_to_document(monthly_salary, organization_id)
            document["updated_at"] = datetime.utcnow()
            
            # Update filter
            update_filter = {
                "employee_id": str(monthly_salary.employee_id),
                "month": monthly_salary.month,
                "year": monthly_salary.year,
                "organization_id": organization_id
            }
            
            # Update document
            result = await collection.update_one(
                update_filter,
                {"$set": document, "$inc": {"version": 1}}
            )
            
            if result.modified_count == 0:
                raise Exception("Failed to update monthly salary record")
            
            logger.info(f"Updated monthly salary for employee {monthly_salary.employee_id}, month {monthly_salary.month}/{monthly_salary.year}")
            
            return monthly_salary
            
        except Exception as e:
            logger.error(f"Error updating monthly salary: {str(e)}")
            raise
    
    async def delete(self, employee_id: str, month: int, year: int, organization_id: str) -> bool:
        """
        Delete monthly salary record.
        
        Args:
            employee_id: Employee ID
            month: Month number
            year: Year
            organization_id: Organization ID for database selection
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Get collection for organization
            collection = await self._get_collection(organization_id)
            
            # Delete filter
            delete_filter = {
                "employee_id": employee_id,
                "month": month,
                "year": year,
                "organization_id": organization_id
            }
            
            result = await collection.delete_one(delete_filter)
            
            if result.deleted_count > 0:
                logger.info(f"Deleted monthly salary for employee {employee_id}, month {month}/{year}")
                return True
            else:
                logger.warning(f"No monthly salary found to delete for employee {employee_id}, month {month}/{year}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting monthly salary: {str(e)}")
            raise
    
    async def get_by_employee_month_year(
        self, 
        employee_id: str, 
        month: int, 
        year: int, 
        organization_id: str
    ) -> Optional[MonthlySalary]:
        """
        Get monthly salary by employee, month, and year.
        
        Args:
            employee_id: Employee ID
            month: Month number
            year: Year
            organization_id: Organization ID for database selection
            
        Returns:
            Monthly salary entity if found, None otherwise
        """
        try:
            # Get collection for organization
            collection = await self._get_collection(organization_id)
            
            # Query filter
            query_filter = {
                "employee_id": employee_id,
                "month": month,
                "year": year,
                "organization_id": organization_id
            }
            
            document = await collection.find_one(query_filter)
            
            if document:
                return self._document_to_entity(document)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting monthly salary: {str(e)}")
            raise
    
    async def get_by_employee(
        self, 
        employee_id: str, 
        organization_id: str,
        limit: int = 12,
        offset: int = 0
    ) -> List[MonthlySalary]:
        """
        Get monthly salaries for an employee.
        
        Args:
            employee_id: Employee ID
            organization_id: Organization ID for database selection
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of monthly salary entities
        """
        try:
            # Get collection for organization
            collection = await self._get_collection(organization_id)
            
            # Query filter
            query_filter = {
                "employee_id": employee_id,
                "organization_id": organization_id
            }
            
            # Sort by year and month (descending)
            cursor = collection.find(query_filter).sort([
                ("year", -1), ("month", -1)
            ]).skip(offset).limit(limit)
            
            documents = await cursor.to_list(length=limit)
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting employee monthly salaries: {str(e)}")
            raise
    
    async def get_by_month_year(
        self, 
        month: int, 
        year: int, 
        organization_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[MonthlySalary]:
        """
        Get all monthly salaries for a specific month and year.
        
        Args:
            month: Month number
            year: Year
            organization_id: Organization ID for database selection
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of monthly salary entities
        """
        try:
            # Get collection for organization
            collection = await self._get_collection(organization_id)
            
            # Query filter
            query_filter = {
                "month": month,
                "year": year,
                "organization_id": organization_id
            }
            
            cursor = collection.find(query_filter).skip(offset).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting monthly salaries by month/year: {str(e)}")
            raise
    
    async def get_by_tax_year(
        self, 
        tax_year: str, 
        organization_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[MonthlySalary]:
        """
        Get all monthly salaries for a specific tax year.
        
        Args:
            tax_year: Tax year string (e.g., "2024-25")
            organization_id: Organization ID for database selection
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of monthly salary entities
        """
        try:
            # Get collection for organization
            collection = await self._get_collection(organization_id)
            
            # Query filter
            query_filter = {
                "tax_year": tax_year,
                "organization_id": organization_id
            }
            
            cursor = collection.find(query_filter).skip(offset).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting monthly salaries by tax year: {str(e)}")
            raise
    
    async def get_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        organization_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[MonthlySalary]:
        """
        Get monthly salaries within a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            organization_id: Organization ID for database selection
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of monthly salary entities
        """
        try:
            # Get collection for organization
            collection = await self._get_collection(organization_id)
            
            # Query filter for date range
            query_filter = {
                "organization_id": organization_id,
                "$or": [
                    {
                        "year": {"$gte": start_date.year, "$lte": end_date.year},
                        "month": {"$gte": start_date.month if start_date.year == end_date.year else 1}
                    },
                    {
                        "year": {"$gte": start_date.year, "$lte": end_date.year},
                        "month": {"$lte": end_date.month if start_date.year == end_date.year else 12}
                    }
                ]
            }
            
            cursor = collection.find(query_filter).skip(offset).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting monthly salaries by date range: {str(e)}")
            raise
    
    async def get_monthly_salaries_for_period(
        self,
        month: int,
        year: int,
        organization_id: str,
        status: Optional[str] = None,
        department: Optional[str] = None,
        employee_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[MonthlySalary]:
        """
        Get monthly salaries for a period with optional filters.
        
        Args:
            month: Month number
            year: Year
            organization_id: Organization ID for database selection
            status: Optional status filter
            department: Optional department filter
            employee_id: Optional employee ID filter
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of monthly salary entities
        """
        try:
            # Get collection for organization
            collection = await self._get_collection(organization_id)
            
            # Build query filter
            query_filter = {
                "month": month,
                "year": year,
                "organization_id": organization_id
            }
            
            # Add optional filters
            if employee_id:
                query_filter["employee_id"] = employee_id
            
            if status:
                query_filter["status"] = status
            
            # Note: Department filtering would require joining with user data
            # For now, we'll return all records and let the caller filter by department
            
            cursor = collection.find(query_filter).skip(offset).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            monthly_salaries = [self._document_to_entity(doc) for doc in documents]
            
            # Apply department filter if provided (this would ideally be done at DB level)
            if department:
                # This is a simplified approach - in a real implementation,
                # you'd want to join with user data at the database level
                filtered_salaries = []
                for salary in monthly_salaries:
                    # For now, we'll skip department filtering as it requires user data
                    # The export controller should handle this filtering
                    filtered_salaries.append(salary)
                return filtered_salaries
            
            return monthly_salaries
            
        except Exception as e:
            logger.error(f"Error getting monthly salaries for period: {str(e)}")
            raise
    
    async def exists(
        self, 
        employee_id: str, 
        month: int, 
        year: int, 
        organization_id: str
    ) -> bool:
        """
        Check if monthly salary exists for employee, month, and year.
        
        Args:
            employee_id: Employee ID
            month: Month number
            year: Year
            organization_id: Organization ID for database selection
            
        Returns:
            True if exists, False otherwise
        """
        try:
            # Get collection for organization
            collection = await self._get_collection(organization_id)
            
            # Query filter
            query_filter = {
                "employee_id": employee_id,
                "month": month,
                "year": year,
                "organization_id": organization_id
            }
            
            count = await collection.count_documents(query_filter)
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking monthly salary existence: {str(e)}")
            raise
    
    async def get_monthly_summary(
        self, 
        month: int, 
        year: int, 
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Get monthly salary summary for a specific month and year.
        
        Args:
            month: Month number
            year: Year
            organization_id: Organization ID for database selection
            
        Returns:
            Dictionary containing summary statistics
        """
        try:
            # Get collection for organization
            collection = await self._get_collection(organization_id)
            
            # Query filter
            query_filter = {
                "month": month,
                "year": year,
                "organization_id": organization_id
            }
            
            # Aggregate pipeline for summary
            pipeline = [
                {"$match": query_filter},
                {"$group": {
                    "_id": None,
                    "total_employees": {"$sum": 1},
                    "total_gross_salary": {"$sum": "$salary.gross_salary"},
                    "total_net_salary": {"$sum": "$net_salary"},
                    "total_tax_amount": {"$sum": "$tax_amount"},
                    "avg_gross_salary": {"$avg": "$salary.gross_salary"},
                    "avg_net_salary": {"$avg": "$net_salary"}
                }}
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=1)
            
            if result:
                summary = result[0]
                return {
                    "month": month,
                    "year": year,
                    "total_employees": summary["total_employees"],
                    "total_gross_salary": summary["total_gross_salary"],
                    "total_net_salary": summary["total_net_salary"],
                    "total_tax_amount": summary["total_tax_amount"],
                    "avg_gross_salary": summary["avg_gross_salary"],
                    "avg_net_salary": summary["avg_net_salary"]
                }
            else:
                return {
                    "month": month,
                    "year": year,
                    "total_employees": 0,
                    "total_gross_salary": 0,
                    "total_net_salary": 0,
                    "total_tax_amount": 0,
                    "avg_gross_salary": 0,
                    "avg_net_salary": 0
                }
                
        except Exception as e:
            logger.error(f"Error getting monthly summary: {str(e)}")
            raise
    
    async def get_employee_salary_history(
        self, 
        employee_id: str, 
        organization_id: str,
        months: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Get salary history for an employee.
        
        Args:
            employee_id: Employee ID
            organization_id: Organization ID for database selection
            months: Number of months to retrieve
            
        Returns:
            List of salary history records
        """
        try:
            # Get collection for organization
            collection = await self._get_collection(organization_id)
            
            # Query filter
            query_filter = {
                "employee_id": employee_id,
                "organization_id": organization_id
            }
            
            # Sort by year and month (descending) and limit
            cursor = collection.find(query_filter).sort([
                ("year", -1), ("month", -1)
            ]).limit(months)
            
            documents = await cursor.to_list(length=months)
            
            # Convert to history format
            history = []
            for doc in documents:
                history.append({
                    "month": doc["month"],
                    "year": doc["year"],
                    "gross_salary": doc["salary"]["gross_salary"],
                    "net_salary": doc["net_salary"],
                    "tax_amount": doc["tax_amount"],
                    "created_at": doc.get("created_at")
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting employee salary history: {str(e)}")
            raise
    
    async def get_payroll_summary(
        self, 
        organization_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get payroll summary for a date range.
        
        Args:
            organization_id: Organization ID for database selection
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary containing payroll summary
        """
        try:
            # Get collection for organization
            collection = await self._get_collection(organization_id)
            
            # Query filter for date range
            query_filter = {
                "organization_id": organization_id,
                "$or": [
                    {
                        "year": {"$gte": start_date.year, "$lte": end_date.year},
                        "month": {"$gte": start_date.month if start_date.year == end_date.year else 1}
                    },
                    {
                        "year": {"$gte": start_date.year, "$lte": end_date.year},
                        "month": {"$lte": end_date.month if start_date.year == end_date.year else 12}
                    }
                ]
            }
            
            # Aggregate pipeline for payroll summary
            pipeline = [
                {"$match": query_filter},
                {"$group": {
                    "_id": None,
                    "total_employees": {"$sum": 1},
                    "total_gross_payroll": {"$sum": "$salary.gross_salary"},
                    "total_net_payroll": {"$sum": "$net_salary"},
                    "total_tax_liability": {"$sum": "$tax_amount"},
                    "avg_gross_salary": {"$avg": "$salary.gross_salary"},
                    "avg_net_salary": {"$avg": "$net_salary"}
                }}
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=1)
            
            if result:
                summary = result[0]
                return {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "total_employees": summary["total_employees"],
                    "total_gross_payroll": summary["total_gross_payroll"],
                    "total_net_payroll": summary["total_net_payroll"],
                    "total_tax_liability": summary["total_tax_liability"],
                    "avg_gross_salary": summary["avg_gross_salary"],
                    "avg_net_salary": summary["avg_net_salary"]
                }
            else:
                return {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "total_employees": 0,
                    "total_gross_payroll": 0,
                    "total_net_payroll": 0,
                    "total_tax_liability": 0,
                    "avg_gross_salary": 0,
                    "avg_net_salary": 0
                }
                
        except Exception as e:
            logger.error(f"Error getting payroll summary: {str(e)}")
            raise
    
    def _entity_to_document(self, monthly_salary: MonthlySalary, organization_id: str) -> Dict[str, Any]:
        """
        Convert MonthlySalary entity to MongoDB document with comprehensive serialization.
        
        Args:
            monthly_salary: Monthly salary entity
            organization_id: Organization ID
            
        Returns:
            MongoDB document with all components fully serialized
        """
        return {
            "employee_id": str(monthly_salary.employee_id),
            "month": monthly_salary.month,
            "year": monthly_salary.year,
            "tax_year": str(monthly_salary.tax_year),
            "tax_regime": monthly_salary.tax_regime.regime_type.value,
            "organization_id": organization_id,
            
            # Comprehensive salary components
            "salary": self._serialize_salary_income(monthly_salary.salary) if monthly_salary.salary else None,
            
            # Comprehensive perquisites payouts
            "perquisites_payouts": self._serialize_perquisites_payouts(monthly_salary.perquisites_payouts) if monthly_salary.perquisites_payouts else None,
            
            # Comprehensive deductions
            "deductions": self._serialize_deductions(monthly_salary.deductions) if monthly_salary.deductions else None,
            
            # Comprehensive retirement benefits
            "retirement": self._serialize_retirement_benefits(monthly_salary.retirement) if monthly_salary.retirement else None,
            
            # LWP details
            "lwp": self._serialize_lwp_details(monthly_salary.lwp) if monthly_salary.lwp else None,
            
            # Tax and net salary
            "tax_amount": monthly_salary.tax_amount.to_float(),
            "net_salary": monthly_salary.net_salary.to_float(),
            
            # Metadata
            "computed_at": datetime.utcnow().isoformat(),
            "status": "computed"
        }
    
    def _document_to_entity(self, document: Dict[str, Any]) -> MonthlySalary:
        """
        Convert MongoDB document to MonthlySalary entity with comprehensive deserialization.
        
        Args:
            document: MongoDB document
            
        Returns:
            Monthly salary entity with all components fully deserialized
        """
        # Reconstruct salary income with all components
        salary_income = self._deserialize_salary_income(document.get("salary", {}))
        
        # Reconstruct perquisites payouts with all components
        perquisites_payouts = self._deserialize_perquisites_payouts(document.get("perquisites_payouts", {}))
        
        # Reconstruct deductions with all components
        deductions = self._deserialize_deductions(document.get("deductions", {}))
        
        # Reconstruct retirement benefits with all components
        retirement = self._deserialize_retirement_benefits(document.get("retirement", {}))
        
        # Reconstruct LWP details
        lwp = self._deserialize_lwp_details(document.get("lwp", {}))
        
        # Create entity
        return MonthlySalary(
            employee_id=EmployeeId(document["employee_id"]),
            month=document["month"],
            year=document["year"],
            salary=salary_income,
            perquisites_payouts=perquisites_payouts,
            deductions=deductions,
            retirement=retirement,
            lwp=lwp,
            tax_year=TaxYear.from_string(document["tax_year"]),
            tax_regime=TaxRegime(document["tax_regime"]),
            tax_amount=Money.from_float(document["tax_amount"]),
            net_salary=Money.from_float(document["net_salary"])
        )
    
    # =============================================================================
    # SERIALIZATION METHODS
    # =============================================================================
    
    def _serialize_salary_income(self, salary_income: SalaryIncome) -> Dict[str, Any]:
        """Serialize SalaryIncome with all components including SpecificAllowances."""
        if salary_income is None:
            return None
        return {
            "basic_salary": salary_income.basic_salary.to_float(),
            "dearness_allowance": salary_income.dearness_allowance.to_float(),
            "hra_provided": salary_income.hra_provided.to_float(),
            "pf_employee_contribution": salary_income.pf_employee_contribution.to_float(),
            "pf_employer_contribution": salary_income.pf_employer_contribution.to_float(),
            "esi_contribution": salary_income.esi_contribution.to_float(),
            "pf_voluntary_contribution": salary_income.pf_voluntary_contribution.to_float(),
            "pf_total_contribution": salary_income.pf_total_contribution.to_float(),
            "special_allowance": salary_income.special_allowance.to_float(),
            "bonus": salary_income.bonus.to_float(),
            "commission": salary_income.commission.to_float(),
            "arrears": salary_income.arrears.to_float(),
            "effective_from": salary_income.effective_from.isoformat() if salary_income.effective_from else None,
            "effective_till": salary_income.effective_till.isoformat() if salary_income.effective_till else None,
            "gross_salary": salary_income.calculate_gross_salary().to_float(),
            "specific_allowances": self._serialize_specific_allowances(salary_income.specific_allowances) if salary_income.specific_allowances else None
        }
    
    def _serialize_specific_allowances(self, specific_allowances: SpecificAllowances) -> Dict[str, Any]:
        """Serialize SpecificAllowances with all fields."""
        if specific_allowances is None:
            return None
        return {
            # Hills/High Altitude Allowances
            "monthly_hills_allowance": specific_allowances.monthly_hills_allowance.to_float(),
            "monthly_hills_exemption_limit": specific_allowances.monthly_hills_exemption_limit.to_float(),
            
            # Border/Remote Area Allowance
            "monthly_border_allowance": specific_allowances.monthly_border_allowance.to_float(),
            "monthly_border_exemption_limit": specific_allowances.monthly_border_exemption_limit.to_float(),
            
            # Transport Employee Allowance
            "transport_employee_allowance": specific_allowances.transport_employee_allowance.to_float(),
            
            # Children Allowances
            "children_education_allowance": specific_allowances.children_education_allowance.to_float(),
            "children_education_count": specific_allowances.children_education_count,
            "hostel_allowance": specific_allowances.hostel_allowance.to_float(),
            "children_hostel_count": specific_allowances.children_hostel_count,
            
            # Disabled Transport Allowance
            "disabled_transport_allowance": specific_allowances.disabled_transport_allowance.to_float(),
            "is_disabled": specific_allowances.is_disabled,
            
            # Underground Mines Allowance
            "underground_mines_allowance": specific_allowances.underground_mines_allowance.to_float(),
            "mine_work_months": specific_allowances.mine_work_months,
            
            # Government Employee Entertainment
            "government_entertainment_allowance": specific_allowances.government_entertainment_allowance.to_float(),
            
            # Additional allowances
            "city_compensatory_allowance": specific_allowances.city_compensatory_allowance.to_float(),
            "rural_allowance": specific_allowances.rural_allowance.to_float(),
            "proctorship_allowance": specific_allowances.proctorship_allowance.to_float(),
            "wardenship_allowance": specific_allowances.wardenship_allowance.to_float(),
            "project_allowance": specific_allowances.project_allowance.to_float(),
            "deputation_allowance": specific_allowances.deputation_allowance.to_float(),
            "overtime_allowance": specific_allowances.overtime_allowance.to_float(),
            "interim_relief": specific_allowances.interim_relief.to_float(),
            "tiffin_allowance": specific_allowances.tiffin_allowance.to_float(),
            "fixed_medical_allowance": specific_allowances.fixed_medical_allowance.to_float(),
            "servant_allowance": specific_allowances.servant_allowance.to_float(),
            "any_other_allowance": specific_allowances.any_other_allowance.to_float(),
            "any_other_allowance_exemption": specific_allowances.any_other_allowance_exemption.to_float(),
            
            # Section 10 exempted allowances
            "govt_employees_outside_india_allowance": specific_allowances.govt_employees_outside_india_allowance.to_float(),
            "supreme_high_court_judges_allowance": specific_allowances.supreme_high_court_judges_allowance.to_float(),
            "judge_compensatory_allowance": specific_allowances.judge_compensatory_allowance.to_float(),
            "section_10_14_special_allowances": specific_allowances.section_10_14_special_allowances.to_float(),
            "travel_on_tour_allowance": specific_allowances.travel_on_tour_allowance.to_float(),
            "tour_daily_charge_allowance": specific_allowances.tour_daily_charge_allowance.to_float(),
            "conveyance_in_performace_of_duties": specific_allowances.conveyance_in_performace_of_duties.to_float(),
            "helper_in_performace_of_duties": specific_allowances.helper_in_performace_of_duties.to_float(),
            "academic_research": specific_allowances.academic_research.to_float(),
            "uniform_allowance": specific_allowances.uniform_allowance.to_float(),
            
            # Alias fields for backward compatibility
            "hills_allowance": specific_allowances.hills_allowance.to_float(),
            "border_allowance": specific_allowances.border_allowance.to_float(),
            "hills_exemption_limit": specific_allowances.hills_exemption_limit.to_float(),
            "border_exemption_limit": specific_allowances.border_exemption_limit.to_float(),
            "children_count": specific_allowances.children_count
        }
    
    def _serialize_perquisites_payouts(self, perquisites_payouts: MonthlyPerquisitesPayouts) -> Dict[str, Any]:
        """Serialize MonthlyPerquisitesPayouts with all components."""
        if perquisites_payouts is None:
            return None
        return {
            "components": [
                {
                    "key": component.key,
                    "display_name": component.display_name,
                    "value": component.value.to_float()
                }
                for component in perquisites_payouts.components
            ],
            "total": perquisites_payouts.total.to_float()
        }

    def _serialize_perquisites(self, perquisites: Perquisites) -> Dict[str, Any]:
        """Serialize Perquisites with all components."""
        if perquisites is None:
            return None
        return {
            "accommodation": self._serialize_accommodation_perquisite(perquisites.accommodation),
            "car": self._serialize_car_perquisite(perquisites.car),
            "lta": self._serialize_lta_perquisite(perquisites.lta),
            "interest_free_loan": self._serialize_interest_free_loan(perquisites.interest_free_loan),
            "esop": self._serialize_esop_perquisite(perquisites.esop),
            "utilities": self._serialize_utilities_perquisite(perquisites.utilities),
            "free_education": self._serialize_free_education_perquisite(perquisites.free_education),
            "lunch_refreshment": self._serialize_lunch_refreshment_perquisite(perquisites.lunch_refreshment),
            "domestic_help": self._serialize_domestic_help_perquisite(perquisites.domestic_help),
            "movable_asset_usage": self._serialize_movable_asset_usage(perquisites.movable_asset_usage),
            "movable_asset_transfer": self._serialize_movable_asset_transfer(perquisites.movable_asset_transfer),
            "gift_voucher": self._serialize_gift_voucher_perquisite(perquisites.gift_voucher),
            "monetary_benefits": self._serialize_monetary_benefits_perquisite(perquisites.monetary_benefits),
            "club_expenses": self._serialize_club_expenses_perquisite(perquisites.club_expenses)
        }
    
    def _serialize_accommodation_perquisite(self, accommodation: Optional[AccommodationPerquisite]) -> Dict[str, Any]:
        """Serialize AccommodationPerquisite."""
        if not accommodation:
            return {"has_accommodation": False}
        
        return {
            "has_accommodation": True,
            "accommodation_type": accommodation.accommodation_type.value,
            "city_population": accommodation.city_population.value,
            "license_fees": accommodation.license_fees.to_float(),
            "employee_rent_payment": accommodation.employee_rent_payment.to_float(),
            "rent_paid_by_employer": accommodation.rent_paid_by_employer.to_float(),
            "hotel_charges": accommodation.hotel_charges.to_float(),
            "stay_days": accommodation.stay_days,
            "furniture_cost": accommodation.furniture_cost.to_float(),
            "furniture_employee_payment": accommodation.furniture_employee_payment.to_float(),
            "is_furniture_owned_by_employer": accommodation.is_furniture_owned_by_employer
        }
    
    def _serialize_car_perquisite(self, car: Optional[CarPerquisite]) -> Dict[str, Any]:
        """Serialize CarPerquisite."""
        if not car:
            return {"has_car": False}
        
        return {
            "has_car": True,
            "car_use_type": car.car_use_type.value,
            "engine_capacity_cc": car.engine_capacity_cc,
            "months_used": car.months_used,
            "months_used_other_vehicle": car.months_used_other_vehicle,
            "car_cost_to_employer": car.car_cost_to_employer.to_float(),
            "other_vehicle_cost": car.other_vehicle_cost.to_float(),
            "has_expense_reimbursement": car.has_expense_reimbursement,
            "driver_provided": car.driver_provided
        }
    
    def _serialize_lta_perquisite(self, lta: Optional[LTAPerquisite]) -> Dict[str, Any]:
        """Serialize LTAPerquisite."""
        if not lta:
            return {"has_lta": False}
        
        return {
            "has_lta": True,
            "lta_amount_claimed": lta.lta_amount_claimed.to_float(),
            "lta_claimed_count": lta.lta_claimed_count,
            "public_transport_cost": lta.public_transport_cost.to_float(),
            "travel_mode": lta.travel_mode,
            "is_monthly_paid": lta.is_monthly_paid
        }
    
    def _serialize_interest_free_loan(self, loan: Optional[InterestFreeConcessionalLoan]) -> Dict[str, Any]:
        """Serialize InterestFreeConcessionalLoan."""
        if not loan:
            return {"has_loan": False}
        
        return {
            "has_loan": True,
            "loan_amount": loan.loan_amount.to_float(),
            "emi_amount": loan.emi_amount.to_float(),
            "company_interest_rate": loan.company_interest_rate.to_float(),
            "sbi_interest_rate": loan.sbi_interest_rate.to_float(),
            "loan_type": loan.loan_type,
            "loan_start_date": loan.loan_start_date.isoformat() if loan.loan_start_date else None
        }
    
    def _serialize_esop_perquisite(self, esop: Optional[ESOPPerquisite]) -> Dict[str, Any]:
        """Serialize ESOPPerquisite."""
        if not esop:
            return {"has_esop": False}
        
        return {
            "has_esop": True,
            "shares_exercised": esop.shares_exercised,
            "exercise_price": esop.exercise_price.to_float(),
            "allotment_price": esop.allotment_price.to_float()
        }
    
    def _serialize_utilities_perquisite(self, utilities: Optional[UtilitiesPerquisite]) -> Dict[str, Any]:
        """Serialize UtilitiesPerquisite."""
        if not utilities:
            return {"has_utilities": False}
        
        return {
            "has_utilities": True,
            "gas_paid_by_employer": utilities.gas_paid_by_employer.to_float(),
            "electricity_paid_by_employer": utilities.electricity_paid_by_employer.to_float(),
            "water_paid_by_employer": utilities.water_paid_by_employer.to_float(),
            "gas_paid_by_employee": utilities.gas_paid_by_employee.to_float(),
            "electricity_paid_by_employee": utilities.electricity_paid_by_employee.to_float(),
            "water_paid_by_employee": utilities.water_paid_by_employee.to_float(),
            "is_gas_manufactured_by_employer": utilities.is_gas_manufactured_by_employer,
            "is_electricity_manufactured_by_employer": utilities.is_electricity_manufactured_by_employer,
            "is_water_manufactured_by_employer": utilities.is_water_manufactured_by_employer
        }
    
    def _serialize_free_education_perquisite(self, education: Optional[FreeEducationPerquisite]) -> Dict[str, Any]:
        """Serialize FreeEducationPerquisite."""
        if not education:
            return {"has_free_education": False}
        
        return {
            "has_free_education": True,
            "monthly_expenses_child1": education.monthly_expenses_child1.to_float(),
            "monthly_expenses_child2": education.monthly_expenses_child2.to_float(),
            "months_child1": education.months_child1,
            "months_child2": education.months_child2,
            "employer_maintained_1st_child": education.employer_maintained_1st_child,
            "employer_maintained_2nd_child": education.employer_maintained_2nd_child
        }
    
    def _serialize_lunch_refreshment_perquisite(self, lunch: Optional[LunchRefreshmentPerquisite]) -> Dict[str, Any]:
        """Serialize LunchRefreshmentPerquisite."""
        if not lunch:
            return {"has_lunch_refreshment": False}
        
        return {
            "has_lunch_refreshment": True,
            "lunch_employer_cost": lunch.lunch_employer_cost.to_float(),
            "lunch_employee_payment": lunch.lunch_employee_payment.to_float(),
            "lunch_meal_days_per_year": lunch.lunch_meal_days_per_year
        }
    
    def _serialize_domestic_help_perquisite(self, domestic_help: Optional[DomesticHelpPerquisite]) -> Dict[str, Any]:
        """Serialize DomesticHelpPerquisite."""
        if not domestic_help:
            return {"has_domestic_help": False}
        
        return {
            "has_domestic_help": True,
            "domestic_help_paid_by_employer": domestic_help.domestic_help_paid_by_employer.to_float(),
            "domestic_help_paid_by_employee": domestic_help.domestic_help_paid_by_employee.to_float()
        }
    
    def _serialize_movable_asset_usage(self, asset_usage: Optional[MovableAssetUsage]) -> Dict[str, Any]:
        """Serialize MovableAssetUsage."""
        if not asset_usage:
            return {"has_movable_asset_usage": False}
        
        return {
            "has_movable_asset_usage": True,
            "movable_asset_type": asset_usage.movable_asset_type,
            "movable_asset_usage_value": asset_usage.movable_asset_usage_value.to_float(),
            "movable_asset_hire_cost": asset_usage.movable_asset_hire_cost.to_float(),
            "movable_asset_employee_payment": asset_usage.movable_asset_employee_payment.to_float(),
            "movable_asset_is_employer_owned": asset_usage.movable_asset_is_employer_owned
        }
    
    def _serialize_movable_asset_transfer(self, asset_transfer: Optional[MovableAssetTransfer]) -> Dict[str, Any]:
        """Serialize MovableAssetTransfer."""
        if not asset_transfer:
            return {"has_movable_asset_transfer": False}
        
        return {
            "has_movable_asset_transfer": True,
            "movable_asset_transfer_type": asset_transfer.movable_asset_transfer_type,
            "movable_asset_transfer_cost": asset_transfer.movable_asset_transfer_cost.to_float(),
            "movable_asset_years_of_use": asset_transfer.movable_asset_years_of_use,
            "movable_asset_transfer_employee_payment": asset_transfer.movable_asset_transfer_employee_payment.to_float()
        }
    
    def _serialize_gift_voucher_perquisite(self, gift_voucher: Optional[GiftVoucherPerquisite]) -> Dict[str, Any]:
        """Serialize GiftVoucherPerquisite."""
        if not gift_voucher:
            return {"has_gift_voucher": False}
        
        return {
            "has_gift_voucher": True,
            "gift_voucher_amount": gift_voucher.gift_voucher_amount.to_float()
        }
    
    def _serialize_monetary_benefits_perquisite(self, monetary_benefits: Optional[MonetaryBenefitsPerquisite]) -> Dict[str, Any]:
        """Serialize MonetaryBenefitsPerquisite."""
        if not monetary_benefits:
            return {"has_monetary_benefits": False}
        
        return {
            "has_monetary_benefits": True,
            "monetary_amount_paid_by_employer": monetary_benefits.monetary_amount_paid_by_employer.to_float(),
            "expenditure_for_official_purpose": monetary_benefits.expenditure_for_official_purpose.to_float(),
            "amount_paid_by_employee": monetary_benefits.amount_paid_by_employee.to_float()
        }
    
    def _serialize_club_expenses_perquisite(self, club_expenses: Optional[ClubExpensesPerquisite]) -> Dict[str, Any]:
        """Serialize ClubExpensesPerquisite."""
        if not club_expenses:
            return {"has_club_expenses": False}
        
        return {
            "has_club_expenses": True,
            "club_expenses_paid_by_employer": club_expenses.club_expenses_paid_by_employer.to_float(),
            "club_expenses_paid_by_employee": club_expenses.club_expenses_paid_by_employee.to_float(),
            "club_expenses_for_official_purpose": club_expenses.club_expenses_for_official_purpose.to_float()
        }
    
    def _serialize_deductions(self, deductions: TaxDeductions) -> Dict[str, Any]:
        """Serialize TaxDeductions with all sections."""
        return {
            "section_80c": self._serialize_section_80c(deductions.section_80c) if deductions.section_80c else None,
            "section_80ccc": self._serialize_section_80ccc(deductions.section_80ccc) if deductions.section_80ccc else None,
            "section_80ccd": self._serialize_section_80ccd(deductions.section_80ccd) if deductions.section_80ccd else None,
            "section_80d": self._serialize_section_80d(deductions.section_80d) if deductions.section_80d else None,
            "section_80dd": self._serialize_section_80dd(deductions.section_80dd) if deductions.section_80dd else None,
            "section_80ddb": self._serialize_section_80ddb(deductions.section_80ddb) if deductions.section_80ddb else None,
            "section_80e": self._serialize_section_80e(deductions.section_80e) if deductions.section_80e else None,
            "section_80eeb": self._serialize_section_80eeb(deductions.section_80eeb) if deductions.section_80eeb else None,
            "section_80g": self._serialize_section_80g(deductions.section_80g) if deductions.section_80g else None,
            "section_80ggc": self._serialize_section_80ggc(deductions.section_80ggc) if deductions.section_80ggc else None,
            "section_80u": self._serialize_section_80u(deductions.section_80u) if deductions.section_80u else None,
            "section_80tta_ttb": self._serialize_section_80tta_ttb(deductions.section_80tta_ttb) if deductions.section_80tta_ttb else None,
            "hra_exemption": self._serialize_hra_exemption(deductions.hra_exemption) if deductions.hra_exemption else None,
            "other_deductions": self._serialize_other_deductions(deductions.other_deductions) if deductions.other_deductions else None
        }
    
    def _serialize_section_80c(self, section_80c: DeductionSection80C) -> Dict[str, Any]:
        """Serialize DeductionSection80C."""
        if section_80c is None:
            return None
        return {
            "life_insurance_premium": section_80c.life_insurance_premium.to_float(),
            "nsc_investment": section_80c.nsc_investment.to_float(),
            "tax_saving_fd": section_80c.tax_saving_fd.to_float(),
            "elss_investment": section_80c.elss_investment.to_float(),
            "home_loan_principal": section_80c.home_loan_principal.to_float(),
            "tuition_fees": section_80c.tuition_fees.to_float(),
            "ulip_premium": section_80c.ulip_premium.to_float(),
            "sukanya_samriddhi": section_80c.sukanya_samriddhi.to_float(),
            "stamp_duty_property": section_80c.stamp_duty_property.to_float(),
            "senior_citizen_savings": section_80c.senior_citizen_savings.to_float(),
            "other_80c_investments": section_80c.other_80c_investments.to_float()
        }
    
    def _serialize_section_80ccc(self, section_80ccc: DeductionSection80CCC) -> Dict[str, Any]:
        """Serialize DeductionSection80CCC."""
        if section_80ccc is None:
            return None
        return {
            "pension_fund_contribution": section_80ccc.pension_fund_contribution.to_float()
        }
    
    def _serialize_section_80ccd(self, section_80ccd: DeductionSection80CCD) -> Dict[str, Any]:
        """Serialize DeductionSection80CCD."""
        if section_80ccd is None:
            return None
        return {
            "employee_nps_contribution": section_80ccd.employee_nps_contribution.to_float(),
            "additional_nps_contribution": section_80ccd.additional_nps_contribution.to_float(),
            "employer_nps_contribution": section_80ccd.employer_nps_contribution.to_float()
        }
    
    def _serialize_section_80d(self, section_80d: DeductionSection80D) -> Dict[str, Any]:
        """Serialize DeductionSection80D."""
        if section_80d is None:
            return None
        return {
            "self_family_premium": section_80d.self_family_premium.to_float(),
            "parent_premium": section_80d.parent_premium.to_float(),
            "preventive_health_checkup": section_80d.preventive_health_checkup.to_float(),
            "parent_age": section_80d.parent_age
        }
    
    def _serialize_section_80dd(self, section_80dd: DeductionSection80DD) -> Dict[str, Any]:
        """Serialize DeductionSection80DD."""
        if section_80dd is None:
            return None
        return {
            "relation": section_80dd.relation.value,
            "disability_percentage": section_80dd.disability_percentage.value
        }
    
    def _serialize_section_80ddb(self, section_80ddb: DeductionSection80DDB) -> Dict[str, Any]:
        """Serialize DeductionSection80DDB."""
        if section_80ddb is None:
            return None
        return {
            "medical_expenses": section_80ddb.medical_expenses.to_float(),
            "relation": section_80ddb.relation.value,
            "dependent_age": section_80ddb.dependent_age
        }
    
    def _serialize_section_80e(self, section_80e: DeductionSection80E) -> Dict[str, Any]:
        """Serialize DeductionSection80E."""
        if section_80e is None:
            return None
        return {
            "education_loan_interest": section_80e.education_loan_interest.to_float(),
            "relation": section_80e.relation.value
        }
    
    def _serialize_section_80eeb(self, section_80eeb: DeductionSection80EEB) -> Dict[str, Any]:
        """Serialize DeductionSection80EEB."""
        if section_80eeb is None:
            return None
        return {
            "ev_loan_interest": section_80eeb.ev_loan_interest.to_float(),
            "ev_purchase_date": section_80eeb.ev_purchase_date.isoformat() if section_80eeb.ev_purchase_date else None
        }
    
    def _serialize_section_80g(self, section_80g: DeductionSection80G) -> Dict[str, Any]:
        """Serialize DeductionSection80G."""
        if section_80g is None:
            return None
        return {
            "pm_relief_fund": section_80g.pm_relief_fund.to_float(),
            "national_defence_fund": section_80g.national_defence_fund.to_float(),
            "cm_relief_fund": section_80g.cm_relief_fund.to_float(),
            "govt_charitable_donations": section_80g.govt_charitable_donations.to_float(),
            "other_charitable_donations": section_80g.other_charitable_donations.to_float(),
            "family_planning_donation": section_80g.family_planning_donation.to_float(),
            "indian_olympic_association": section_80g.indian_olympic_association.to_float(),
            "other_100_percent_w_limit": section_80g.other_100_percent_w_limit.to_float(),
            "housing_authorities_donations": section_80g.housing_authorities_donations.to_float(),
            "religious_renovation_donations": section_80g.religious_renovation_donations.to_float(),
            "other_50_percent_w_limit": section_80g.other_50_percent_w_limit.to_float()
        }
    
    def _serialize_section_80ggc(self, section_80ggc: DeductionSection80GGC) -> Dict[str, Any]:
        """Serialize DeductionSection80GGC."""
        if section_80ggc is None:
            return None
        return {
            "political_party_contribution": section_80ggc.political_party_contribution.to_float()
        }
    
    def _serialize_section_80u(self, section_80u: DeductionSection80U) -> Dict[str, Any]:
        """Serialize DeductionSection80U."""
        if section_80u is None:
            return None
        return {
            "disability_percentage": section_80u.disability_percentage.value
        }
    
    def _serialize_section_80tta_ttb(self, section_80tta_ttb: DeductionSection80TTA_TTB) -> Dict[str, Any]:
        """Serialize DeductionSection80TTA_TTB."""
        if section_80tta_ttb is None:
            return None
        return {
            "savings_interest": section_80tta_ttb.savings_interest.to_float(),
            "fd_interest": section_80tta_ttb.fd_interest.to_float(),
            "rd_interest": section_80tta_ttb.rd_interest.to_float(),
            "post_office_interest": section_80tta_ttb.post_office_interest.to_float(),
            "age": section_80tta_ttb.age
        }
    
    def _serialize_hra_exemption(self, hra_exemption: HRAExemption) -> Dict[str, Any]:
        """Serialize HRAExemption."""
        if hra_exemption is None:
            return None
        return {
            "actual_rent_paid": hra_exemption.actual_rent_paid.to_float(),
            "hra_city_type": hra_exemption.hra_city_type
        }
    
    def _serialize_other_deductions(self, other_deductions: OtherDeductions) -> Dict[str, Any]:
        """Serialize OtherDeductions."""
        if other_deductions is None:
            return None
        return {
            "other_deductions": other_deductions.other_deductions.to_float()
        }
    
    def _serialize_retirement_benefits(self, retirement_benefits: RetirementBenefits) -> Dict[str, Any]:
        """Serialize RetirementBenefits with all components."""
        if retirement_benefits is None:
            return None
        return {
            "leave_encashment": self._serialize_leave_encashment(retirement_benefits.leave_encashment),
            "gratuity": self._serialize_gratuity(retirement_benefits.gratuity),
            "vrs": self._serialize_vrs(retirement_benefits.vrs),
            "pension": self._serialize_pension(retirement_benefits.pension),
            "retrenchment_compensation": self._serialize_retrenchment_compensation(retirement_benefits.retrenchment_compensation)
        }
    
    def _serialize_leave_encashment(self, leave_encashment: LeaveEncashment) -> Dict[str, Any]:
        """Serialize LeaveEncashment."""
        if leave_encashment is None:
            return None
        return {
            "has_leave_encashment": True,
            "leave_encashment_amount": leave_encashment.leave_encashment_amount.to_float(),
            "average_monthly_salary": leave_encashment.average_monthly_salary.to_float(),
            "leave_days_encashed": leave_encashment.leave_days_encashed,
            "is_deceased": leave_encashment.is_deceased,
            "during_employment": leave_encashment.during_employment
        }
    
    def _serialize_gratuity(self, gratuity: Gratuity) -> Dict[str, Any]:
        """Serialize Gratuity."""
        if gratuity is None:
            return None
        return {
            "has_gratuity": True,
            "gratuity_amount": gratuity.gratuity_amount.to_float(),
            "monthly_salary": gratuity.monthly_salary.to_float(),
            "service_years": float(gratuity.service_years)
        }
    
    def _serialize_vrs(self, vrs: VRS) -> Dict[str, Any]:
        """Serialize VRS."""
        if vrs is None:
            return None
        return {
            "has_vrs": True,
            "vrs_amount": vrs.vrs_amount.to_float(),
            "monthly_salary": vrs.monthly_salary.to_float(),
            "service_years": float(vrs.service_years)
        }
    
    def _serialize_pension(self, pension: Pension) -> Dict[str, Any]:
        """Serialize Pension."""
        if pension is None:
            return None
        return {
            "has_pension": True,
            "regular_pension": pension.regular_pension.to_float(),
            "commuted_pension": pension.commuted_pension.to_float(),
            "total_pension": pension.total_pension.to_float(),
            "gratuity_received": pension.gratuity_received
        }
    
    def _serialize_retrenchment_compensation(self, retrenchment_compensation: RetrenchmentCompensation) -> Dict[str, Any]:
        """Serialize RetrenchmentCompensation."""
        if retrenchment_compensation is None:
            return None
        return {
            "has_retrenchment_compensation": True,
            "retrenchment_amount": retrenchment_compensation.retrenchment_amount.to_float(),
            "monthly_salary": retrenchment_compensation.monthly_salary.to_float(),
            "service_years": float(retrenchment_compensation.service_years)
        }
    
    def _serialize_lwp_details(self, lwp: LWPDetails) -> Dict[str, Any]:
        """Serialize LWPDetails."""
        return {
            "lwp_days": lwp.lwp_days,
            "total_working_days": lwp.total_working_days,
            "month": lwp.month,
            "year": lwp.year
        }
    
    # =============================================================================
    # DESERIALIZATION METHODS
    # =============================================================================
    
    def _deserialize_salary_income(self, salary_doc: Dict[str, Any]) -> SalaryIncome:
        """Deserialize SalaryIncome with all components including SpecificAllowances."""
        # Parse dates
        effective_from = None
        effective_till = None
        if salary_doc.get("effective_from"):
            effective_from = datetime.fromisoformat(salary_doc["effective_from"])
        if salary_doc.get("effective_till"):
            effective_till = datetime.fromisoformat(salary_doc["effective_till"])
        
        # Create specific allowances
        specific_allowances = self._deserialize_specific_allowances(salary_doc.get("specific_allowances", {}))
        
        return SalaryIncome(
            basic_salary=Money.from_float(salary_doc.get("basic_salary", 0.0)),
            dearness_allowance=Money.from_float(salary_doc.get("dearness_allowance", 0.0)),
            hra_provided=Money.from_float(salary_doc.get("hra_provided", 0.0)),
            pf_employee_contribution=Money.from_float(salary_doc.get("pf_employee_contribution", 0.0)),
            pf_employer_contribution=Money.from_float(salary_doc.get("pf_employer_contribution", 0.0)),
            esi_contribution=Money.from_float(salary_doc.get("esi_contribution", 0.0)),
            pf_voluntary_contribution=Money.from_float(salary_doc.get("pf_voluntary_contribution", 0.0)),
            pf_total_contribution=Money.from_float(salary_doc.get("pf_total_contribution", 0.0)),
            special_allowance=Money.from_float(salary_doc.get("special_allowance", 0.0)),
            bonus=Money.from_float(salary_doc.get("bonus", 0.0)),
            commission=Money.from_float(salary_doc.get("commission", 0.0)),
            arrears=Money.from_float(salary_doc.get("arrears", 0.0)),
            effective_from=effective_from,
            effective_till=effective_till,
            specific_allowances=specific_allowances
        )
    
    def _deserialize_specific_allowances(self, specific_allowances_doc: Dict[str, Any]) -> SpecificAllowances:
        """Deserialize SpecificAllowances with all fields."""
        return SpecificAllowances(
            monthly_hills_allowance=Money.from_float(specific_allowances_doc.get("monthly_hills_allowance", 0.0)),
            monthly_hills_exemption_limit=Money.from_float(specific_allowances_doc.get("monthly_hills_exemption_limit", 0.0)),
            monthly_border_allowance=Money.from_float(specific_allowances_doc.get("monthly_border_allowance", 0.0)),
            monthly_border_exemption_limit=Money.from_float(specific_allowances_doc.get("monthly_border_exemption_limit", 0.0)),
            transport_employee_allowance=Money.from_float(specific_allowances_doc.get("transport_employee_allowance", 0.0)),
            children_education_allowance=Money.from_float(specific_allowances_doc.get("children_education_allowance", 0.0)),
            children_education_count=specific_allowances_doc.get("children_education_count", 0),
            hostel_allowance=Money.from_float(specific_allowances_doc.get("hostel_allowance", 0.0)),
            children_hostel_count=specific_allowances_doc.get("children_hostel_count", 0),
            disabled_transport_allowance=Money.from_float(specific_allowances_doc.get("disabled_transport_allowance", 0.0)),
            is_disabled=specific_allowances_doc.get("is_disabled", False),
            underground_mines_allowance=Money.from_float(specific_allowances_doc.get("underground_mines_allowance", 0.0)),
            mine_work_months=specific_allowances_doc.get("mine_work_months", 0),
            government_entertainment_allowance=Money.from_float(specific_allowances_doc.get("government_entertainment_allowance", 0.0)),
            city_compensatory_allowance=Money.from_float(specific_allowances_doc.get("city_compensatory_allowance", 0.0)),
            rural_allowance=Money.from_float(specific_allowances_doc.get("rural_allowance", 0.0)),
            proctorship_allowance=Money.from_float(specific_allowances_doc.get("proctorship_allowance", 0.0)),
            wardenship_allowance=Money.from_float(specific_allowances_doc.get("wardenship_allowance", 0.0)),
            project_allowance=Money.from_float(specific_allowances_doc.get("project_allowance", 0.0)),
            deputation_allowance=Money.from_float(specific_allowances_doc.get("deputation_allowance", 0.0)),
            overtime_allowance=Money.from_float(specific_allowances_doc.get("overtime_allowance", 0.0)),
            interim_relief=Money.from_float(specific_allowances_doc.get("interim_relief", 0.0)),
            tiffin_allowance=Money.from_float(specific_allowances_doc.get("tiffin_allowance", 0.0)),
            fixed_medical_allowance=Money.from_float(specific_allowances_doc.get("fixed_medical_allowance", 0.0)),
            servant_allowance=Money.from_float(specific_allowances_doc.get("servant_allowance", 0.0)),
            any_other_allowance=Money.from_float(specific_allowances_doc.get("any_other_allowance", 0.0)),
            any_other_allowance_exemption=Money.from_float(specific_allowances_doc.get("any_other_allowance_exemption", 0.0)),
            govt_employees_outside_india_allowance=Money.from_float(specific_allowances_doc.get("govt_employees_outside_india_allowance", 0.0)),
            supreme_high_court_judges_allowance=Money.from_float(specific_allowances_doc.get("supreme_high_court_judges_allowance", 0.0)),
            judge_compensatory_allowance=Money.from_float(specific_allowances_doc.get("judge_compensatory_allowance", 0.0)),
            section_10_14_special_allowances=Money.from_float(specific_allowances_doc.get("section_10_14_special_allowances", 0.0)),
            travel_on_tour_allowance=Money.from_float(specific_allowances_doc.get("travel_on_tour_allowance", 0.0)),
            tour_daily_charge_allowance=Money.from_float(specific_allowances_doc.get("tour_daily_charge_allowance", 0.0)),
            conveyance_in_performace_of_duties=Money.from_float(specific_allowances_doc.get("conveyance_in_performace_of_duties", 0.0)),
            helper_in_performace_of_duties=Money.from_float(specific_allowances_doc.get("helper_in_performace_of_duties", 0.0)),
            academic_research=Money.from_float(specific_allowances_doc.get("academic_research", 0.0)),
            uniform_allowance=Money.from_float(specific_allowances_doc.get("uniform_allowance", 0.0)),
            hills_allowance=Money.from_float(specific_allowances_doc.get("hills_allowance", 0.0)),
            border_allowance=Money.from_float(specific_allowances_doc.get("border_allowance", 0.0)),
            hills_exemption_limit=Money.from_float(specific_allowances_doc.get("hills_exemption_limit", 0.0)),
            border_exemption_limit=Money.from_float(specific_allowances_doc.get("border_exemption_limit", 0.0)),
            children_count=specific_allowances_doc.get("children_count", 0)
        )

    # --- PERQUISITES ---
    def _deserialize_perquisites(self, perq_doc: Dict[str, Any]) -> Perquisites:
        # Each perquisite type should be deserialized with robust fallback for missing fields
        def get_money(doc, key):
            return Money.from_float(doc.get(key, 0.0))
        def get_bool(doc, key):
            return bool(doc.get(key, False))
        def get_int(doc, key):
            return int(doc.get(key, 0))
        def get_str(doc, key, default=None):
            return doc.get(key, default)
        # Accommodation
        acc = perq_doc.get("accommodation", {})
        accommodation = None
        if acc.get("has_accommodation"):
            from app.domain.entities.taxation.perquisites import AccommodationType, CityPopulation
            accommodation = AccommodationPerquisite(
                accommodation_type=AccommodationType(acc.get("accommodation_type", "Employer-Owned")),
                city_population=CityPopulation(acc.get("city_population", "Below 15 Lakhs")),
                license_fees=get_money(acc, "license_fees"),
                employee_rent_payment=get_money(acc, "employee_rent_payment"),
                rent_paid_by_employer=get_money(acc, "rent_paid_by_employer"),
                hotel_charges=get_money(acc, "hotel_charges"),
                stay_days=get_int(acc, "stay_days"),
                furniture_cost=get_money(acc, "furniture_cost"),
                furniture_employee_payment=get_money(acc, "furniture_employee_payment"),
                is_furniture_owned_by_employer=get_bool(acc, "is_furniture_owned_by_employer")
            )
        # Car
        car_doc = perq_doc.get("car", {})
        car = None
        if car_doc.get("has_car"):
            from app.domain.entities.taxation.perquisites import CarUseType
            car = CarPerquisite(
                car_use_type=CarUseType(car_doc.get("car_use_type", "Personal")),
                engine_capacity_cc=get_int(car_doc, "engine_capacity_cc"),
                months_used=get_int(car_doc, "months_used"),
                months_used_other_vehicle=get_int(car_doc, "months_used_other_vehicle"),
                car_cost_to_employer=get_money(car_doc, "car_cost_to_employer"),
                other_vehicle_cost=get_money(car_doc, "other_vehicle_cost"),
                has_expense_reimbursement=get_bool(car_doc, "has_expense_reimbursement"),
                driver_provided=get_bool(car_doc, "driver_provided")
            )
        # LTA
        lta_doc = perq_doc.get("lta", {})
        lta = None
        if lta_doc.get("has_lta"):
            lta = LTAPerquisite(
                is_monthly_paid=get_bool(lta_doc, "is_monthly_paid"),
                lta_amount_claimed=get_money(lta_doc, "lta_amount_claimed"),
                lta_claimed_count=get_int(lta_doc, "lta_claimed_count"),
                public_transport_cost=get_money(lta_doc, "public_transport_cost"),
                travel_mode=get_str(lta_doc, "travel_mode", "Air")
            )
        # Interest Free Loan
        loan_doc = perq_doc.get("interest_free_loan", {})
        interest_free_loan = None
        if loan_doc.get("has_loan"):
            interest_free_loan = InterestFreeConcessionalLoan(
                loan_amount=get_money(loan_doc, "loan_amount"),
                emi_amount=get_money(loan_doc, "emi_amount"),
                company_interest_rate=get_money(loan_doc, "company_interest_rate"),
                sbi_interest_rate=get_money(loan_doc, "sbi_interest_rate"),
                loan_type=get_str(loan_doc, "loan_type", "Personal"),
                loan_start_date=None  # Could parse if needed
            )
        # ESOP
        esop_doc = perq_doc.get("esop", {})
        esop = None
        if esop_doc.get("has_esop"):
            esop = ESOPPerquisite(
                shares_exercised=get_int(esop_doc, "shares_exercised"),
                exercise_price=get_money(esop_doc, "exercise_price"),
                allotment_price=get_money(esop_doc, "allotment_price")
            )
        # Utilities
        util_doc = perq_doc.get("utilities", {})
        utilities = None
        if util_doc.get("has_utilities"):
            utilities = UtilitiesPerquisite(
                gas_paid_by_employer=get_money(util_doc, "gas_paid_by_employer"),
                electricity_paid_by_employer=get_money(util_doc, "electricity_paid_by_employer"),
                water_paid_by_employer=get_money(util_doc, "water_paid_by_employer"),
                gas_paid_by_employee=get_money(util_doc, "gas_paid_by_employee"),
                electricity_paid_by_employee=get_money(util_doc, "electricity_paid_by_employee"),
                water_paid_by_employee=get_money(util_doc, "water_paid_by_employee"),
                is_gas_manufactured_by_employer=get_bool(util_doc, "is_gas_manufactured_by_employer"),
                is_electricity_manufactured_by_employer=get_bool(util_doc, "is_electricity_manufactured_by_employer"),
                is_water_manufactured_by_employer=get_bool(util_doc, "is_water_manufactured_by_employer")
            )
        # Free Education
        edu_doc = perq_doc.get("free_education", {})
        free_education = None
        if edu_doc.get("has_free_education"):
            free_education = FreeEducationPerquisite(
                monthly_expenses_child1=get_money(edu_doc, "monthly_expenses_child1"),
                monthly_expenses_child2=get_money(edu_doc, "monthly_expenses_child2"),
                months_child1=get_int(edu_doc, "months_child1"),
                months_child2=get_int(edu_doc, "months_child2"),
                employer_maintained_1st_child=get_bool(edu_doc, "employer_maintained_1st_child"),
                employer_maintained_2nd_child=get_bool(edu_doc, "employer_maintained_2nd_child")
            )
        # Lunch Refreshment
        lunch_doc = perq_doc.get("lunch_refreshment", {})
        lunch_refreshment = None
        if lunch_doc.get("has_lunch_refreshment"):
            lunch_refreshment = LunchRefreshmentPerquisite(
                lunch_employer_cost=get_money(lunch_doc, "lunch_employer_cost"),
                lunch_employee_payment=get_money(lunch_doc, "lunch_employee_payment"),
                lunch_meal_days_per_year=get_int(lunch_doc, "lunch_meal_days_per_year")
            )
        # Domestic Help
        dh_doc = perq_doc.get("domestic_help", {})
        domestic_help = None
        if dh_doc.get("has_domestic_help"):
            domestic_help = DomesticHelpPerquisite(
                domestic_help_paid_by_employer=get_money(dh_doc, "domestic_help_paid_by_employer"),
                domestic_help_paid_by_employee=get_money(dh_doc, "domestic_help_paid_by_employee")
            )
        # Movable Asset Usage
        asset_usage_doc = perq_doc.get("movable_asset_usage", {})
        movable_asset_usage = None
        if asset_usage_doc.get("has_movable_asset_usage"):
            movable_asset_usage = MovableAssetUsage(
                movable_asset_type=get_str(asset_usage_doc, "movable_asset_type", "Electronics"),
                movable_asset_usage_value=get_money(asset_usage_doc, "movable_asset_usage_value"),
                movable_asset_hire_cost=get_money(asset_usage_doc, "movable_asset_hire_cost"),
                movable_asset_employee_payment=get_money(asset_usage_doc, "movable_asset_employee_payment"),
                movable_asset_is_employer_owned=get_bool(asset_usage_doc, "movable_asset_is_employer_owned")
            )
        # Movable Asset Transfer
        asset_transfer_doc = perq_doc.get("movable_asset_transfer", {})
        movable_asset_transfer = None
        if asset_transfer_doc.get("has_movable_asset_transfer"):
            movable_asset_transfer = MovableAssetTransfer(
                movable_asset_transfer_type=get_str(asset_transfer_doc, "movable_asset_transfer_type", "Electronics"),
                movable_asset_transfer_cost=get_money(asset_transfer_doc, "movable_asset_transfer_cost"),
                movable_asset_years_of_use=get_int(asset_transfer_doc, "movable_asset_years_of_use"),
                movable_asset_transfer_employee_payment=get_money(asset_transfer_doc, "movable_asset_transfer_employee_payment")
            )
        # Gift Voucher
        gift_doc = perq_doc.get("gift_voucher", {})
        gift_voucher = None
        if gift_doc.get("has_gift_voucher"):
            gift_voucher = GiftVoucherPerquisite(
                gift_voucher_amount=get_money(gift_doc, "gift_voucher_amount")
            )
        # Monetary Benefits
        mb_doc = perq_doc.get("monetary_benefits", {})
        monetary_benefits = None
        if mb_doc.get("has_monetary_benefits"):
            monetary_benefits = MonetaryBenefitsPerquisite(
                monetary_amount_paid_by_employer=get_money(mb_doc, "monetary_amount_paid_by_employer"),
                expenditure_for_official_purpose=get_money(mb_doc, "expenditure_for_official_purpose"),
                amount_paid_by_employee=get_money(mb_doc, "amount_paid_by_employee")
            )
        # Club Expenses
        club_doc = perq_doc.get("club_expenses", {})
        club_expenses = None
        if club_doc.get("has_club_expenses"):
            club_expenses = ClubExpensesPerquisite(
                club_expenses_paid_by_employer=get_money(club_doc, "club_expenses_paid_by_employer"),
                club_expenses_paid_by_employee=get_money(club_doc, "club_expenses_paid_by_employee"),
                club_expenses_for_official_purpose=get_money(club_doc, "club_expenses_for_official_purpose")
            )
        return Perquisites(
            accommodation=accommodation,
            car=car,
            lta=lta,
            interest_free_loan=interest_free_loan,
            esop=esop,
            utilities=utilities,
            free_education=free_education,
            lunch_refreshment=lunch_refreshment,
            domestic_help=domestic_help,
            movable_asset_usage=movable_asset_usage,
            movable_asset_transfer=movable_asset_transfer,
            gift_voucher=gift_voucher,
            monetary_benefits=monetary_benefits,
            club_expenses=club_expenses
        )

    def _deserialize_perquisites_payouts(self, perq_payouts_doc: Dict[str, Any]) -> MonthlyPerquisitesPayouts:
        """Deserialize MonthlyPerquisitesPayouts from document format."""
        if not perq_payouts_doc:
            return MonthlyPerquisitesPayouts(components=[], total=Money.zero())
        
        components = []
        for comp_doc in perq_payouts_doc.get("components", []):
            component = MonthlyPerquisitesComponents(
                key=comp_doc.get("key", ""),
                display_name=comp_doc.get("display_name", ""),
                value=Money.from_float(comp_doc.get("value", 0.0))
            )
            components.append(component)
        
        total = Money.from_float(perq_payouts_doc.get("total", 0.0))
        
        return MonthlyPerquisitesPayouts(components=components, total=total)

    # --- DEDUCTIONS ---
    def _deserialize_deductions(self, ded_doc: Dict[str, Any]) -> TaxDeductions:
        # Each deduction section should be deserialized with robust fallback for missing fields
        from app.domain.entities.taxation.deductions import (
            DeductionSection80C, DeductionSection80CCC, DeductionSection80CCD, DeductionSection80D, DeductionSection80DD, DeductionSection80DDB, DeductionSection80E, DeductionSection80EEB, DeductionSection80G, DeductionSection80GGC, DeductionSection80U, DeductionSection80TTA_TTB, HRAExemption, OtherDeductions
        )
        section_80c = ded_doc.get("section_80c") or {}
        section_80ccc = ded_doc.get("section_80ccc") or {}
        section_80ccd = ded_doc.get("section_80ccd") or {}
        section_80d = ded_doc.get("section_80d") or {}
        section_80dd = ded_doc.get("section_80dd") or {}
        section_80ddb = ded_doc.get("section_80ddb") or {}
        section_80e = ded_doc.get("section_80e") or {}
        section_80eeb = ded_doc.get("section_80eeb") or {}
        section_80g = ded_doc.get("section_80g") or {}
        section_80ggc = ded_doc.get("section_80ggc") or {}
        section_80u = ded_doc.get("section_80u") or {}
        section_80tta_ttb = ded_doc.get("section_80tta_ttb") or {}
        hra_exemption = ded_doc.get("hra_exemption") or {}
        other_deductions = ded_doc.get("other_deductions") or {}
        return TaxDeductions(
            section_80c=DeductionSection80C(
                life_insurance_premium=Money.from_float(section_80c.get("life_insurance_premium", 0.0)),
                nsc_investment=Money.from_float(section_80c.get("nsc_investment", 0.0)),
                tax_saving_fd=Money.from_float(section_80c.get("tax_saving_fd", 0.0)),
                elss_investment=Money.from_float(section_80c.get("elss_investment", 0.0)),
                home_loan_principal=Money.from_float(section_80c.get("home_loan_principal", 0.0)),
                tuition_fees=Money.from_float(section_80c.get("tuition_fees", 0.0)),
                ulip_premium=Money.from_float(section_80c.get("ulip_premium", 0.0)),
                sukanya_samriddhi=Money.from_float(section_80c.get("sukanya_samriddhi", 0.0)),
                stamp_duty_property=Money.from_float(section_80c.get("stamp_duty_property", 0.0)),
                senior_citizen_savings=Money.from_float(section_80c.get("senior_citizen_savings", 0.0)),
                other_80c_investments=Money.from_float(section_80c.get("other_80c_investments", 0.0))
            ),
            section_80ccc=DeductionSection80CCC(
                pension_fund_contribution=Money.from_float(section_80ccc.get("pension_fund_contribution", 0.0))
            ),
            section_80ccd=DeductionSection80CCD(
                employee_nps_contribution=Money.from_float(section_80ccd.get("employee_nps_contribution", 0.0)),
                additional_nps_contribution=Money.from_float(section_80ccd.get("additional_nps_contribution", 0.0)),
                employer_nps_contribution=Money.from_float(section_80ccd.get("employer_nps_contribution", 0.0))
            ),
            section_80d=DeductionSection80D(
                self_family_premium=Money.from_float(section_80d.get("self_family_premium", 0.0)),
                parent_premium=Money.from_float(section_80d.get("parent_premium", 0.0)),
                preventive_health_checkup=Money.from_float(section_80d.get("preventive_health_checkup", 0.0)),
                parent_age=section_80d.get("parent_age", 55)
            ),
            section_80dd=DeductionSection80DD(
                relation=RelationType(section_80dd.get("relation", "Self")),
                disability_percentage=DisabilityPercentage(section_80dd.get("disability_percentage", "Between 40%-80%"))
            ),
            section_80ddb=DeductionSection80DDB(
                dependent_age=section_80ddb.get("dependent_age", 0),
                medical_expenses=Money.from_float(section_80ddb.get("medical_expenses", 0.0)),
                relation=RelationType(section_80ddb.get("relation", "Self"))
            ),
            section_80e=DeductionSection80E(
                education_loan_interest=Money.from_float(section_80e.get("education_loan_interest", 0.0)),
                relation=RelationType(section_80e.get("relation", "Self"))
            ),
            section_80eeb=DeductionSection80EEB(
                ev_loan_interest=Money.from_float(section_80eeb.get("ev_loan_interest", 0.0)),
                ev_purchase_date=None
            ),
            section_80g=DeductionSection80G(
                pm_relief_fund=Money.from_float(section_80g.get("pm_relief_fund", 0.0)),
                national_defence_fund=Money.from_float(section_80g.get("national_defence_fund", 0.0)),
                cm_relief_fund=Money.from_float(section_80g.get("cm_relief_fund", 0.0)),
                govt_charitable_donations=Money.from_float(section_80g.get("govt_charitable_donations", 0.0)),
                other_charitable_donations=Money.from_float(section_80g.get("other_charitable_donations", 0.0)),
                family_planning_donation=Money.from_float(section_80g.get("family_planning_donation", 0.0)),
                indian_olympic_association=Money.from_float(section_80g.get("indian_olympic_association", 0.0)),
                other_100_percent_w_limit=Money.from_float(section_80g.get("other_100_percent_w_limit", 0.0)),
                housing_authorities_donations=Money.from_float(section_80g.get("housing_authorities_donations", 0.0)),
                religious_renovation_donations=Money.from_float(section_80g.get("religious_renovation_donations", 0.0)),
                other_50_percent_w_limit=Money.from_float(section_80g.get("other_50_percent_w_limit", 0.0))
            ),
            section_80ggc=DeductionSection80GGC(
                political_party_contribution=Money.from_float(section_80ggc.get("political_party_contribution", 0.0))
            ),
            section_80u=DeductionSection80U(
                disability_percentage=DisabilityPercentage(section_80u.get("disability_percentage", "Between 40%-80%"))
            ),
            section_80tta_ttb=DeductionSection80TTA_TTB(
                savings_interest=Money.from_float(section_80tta_ttb.get("savings_interest", 0.0)),
                fd_interest=Money.from_float(section_80tta_ttb.get("fd_interest", 0.0)),
                rd_interest=Money.from_float(section_80tta_ttb.get("rd_interest", 0.0)),
                post_office_interest=Money.from_float(section_80tta_ttb.get("post_office_interest", 0.0)),
                age=section_80tta_ttb.get("age", 0)
            ),
            hra_exemption=HRAExemption(
                actual_rent_paid=Money.from_float(hra_exemption.get("actual_rent_paid", 0.0)),
                hra_city_type=hra_exemption.get("hra_city_type", "non_metro")
            ),
            other_deductions=OtherDeductions(
                other_deductions=Money.from_float(other_deductions.get("other_deductions", 0.0))
            )
        )

    # --- RETIREMENT BENEFITS ---
    def _deserialize_retirement_benefits(self, ret_doc: Dict[str, Any]) -> RetirementBenefits:
        leave_doc = ret_doc.get("leave_encashment", {})
        gratuity_doc = ret_doc.get("gratuity", {})
        vrs_doc = ret_doc.get("vrs", {})
        pension_doc = ret_doc.get("pension", {})
        retrench_doc = ret_doc.get("retrenchment_compensation", {})
        leave_encashment = None
        if leave_doc.get("has_leave_encashment"):
            leave_encashment = LeaveEncashment(
                leave_encashment_amount=Money.from_float(leave_doc.get("leave_encashment_amount", 0.0)),
                average_monthly_salary=Money.from_float(leave_doc.get("average_monthly_salary", 0.0)),
                leave_days_encashed=leave_doc.get("leave_days_encashed", 0),
                is_deceased=leave_doc.get("is_deceased", False),
                during_employment=leave_doc.get("during_employment", False)
            )
        gratuity = None
        if gratuity_doc.get("has_gratuity"):
            gratuity = Gratuity(
                gratuity_amount=Money.from_float(gratuity_doc.get("gratuity_amount", 0.0)),
                monthly_salary=Money.from_float(gratuity_doc.get("monthly_salary", 0.0)),
                service_years=Decimal(str(gratuity_doc.get("service_years", 0.0)))
            )
        vrs = None
        if vrs_doc.get("has_vrs"):
            vrs = VRS(
                vrs_amount=Money.from_float(vrs_doc.get("vrs_amount", 0.0)),
                monthly_salary=Money.from_float(vrs_doc.get("monthly_salary", 0.0)),
                service_years=Decimal(str(vrs_doc.get("service_years", 0.0)))
            )
        pension = None
        if pension_doc.get("has_pension"):
            pension = Pension(
                regular_pension=Money.from_float(pension_doc.get("regular_pension", 0.0)),
                commuted_pension=Money.from_float(pension_doc.get("commuted_pension", 0.0)),
                total_pension=Money.from_float(pension_doc.get("total_pension", 0.0)),
                gratuity_received=pension_doc.get("gratuity_received", False)
            )
        retrenchment_compensation = None
        if retrench_doc.get("has_retrenchment_compensation"):
            retrenchment_compensation = RetrenchmentCompensation(
                retrenchment_amount=Money.from_float(retrench_doc.get("retrenchment_amount", 0.0)),
                monthly_salary=Money.from_float(retrench_doc.get("monthly_salary", 0.0)),
                service_years=Decimal(str(retrench_doc.get("service_years", 0.0)))
            )
        return RetirementBenefits(
            leave_encashment=leave_encashment,
            gratuity=gratuity,
            vrs=vrs,
            pension=pension,
            retrenchment_compensation=retrenchment_compensation
        )

    # --- LWP DETAILS ---
    def _deserialize_lwp_details(self, lwp_doc: Dict[str, Any]) -> LWPDetails:
        return LWPDetails(
            lwp_days=lwp_doc.get("lwp_days", 0),
            total_working_days=lwp_doc.get("total_working_days", 30),
            month=lwp_doc.get("month", 1),
            year=lwp_doc.get("year", 2024)
        ) 