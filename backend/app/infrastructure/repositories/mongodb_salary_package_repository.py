"""
MongoDB Salary Package Repository
MongoDB implementation of the salary package repository
"""

from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from bson import ObjectId
from app.utils.logger import get_logger


from app.application.interfaces.repositories.salary_package_repository import SalaryPackageRepository
from app.domain.entities.taxation.taxation_record import SalaryPackageRecord
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
from app.domain.entities.taxation.salary_income import SalaryIncome, SpecificAllowances
from app.domain.entities.taxation.deductions import (
    TaxDeductions, DeductionSection80C, DeductionSection80D, DeductionSection80E, DeductionSection80G, DeductionSection80TTA_TTB, OtherDeductions
)
from app.domain.entities.taxation.perquisites import (
    Perquisites, AccommodationPerquisite, CarPerquisite, 
    LTAPerquisite, InterestFreeConcessionalLoan, ESOPPerquisite, UtilitiesPerquisite,
    FreeEducationPerquisite, LunchRefreshmentPerquisite, DomesticHelpPerquisite,
    MovableAssetUsage, MovableAssetTransfer, GiftVoucherPerquisite, 
    MonetaryBenefitsPerquisite, ClubExpensesPerquisite,
    AccommodationType, CityPopulation, CarUseType, AssetType
)
from app.domain.entities.taxation.other_income import OtherIncome, InterestIncome
from app.domain.entities.taxation.house_property_income import HousePropertyIncome
from app.domain.entities.taxation.capital_gains import CapitalGainsIncome
from app.domain.entities.taxation.retirement_benefits import (
    RetirementBenefits, LeaveEncashment, Gratuity, VRS, Pension, RetrenchmentCompensation
)
from app.domain.value_objects.money import Money
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.tax_year import TaxYear
from app.domain.services.taxation.tax_calculation_service import TaxCalculationResult
from app.infrastructure.database.database_connector import DatabaseConnector
from app.utils.table_logger import log_salary_summary
import io

logger = get_logger(__name__)


