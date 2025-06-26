"""
MongoDB Salary Package Repository
MongoDB implementation of the salary package repository
"""

from typing import List, Optional
from datetime import date
from decimal import Decimal
from bson import ObjectId

from app.application.interfaces.repositories.salary_package_repository import SalaryPackageRepository
from app.domain.entities.taxation.taxation_record import SalaryPackageRecord
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
from app.domain.entities.taxation.salary_income import SalaryIncome, SpecificAllowances
from app.domain.entities.taxation.deductions import (
    TaxDeductions, DeductionSection80C, DeductionSection80D, DeductionSection80E, DeductionSection80G, DeductionSection80TTA_TTB, OtherDeductions
)
from app.domain.entities.taxation.perquisites import Perquisites
from app.domain.entities.taxation.other_income import OtherIncome
from app.domain.entities.taxation.house_property_income import HousePropertyIncome
from app.domain.entities.taxation.capital_gains import CapitalGainsIncome
from app.domain.entities.taxation.retirement_benefits import RetirementBenefits
from app.domain.value_objects.money import Money
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.tax_year import TaxYear
from app.domain.services.taxation.tax_calculation_service import TaxCalculationResult
from app.infrastructure.database.database_connector import DatabaseConnector


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
        import logging
        logger = logging.getLogger(__name__)
        
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
        collection = await self._get_collection(organization_id)
        document = self._convert_to_document(salary_package_record)
        
        # Check if record already exists - convert value objects to strings for MongoDB query
        existing = await collection.find_one({
            "employee_id": str(salary_package_record.employee_id),
            "tax_year": str(salary_package_record.tax_year)
        })
        
        if existing:
            # Update existing record
            document["_id"] = existing["_id"]
            await collection.replace_one({"_id": existing["_id"]}, document)
        else:
            # Insert new record
            result = await collection.insert_one(document)
            document["_id"] = result.inserted_id
        
        # Return the saved record
        return self._convert_to_entity(document)
    
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
        import logging
        logger = logging.getLogger(__name__)
        
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
        document = {
            # Core identification
            "employee_id": str(record.employee_id),
            "tax_year": str(record.tax_year),
            "age": record.age,
            "is_government_employee": record.is_government_employee,
            
            # Core data - Salary incomes (list)
            "salary_incomes": [self._serialize_salary_income(salary) for salary in record.salary_incomes],
            
            # Core data - Tax deductions
            "deductions": self._serialize_deductions(record.deductions),
            
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
            "version": record.version
        }
        
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
        
        # Create SalaryPackageRecord
        record = SalaryPackageRecord(
            employee_id=EmployeeId(document["employee_id"]),
            tax_year=TaxYear.from_string(document["tax_year"]),
            age=document["age"],
            is_government_employee=document.get("is_government_employee", False),
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
            version=document.get("version", 1)
        )
        
        return record
    
    def _serialize_specific_allowances(self, specific_allowances: SpecificAllowances) -> dict:
        """Serialize specific allowances to document format."""
        if not specific_allowances:
            return {}
        
        return {
            "hills_allowance": specific_allowances.hills_allowance.to_float(),
            "hills_exemption_limit": specific_allowances.hills_exemption_limit.to_float(),

            "border_allowance": specific_allowances.border_allowance.to_float(),
            "border_exemption_limit": specific_allowances.border_exemption_limit.to_float(),

            "transport_employee_allowance": specific_allowances.transport_employee_allowance.to_float(),
            
            "children_education_allowance": specific_allowances.children_education_allowance.to_float(),
            "children_count": specific_allowances.children_count,
            "children_education_months": specific_allowances.children_education_months,

            "hostel_allowance": specific_allowances.hostel_allowance.to_float(),
            "hostel_count": specific_allowances.hostel_count,
            "hostel_months": specific_allowances.hostel_months,

            "disabled_transport_allowance": specific_allowances.disabled_transport_allowance.to_float(),
            "transport_months": specific_allowances.transport_months,
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
    def _serialize_salary_income(self, salary_income: SalaryIncome) -> dict:
        """Serialize salary income to document format."""
        return {
            "basic_salary": salary_income.basic_salary.to_float(),
            "dearness_allowance": salary_income.dearness_allowance.to_float(),
            "hra_provided": salary_income.hra_provided.to_float(),
            "special_allowance": salary_income.special_allowance.to_float(),
            "bonus": salary_income.bonus.to_float(),
            "commission": salary_income.commission.to_float(),
            "arrears": salary_income.arrears.to_float(),
            "effective_from": salary_income.effective_from.isoformat(),
            "effective_till": salary_income.effective_till.isoformat(),
            "specific_allowances": self._serialize_specific_allowances(salary_income.specific_allowances)
        }   
    
    def _serialize_deductions(self, deductions: TaxDeductions) -> dict:
        """Serialize deductions to document format."""
        return {
            "section_80c": self._serialize_section_80c(deductions.section_80c),
            "section_80d": self._serialize_section_80d(deductions.section_80d),
            "section_80g": self._serialize_section_80g(deductions.section_80g),
            "section_80e": self._serialize_section_80e(deductions.section_80e),
            "section_80tta_ttb": self._serialize_section_80tta_ttb(deductions.section_80tta_ttb),
            "other_deductions": self._serialize_other_deductions(deductions.other_deductions)
        }
    
    def _serialize_section_80c(self, section_80c) -> dict:
        """Serialize Section 80C deductions to document format."""
        if not section_80c:
            return {}
        
        return {
            "life_insurance_premium": section_80c.life_insurance_premium.to_float(),
            "epf_contribution": section_80c.epf_contribution.to_float(),
            "ppf_contribution": section_80c.ppf_contribution.to_float(),
            "nsc_investment": section_80c.nsc_investment.to_float(),
            "tax_saving_fd": section_80c.tax_saving_fd.to_float(),
            "elss_investment": section_80c.elss_investment.to_float(),
            "home_loan_principal": section_80c.home_loan_principal.to_float(),
            "tuition_fees": section_80c.tuition_fees.to_float(),
            "ulip_premium": section_80c.ulip_premium.to_float(),
            "sukanya_samriddhi": section_80c.sukanya_samriddhi.to_float(),
            "stamp_duty_property": section_80c.stamp_duty_property.to_float(),
            "senior_citizen_savings": section_80c.senior_citizen_savings.to_float(),
            "other_80c_investments": section_80c.other_80c_investments.to_float(),
            "total_investment": section_80c.calculate_total_investment().to_float()
        }
    
    def _serialize_section_80d(self, section_80d) -> dict:
        """Serialize Section 80D deductions to document format."""
        if not section_80d:
            return {}
        
        return {
            "self_family_premium": section_80d.self_family_premium.to_float(),
            "parent_premium": section_80d.parent_premium.to_float(),
            "preventive_health_checkup": section_80d.preventive_health_checkup.to_float(),
            "parent_age": section_80d.parent_age
        }
    
    def _serialize_section_80g(self, section_80g) -> dict:
        """Serialize Section 80G deductions to document format."""
        if not section_80g:
            return {}
        
        return {
            "pm_relief_fund": section_80g.pm_relief_fund.to_float(),
            "national_defence_fund": section_80g.national_defence_fund.to_float(),
            "national_foundation_communal_harmony": section_80g.national_foundation_communal_harmony.to_float(),
            "zila_saksharta_samiti": section_80g.zila_saksharta_samiti.to_float(),
            "national_illness_assistance_fund": section_80g.national_illness_assistance_fund.to_float(),
            "national_blood_transfusion_council": section_80g.national_blood_transfusion_council.to_float(),
            "national_trust_autism_fund": section_80g.national_trust_autism_fund.to_float(),
            "national_sports_fund": section_80g.national_sports_fund.to_float(),
            "national_cultural_fund": section_80g.national_cultural_fund.to_float(),
            "technology_development_fund": section_80g.technology_development_fund.to_float(),
            "national_children_fund": section_80g.national_children_fund.to_float(),
            "cm_relief_fund": section_80g.cm_relief_fund.to_float(),
            "army_naval_air_force_funds": section_80g.army_naval_air_force_funds.to_float(),
            "swachh_bharat_kosh": section_80g.swachh_bharat_kosh.to_float(),
            "clean_ganga_fund": section_80g.clean_ganga_fund.to_float(),
            "drug_abuse_control_fund": section_80g.drug_abuse_control_fund.to_float(),
            "other_100_percent_wo_limit": section_80g.other_100_percent_wo_limit.to_float(),
            "jn_memorial_fund": section_80g.jn_memorial_fund.to_float(),
            "pm_drought_relief": section_80g.pm_drought_relief.to_float(),
            "indira_gandhi_memorial_trust": section_80g.indira_gandhi_memorial_trust.to_float(),
            "rajiv_gandhi_foundation": section_80g.rajiv_gandhi_foundation.to_float(),
            "other_50_percent_wo_limit": section_80g.other_50_percent_wo_limit.to_float(),
            "family_planning_donation": section_80g.family_planning_donation.to_float(),
            "indian_olympic_association": section_80g.indian_olympic_association.to_float(),
            "other_100_percent_w_limit": section_80g.other_100_percent_w_limit.to_float(),
            "govt_charitable_donations": section_80g.govt_charitable_donations.to_float(),
            "housing_authorities_donations": section_80g.housing_authorities_donations.to_float(),
            "religious_renovation_donations": section_80g.religious_renovation_donations.to_float(),
            "other_charitable_donations": section_80g.other_charitable_donations.to_float(),
            "other_50_percent_w_limit": section_80g.other_50_percent_w_limit.to_float()
        }
    
    def _serialize_section_80e(self, section_80e) -> dict:
        """Serialize Section 80E deductions to document format."""
        if not section_80e:
            return {}
        
        return {
            "education_loan_interest": section_80e.education_loan_interest.to_float(),
            "relation": section_80e.relation.value if hasattr(section_80e, 'relation') and section_80e.relation else 'SELF'
        }
    
    def _serialize_section_80tta_ttb(self, section_80tta_ttb) -> dict:
        """Serialize Section 80TTA/80TTB deductions to document format."""
        if not section_80tta_ttb:
            return {}
        
        return {
            "savings_interest": section_80tta_ttb.savings_interest.to_float(),
            "fd_interest": section_80tta_ttb.fd_interest.to_float(),
            "rd_interest": section_80tta_ttb.rd_interest.to_float(),
            "post_office_interest": section_80tta_ttb.post_office_interest.to_float(),
            "age": section_80tta_ttb.age
        }
    
    def _serialize_other_deductions(self, other_deductions) -> dict:
        """Serialize other deductions to document format."""
        if not other_deductions:
            return {}
        
        return {
            "education_loan_interest": other_deductions.education_loan_interest.to_float(),
            "charitable_donations": other_deductions.charitable_donations.to_float(),
            "savings_interest": other_deductions.savings_interest.to_float(),
            "nps_contribution": other_deductions.nps_contribution.to_float(),
            "other_deductions": other_deductions.other_deductions.to_float(),
            "total": other_deductions.calculate_total().to_float()
        }
    
    def _serialize_perquisites(self, perquisites: Optional[Perquisites]) -> Optional[dict]:
        """Serialize perquisites to document format."""
        if not perquisites:
            return None
        
        return {
            "has_perquisites": True,
            "total_value": perquisites.calculate_total_perquisites(TaxRegime.old_regime()).to_float(),
            # Store summary for now - detailed structure can be added later
        }
    
    def _serialize_retirement_benefits(self, retirement_benefits: Optional[RetirementBenefits]) -> Optional[dict]:
        """Serialize retirement benefits to document format."""
        if not retirement_benefits:
            return None
        
        return {
            "has_retirement_benefits": True,
            "total_value": retirement_benefits.calculate_total_retirement_income(TaxRegime.old_regime()).to_float(),
            # Store summary for now - detailed structure can be added later
        }
    
    def _serialize_other_income(self, other_income: Optional[OtherIncome]) -> Optional[dict]:
        """Serialize other income to document format."""
        if not other_income:
            return None
        
        return {
            "has_other_income": True,
            "total_value": other_income.calculate_total_other_income(TaxRegime.old_regime(), 30).to_float(),
            # Store summary for now - detailed structure can be added later
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
            "tax_breakdown": calculation_result.tax_breakdown,
            "regime_comparison": calculation_result.regime_comparison
        }
    
    def _deserialize_specific_allowances(self, specific_allowances_doc: dict) -> SpecificAllowances:
        """Deserialize specific allowances from document format."""
        return SpecificAllowances(
            hills_allowance=Money.from_float(specific_allowances_doc.get("hills_allowance", 0.0)),
            hills_exemption_limit=Money.from_float(specific_allowances_doc.get("hills_exemption_limit", 0.0)),

            border_allowance=Money.from_float(specific_allowances_doc.get("border_allowance", 0.0)),
            border_exemption_limit=Money.from_float(specific_allowances_doc.get("border_exemption_limit", 0.0)),

            transport_employee_allowance=Money.from_float(specific_allowances_doc.get("transport_employee_allowance", 0.0)),

            children_education_allowance=Money.from_float(specific_allowances_doc.get("children_education_allowance", 0.0)),
            children_count=specific_allowances_doc.get("children_count", 0),
            children_education_months=specific_allowances_doc.get("children_education_months", 0),

            hostel_allowance=Money.from_float(specific_allowances_doc.get("hostel_allowance", 0.0)),
            hostel_count=specific_allowances_doc.get("hostel_count", 0),
            hostel_months=specific_allowances_doc.get("hostel_months", 0),

            disabled_transport_allowance=Money.from_float(specific_allowances_doc.get("disabled_transport_allowance", 0.0)),
            transport_months=specific_allowances_doc.get("transport_months", 0),
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
        
        return SalaryIncome(
            effective_from=effective_from,
            effective_till=effective_till,
            basic_salary=Money.from_float(salary_doc.get("basic_salary", 0.0)),
            dearness_allowance=Money.from_float(salary_doc.get("dearness_allowance", 0.0)),
            hra_provided=Money.from_float(salary_doc.get("hra_provided", 0.0)),
            special_allowance=Money.from_float(salary_doc.get("special_allowance", 0.0)),
            bonus=Money.from_float(salary_doc.get("bonus", 0.0)),
            commission=Money.from_float(salary_doc.get("commission", 0.0)),
            arrears=Money.from_float(salary_doc.get("arrears", 0.0)),
            specific_allowances=self._deserialize_specific_allowances(salary_doc.get("specific_allowances", {})),
            # Note: hra_city_type and actual_rent_paid are now handled in deductions module
        )
    
    def _deserialize_deductions(self, deductions_doc: dict) -> TaxDeductions:
        """Deserialize deductions from document format."""
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
        return DeductionSection80C(
            life_insurance_premium=Money.from_float(section_80c_doc.get("life_insurance_premium", 0.0)),
            epf_contribution=Money.from_float(section_80c_doc.get("epf_contribution", 0.0)),
            ppf_contribution=Money.from_float(section_80c_doc.get("ppf_contribution", 0.0)),
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
        return DeductionSection80D(
            self_family_premium=Money.from_float(section_80d_doc.get("self_family_premium", 0.0)),
            parent_premium=Money.from_float(section_80d_doc.get("parent_premium", 0.0)),
            preventive_health_checkup=Money.from_float(section_80d_doc.get("preventive_health_checkup", 0.0)),
            parent_age=section_80d_doc.get("parent_age", 55)
        )
    
    def _deserialize_section_80g(self, section_80g_doc: dict) -> DeductionSection80G:
        """Deserialize Section 80G from document format."""
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
        return DeductionSection80TTA_TTB(
            savings_interest=Money.from_float(section_80tta_ttb_doc.get("savings_interest", 0.0)),
            fd_interest=Money.from_float(section_80tta_ttb_doc.get("fd_interest", 0.0)),
            rd_interest=Money.from_float(section_80tta_ttb_doc.get("rd_interest", 0.0)),
            post_office_interest=Money.from_float(section_80tta_ttb_doc.get("post_office_interest", 0.0)),
            age=section_80tta_ttb_doc.get("age", 30)
        )
    
    def _deserialize_other_deductions(self, other_deductions_doc: dict) -> OtherDeductions:
        """Deserialize other deductions from document format."""
        return OtherDeductions(
            education_loan_interest=Money.from_float(other_deductions_doc.get("education_loan_interest", 0.0)),
            charitable_donations=Money.from_float(other_deductions_doc.get("charitable_donations", 0.0)),
            savings_interest=Money.from_float(other_deductions_doc.get("savings_interest", 0.0)),
            nps_contribution=Money.from_float(other_deductions_doc.get("nps_contribution", 0.0)),
            other_deductions=Money.from_float(other_deductions_doc.get("other_deductions", 0.0))
        )
    
    def _deserialize_perquisites(self, perquisites_doc: Optional[dict]) -> Optional[Perquisites]:
        """Deserialize perquisites from document format."""
        if not perquisites_doc:
            return None
        
        # For now, return a basic Perquisites object
        # Detailed deserialization can be added later
        return Perquisites()
    
    def _deserialize_retirement_benefits(self, retirement_benefits_doc: Optional[dict]) -> Optional[RetirementBenefits]:
        """Deserialize retirement benefits from document format."""
        if not retirement_benefits_doc:
            return None
        
        # For now, return a basic RetirementBenefits object
        # Detailed deserialization can be added later
        return RetirementBenefits()
    
    def _deserialize_other_income(self, other_income_doc: Optional[dict]) -> Optional[OtherIncome]:
        """Deserialize other income from document format."""
        if not other_income_doc:
            return None
        
        # For now, return a basic OtherIncome object
        # Detailed deserialization can be added later
        return OtherIncome()
    
    def _deserialize_calculation_result(self, calc_data: Optional[dict]) -> Optional[TaxCalculationResult]:
        """Deserialize calculation result from document format."""
        if not calc_data:
            return None
        
        return TaxCalculationResult(
            total_income=Money(calc_data.get("total_income", 0)),
            total_exemptions=Money(calc_data.get("total_exemptions", 0)),
            total_deductions=Money(calc_data.get("total_deductions", 0)),
            taxable_income=Money(calc_data.get("taxable_income", 0)),
            tax_liability=Money(calc_data.get("tax_liability", 0)),
            tax_breakdown=calc_data.get("tax_breakdown", {}),
            regime_comparison=calc_data.get("regime_comparison")
        ) 