class MongoDBSalaryPackageRepository(SalaryPackageRepository):
    """MongoDB implementation of salary package repository."""
    
    def __init__(self, db_connector: DatabaseConnector):
        self.db_connector = db_connector
        self._collection_name = "monthly_package_record"
        self._connection_string = None
        self._client_options = None
    
    async def _get_collection(self, organisation_id: str = None):
        """
        Get salary package collection for specific organisation or global.
        
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
    
    async def save(self, salary_package_record: SalaryPackageRecord, organization_id: str) -> SalaryPackageRecord:
        """
        Save or update a salary package record.
        
        Args:
            salary_package_record: Salary package record to save
            
        Returns:
            SalaryPackageRecord: Saved salary package record
        """
        
        logger.info(f"Starting save operation for employee {salary_package_record.employee_id}, tax_year {salary_package_record.tax_year}")
        
        try:
            collection = await self._get_collection(organization_id)
            logger.info(f"Successfully got collection for organization {organization_id}")
            
            document = self._convert_to_document(salary_package_record)
            logger.info(f"Successfully converted record to document")
            
            # Check if record already exists - convert value objects to strings for MongoDB query
            query = {
                "employee_id": str(salary_package_record.employee_id),
                "tax_year": str(salary_package_record.tax_year)
            }
            logger.info(f"Checking for existing record with query: {query}")
            
            existing = await collection.find_one(query)
            
            if existing:
                logger.info(f"Found existing record with _id: {existing['_id']}")
                # Update existing record
                document["_id"] = existing["_id"]
                
                # Log before update
                logger.info(f"Updating existing record in database")
                result = await collection.replace_one({"_id": existing["_id"]}, document)
                logger.info(f"Update result - matched: {result.matched_count}, modified: {result.modified_count}")
                
                if result.modified_count == 0:
                    logger.warning("No documents were modified during update operation")
                else:
                    logger.info("Document successfully updated in database")
            else:
                logger.info("No existing record found, inserting new record")
                # Insert new record
                result = await collection.insert_one(document)
                logger.info(f"Insert result - inserted_id: {result.inserted_id}")
                document["_id"] = result.inserted_id
            
            # Verify the save by reading back from database
            logger.info("Verifying save operation by reading back from database")
            verification_doc = await collection.find_one(query)
            if verification_doc:
                logger.info("Successfully verified save - record exists in database")
                logger.debug(f"Verification document deductions: {verification_doc.get('deductions', {})}")
            else:
                logger.error("SAVE VERIFICATION FAILED - record not found in database after save")
            
            # Return the saved record
            logger.info("Converting saved document back to entity")
            saved_record = self._convert_to_entity(document)
            logger.info(f"Save operation completed successfully for record ID: {saved_record.salary_package_id}")
            
            return saved_record
            
        except Exception as e:
            logger.error(f"Error during save operation: {str(e)}", exc_info=True)
            raise
    
    async def get_by_id(self, salary_package_id: str, organization_id: str) -> Optional[SalaryPackageRecord]:
        """
        Get salary package record by ID.
        
        Args:
            salary_package_id: Salary package record ID
            organization_id: Organization ID
            
        Returns:
            Optional[SalaryPackageRecord]: Salary package record if found
        """
        collection = await self._get_collection(organization_id)
        document = await collection.find_one({"_id": ObjectId(salary_package_id)})
        
        if document:
            return self._convert_to_entity(document)
        return None
    
    async def get_salary_package_record(self, employee_id: str, tax_year: str, organization_id: str) -> Optional[SalaryPackageRecord]:
        """
        Get salary package record by employee ID and tax year.
        
        Args:
            employee_id: Employee ID as string
            tax_year: Tax year as string
            organization_id: Organization ID
            
        Returns:
            Optional[SalaryPackageRecord]: Salary package record if found
        """
        
        logger.debug(f"get_salary_package_record: Starting search for employee {employee_id}, tax_year {tax_year}, organization {organization_id}")
        
        try:
            logger.debug(f"get_salary_package_record: Getting collection for organization {organization_id}")
            collection = await self._get_collection(organization_id)
            
            query = {
                "employee_id": employee_id,
                "tax_year": tax_year
            }
            logger.debug(f"get_salary_package_record: Executing query: {query}")
            
            document = await collection.find_one(query)
            
            if document:
                logger.debug(f"get_salary_package_record: Found document with _id: {document.get('_id')}")
                logger.debug(f"get_salary_package_record: Document has keys: {list(document.keys())}")
                
                # Convert to entity
                logger.debug("get_salary_package_record: Converting document to entity")
                entity = self._convert_to_entity(document)
                logger.debug(f"get_salary_package_record: Successfully converted to entity")
                
                return entity
            else:
                logger.warning(f"get_salary_package_record: No document found for employee {employee_id}, tax_year {tax_year}")
                return None
                
        except Exception as e:
            logger.error(f"get_salary_package_record: Error occurred: {str(e)}", exc_info=True)
            raise
    
    async def get_by_user_and_year(self, 
                                 employee_id: EmployeeId, 
                                 tax_year: TaxYear,
                                 organization_id: str) -> Optional[SalaryPackageRecord]:
        """
        Get salary package record by user and tax year.
        
        Args:
            employee_id: User ID
            tax_year: Tax year
            organization_id: Organization ID
            
        Returns:
            Optional[SalaryPackageRecord]: Salary package record if found
        """
        collection = await self._get_collection(organization_id)
        document = await collection.find_one({
            "employee_id": str(employee_id),
            "tax_year": str(tax_year)
        })
        
        if document:
            return self._convert_to_entity(document)
        return None
    
    async def get_by_user(self, 
                        employee_id: EmployeeId, 
                        organization_id: str,
                        limit: int = 10,
                        offset: int = 0) -> List[SalaryPackageRecord]:
        """
        Get all salary package records for a user.
        
        Args:
            employee_id: User ID
            organization_id: Organization ID
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[SalaryPackageRecord]: List of salary package records
        """
        collection = await self._get_collection(organization_id)
        cursor = collection.find({"employee_id": str(employee_id)}).skip(offset).limit(limit)
        
        documents = await cursor.to_list(length=None)
        return [self._convert_to_entity(doc) for doc in documents]
    
    async def get_by_tax_year(self, 
                            tax_year: TaxYear,
                            organization_id: str,
                            limit: int = 100,
                            offset: int = 0) -> List[SalaryPackageRecord]:
        """
        Get all salary package records for a tax year.
        
        Args:
            tax_year: Tax year
            organization_id: Organization ID
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[SalaryPackageRecord]: List of salary package records
        """
        collection = await self._get_collection(organization_id)
        cursor = collection.find({"tax_year": str(tax_year)}).skip(offset).limit(limit)
        
        documents = await cursor.to_list(length=None)
        return [self._convert_to_entity(doc) for doc in documents]
    
    async def get_by_organization(self, 
                                organization_id: str,
                                limit: int = 100,
                                offset: int = 0) -> List[SalaryPackageRecord]:
        """
        Get all salary package records for an organization.
        
        Args:
            organization_id: Organization ID
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[SalaryPackageRecord]: List of salary package records
        """
        collection = await self._get_collection(organization_id)
        cursor = collection.find({}).skip(offset).limit(limit)
        
        documents = await cursor.to_list(length=None)
        return [self._convert_to_entity(doc) for doc in documents]
    
    async def search(self, 
                   organization_id: str,
                   employee_id: Optional[EmployeeId] = None,
                   tax_year: Optional[TaxYear] = None,
                   regime: Optional[str] = None,
                   is_final: Optional[bool] = None,
                   limit: int = 100,
                   offset: int = 0) -> List[SalaryPackageRecord]:
        """
        Search salary package records with filters.
        
        Args:
            organization_id: Organization ID
            employee_id: Optional user ID filter
            tax_year: Optional tax year filter
            regime: Optional regime filter ('old' or 'new')
            is_final: Optional finalization status filter
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[SalaryPackageRecord]: List of matching salary package records
        """
        collection = await self._get_collection(organization_id)
        
        # Build query filter
        query_filter = {}
        
        if employee_id:
            query_filter["employee_id"] = str(employee_id)
        
        if tax_year:
            query_filter["tax_year"] = str(tax_year)
        
        if regime:
            query_filter["regime.regime_type"] = regime
        
        if is_final is not None:
            query_filter["is_final"] = is_final
        
        cursor = collection.find(query_filter).skip(offset).limit(limit)
        documents = await cursor.to_list(length=None)
        
        return [self._convert_to_entity(doc) for doc in documents]
    
    async def count(self, 
                  organization_id: str,
                  employee_id: Optional[EmployeeId] = None,
                  tax_year: Optional[TaxYear] = None,
                  regime: Optional[str] = None,
                  is_final: Optional[bool] = None) -> int:
        """
        Count salary package records with filters.
        
        Args:
            organization_id: Organization ID
            employee_id: Optional user ID filter
            tax_year: Optional tax year filter
            regime: Optional regime filter
            is_final: Optional finalization status filter
            
        Returns:
            int: Number of matching records
        """
        collection = await self._get_collection(organization_id)
        
        # Build query filter
        query_filter = {}
        
        if employee_id:
            query_filter["employee_id"] = str(employee_id)
        
        if tax_year:
            query_filter["tax_year"] = str(tax_year)
        
        if regime:
            query_filter["regime.regime_type"] = regime
        
        if is_final is not None:
            query_filter["is_final"] = is_final
        
        return await collection.count_documents(query_filter)
    
    async def delete(self, salary_package_id: str, organization_id: str) -> bool:
        """
        Delete a salary package record.
        
        Args:
            salary_package_id: Salary package record ID
            organization_id: Organization ID
            
        Returns:
            bool: True if record was deleted
        """
        collection = await self._get_collection(organization_id)
        result = await collection.delete_one({"_id": ObjectId(salary_package_id)})
        return result.deleted_count > 0
    
    async def exists(self, 
                   employee_id: EmployeeId, 
                   tax_year: TaxYear,
                   organization_id: str) -> bool:
        """
        Check if salary package record exists for user and tax year.
        
        Args:
            employee_id: User ID
            tax_year: Tax year
            organization_id: Organization ID
            
        Returns:
            bool: True if record exists
        """
        collection = await self._get_collection(organization_id)
        document = await collection.find_one({
            "employee_id": str(employee_id),
            "tax_year": str(tax_year)
        })
        return document is not None
    
    def _convert_to_document(self, record: SalaryPackageRecord) -> dict:
        """Convert salary package record to MongoDB document."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.debug(f"Converting salary package record to document for employee {record.employee_id}")
        
        # Serialize deductions
        deductions_doc = self._serialize_deductions(record.deductions)
        
        document = {
            # Core identification
            "employee_id": str(record.employee_id),
            "tax_year": str(record.tax_year),
            "age": record.age,
            "is_government_employee": record.is_government_employee,
            "is_regime_update_allowed": record.is_regime_update_allowed,  # <--- Add this line
            
            # Core data - Salary incomes (list)
            "salary_incomes": [self._serialize_salary_income(salary) for salary in record.salary_incomes],
            
            # Core data - Tax deductions
            "deductions": deductions_doc,
            
            # Tax regime
            "regime": {
                "regime_type": record.regime.regime_type.value
            },
            
            # Comprehensive income components (optional)
            "perquisites": self._serialize_perquisites(record.perquisites),
            "retirement_benefits": self._serialize_retirement_benefits(record.retirement_benefits),
            "other_income": self._serialize_other_income(record.other_income),
            
            # Calculation results
            "calculation_result": self._serialize_calculation_result(record.calculation_result),
            "last_calculated_at": record.last_calculated_at.isoformat() if record.last_calculated_at else None,
            
            # Metadata
            "is_final": record.is_final,
            "submitted_at": record.submitted_at.isoformat() if record.submitted_at else None,
            
            # Audit fields
            "created_at": record.created_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
            "version": record.version,

            # Monthly salary records
            "monthly_salary_records": [self._serialize_monthly_salary(salary) for salary in record.monthly_salary_records],
            "summary_data_text": record.summary_data_txt if hasattr(record, 'summary_data_txt') else None,
        }
     
        logger.debug(f"Successfully converted record to document with {len(document)} fields")
        return document
    
    def _convert_to_entity(self, document: dict) -> SalaryPackageRecord:
        """Convert MongoDB document to salary package record."""
        from datetime import datetime
        
        # Deserialize salary incomes (list)
        salary_incomes = [self._deserialize_salary_income(salary_doc) for salary_doc in document.get("salary_incomes", [])]
        
        # Deserialize tax deductions
        deductions = self._deserialize_deductions(document.get("deductions", {}))
        
        # Deserialize regime
        regime = TaxRegime(TaxRegimeType(document["regime"]["regime_type"]))
        
        # Deserialize calculation result if present
        calculation_result = self._deserialize_calculation_result(document.get("calculation_result"))

        # Deserialize monthly_salary_records
        monthly_salary_records = [self._deserialize_monthly_salary(ms_doc) for ms_doc in document.get("monthly_salary_records", [])]
        
        # Deserialize lwps (list of LWPDetails)
        lwps_docs = document.get("lwps", [])
        if lwps_docs:
            lwps = [self._deserialize_lwp_details(lwp_doc) for lwp_doc in lwps_docs]
        else:
            from app.domain.entities.taxation.lwp_details import LWPDetails
            lwps = [LWPDetails(month=i+1) for i in range(12)]
        
        # Create SalaryPackageRecord
        record = SalaryPackageRecord(
            employee_id=EmployeeId(document["employee_id"]),
            tax_year=TaxYear.from_string(document["tax_year"]),
            age=document["age"],
            is_government_employee=document.get("is_government_employee", False),
            is_regime_update_allowed=document.get("is_regime_update_allowed", True),  # <--- Add this line
            regime=regime,
            salary_incomes=salary_incomes,
            deductions=deductions,
            
            # Optional comprehensive income components
            perquisites=self._deserialize_perquisites(document.get("perquisites")),
            retirement_benefits=self._deserialize_retirement_benefits(document.get("retirement_benefits")),
            other_income=self._deserialize_other_income(document.get("other_income")),
            
            # Calculated fields
            calculation_result=calculation_result,
            last_calculated_at=datetime.fromisoformat(document["last_calculated_at"]) if document.get("last_calculated_at") else None,
            
            # Metadata
            is_final=document.get("is_final", False),
            submitted_at=datetime.fromisoformat(document["submitted_at"]) if document.get("submitted_at") else None,
            
            # Audit fields
            created_at=datetime.fromisoformat(document["created_at"]),
            updated_at=datetime.fromisoformat(document["updated_at"]),
            version=document.get("version", 1),

            # Monthly salary records
            monthly_salary_records=monthly_salary_records,
        )
        
        # Attach summary_data_txt for export
        record.summary_data_txt = document.get('summary_data_text')
        
        return record

    def _deserialize_monthly_salary(self, ms_doc: dict):
        """Deserialize a single monthly salary record from document format."""
        from app.domain.value_objects.employee_id import EmployeeId
        from app.domain.value_objects.tax_year import TaxYear
        from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
        from app.domain.value_objects.money import Money
        from app.domain.entities.taxation.monthly_salary import MonthlySalary
        from datetime import datetime
        from datetime import date as dt_date
        transfer_date = None
        if ms_doc.get("transfer_date"):
            try:
                transfer_date = dt_date.fromisoformat(ms_doc["transfer_date"])
            except Exception:
                transfer_date = None
        return MonthlySalary(
            employee_id=EmployeeId(ms_doc["employee_id"]),
            month=ms_doc["month"],
            year=ms_doc["year"],
            salary=self._deserialize_salary_income(ms_doc.get("salary", {})),
            perquisites_payouts=self._deserialize_perquisites_payouts(ms_doc.get("perquisites_payouts", {})),
            deductions=self._deserialize_deductions(ms_doc.get("deductions", {})),
            retirement=self._deserialize_retirement_benefits(ms_doc.get("retirement", {})),
            lwp=self._deserialize_lwp_details(ms_doc.get("lwp", {})),
            tax_year=TaxYear.from_string(ms_doc["tax_year"]),
            tax_regime=TaxRegime(TaxRegimeType(ms_doc["tax_regime"])),
            tax_amount=Money.from_float(ms_doc.get("tax_amount", 0.0)),
            net_salary=Money.from_float(ms_doc.get("net_salary", 0.0)),
            one_time_arrear=Money.from_float(ms_doc.get("one_time_arrear", 0.0)),
            one_time_bonus=Money.from_float(ms_doc.get("one_time_bonus", 0.0)),
            tds_status=self._deserialize_tds_status(ms_doc.get("tds_status", {})) if hasattr(self, '_deserialize_tds_status') and ms_doc.get("tds_status") else None,
            payout_status=self._deserialize_payout_status(ms_doc.get("payout_status", {})) if hasattr(self, '_deserialize_payout_status') and ms_doc.get("payout_status") else None,
            pf_status=self._deserialize_pf_status(ms_doc.get("pf_status", {})) if hasattr(self, '_deserialize_pf_status') and ms_doc.get("pf_status") else None,
        )
    
    def _serialize_specific_allowances(self, specific_allowances: SpecificAllowances) -> dict:
        """Serialize specific allowances to document format."""
        if not specific_allowances:
            return {}
        
        return {
            "hills_allowance": specific_allowances.monthly_hills_allowance.to_float(),
            "hills_exemption_limit": specific_allowances.monthly_hills_exemption_limit.to_float(),

            "border_allowance": specific_allowances.monthly_border_allowance.to_float(),
            "border_exemption_limit": specific_allowances.monthly_border_exemption_limit.to_float(),

            "transport_employee_allowance": specific_allowances.transport_employee_allowance.to_float(),
            
            "children_education_allowance": specific_allowances.children_education_allowance.to_float(),
            "children_education_count": specific_allowances.children_education_count,

            "hostel_allowance": specific_allowances.hostel_allowance.to_float(),
            "children_hostel_count": specific_allowances.children_hostel_count,

            "disabled_transport_allowance": specific_allowances.disabled_transport_allowance.to_float(),
            "is_disabled": specific_allowances.is_disabled,

            "underground_mines_allowance": specific_allowances.underground_mines_allowance.to_float(),
            "mine_work_months": specific_allowances.mine_work_months,

            "government_entertainment_allowance": specific_allowances.government_entertainment_allowance.to_float(),

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

            "govt_employees_outside_india_allowance": specific_allowances.govt_employees_outside_india_allowance.to_float(),
            "supreme_high_court_judges_allowance": specific_allowances.supreme_high_court_judges_allowance.to_float(),
            "judge_compensatory_allowance": specific_allowances.judge_compensatory_allowance.to_float(),
            "section_10_14_special_allowances": specific_allowances.section_10_14_special_allowances.to_float(),
            "travel_on_tour_allowance": specific_allowances.travel_on_tour_allowance.to_float(),
            "tour_daily_charge_allowance": specific_allowances.tour_daily_charge_allowance.to_float(),
            "conveyance_in_performace_of_duties": specific_allowances.conveyance_in_performace_of_duties.to_float(),
            "helper_in_performace_of_duties": specific_allowances.helper_in_performace_of_duties.to_float(),
            "academic_research": specific_allowances.academic_research.to_float(),
            "uniform_allowance": specific_allowances.uniform_allowance.to_float()
        }

    # Serialization methods (reuse from MongoDBTaxationRepository)
    def _serialize_salary_income(self, salary_income):
        if salary_income is None:
            return None
        return {
            "basic_salary": salary_income.basic_salary.to_float() if salary_income.basic_salary else 0.0,
            "dearness_allowance": salary_income.dearness_allowance.to_float() if salary_income.dearness_allowance else 0.0,
            "hra_provided": salary_income.hra_provided.to_float() if salary_income.hra_provided else 0.0,
            "epf_employee": salary_income.epf_employee.to_float() if hasattr(salary_income, 'epf_employee') and salary_income.epf_employee else 0.0,  # Added
            "epf_employer": salary_income.epf_employer.to_float() if hasattr(salary_income, 'epf_employer') and salary_income.epf_employer else 0.0,  # Added
            "eps_employee": salary_income.eps_employee.to_float() if salary_income.eps_employee else 0.0,
            "eps_employer": salary_income.eps_employer.to_float() if salary_income.eps_employer else 0.0,
            "esi_contribution": salary_income.esi_contribution.to_float() if salary_income.esi_contribution else 0.0,
            "vps_employee": salary_income.vps_employee.to_float() if salary_income.vps_employee else 0.0,
            "special_allowance": salary_income.special_allowance.to_float() if salary_income.special_allowance else 0.0,
            "commission": salary_income.commission.to_float() if salary_income.commission else 0.0,
            "effective_from": salary_income.effective_from.isoformat() if salary_income.effective_from else None,
            "effective_till": salary_income.effective_till.isoformat() if salary_income.effective_till else None,
            "gross_salary": salary_income.calculate_gross_salary().to_float() if hasattr(salary_income, 'calculate_gross_salary') else 0.0,
            "specific_allowances": self._serialize_specific_allowances(salary_income.specific_allowances) if salary_income.specific_allowances else None
        }

    def _serialize_deductions(self, deductions):
        return {
            "section_80c": self._serialize_section_80c(deductions.section_80c) if deductions.section_80c else None,
            "section_80d": self._serialize_section_80d(deductions.section_80d) if deductions.section_80d else None,
            "section_80g": self._serialize_section_80g(deductions.section_80g) if deductions.section_80g else None,
            "section_80e": self._serialize_section_80e(deductions.section_80e) if deductions.section_80e else None,
            "section_80tta_ttb": self._serialize_section_80tta_ttb(deductions.section_80tta_ttb) if deductions.section_80tta_ttb else None,
            "other_deductions": self._serialize_other_deductions(deductions.other_deductions) if deductions.other_deductions else None
        }

    def _serialize_section_80c(self, section_80c):
        if not section_80c:
            return {}
        return {
            "life_insurance_premium": section_80c.life_insurance_premium.to_float() if section_80c.life_insurance_premium else 0.0,
            "nsc_investment": section_80c.nsc_investment.to_float() if section_80c.nsc_investment else 0.0,
            "tax_saving_fd": section_80c.tax_saving_fd.to_float() if section_80c.tax_saving_fd else 0.0,
            "elss_investment": section_80c.elss_investment.to_float() if section_80c.elss_investment else 0.0,
            "home_loan_principal": section_80c.home_loan_principal.to_float() if section_80c.home_loan_principal else 0.0,
            "tuition_fees": section_80c.tuition_fees.to_float() if section_80c.tuition_fees else 0.0,
            "ulip_premium": section_80c.ulip_premium.to_float() if section_80c.ulip_premium else 0.0,
            "sukanya_samriddhi": section_80c.sukanya_samriddhi.to_float() if section_80c.sukanya_samriddhi else 0.0,
            "stamp_duty_property": section_80c.stamp_duty_property.to_float() if section_80c.stamp_duty_property else 0.0,
            "senior_citizen_savings": section_80c.senior_citizen_savings.to_float() if section_80c.senior_citizen_savings else 0.0,
            "other_80c_investments": section_80c.other_80c_investments.to_float() if section_80c.other_80c_investments else 0.0,
            "total_investment": section_80c.calculate_total_investment().to_float() if hasattr(section_80c, 'calculate_total_investment') else 0.0
        }

    def _serialize_section_80d(self, section_80d):
        if not section_80d:
            return {}
        return {
            "self_family_premium": section_80d.self_family_premium.to_float() if section_80d.self_family_premium else 0.0,
            "parent_premium": section_80d.parent_premium.to_float() if section_80d.parent_premium else 0.0,
            "preventive_health_checkup": section_80d.preventive_health_checkup.to_float() if section_80d.preventive_health_checkup else 0.0,
            "parent_age": section_80d.parent_age
        }

    def _serialize_section_80g(self, section_80g):
        if not section_80g:
            return {}
        return {
            "pm_relief_fund": section_80g.pm_relief_fund.to_float() if section_80g.pm_relief_fund else 0.0,
            "national_defence_fund": section_80g.national_defence_fund.to_float() if section_80g.national_defence_fund else 0.0,
            "national_foundation_communal_harmony": section_80g.national_foundation_communal_harmony.to_float() if section_80g.national_foundation_communal_harmony else 0.0,
            "zila_saksharta_samiti": section_80g.zila_saksharta_samiti.to_float() if section_80g.zila_saksharta_samiti else 0.0,
            "national_illness_assistance_fund": section_80g.national_illness_assistance_fund.to_float() if section_80g.national_illness_assistance_fund else 0.0,
            "national_blood_transfusion_council": section_80g.national_blood_transfusion_council.to_float() if section_80g.national_blood_transfusion_council else 0.0,
            "national_trust_autism_fund": section_80g.national_trust_autism_fund.to_float() if section_80g.national_trust_autism_fund else 0.0,
            "national_sports_fund": section_80g.national_sports_fund.to_float() if section_80g.national_sports_fund else 0.0,
            "national_cultural_fund": section_80g.national_cultural_fund.to_float() if section_80g.national_cultural_fund else 0.0,
            "technology_development_fund": section_80g.technology_development_fund.to_float() if section_80g.technology_development_fund else 0.0,
            "national_children_fund": section_80g.national_children_fund.to_float() if section_80g.national_children_fund else 0.0,
            "cm_relief_fund": section_80g.cm_relief_fund.to_float() if section_80g.cm_relief_fund else 0.0,
            "army_naval_air_force_funds": section_80g.army_naval_air_force_funds.to_float() if section_80g.army_naval_air_force_funds else 0.0,
            "swachh_bharat_kosh": section_80g.swachh_bharat_kosh.to_float() if section_80g.swachh_bharat_kosh else 0.0,
            "clean_ganga_fund": section_80g.clean_ganga_fund.to_float() if section_80g.clean_ganga_fund else 0.0,
            "drug_abuse_control_fund": section_80g.drug_abuse_control_fund.to_float() if section_80g.drug_abuse_control_fund else 0.0,
            "other_100_percent_wo_limit": section_80g.other_100_percent_wo_limit.to_float() if section_80g.other_100_percent_wo_limit else 0.0,
            "jn_memorial_fund": section_80g.jn_memorial_fund.to_float() if section_80g.jn_memorial_fund else 0.0,
            "pm_drought_relief": section_80g.pm_drought_relief.to_float() if section_80g.pm_drought_relief else 0.0,
            "indira_gandhi_memorial_trust": section_80g.indira_gandhi_memorial_trust.to_float() if section_80g.indira_gandhi_memorial_trust else 0.0,
            "rajiv_gandhi_foundation": section_80g.rajiv_gandhi_foundation.to_float() if section_80g.rajiv_gandhi_foundation else 0.0,
            "other_50_percent_wo_limit": section_80g.other_50_percent_wo_limit.to_float() if section_80g.other_50_percent_wo_limit else 0.0,
            "family_planning_donation": section_80g.family_planning_donation.to_float() if section_80g.family_planning_donation else 0.0,
            "indian_olympic_association": section_80g.indian_olympic_association.to_float() if section_80g.indian_olympic_association else 0.0,
            "other_100_percent_w_limit": section_80g.other_100_percent_w_limit.to_float() if section_80g.other_100_percent_w_limit else 0.0,
            "govt_charitable_donations": section_80g.govt_charitable_donations.to_float() if section_80g.govt_charitable_donations else 0.0,
            "housing_authorities_donations": section_80g.housing_authorities_donations.to_float() if section_80g.housing_authorities_donations else 0.0,
            "religious_renovation_donations": section_80g.religious_renovation_donations.to_float() if section_80g.religious_renovation_donations else 0.0,
            "other_charitable_donations": section_80g.other_charitable_donations.to_float() if section_80g.other_charitable_donations else 0.0,
            "other_50_percent_w_limit": section_80g.other_50_percent_w_limit.to_float() if section_80g.other_50_percent_w_limit else 0.0
        }

    def _serialize_section_80e(self, section_80e):
        if not section_80e:
            return {}
        return {
            "education_loan_interest": section_80e.education_loan_interest.to_float() if section_80e.education_loan_interest else 0.0,
            "relation": section_80e.relation.value if hasattr(section_80e, 'relation') and section_80e.relation else 'SELF'
        }

    def _serialize_section_80tta_ttb(self, section_80tta_ttb):
        if not section_80tta_ttb:
            return {}
        return {
            "savings_interest": section_80tta_ttb.savings_interest.to_float() if section_80tta_ttb.savings_interest else 0.0,
            "fd_interest": section_80tta_ttb.fd_interest.to_float() if section_80tta_ttb.fd_interest else 0.0,
            "rd_interest": section_80tta_ttb.rd_interest.to_float() if section_80tta_ttb.rd_interest else 0.0,
            "post_office_interest": section_80tta_ttb.post_office_interest.to_float() if section_80tta_ttb.post_office_interest else 0.0,
            "age": section_80tta_ttb.age
        }

    def _serialize_other_deductions(self, other_deductions):
        if not other_deductions:
            return {}
        return {
            "other_deductions": other_deductions.other_deductions.to_float() if other_deductions.other_deductions else 0.0,
            "total": other_deductions.calculate_total().to_float() if hasattr(other_deductions, 'calculate_total') else 0.0
        }
    
    def _serialize_perquisites(self, perquisites: Optional[Perquisites]) -> Optional[dict]:
        """Serialize perquisites to document format."""
        if not perquisites:
            return None
        
        # Get detailed breakdown
        
        return {
            "has_perquisites": True,
            
            # Core perquisites
            "accommodation": {
                "has_accommodation": perquisites.accommodation is not None,
                "accommodation_type": perquisites.accommodation.accommodation_type.value if perquisites.accommodation else None,
                "city_population": perquisites.accommodation.city_population.value if perquisites.accommodation else None,
                "license_fees": perquisites.accommodation.license_fees.to_float() if perquisites.accommodation else 0.0,
                "employee_rent_payment": perquisites.accommodation.employee_rent_payment.to_float() if perquisites.accommodation else 0.0,
                "rent_paid_by_employer": perquisites.accommodation.rent_paid_by_employer.to_float() if perquisites.accommodation else 0.0,
                "hotel_charges": perquisites.accommodation.hotel_charges.to_float() if perquisites.accommodation else 0.0,
                "stay_days": perquisites.accommodation.stay_days if perquisites.accommodation else 0,
                "furniture_cost": perquisites.accommodation.furniture_cost.to_float() if perquisites.accommodation else 0.0,
                "furniture_employee_payment": perquisites.accommodation.furniture_employee_payment.to_float() if perquisites.accommodation else 0.0,
                "is_furniture_owned_by_employer": perquisites.accommodation.is_furniture_owned_by_employer if perquisites.accommodation else False,
            },
            
            "car": {
                "has_car": perquisites.car is not None,
                "car_use_type": perquisites.car.car_use_type.value if perquisites.car else None,
                "engine_capacity_cc": perquisites.car.engine_capacity_cc if perquisites.car else 0,
                "months_used": perquisites.car.months_used if perquisites.car else 0,
                "months_used_other_vehicle": perquisites.car.months_used_other_vehicle if perquisites.car else 0,
                "car_cost_to_employer": perquisites.car.car_cost_to_employer.to_float() if perquisites.car else 0.0,
                "other_vehicle_cost": perquisites.car.other_vehicle_cost.to_float() if perquisites.car else 0.0,
                "has_expense_reimbursement": perquisites.car.has_expense_reimbursement if perquisites.car else False,
                "driver_provided": perquisites.car.driver_provided if perquisites.car else False,
            },
            
            "lta": {
                "has_lta": perquisites.lta is not None,
                "lta_amount_claimed": perquisites.lta.lta_amount_claimed.to_float() if perquisites.lta else 0.0,
                "lta_claimed_count": perquisites.lta.lta_claimed_count if perquisites.lta else 0,
                "public_transport_cost": perquisites.lta.public_transport_cost.to_float() if perquisites.lta else 0.0,
                "travel_mode": perquisites.lta.travel_mode if perquisites.lta else "Air",
                "is_monthly_paid": perquisites.lta.is_monthly_paid if perquisites.lta else False,
            },
            
            # Financial perquisites
            "interest_free_loan": {
                "has_loan": perquisites.interest_free_loan is not None,
                "emi_amount": perquisites.interest_free_loan.emi_amount.to_float() if perquisites.interest_free_loan else 0.0,
                "loan_amount": perquisites.interest_free_loan.loan_amount.to_float() if perquisites.interest_free_loan else 0.0,
                "outstanding_amount": perquisites.interest_free_loan.outstanding_amount.to_float() if perquisites.interest_free_loan else 0.0,
                "company_interest_rate": float(perquisites.interest_free_loan.company_interest_rate) if perquisites.interest_free_loan else 0.0,
                "sbi_interest_rate": float(perquisites.interest_free_loan.sbi_interest_rate) if perquisites.interest_free_loan else 0.0,
                "loan_type": perquisites.interest_free_loan.loan_type if perquisites.interest_free_loan else "Personal",
                "loan_start_date": perquisites.interest_free_loan.loan_start_date.isoformat() if perquisites.interest_free_loan and perquisites.interest_free_loan.loan_start_date else None,
            },
            
            "esop": {
                "has_esop": perquisites.esop is not None,
                "shares_exercised": perquisites.esop.shares_exercised if perquisites.esop else 0,
                "exercise_price": perquisites.esop.exercise_price.to_float() if perquisites.esop else 0.0,
                "allotment_price": perquisites.esop.allotment_price.to_float() if perquisites.esop else 0.0,
            },
            
            # Utilities and facilities
            "utilities": {
                "has_utilities": perquisites.utilities is not None,
                "gas_paid_by_employer": perquisites.utilities.gas_paid_by_employer.to_float() if perquisites.utilities else 0.0,
                "electricity_paid_by_employer": perquisites.utilities.electricity_paid_by_employer.to_float() if perquisites.utilities else 0.0,
                "water_paid_by_employer": perquisites.utilities.water_paid_by_employer.to_float() if perquisites.utilities else 0.0,
                "gas_paid_by_employee": perquisites.utilities.gas_paid_by_employee.to_float() if perquisites.utilities else 0.0,
                "electricity_paid_by_employee": perquisites.utilities.electricity_paid_by_employee.to_float() if perquisites.utilities else 0.0,
                "water_paid_by_employee": perquisites.utilities.water_paid_by_employee.to_float() if perquisites.utilities else 0.0,
                "is_gas_manufactured_by_employer": perquisites.utilities.is_gas_manufactured_by_employer if perquisites.utilities else False,
                "is_electricity_manufactured_by_employer": perquisites.utilities.is_electricity_manufactured_by_employer if perquisites.utilities else False,
                "is_water_manufactured_by_employer": perquisites.utilities.is_water_manufactured_by_employer if perquisites.utilities else False,
            },
            
            "free_education": {
                "has_free_education": perquisites.free_education is not None,
                "monthly_expenses_child1": perquisites.free_education.monthly_expenses_child1.to_float() if perquisites.free_education else 0.0,
                "monthly_expenses_child2": perquisites.free_education.monthly_expenses_child2.to_float() if perquisites.free_education else 0.0,
                "months_child1": perquisites.free_education.months_child1 if perquisites.free_education else 0,
                "months_child2": perquisites.free_education.months_child2 if perquisites.free_education else 0,
                "employer_maintained_1st_child": perquisites.free_education.employer_maintained_1st_child if perquisites.free_education else False,
                "employer_maintained_2nd_child": perquisites.free_education.employer_maintained_2nd_child if perquisites.free_education else False,
            },
            
            "lunch_refreshment": {
                "has_lunch_refreshment": perquisites.lunch_refreshment is not None,
                "employer_cost": perquisites.lunch_refreshment.employer_cost.to_float() if perquisites.lunch_refreshment else 0.0,
                "employee_payment": perquisites.lunch_refreshment.employee_payment.to_float() if perquisites.lunch_refreshment else 0.0,
                "meal_days_per_year": perquisites.lunch_refreshment.meal_days_per_year if perquisites.lunch_refreshment else 0,
            },
            
            "domestic_help": {
                "has_domestic_help": perquisites.domestic_help is not None,
                "domestic_help_paid_by_employer": perquisites.domestic_help.domestic_help_paid_by_employer.to_float() if perquisites.domestic_help else 0.0,
                "domestic_help_paid_by_employee": perquisites.domestic_help.domestic_help_paid_by_employee.to_float() if perquisites.domestic_help else 0.0,    
            },
            
            # Asset-related perquisites
            "movable_asset_usage": {
                "has_movable_asset_usage": perquisites.movable_asset_usage is not None,
                "asset_type": perquisites.movable_asset_usage.asset_type.value if perquisites.movable_asset_usage else None,
                "asset_value": perquisites.movable_asset_usage.asset_value.to_float() if perquisites.movable_asset_usage else 0.0,
                "employee_payment": perquisites.movable_asset_usage.employee_payment.to_float() if perquisites.movable_asset_usage else 0.0,
                "is_employer_owned": perquisites.movable_asset_usage.is_employer_owned if perquisites.movable_asset_usage else False,
            },
            
            "movable_asset_transfer": {
                "has_movable_asset_transfer": perquisites.movable_asset_transfer is not None,
                "asset_type": perquisites.movable_asset_transfer.asset_type.value if perquisites.movable_asset_transfer else None,
                "asset_cost": perquisites.movable_asset_transfer.asset_cost.to_float() if perquisites.movable_asset_transfer else 0.0,
                "years_of_use": perquisites.movable_asset_transfer.years_of_use if perquisites.movable_asset_transfer else 0,
                "employee_payment": perquisites.movable_asset_transfer.employee_payment.to_float() if perquisites.movable_asset_transfer else 0.0,
            },
            
            # Miscellaneous perquisites
            "gift_voucher": {
                "has_gift_voucher": perquisites.gift_voucher is not None,
                "gift_voucher_amount": perquisites.gift_voucher.gift_voucher_amount.to_float() if perquisites.gift_voucher else 0.0,
            },
            
            "monetary_benefits": {
                "has_monetary_benefits": perquisites.monetary_benefits is not None,
                "monetary_amount_paid_by_employer": perquisites.monetary_benefits.monetary_amount_paid_by_employer.to_float() if perquisites.monetary_benefits else 0.0,
                "expenditure_for_official_purpose": perquisites.monetary_benefits.expenditure_for_official_purpose.to_float() if perquisites.monetary_benefits else 0.0,
                "amount_paid_by_employee": perquisites.monetary_benefits.amount_paid_by_employee.to_float() if perquisites.monetary_benefits else 0.0,
            },
            
            "club_expenses": {
                "has_club_expenses": perquisites.club_expenses is not None,
                "club_expenses_paid_by_employer": perquisites.club_expenses.club_expenses_paid_by_employer.to_float() if perquisites.club_expenses else 0.0,
                "club_expenses_paid_by_employee": perquisites.club_expenses.club_expenses_paid_by_employee.to_float() if perquisites.club_expenses else 0.0,
                "club_expenses_for_official_purpose": perquisites.club_expenses.club_expenses_for_official_purpose.to_float() if perquisites.club_expenses else 0.0,
            }
        }
    
    def _serialize_retirement_benefits(self, retirement_benefits: Optional[RetirementBenefits]) -> Optional[dict]:
        """Serialize retirement benefits to document format."""
        if not retirement_benefits:
            return None
        
        doc = {
            "has_retirement_benefits": True,
            
            # Leave encashment
            "leave_encashment": {
                "has_leave_encashment": retirement_benefits.leave_encashment is not None,
                "leave_encashment_amount": retirement_benefits.leave_encashment.leave_encashment_amount.to_float() if retirement_benefits.leave_encashment else 0.0,
                "average_monthly_salary": retirement_benefits.leave_encashment.average_monthly_salary.to_float() if retirement_benefits.leave_encashment else 0.0,
                "leave_days_encashed": retirement_benefits.leave_encashment.leave_days_encashed if retirement_benefits.leave_encashment else 0,
                "is_deceased": retirement_benefits.leave_encashment.is_deceased if retirement_benefits.leave_encashment else False,
                "during_employment": retirement_benefits.leave_encashment.during_employment if retirement_benefits.leave_encashment else False,
            },
            
            # Gratuity
            "gratuity": {
                "has_gratuity": retirement_benefits.gratuity is not None,
                "gratuity_amount": retirement_benefits.gratuity.gratuity_amount.to_float() if retirement_benefits.gratuity else 0.0,
                "monthly_salary": retirement_benefits.gratuity.monthly_salary.to_float() if retirement_benefits.gratuity else 0.0,
                "service_years": float(retirement_benefits.gratuity.service_years) if retirement_benefits.gratuity else 0.0,
            },
            
            # VRS
            "vrs": {
                "has_vrs": retirement_benefits.vrs is not None,
                "vrs_amount": retirement_benefits.vrs.vrs_amount.to_float() if retirement_benefits.vrs else 0.0,
                "monthly_salary": retirement_benefits.vrs.monthly_salary.to_float() if retirement_benefits.vrs else 0.0,
                "service_years": float(retirement_benefits.vrs.service_years) if retirement_benefits.vrs else 0.0,
            },
            
            # Pension
            "pension": {
                "has_pension": retirement_benefits.pension is not None,
                "regular_pension": retirement_benefits.pension.regular_pension.to_float() if retirement_benefits.pension else 0.0,
                "commuted_pension": retirement_benefits.pension.commuted_pension.to_float() if retirement_benefits.pension else 0.0,
                "total_pension": retirement_benefits.pension.total_pension.to_float() if retirement_benefits.pension else 0.0,
                "gratuity_received": retirement_benefits.pension.gratuity_received if retirement_benefits.pension else False,
            },
            
            # Retrenchment compensation
            "retrenchment_compensation": {
                "has_retrenchment_compensation": retirement_benefits.retrenchment_compensation is not None,
                "retrenchment_amount": retirement_benefits.retrenchment_compensation.retrenchment_amount.to_float() if retirement_benefits.retrenchment_compensation else 0.0,
                "monthly_salary": retirement_benefits.retrenchment_compensation.monthly_salary.to_float() if retirement_benefits.retrenchment_compensation else 0.0,
                "service_years": float(retirement_benefits.retrenchment_compensation.service_years) if retirement_benefits.retrenchment_compensation else 0.0,
            }
        }
        # Serialize monthly_salary_paid
        if hasattr(retirement_benefits, 'monthly_salary_paid') and retirement_benefits.monthly_salary_paid is not None:
            doc["monthly_salary_paid"] = [float(m.amount) for m in retirement_benefits.monthly_salary_paid]
        return doc
    
    def _serialize_other_income(self, other_income: Optional[OtherIncome]) -> Optional[dict]:
        """Serialize other income to document format."""
        if not other_income:
            return None
        
        return {
            "has_other_income": True,
            
            # Interest income
            "interest_income": {
                "has_interest_income": other_income.interest_income is not None,
                "savings_account_interest": other_income.interest_income.savings_account_interest.to_float() if other_income.interest_income else 0.0,
                "fixed_deposit_interest": other_income.interest_income.fixed_deposit_interest.to_float() if other_income.interest_income else 0.0,
                "recurring_deposit_interest": other_income.interest_income.recurring_deposit_interest.to_float() if other_income.interest_income else 0.0,
                "post_office_interest": other_income.interest_income.post_office_interest.to_float() if other_income.interest_income else 0.0,
            },
            
            # House property income
            "house_property_income": {
                "has_house_property_income": other_income.house_property_income is not None,
                "property_type": other_income.house_property_income.property_type.value if other_income.house_property_income else None,
                "address": other_income.house_property_income.address if other_income.house_property_income else "",
                "annual_rent_received": other_income.house_property_income.annual_rent_received.to_float() if other_income.house_property_income else 0.0,
                "municipal_taxes_paid": other_income.house_property_income.municipal_taxes_paid.to_float() if other_income.house_property_income else 0.0,
                "home_loan_interest": other_income.house_property_income.home_loan_interest.to_float() if other_income.house_property_income else 0.0,
                "pre_construction_interest": other_income.house_property_income.pre_construction_interest.to_float() if other_income.house_property_income else 0.0,
            },
            
            # Capital gains income
            "capital_gains_income": {
                "has_capital_gains_income": other_income.capital_gains_income is not None,
                "stcg_111a_equity_stt": other_income.capital_gains_income.stcg_111a_equity_stt.to_float() if other_income.capital_gains_income else 0.0,
                "stcg_other_assets": other_income.capital_gains_income.stcg_other_assets.to_float() if other_income.capital_gains_income else 0.0,
                "stcg_debt_mf": other_income.capital_gains_income.stcg_debt_mf.to_float() if other_income.capital_gains_income else 0.0,
                "ltcg_112a_equity_stt": other_income.capital_gains_income.ltcg_112a_equity_stt.to_float() if other_income.capital_gains_income else 0.0,
                "ltcg_other_assets": other_income.capital_gains_income.ltcg_other_assets.to_float() if other_income.capital_gains_income else 0.0,
                "ltcg_debt_mf": other_income.capital_gains_income.ltcg_debt_mf.to_float() if other_income.capital_gains_income else 0.0,
            },
            
            # Other miscellaneous income
            "dividend_income": other_income.dividend_income.to_float(),
            "gifts_received": other_income.gifts_received.to_float(),
            "business_professional_income": other_income.business_professional_income.to_float(),
            "other_miscellaneous_income": other_income.other_miscellaneous_income.to_float()
        }
    
    def _serialize_calculation_result(self, calculation_result: Optional[TaxCalculationResult]) -> Optional[dict]:
        """Serialize calculation result to document format."""
        if not calculation_result:
            return None
        
        return {
            "total_income": calculation_result.total_income.to_float(),
            "total_exemptions": calculation_result.total_exemptions.to_float(),
            "total_deductions": calculation_result.total_deductions.to_float(),
            "taxable_income": calculation_result.taxable_income.to_float(),
            "tax_liability": calculation_result.tax_liability.to_float(),
            "professional_tax": calculation_result.professional_tax.to_float(),
            "cess": calculation_result.cess.to_float(),
            "surcharge": calculation_result.surcharge.to_float(),       
            "tax_breakdown": calculation_result.tax_breakdown,
            "regime_comparison": calculation_result.regime_comparison
        }
    
    def _deserialize_specific_allowances(self, specific_allowances_doc: dict) -> SpecificAllowances:
        """Deserialize specific allowances from document format."""
        return SpecificAllowances(
            monthly_hills_allowance=Money.from_float(specific_allowances_doc.get("hills_allowance", 0.0)),
            monthly_hills_exemption_limit=Money.from_float(specific_allowances_doc.get("hills_exemption_limit", 0.0)),

            monthly_border_allowance=Money.from_float(specific_allowances_doc.get("border_allowance", 0.0)),
            monthly_border_exemption_limit=Money.from_float(specific_allowances_doc.get("border_exemption_limit", 0.0)),

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
            uniform_allowance=Money.from_float(specific_allowances_doc.get("uniform_allowance", 0.0))
        )
    
    # Deserialization methods
    def _deserialize_salary_income(self, salary_doc: dict) -> SalaryIncome:
        """Deserialize salary income from document format."""
        from datetime import datetime
        from app.domain.value_objects.tax_year import TaxYear
        
        # Get effective dates from document or use defaults
        effective_from = None
        effective_till = None
        
        if salary_doc.get("effective_from"):
            effective_from = datetime.fromisoformat(salary_doc["effective_from"])
        else:
            # Default to start of current tax year
            current_tax_year = TaxYear.current()
            effective_from = datetime.combine(current_tax_year.get_start_date(), datetime.min.time())
        
        if salary_doc.get("effective_till"):
            effective_till = datetime.fromisoformat(salary_doc["effective_till"])
        else:
            # Default to end of current tax year
            current_tax_year = TaxYear.current()
            effective_till = datetime.combine(current_tax_year.get_end_date(), datetime.min.time())
        
        specific_allowances = self._deserialize_specific_allowances(salary_doc.get("specific_allowances", {}))
        from app.domain.entities.taxation.salary_income import SalaryIncome
        from app.domain.value_objects.money import Money
        return SalaryIncome(
            basic_salary=Money.from_float(salary_doc.get("basic_salary", 0.0)),
            dearness_allowance=Money.from_float(salary_doc.get("dearness_allowance", 0.0)),
            hra_provided=Money.from_float(salary_doc.get("hra_provided", 0.0)),
            epf_employee=Money.from_float(salary_doc.get("epf_employee", 0.0)),  # Added
            epf_employer=Money.from_float(salary_doc.get("epf_employer", 0.0)),  # Added
            eps_employee=Money.from_float(salary_doc.get("eps_employee", 0.0)),
            eps_employer=Money.from_float(salary_doc.get("eps_employer", 0.0)),
            esi_contribution=Money.from_float(salary_doc.get("esi_contribution", 0.0)),
            vps_employee=Money.from_float(salary_doc.get("vps_employee", 0.0)),
            special_allowance=Money.from_float(salary_doc.get("special_allowance", 0.0)),
            commission=Money.from_float(salary_doc.get("commission", 0.0)),
            effective_from=effective_from,
            effective_till=effective_till,
            specific_allowances=specific_allowances
        )
    
    def _deserialize_deductions(self, deductions_doc: dict) -> TaxDeductions:
        """Deserialize deductions from document format."""
        if deductions_doc is None:
            return TaxDeductions()
        
        return TaxDeductions(
            section_80c=self._deserialize_section_80c(deductions_doc.get("section_80c", {})),
            section_80d=self._deserialize_section_80d(deductions_doc.get("section_80d", {})),
            section_80g=self._deserialize_section_80g(deductions_doc.get("section_80g", {})),
            section_80e=self._deserialize_section_80e(deductions_doc.get("section_80e", {})),
            section_80tta_ttb=self._deserialize_section_80tta_ttb(deductions_doc.get("section_80tta_ttb", {})),
            other_deductions=self._deserialize_other_deductions(deductions_doc.get("other_deductions", {}))
        )
    
    def _deserialize_section_80c(self, section_80c_doc: dict) -> DeductionSection80C:
        """Deserialize Section 80C from document format."""
        if section_80c_doc is None:
            return DeductionSection80C()
        
        return DeductionSection80C(
            life_insurance_premium=Money.from_float(section_80c_doc.get("life_insurance_premium", 0.0)),
            nsc_investment=Money.from_float(section_80c_doc.get("nsc_investment", 0.0)),
            tax_saving_fd=Money.from_float(section_80c_doc.get("tax_saving_fd", 0.0)),
            elss_investment=Money.from_float(section_80c_doc.get("elss_investment", 0.0)),
            home_loan_principal=Money.from_float(section_80c_doc.get("home_loan_principal", 0.0)),
            tuition_fees=Money.from_float(section_80c_doc.get("tuition_fees", 0.0)),
            ulip_premium=Money.from_float(section_80c_doc.get("ulip_premium", 0.0)),
            sukanya_samriddhi=Money.from_float(section_80c_doc.get("sukanya_samriddhi", 0.0)),
            stamp_duty_property=Money.from_float(section_80c_doc.get("stamp_duty_property", 0.0)),
            senior_citizen_savings=Money.from_float(section_80c_doc.get("senior_citizen_savings", 0.0)),
            other_80c_investments=Money.from_float(section_80c_doc.get("other_80c_investments", 0.0))
        )
    
    def _deserialize_section_80d(self, section_80d_doc: dict) -> DeductionSection80D:
        """Deserialize Section 80D from document format."""
        if section_80d_doc is None:
            return DeductionSection80D()
        
        return DeductionSection80D(
            self_family_premium=Money.from_float(section_80d_doc.get("self_family_premium", 0.0)),
            parent_premium=Money.from_float(section_80d_doc.get("parent_premium", 0.0)),
            preventive_health_checkup=Money.from_float(section_80d_doc.get("preventive_health_checkup", 0.0)),
            parent_age=section_80d_doc.get("parent_age", 55)
        )
    
    def _deserialize_section_80g(self, section_80g_doc: dict) -> DeductionSection80G:
        """Deserialize Section 80G from document format."""
        if section_80g_doc is None:
            return DeductionSection80G()
        
        return DeductionSection80G(
            # 100% deduction without qualifying limit
            pm_relief_fund=Money.from_float(section_80g_doc.get("pm_relief_fund", 0.0)),
            national_defence_fund=Money.from_float(section_80g_doc.get("national_defence_fund", 0.0)),
            national_foundation_communal_harmony=Money.from_float(section_80g_doc.get("national_foundation_communal_harmony", 0.0)),
            zila_saksharta_samiti=Money.from_float(section_80g_doc.get("zila_saksharta_samiti", 0.0)),
            national_illness_assistance_fund=Money.from_float(section_80g_doc.get("national_illness_assistance_fund", 0.0)),
            national_blood_transfusion_council=Money.from_float(section_80g_doc.get("national_blood_transfusion_council", 0.0)),
            national_trust_autism_fund=Money.from_float(section_80g_doc.get("national_trust_autism_fund", 0.0)),
            national_sports_fund=Money.from_float(section_80g_doc.get("national_sports_fund", 0.0)),
            national_cultural_fund=Money.from_float(section_80g_doc.get("national_cultural_fund", 0.0)),
            technology_development_fund=Money.from_float(section_80g_doc.get("technology_development_fund", 0.0)),
            national_children_fund=Money.from_float(section_80g_doc.get("national_children_fund", 0.0)),
            cm_relief_fund=Money.from_float(section_80g_doc.get("cm_relief_fund", 0.0)),
            army_naval_air_force_funds=Money.from_float(section_80g_doc.get("army_naval_air_force_funds", 0.0)),
            swachh_bharat_kosh=Money.from_float(section_80g_doc.get("swachh_bharat_kosh", 0.0)),
            clean_ganga_fund=Money.from_float(section_80g_doc.get("clean_ganga_fund", 0.0)),
            drug_abuse_control_fund=Money.from_float(section_80g_doc.get("drug_abuse_control_fund", 0.0)),
            other_100_percent_wo_limit=Money.from_float(section_80g_doc.get("other_100_percent_wo_limit", 0.0)),
            
            # 50% deduction without qualifying limit
            jn_memorial_fund=Money.from_float(section_80g_doc.get("jn_memorial_fund", 0.0)),
            pm_drought_relief=Money.from_float(section_80g_doc.get("pm_drought_relief", 0.0)),
            indira_gandhi_memorial_trust=Money.from_float(section_80g_doc.get("indira_gandhi_memorial_trust", 0.0)),
            rajiv_gandhi_foundation=Money.from_float(section_80g_doc.get("rajiv_gandhi_foundation", 0.0)),
            other_50_percent_wo_limit=Money.from_float(section_80g_doc.get("other_50_percent_wo_limit", 0.0)),
            
            # 100% deduction with qualifying limit
            family_planning_donation=Money.from_float(section_80g_doc.get("family_planning_donation", 0.0)),
            indian_olympic_association=Money.from_float(section_80g_doc.get("indian_olympic_association", 0.0)),
            other_100_percent_w_limit=Money.from_float(section_80g_doc.get("other_100_percent_w_limit", 0.0)),
            
            # 50% deduction with qualifying limit
            govt_charitable_donations=Money.from_float(section_80g_doc.get("govt_charitable_donations", 0.0)),
            housing_authorities_donations=Money.from_float(section_80g_doc.get("housing_authorities_donations", 0.0)),
            religious_renovation_donations=Money.from_float(section_80g_doc.get("religious_renovation_donations", 0.0)),
            other_charitable_donations=Money.from_float(section_80g_doc.get("other_charitable_donations", 0.0)),
            other_50_percent_w_limit=Money.from_float(section_80g_doc.get("other_50_percent_w_limit", 0.0))
        )
    
    def _deserialize_section_80e(self, section_80e_doc: dict) -> DeductionSection80E:
        """Deserialize Section 80E from document format."""
        from app.domain.entities.taxation.deductions import RelationType

        if section_80e_doc is None:
            return DeductionSection80E()
        
        relation_str = section_80e_doc.get("relation", "SELF")
        try:
            relation = RelationType(relation_str)
        except ValueError:
            relation = RelationType.SELF
        
        return DeductionSection80E(
            education_loan_interest=Money.from_float(section_80e_doc.get("education_loan_interest", 0.0)),
            relation=relation
        )
    
    def _deserialize_section_80tta_ttb(self, section_80tta_ttb_doc: dict) -> DeductionSection80TTA_TTB:
        """Deserialize Section 80TTA/TTB from document format."""
        if section_80tta_ttb_doc is None:
            return DeductionSection80TTA_TTB()
        
        return DeductionSection80TTA_TTB(
            savings_interest=Money.from_float(section_80tta_ttb_doc.get("savings_interest", 0.0)),
            fd_interest=Money.from_float(section_80tta_ttb_doc.get("fd_interest", 0.0)),
            rd_interest=Money.from_float(section_80tta_ttb_doc.get("rd_interest", 0.0)),
            post_office_interest=Money.from_float(section_80tta_ttb_doc.get("post_office_interest", 0.0)),
            age=section_80tta_ttb_doc.get("age", 30)
        )
    
    def _deserialize_other_deductions(self, other_deductions_doc: dict) -> OtherDeductions:
        """Deserialize other deductions from document format."""
        if other_deductions_doc is None:
            return OtherDeductions()
        
        return OtherDeductions(
            other_deductions=Money.from_float(other_deductions_doc.get("other_deductions", 0.0))
        )
    
    def _deserialize_perquisites(self, perquisites_doc: Optional[dict]) -> Optional[Perquisites]:
        """Deserialize perquisites from document format."""
        if not perquisites_doc:
            return Perquisites()
        
        # Deserialize accommodation perquisite
        accommodation = None
        if perquisites_doc.get("accommodation", {}).get("has_accommodation"):
            acc_doc = perquisites_doc["accommodation"]
            try:
                accommodation_type = AccommodationType(acc_doc.get("accommodation_type", "Employer-Owned"))
            except ValueError:
                accommodation_type = AccommodationType.EMPLOYER_OWNED
            
            try:
                city_population = CityPopulation(acc_doc.get("city_population", "Below 15 lakhs"))
            except ValueError:
                city_population = CityPopulation.BELOW_15_LAKHS
            
            accommodation = AccommodationPerquisite(
                accommodation_type=accommodation_type,
                city_population=city_population,
                license_fees=Money.from_float(acc_doc.get("license_fees", 0.0)),
                employee_rent_payment=Money.from_float(acc_doc.get("employee_rent_payment", 0.0)),
                rent_paid_by_employer=Money.from_float(acc_doc.get("rent_paid_by_employer", 0.0)),
                hotel_charges=Money.from_float(acc_doc.get("hotel_charges", 0.0)),
                stay_days=acc_doc.get("stay_days", 0),
                furniture_cost=Money.from_float(acc_doc.get("furniture_cost", 0.0)),
                furniture_employee_payment=Money.from_float(acc_doc.get("furniture_employee_payment", 0.0)),
                is_furniture_owned_by_employer=acc_doc.get("is_furniture_owned_by_employer", True)
            )
        
        # Deserialize car perquisite
        car = None
        if perquisites_doc.get("car", {}).get("has_car"):
            car_doc = perquisites_doc["car"]
            try:
                car_use_type = CarUseType(car_doc.get("car_use_type", "Personal"))
            except ValueError:
                car_use_type = CarUseType.PERSONAL
            
            car = CarPerquisite(
                car_use_type=car_use_type,
                engine_capacity_cc=car_doc.get("engine_capacity_cc", 1600),
                months_used=car_doc.get("months_used", 12),
                months_used_other_vehicle=car_doc.get("months_used_other_vehicle", 12),
                car_cost_to_employer=Money.from_float(car_doc.get("car_cost_to_employer", 0.0)),
                other_vehicle_cost=Money.from_float(car_doc.get("other_vehicle_cost", 0.0)),
                has_expense_reimbursement=car_doc.get("has_expense_reimbursement", False),
                driver_provided=car_doc.get("driver_provided", False)
            )
        
        # Deserialize LTA
        lta = None
        if perquisites_doc.get("lta", {}).get("has_lta"):
            lta_doc = perquisites_doc["lta"]
            lta = LTAPerquisite(
                is_monthly_paid=lta_doc.get("is_monthly_paid", False),
                lta_amount_claimed=Money.from_float(lta_doc.get("lta_amount_claimed", 0.0)),
                lta_claimed_count=lta_doc.get("lta_claimed_count", 0),
                public_transport_cost=Money.from_float(lta_doc.get("public_transport_cost", 0.0)),
                travel_mode=lta_doc.get("travel_mode", "Air")
            )
        
        # Deserialize interest-free loan
        interest_free_loan = None
        if perquisites_doc.get("interest_free_loan", {}).get("has_loan"):
            loan_doc = perquisites_doc["interest_free_loan"]
            loan_start_date = None
            if loan_doc.get("loan_start_date"):
                try:
                    loan_start_date = datetime.fromisoformat(loan_doc.get("loan_start_date")).date()
                except (ValueError, TypeError):
                    loan_start_date = None
            
            interest_free_loan = InterestFreeConcessionalLoan(
                loan_amount=Money.from_float(loan_doc.get("loan_amount", 0.0)),
                emi_amount=Money.from_float(loan_doc.get("emi_amount", 0.0)),
                outstanding_amount=Money.from_float(loan_doc.get("outstanding_amount", 0.0)),
                company_interest_rate=Decimal(str(loan_doc.get("company_interest_rate", 0.0))),
                sbi_interest_rate=Decimal(str(loan_doc.get("sbi_interest_rate", 8.5))),
                loan_type=loan_doc.get("loan_type", "Personal"),
                loan_start_date=loan_start_date
            )
        
        # Deserialize ESOP
        esop = None
        if perquisites_doc.get("esop", {}).get("has_esop"):
            esop_doc = perquisites_doc["esop"]
            esop = ESOPPerquisite(
                shares_exercised=esop_doc.get("shares_exercised", 0),
                exercise_price=Money.from_float(esop_doc.get("exercise_price", 0.0)),
                allotment_price=Money.from_float(esop_doc.get("allotment_price", 0.0))
            )
        
        # Deserialize utilities
        utilities = None
        if perquisites_doc.get("utilities", {}).get("has_utilities"):
            util_doc = perquisites_doc["utilities"]
            utilities = UtilitiesPerquisite(
                gas_paid_by_employer=Money.from_float(util_doc.get("gas_paid_by_employer", 0.0)),
                electricity_paid_by_employer=Money.from_float(util_doc.get("electricity_paid_by_employer", 0.0)),
                water_paid_by_employer=Money.from_float(util_doc.get("water_paid_by_employer", 0.0)),
                gas_paid_by_employee=Money.from_float(util_doc.get("gas_paid_by_employee", 0.0)),
                electricity_paid_by_employee=Money.from_float(util_doc.get("electricity_paid_by_employee", 0.0)),
                water_paid_by_employee=Money.from_float(util_doc.get("water_paid_by_employee", 0.0)),
                is_gas_manufactured_by_employer=util_doc.get("is_gas_manufactured_by_employer", False),
                is_electricity_manufactured_by_employer=util_doc.get("is_electricity_manufactured_by_employer", False),
                is_water_manufactured_by_employer=util_doc.get("is_water_manufactured_by_employer", False)
            )
        
        # Deserialize free education
        free_education = None
        if perquisites_doc.get("free_education", {}).get("has_free_education"):
            edu_doc = perquisites_doc["free_education"]
            free_education = FreeEducationPerquisite(
                monthly_expenses_child1=Money.from_float(edu_doc.get("monthly_expenses_child1", 0.0)),
                monthly_expenses_child2=Money.from_float(edu_doc.get("monthly_expenses_child2", 0.0)),
                months_child1=edu_doc.get("months_child1", 12),
                months_child2=edu_doc.get("months_child2", 12),
                employer_maintained_1st_child=edu_doc.get("employer_maintained_1st_child", False),
                employer_maintained_2nd_child=edu_doc.get("employer_maintained_2nd_child", False)
            )
        
        # Deserialize lunch refreshment
        lunch_refreshment = None
        if perquisites_doc.get("lunch_refreshment", {}).get("has_lunch_refreshment"):
            lunch_doc = perquisites_doc["lunch_refreshment"]
            lunch_refreshment = LunchRefreshmentPerquisite(
                employer_cost=Money.from_float(lunch_doc.get("employer_cost", 0.0)),
                employee_payment=Money.from_float(lunch_doc.get("employee_payment", 0.0)),
                meal_days_per_year=lunch_doc.get("meal_days_per_year", 250)
            )
        
        # Deserialize domestic help
        domestic_help = None
        if perquisites_doc.get("domestic_help", {}).get("has_domestic_help"):
            help_doc = perquisites_doc["domestic_help"]
            domestic_help = DomesticHelpPerquisite(
                domestic_help_paid_by_employer=Money.from_float(help_doc.get("domestic_help_paid_by_employer", 0.0)),
                domestic_help_paid_by_employee=Money.from_float(help_doc.get("domestic_help_paid_by_employee", 0.0))
            )
        
        # Deserialize movable asset usage
        movable_asset_usage = None
        if perquisites_doc.get("movable_asset_usage", {}).get("has_movable_asset_usage"):
            asset_doc = perquisites_doc["movable_asset_usage"]
            try:
                asset_type = AssetType(asset_doc.get("asset_type", "Electronics"))
            except ValueError:
                asset_type = AssetType.ELECTRONICS
            
            movable_asset_usage = MovableAssetUsage(
                asset_type=asset_type,
                asset_value=Money.from_float(asset_doc.get("asset_value", 0.0)),
                hire_cost=Money.from_float(asset_doc.get("hire_cost", 0.0)),
                employee_payment=Money.from_float(asset_doc.get("employee_payment", 0.0)),
                is_employer_owned=asset_doc.get("is_employer_owned", True)
            )
        
        # Deserialize movable asset transfer
        movable_asset_transfer = None
        if perquisites_doc.get("movable_asset_transfer", {}).get("has_movable_asset_transfer"):
            transfer_doc = perquisites_doc["movable_asset_transfer"]
            try:
                asset_type = AssetType(transfer_doc.get("asset_type", "Electronics"))
            except ValueError:
                asset_type = AssetType.ELECTRONICS
            
            movable_asset_transfer = MovableAssetTransfer(
                asset_type=asset_type,
                asset_cost=Money.from_float(transfer_doc.get("asset_cost", 0.0)),
                years_of_use=transfer_doc.get("years_of_use", 1),
                employee_payment=Money.from_float(transfer_doc.get("employee_payment", 0.0))
            )
        
        # Deserialize gift voucher
        gift_voucher = None
        if perquisites_doc.get("gift_voucher", {}).get("has_gift_voucher"):
            gift_doc = perquisites_doc["gift_voucher"]
            gift_voucher = GiftVoucherPerquisite(
                gift_voucher_amount=Money.from_float(gift_doc.get("gift_voucher_amount", 0.0))
            )
        
        # Deserialize monetary benefits
        monetary_benefits = None
        if perquisites_doc.get("monetary_benefits", {}).get("has_monetary_benefits"):
            money_doc = perquisites_doc["monetary_benefits"]
            monetary_benefits = MonetaryBenefitsPerquisite(
                monetary_amount_paid_by_employer=Money.from_float(money_doc.get("monetary_amount_paid_by_employer", 0.0)),
                expenditure_for_official_purpose=Money.from_float(money_doc.get("expenditure_for_official_purpose", 0.0)),
                amount_paid_by_employee=Money.from_float(money_doc.get("amount_paid_by_employee", 0.0))
            )
        
        # Deserialize club expenses
        club_expenses = None
        if perquisites_doc.get("club_expenses", {}).get("has_club_expenses"):
            club_doc = perquisites_doc["club_expenses"]
            club_expenses = ClubExpensesPerquisite(
                club_expenses_paid_by_employer=Money.from_float(club_doc.get("club_expenses_paid_by_employer", 0.0)),
                club_expenses_paid_by_employee=Money.from_float(club_doc.get("club_expenses_paid_by_employee", 0.0)),
                club_expenses_for_official_purpose=Money.from_float(club_doc.get("club_expenses_for_official_purpose", 0.0))
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
    
    def _deserialize_retirement_benefits(self, retirement_benefits_doc: Optional[dict]) -> Optional[RetirementBenefits]:
        """Deserialize retirement benefits from document format."""
        if not retirement_benefits_doc:
            return RetirementBenefits()
        
        # Deserialize leave encashment
        leave_encashment = None
        if retirement_benefits_doc.get("leave_encashment", {}).get("has_leave_encashment"):
            leave_doc = retirement_benefits_doc["leave_encashment"]
            leave_encashment = LeaveEncashment(
                leave_encashment_amount=Money.from_float(leave_doc.get("leave_encashment_amount", 0.0)),
                average_monthly_salary=Money.from_float(leave_doc.get("average_monthly_salary", 0.0)),
                leave_days_encashed=leave_doc.get("leave_days_encashed", 0),
                is_deceased=leave_doc.get("is_deceased", False),
                during_employment=leave_doc.get("during_employment", False)
            )
        
        # Deserialize gratuity
        gratuity = None
        if retirement_benefits_doc.get("gratuity", {}).get("has_gratuity"):
            grat_doc = retirement_benefits_doc["gratuity"]
            gratuity = Gratuity(
                gratuity_amount=Money.from_float(grat_doc.get("gratuity_amount", 0.0)),
                monthly_salary=Money.from_float(grat_doc.get("monthly_salary", 0.0)),
                service_years=Decimal(str(grat_doc.get("service_years", 0.0)))
            )
        
        # Deserialize VRS
        vrs = None
        if retirement_benefits_doc.get("vrs", {}).get("has_vrs"):
            vrs_doc = retirement_benefits_doc["vrs"]
            vrs = VRS(
                vrs_amount=Money.from_float(vrs_doc.get("vrs_amount", 0.0)),
                monthly_salary=Money.from_float(vrs_doc.get("monthly_salary", 0.0)),
                service_years=Decimal(str(vrs_doc.get("service_years", 0.0)))
            )
        
        # Deserialize pension
        pension = None
        if retirement_benefits_doc.get("pension", {}).get("has_pension"):
            pension_doc = retirement_benefits_doc["pension"]
            pension = Pension(
                regular_pension=Money.from_float(pension_doc.get("regular_pension", 0.0)),
                commuted_pension=Money.from_float(pension_doc.get("commuted_pension", 0.0)),
                total_pension=Money.from_float(pension_doc.get("total_pension", 0.0)),
                gratuity_received=pension_doc.get("gratuity_received", False)
            )
        
        # Deserialize retrenchment compensation
        retrenchment_compensation = None
        if retirement_benefits_doc.get("retrenchment_compensation", {}).get("has_retrenchment_compensation"):
            retrench_doc = retirement_benefits_doc["retrenchment_compensation"]
            retrenchment_compensation = RetrenchmentCompensation(
                retrenchment_amount=Money.from_float(retrench_doc.get("retrenchment_amount", 0.0)),
                monthly_salary=Money.from_float(retrench_doc.get("monthly_salary", 0.0)),
                service_years=Decimal(str(retrench_doc.get("service_years", 0.0)))
            )
        
        # Deserialize monthly_salary_paid
        monthly_salary_paid = None
        if "monthly_salary_paid" in retirement_benefits_doc and isinstance(retirement_benefits_doc["monthly_salary_paid"], list):
            monthly_salary_paid = [Money.from_float(float(x)) for x in retirement_benefits_doc["monthly_salary_paid"]]
        
        return RetirementBenefits(
            leave_encashment=leave_encashment,
            gratuity=gratuity,
            vrs=vrs,
            pension=pension,
            retrenchment_compensation=retrenchment_compensation,
            monthly_salary_paid=monthly_salary_paid
        )
    
    def _deserialize_other_income(self, other_income_doc: Optional[dict]) -> Optional[OtherIncome]:
        """Deserialize other income from document format."""
        if not other_income_doc:
            return OtherIncome()
        
        # Deserialize interest income
        interest_income = None
        if other_income_doc.get("interest_income", {}).get("has_interest_income"):
            interest_doc = other_income_doc["interest_income"]
            interest_income = InterestIncome(
                savings_account_interest=Money.from_float(interest_doc.get("savings_account_interest", 0.0)),
                fixed_deposit_interest=Money.from_float(interest_doc.get("fixed_deposit_interest", 0.0)),
                recurring_deposit_interest=Money.from_float(interest_doc.get("recurring_deposit_interest", 0.0)),
                post_office_interest=Money.from_float(interest_doc.get("post_office_interest", 0.0))
            )
        
        # Deserialize house property income
        house_property_income = None
        if other_income_doc.get("house_property_income", {}).get("has_house_property_income"):
            house_doc = other_income_doc["house_property_income"]
            from app.domain.entities.taxation.house_property_income import PropertyType
            
            try:
                property_type = PropertyType(house_doc.get("property_type", "Self-Occupied"))
            except ValueError:
                property_type = PropertyType.SELF_OCCUPIED
            
            house_property_income = HousePropertyIncome(
                property_type=property_type,
                address=house_doc.get("address", ""),
                annual_rent_received=Money.from_float(house_doc.get("annual_rent_received", 0.0)),
                municipal_taxes_paid=Money.from_float(house_doc.get("municipal_taxes_paid", 0.0)),
                home_loan_interest=Money.from_float(house_doc.get("home_loan_interest", 0.0)),
                pre_construction_interest=Money.from_float(house_doc.get("pre_construction_interest", 0.0))
            )
        
        # Deserialize capital gains income
        capital_gains_income = None
        if other_income_doc.get("capital_gains_income", {}).get("has_capital_gains_income"):
            cap_gains_doc = other_income_doc["capital_gains_income"]
            capital_gains_income = CapitalGainsIncome(
                stcg_111a_equity_stt=Money.from_float(cap_gains_doc.get("stcg_111a_equity_stt", 0.0)),
                stcg_other_assets=Money.from_float(cap_gains_doc.get("stcg_other_assets", 0.0)),
                stcg_debt_mf=Money.from_float(cap_gains_doc.get("stcg_debt_mf", 0.0)),
                ltcg_112a_equity_stt=Money.from_float(cap_gains_doc.get("ltcg_112a_equity_stt", 0.0)),
                ltcg_other_assets=Money.from_float(cap_gains_doc.get("ltcg_other_assets", 0.0)),
                ltcg_debt_mf=Money.from_float(cap_gains_doc.get("ltcg_debt_mf", 0.0))
            )
        
        return OtherIncome(
            business_professional_income=Money.from_float(other_income_doc.get("business_professional_income", 0.0)),
            house_property_income=house_property_income,
            interest_income=interest_income,
            dividend_income=Money.from_float(other_income_doc.get("dividend_income", 0.0)),
            gifts_received=Money.from_float(other_income_doc.get("gifts_received", 0.0)),
            other_miscellaneous_income=Money.from_float(other_income_doc.get("other_miscellaneous_income", 0.0)),
            capital_gains_income=capital_gains_income
        )
    
    def _deserialize_calculation_result(self, calc_data: Optional[dict]) -> Optional[TaxCalculationResult]:
        """Deserialize calculation result from document format."""
        if not calc_data:
            return None
        
        # Helper function to safely convert values to Money
        def safe_money_from_value(value, default=0):
            """Safely convert a value to Money, handling various edge cases."""
            import decimal
            try:
                # Handle None or empty values
                if value is None or value == "":
                    return Money.from_decimal(default)
                
                # Handle string values that might be invalid
                if isinstance(value, str):
                    # Strip whitespace and handle common invalid values
                    value = value.strip()
                    if value.lower() in ['null', 'undefined', 'nan', 'none', '']:
                        return Money.from_decimal(default)
                
                # Handle Decimal objects (common when retrieving from MongoDB)
                if isinstance(value, decimal.Decimal):
                    return Money.from_decimal(value)
                
                # Try to convert to float first, then to decimal
                if isinstance(value, (int, float)):
                    return Money.from_decimal(float(value))
                elif isinstance(value, str):
                    return Money.from_decimal(float(value))
                else:
                    # For any other type, try direct conversion
                    return Money.from_decimal(value)
                    
            except (ValueError, TypeError, decimal.InvalidOperation, decimal.ConversionSyntax) as e:
                logger.warning(f"Failed to convert value '{value}' (type: {type(value)}) to Money, using default {default}: {str(e)}")
                return Money.from_decimal(default)
        
        # Add debugging to log the values being processed
        tax_liability_value = calc_data.get("tax_liability", 0)
        logger.debug(f"Deserializing tax_liability: value={tax_liability_value}, type={type(tax_liability_value)}")
        
        result = TaxCalculationResult(
            total_income=safe_money_from_value(calc_data.get("total_income", 0)),
            professional_tax=safe_money_from_value(calc_data.get("professional_tax", 0)),
            total_exemptions=safe_money_from_value(calc_data.get("total_exemptions", 0)),
            total_deductions=safe_money_from_value(calc_data.get("total_deductions", 0)),
            taxable_income=safe_money_from_value(calc_data.get("taxable_income", 0)),
            tax_amount=safe_money_from_value(calc_data.get("tax_amount", 0)),
            surcharge=safe_money_from_value(calc_data.get("surcharge", 0)),
            cess=safe_money_from_value(calc_data.get("cess", 0)),
            tax_liability=safe_money_from_value(tax_liability_value),
            tax_breakdown=calc_data.get("tax_breakdown", {}),
            regime_comparison=calc_data.get("regime_comparison")
        )
        
        return result 

    def _serialize_monthly_salary(self, monthly_salary) -> dict:
        """
        Serialize a MonthlySalary entity to a MongoDB document (dict), including all nested components.
        Mirrors the logic from MongoDBMonthlySalaryRepository._entity_to_document.
        """
        from datetime import datetime
        return {
            "employee_id": str(monthly_salary.employee_id),
            "month": monthly_salary.month,
            "year": monthly_salary.year,
            "tax_year": str(monthly_salary.tax_year),
            "tax_regime": monthly_salary.tax_regime.regime_type.value,
            # Comprehensive salary components
            "salary": self._serialize_salary_income(monthly_salary.salary) if monthly_salary.salary else None,
            # Comprehensive perquisites payouts
            "perquisites_payouts": self._serialize_perquisites_payouts(monthly_salary.perquisites_payouts) if hasattr(self, '_serialize_perquisites_payouts') and monthly_salary.perquisites_payouts else None,
            # Comprehensive deductions
            "deductions": self._serialize_deductions(monthly_salary.deductions) if monthly_salary.deductions else None,
            # Comprehensive retirement benefits
            "retirement": self._serialize_retirement_benefits(monthly_salary.retirement) if monthly_salary.retirement else None,
            # LWP details
            "lwp": self._serialize_lwp_details(monthly_salary.lwp) if hasattr(self, '_serialize_lwp_details') and monthly_salary.lwp else None,
            # Tax and net salary
            "tax_amount": monthly_salary.tax_amount.to_float(),
            "net_salary": monthly_salary.net_salary.to_float(),
            # Metadata
            "computed_at": datetime.utcnow().isoformat(),
            "one_time_arrear": monthly_salary.one_time_arrear.to_float() if hasattr(monthly_salary, 'one_time_arrear') else 0.0,
            "one_time_bonus": monthly_salary.one_time_bonus.to_float() if hasattr(monthly_salary, 'one_time_bonus') else 0.0,
            "tds_status": self._serialize_tds_status(monthly_salary.tds_status) if hasattr(self, '_serialize_tds_status') and monthly_salary.tds_status else None,
            "payout_status": self._serialize_payout_status(monthly_salary.payout_status) if hasattr(self, '_serialize_payout_status') and monthly_salary.payout_status else None,
            "pf_status": self._serialize_pf_status(monthly_salary.pf_status) if hasattr(self, '_serialize_pf_status') and monthly_salary.pf_status else None,
        }

    # --- MONTHLY SALARY SERIALIZATION HELPERS ---
    def _serialize_salary_income(self, salary_income):
        if salary_income is None:
            return None
        return {
            "basic_salary": salary_income.basic_salary.to_float() if salary_income.basic_salary else 0.0,
            "dearness_allowance": salary_income.dearness_allowance.to_float() if salary_income.dearness_allowance else 0.0,
            "hra_provided": salary_income.hra_provided.to_float() if salary_income.hra_provided else 0.0,
            "epf_employee": salary_income.epf_employee.to_float() if hasattr(salary_income, 'epf_employee') and salary_income.epf_employee else 0.0,  # Added
            "epf_employer": salary_income.epf_employer.to_float() if hasattr(salary_income, 'epf_employer') and salary_income.epf_employer else 0.0,  # Added
            "eps_employee": salary_income.eps_employee.to_float() if salary_income.eps_employee else 0.0,
            "eps_employer": salary_income.eps_employer.to_float() if salary_income.eps_employer else 0.0,
            "esi_contribution": salary_income.esi_contribution.to_float() if salary_income.esi_contribution else 0.0,
            "vps_employee": salary_income.vps_employee.to_float() if salary_income.vps_employee else 0.0,
            "special_allowance": salary_income.special_allowance.to_float() if salary_income.special_allowance else 0.0,
            "commission": salary_income.commission.to_float() if salary_income.commission else 0.0,
            "effective_from": salary_income.effective_from.isoformat() if salary_income.effective_from else None,
            "effective_till": salary_income.effective_till.isoformat() if salary_income.effective_till else None,
            "gross_salary": salary_income.calculate_gross_salary().to_float() if hasattr(salary_income, 'calculate_gross_salary') else 0.0,
            "specific_allowances": self._serialize_specific_allowances(salary_income.specific_allowances) if salary_income.specific_allowances else None
        }

    def _serialize_specific_allowances(self, specific_allowances):
        if specific_allowances is None:
            return None
        # Ensure all fields are float, not Money objects
        return {
            "monthly_hills_allowance": specific_allowances.monthly_hills_allowance.to_float() if specific_allowances.monthly_hills_allowance else 0.0,
            "monthly_hills_exemption_limit": specific_allowances.monthly_hills_exemption_limit.to_float() if specific_allowances.monthly_hills_exemption_limit else 0.0,
            "monthly_border_allowance": specific_allowances.monthly_border_allowance.to_float() if specific_allowances.monthly_border_allowance else 0.0,
            "monthly_border_exemption_limit": specific_allowances.monthly_border_exemption_limit.to_float() if specific_allowances.monthly_border_exemption_limit else 0.0,
            "transport_employee_allowance": specific_allowances.transport_employee_allowance.to_float() if specific_allowances.transport_employee_allowance else 0.0,
            "children_education_allowance": specific_allowances.children_education_allowance.to_float() if specific_allowances.children_education_allowance else 0.0,
            "children_education_count": specific_allowances.children_education_count,
            "hostel_allowance": specific_allowances.hostel_allowance.to_float() if specific_allowances.hostel_allowance else 0.0,
            "children_hostel_count": specific_allowances.children_hostel_count,
            "disabled_transport_allowance": specific_allowances.disabled_transport_allowance.to_float() if specific_allowances.disabled_transport_allowance else 0.0,
            "is_disabled": specific_allowances.is_disabled,
            "underground_mines_allowance": specific_allowances.underground_mines_allowance.to_float() if specific_allowances.underground_mines_allowance else 0.0,
            "mine_work_months": specific_allowances.mine_work_months,
            "government_entertainment_allowance": specific_allowances.government_entertainment_allowance.to_float() if specific_allowances.government_entertainment_allowance else 0.0,
            "city_compensatory_allowance": specific_allowances.city_compensatory_allowance.to_float() if specific_allowances.city_compensatory_allowance else 0.0,
            "rural_allowance": specific_allowances.rural_allowance.to_float() if specific_allowances.rural_allowance else 0.0,
            "proctorship_allowance": specific_allowances.proctorship_allowance.to_float() if specific_allowances.proctorship_allowance else 0.0,
            "wardenship_allowance": specific_allowances.wardenship_allowance.to_float() if specific_allowances.wardenship_allowance else 0.0,
            "project_allowance": specific_allowances.project_allowance.to_float() if specific_allowances.project_allowance else 0.0,
            "deputation_allowance": specific_allowances.deputation_allowance.to_float() if specific_allowances.deputation_allowance else 0.0,
            "overtime_allowance": specific_allowances.overtime_allowance.to_float() if specific_allowances.overtime_allowance else 0.0,
            "interim_relief": specific_allowances.interim_relief.to_float() if specific_allowances.interim_relief else 0.0,
            "tiffin_allowance": specific_allowances.tiffin_allowance.to_float() if specific_allowances.tiffin_allowance else 0.0,
            "fixed_medical_allowance": specific_allowances.fixed_medical_allowance.to_float() if specific_allowances.fixed_medical_allowance else 0.0,
            "servant_allowance": specific_allowances.servant_allowance.to_float() if specific_allowances.servant_allowance else 0.0,
            "any_other_allowance": specific_allowances.any_other_allowance.to_float() if specific_allowances.any_other_allowance else 0.0,
            "any_other_allowance_exemption": specific_allowances.any_other_allowance_exemption.to_float() if specific_allowances.any_other_allowance_exemption else 0.0,
            "govt_employees_outside_india_allowance": specific_allowances.govt_employees_outside_india_allowance.to_float() if specific_allowances.govt_employees_outside_india_allowance else 0.0,
            "supreme_high_court_judges_allowance": specific_allowances.supreme_high_court_judges_allowance.to_float() if specific_allowances.supreme_high_court_judges_allowance else 0.0,
            "judge_compensatory_allowance": specific_allowances.judge_compensatory_allowance.to_float() if specific_allowances.judge_compensatory_allowance else 0.0,
            "section_10_14_special_allowances": specific_allowances.section_10_14_special_allowances.to_float() if specific_allowances.section_10_14_special_allowances else 0.0,
            "travel_on_tour_allowance": specific_allowances.travel_on_tour_allowance.to_float() if specific_allowances.travel_on_tour_allowance else 0.0,
            "tour_daily_charge_allowance": specific_allowances.tour_daily_charge_allowance.to_float() if specific_allowances.tour_daily_charge_allowance else 0.0,
            "conveyance_in_performace_of_duties": specific_allowances.conveyance_in_performace_of_duties.to_float() if specific_allowances.conveyance_in_performace_of_duties else 0.0,
            "helper_in_performace_of_duties": specific_allowances.helper_in_performace_of_duties.to_float() if specific_allowances.helper_in_performace_of_duties else 0.0,
            "academic_research": specific_allowances.academic_research.to_float() if specific_allowances.academic_research else 0.0,
            "uniform_allowance": specific_allowances.uniform_allowance.to_float() if specific_allowances.uniform_allowance else 0.0,
            # Aliases for backward compatibility, always as float
            "hills_allowance": specific_allowances.hills_allowance.to_float() if specific_allowances.hills_allowance else 0.0,
            "border_allowance": specific_allowances.border_allowance.to_float() if specific_allowances.border_allowance else 0.0,
            "hills_exemption_limit": specific_allowances.hills_exemption_limit.to_float() if specific_allowances.hills_exemption_limit else 0.0,
            "border_exemption_limit": specific_allowances.border_exemption_limit.to_float() if specific_allowances.border_exemption_limit else 0.0,
            "children_count": getattr(specific_allowances, "children_count", 0)
        }

    def _serialize_perquisites_payouts(self, perquisites_payouts):
        if perquisites_payouts is None:
            return None
        return {
            "components": [
                {
                    "key": component.key,
                    "display_name": component.display_name,
                    "value": component.value.to_float() if component.value else 0.0
                }
                for component in perquisites_payouts.components
            ],
            "total": perquisites_payouts.total.to_float() if perquisites_payouts.total else 0.0
        }

    def _serialize_lwp_details(self, lwp):
        return {
            "lwp_days": lwp.lwp_days,
            "total_working_days": lwp.total_working_days,
            "month": lwp.month,
            "year": lwp.year
        }

    # --- MONTHLY SALARY DESERIALIZATION HELPERS ---
    def _deserialize_salary_income(self, salary_doc):
        from datetime import datetime
        effective_from = None
        effective_till = None
        if salary_doc.get("effective_from"):
            effective_from = datetime.fromisoformat(salary_doc["effective_from"])
        if salary_doc.get("effective_till"):
            effective_till = datetime.fromisoformat(salary_doc["effective_till"])
        specific_allowances = self._deserialize_specific_allowances(salary_doc.get("specific_allowances", {}))
        from app.domain.entities.taxation.salary_income import SalaryIncome
        from app.domain.value_objects.money import Money
        return SalaryIncome(
            basic_salary=Money.from_float(salary_doc.get("basic_salary", 0.0)),
            dearness_allowance=Money.from_float(salary_doc.get("dearness_allowance", 0.0)),
            hra_provided=Money.from_float(salary_doc.get("hra_provided", 0.0)),
            epf_employee=Money.from_float(salary_doc.get("epf_employee", 0.0)),  # Added
            epf_employer=Money.from_float(salary_doc.get("epf_employer", 0.0)),  # Added
            eps_employee=Money.from_float(salary_doc.get("eps_employee", 0.0)),
            eps_employer=Money.from_float(salary_doc.get("eps_employer", 0.0)),
            esi_contribution=Money.from_float(salary_doc.get("esi_contribution", 0.0)),
            vps_employee=Money.from_float(salary_doc.get("vps_employee", 0.0)),
            special_allowance=Money.from_float(salary_doc.get("special_allowance", 0.0)),
            commission=Money.from_float(salary_doc.get("commission", 0.0)),
            effective_from=effective_from,
            effective_till=effective_till,
            specific_allowances=specific_allowances
        )

    def _deserialize_specific_allowances(self, specific_allowances_doc):
        from app.domain.entities.taxation.salary_income import SpecificAllowances
        from app.domain.value_objects.money import Money
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

    def _deserialize_perquisites_payouts(self, perq_payouts_doc):
        from app.domain.entities.taxation.perquisites import MonthlyPerquisitesPayouts, MonthlyPerquisitesComponents
        from app.domain.value_objects.money import Money
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

    def _deserialize_lwp_details(self, lwp_doc):
        from app.domain.entities.taxation.lwp_details import LWPDetails
        return LWPDetails(
            lwp_days=lwp_doc.get("lwp_days", 0),
            total_working_days=lwp_doc.get("total_working_days", 30),
            month=lwp_doc.get("month", 1),
            year=lwp_doc.get("year", 2024)
        )

    async def get_monthly_salaries_for_period(
        self,
        month: int,
        tax_year: str,
        organization_id: str,
        status: Optional[str] = None,
        department: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """
        Aggregate all monthly_salary_records for the given month/tax_year from all SalaryPackageRecords in the organization.
        Returns a flat list of MonthlySalary objects (or dicts if serialization is needed).
        """
        # Get all salary package records for the organization for the given tax_year
        package_records = await self.get_by_tax_year(tax_year, organization_id, limit=10000, offset=0)  # Large limit to get all
        result = []
        for package in package_records:
            for ms in getattr(package, 'monthly_salary_records', []):
                if ms.month == month and str(package.tax_year) == tax_year:
                    # Optionally filter by status/department if needed
                    result.append(ms)
        # Pagination
        paginated = result[skip:skip+limit]
        return paginated

    # Utility for safe Money to float conversion
    def _to_float(self, val):
        return val.to_float() if hasattr(val, 'to_float') else float(val) if val is not None else 0.0

    async def get_monthly_summary(
        self,
        month: int,
        tax_year: str,
        organization_id: str
    ) -> dict:
        """
        Aggregate all monthly_salary_records for the given month/tax_year from all SalaryPackageRecords in the organization,
        and return summary statistics (total gross, deductions, net, tds, count).
        """
        # Get all salary package records for the organization for the given tax_year
        package_records = await self.get_by_tax_year(tax_year, organization_id, limit=10000, offset=0)
        result = []
        for package in package_records:
            for ms in getattr(package, 'monthly_salary_records', []):
                if ms.month == month and str(package.tax_year) == tax_year:
                    result.append(ms)
        # Compute summary statistics
        total_gross_salary = 0.0
        total_deductions = 0.0
        total_net_salary = 0.0
        total_tds = 0.0
        count = len(result)
        for ms in result:
            gross = ms.salary.calculate_gross_salary().to_float() if hasattr(ms.salary, 'calculate_gross_salary') else 0.0
            net = ms.net_salary.to_float() if hasattr(ms.net_salary, 'to_float') else 0.0
            tds = ms.tax_amount.to_float() if hasattr(ms.tax_amount, 'to_float') else 0.0
            deductions = gross - net if gross >= net else 0.0
            total_gross_salary += gross
            total_net_salary += net
            total_tds += tds
            total_deductions += deductions
        return {
            "total_gross_salary": total_gross_salary,
            "total_deductions": total_deductions,
            "total_net_salary": total_net_salary,
            "total_tds": total_tds,
            "count": count
        }

    def _serialize_tds_status(self, tds_status):
        """Serialize TDSStatus to dict for MongoDB."""
        if tds_status is None:
            return None
        # Handle both Money and float types for total_tax_liability
        ttl = tds_status.total_tax_liability
        if hasattr(ttl, 'to_float'):
            ttl_val = ttl.to_float()
        else:
            ttl_val = float(ttl) if ttl is not None else 0.0
        # Use 'challan_number' for DTO, fallback to 'tds_challan_number' for entity
        challan_number = getattr(tds_status, 'challan_number', None)
        if challan_number is None:
            challan_number = getattr(tds_status, 'tds_challan_number', None)
        # Use 'tds_challan_date' and 'tds_challan_file_path' if present
        tds_challan_date = getattr(tds_status, 'tds_challan_date', None)
        tds_challan_file_path = getattr(tds_status, 'tds_challan_file_path', None)
        return {
            "status": getattr(tds_status, 'status', 'unpaid'),
            "total_tax_liability": ttl_val,
            "tds_challan_number": challan_number,
            "tds_challan_date": tds_challan_date.isoformat() if tds_challan_date else None,
            "tds_challan_file_path": tds_challan_file_path,
        }

    def _deserialize_tds_status(self, tds_status_doc):
        """Deserialize dict to TDSStatus."""
        from app.domain.entities.taxation.monthly_salary_status import TDSStatus
        from app.domain.value_objects.money import Money
        from datetime import date
        if not tds_status_doc:
            return None
        tds_challan_date = None
        if tds_status_doc.get("tds_challan_date"):
            try:
                tds_challan_date = date.fromisoformat(tds_status_doc["tds_challan_date"])
            except Exception:
                tds_challan_date = None
        return TDSStatus(
            status=tds_status_doc.get("status", "unpaid"),
            total_tax_liability=Money.from_float(tds_status_doc.get("total_tax_liability", 0.0)),
            tds_challan_number=tds_status_doc.get("tds_challan_number"),
            tds_challan_date=tds_challan_date,
            tds_challan_file_path=tds_status_doc.get("tds_challan_file_path"),
        )

    def _serialize_payout_status(self, payout_status):
        """Serialize PayoutStatus to dict for MongoDB."""
        if payout_status is None:
            return None
        return {
            "status": payout_status.status,
            "comments": payout_status.comments,
            "transaction_id": payout_status.transaction_id,
            "transfer_date": payout_status.transfer_date.isoformat() if payout_status.transfer_date else None,
        }

    def _deserialize_payout_status(self, payout_status_doc):
        """Deserialize dict to PayoutStatus."""
        from app.domain.entities.taxation.monthly_salary_status import PayoutStatus
        from datetime import date
        if not payout_status_doc:
            return None
        transfer_date = None
        if payout_status_doc.get("transfer_date"):
            try:
                transfer_date = date.fromisoformat(payout_status_doc["transfer_date"])
            except Exception:
                transfer_date = None
        return PayoutStatus(
            status=payout_status_doc.get("status", "computed"),
            comments=payout_status_doc.get("comments"),
            transaction_id=payout_status_doc.get("transaction_id"),
            transfer_date=transfer_date,
        )

    def _serialize_pf_status(self, pf_status):
        if pf_status is None:
            return None
        return {
            "status": pf_status.status,
            "comments": pf_status.comments,
            "transaction_id": pf_status.transaction_id,
            "transfer_date": pf_status.transfer_date.isoformat() if pf_status.transfer_date else None,
        }

    def _deserialize_pf_status(self, pf_status_doc):
        from app.domain.entities.taxation.monthly_salary_status import PfStatus
        from datetime import date
        if not pf_status_doc:
            return None
        transfer_date = None
        if pf_status_doc.get("transfer_date"):
            try:
                transfer_date = date.fromisoformat(pf_status_doc["transfer_date"])
            except Exception:
                transfer_date = None
        return PfStatus(
            status=pf_status_doc.get("status", "computed"),
            comments=pf_status_doc.get("comments"),
            transaction_id=pf_status_doc.get("transaction_id"),
            transfer_date=transfer_date,
        )