"""
MongoDB Taxation Repository
MongoDB implementation of the taxation repository
"""

from typing import List, Optional
from datetime import date
from decimal import Decimal
from bson import ObjectId

from app.domain.repositories.taxation_repository import TaxationRepository
from app.domain.entities.taxation.taxation_record import TaxationRecord
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
from app.domain.entities.taxation.salary_income import SalaryIncome
from app.domain.entities.taxation.deductions import TaxDeductions
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


class MongoDBTaxationRepository(TaxationRepository):
    """MongoDB implementation of the taxation repository."""
    
    def __init__(self, database_connector: DatabaseConnector):
        """
        Initialize the repository.
        
        Args:
            database_connector: Database connection abstraction
        """
        self.db_connector = database_connector
        self._collection_name = "taxation_records"
        
        # Connection configuration (will be set by dependency container)
        self._connection_string = None
        self._client_options = None
        
    def set_connection_config(self, connection_string: str, client_options: dict):
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
        Get taxation collection for specific organisation or global.
        
        Ensures database connection is established in the correct event loop.
        """
        db_name = organisation_id if organisation_id else "pms_global_database"
        
        # Ensure database is connected in the current event loop
        if not self.db_connector.is_connected:
            try:
                # Use stored connection configuration or fallback to config functions
                if self._connection_string and self._client_options:
                    connection_string = self._connection_string
                    options = self._client_options
                else:
                    # Fallback to config functions if connection config not set
                    from app.config.mongodb_config import get_mongodb_connection_string, get_mongodb_client_options
                    connection_string = get_mongodb_connection_string()
                    options = get_mongodb_client_options()
                
                await self.db_connector.connect(connection_string, **options)
                
            except Exception as e:
                raise RuntimeError(f"Database connection failed: {e}")
        
        # Get collection
        try:
            db = self.db_connector.get_database('pms_'+db_name)
            collection = db[self._collection_name]
            return collection
            
        except Exception as e:
            raise RuntimeError(f"Collection access failed: {e}")
    
    async def save_taxation_record(self, record: TaxationRecord, organization_id: str) -> None:
        """
        Save a taxation record.
        
        Args:
            record: Taxation record to save
        """
        collection = await self._get_collection(organization_id)
        document = self._convert_to_document(record)
        await collection.insert_one(document)
    
    async def get_taxation_record(self, 
                                employee_id: str,
                                tax_year: str,
                                organisation_id: str) -> Optional[TaxationRecord]:
        """
        Get a taxation record.
        
        Args: employee_id: Employee ID
            tax_year: Tax year (e.g., "2025-26")
            organisation_id: Organisation ID for database selection
            
        Returns:
            Optional[TaxationRecord]: Taxation record if found, None otherwise
        """
        collection = await self._get_collection(organisation_id)
        document = await collection.find_one({
            "employee_id": employee_id,
            "tax_year": tax_year
        })
        
        if document:
            return self._convert_to_entity(document)
        return None
    
    async def get_taxation_records(self,
                                 employee_id: str,
                                 tax_year: str,
                                 organisation_id: str) -> List[TaxationRecord]:
        """
        Get taxation records for an employee.
        
        Args:
            employee_id: Employee ID
            tax_year: Tax year
            organization_id: Organization ID for database selection
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        collection = await self._get_collection(organisation_id)
        query = {"employee_id": employee_id}
        
        # Add tax_year filter if provided
        if tax_year:
            query["tax_year"] = tax_year
        
        cursor = collection.find(query)
        documents = await cursor.to_list(length=None)
        
        return [self._convert_to_entity(doc) for doc in documents]
    
    async def get_taxation_records_by_regime(self,
                                           regime: TaxRegimeType,
                                           tax_year: str,
                                           organisation_id: str) -> List[TaxationRecord]:
        """
        Get taxation records by regime.
        
        Args:
            regime: Tax regime
            tax_year: Tax year (e.g., "2025-26")
            organisation_id: Organisation ID for database selection
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        collection = await self._get_collection(organisation_id)
        cursor = collection.find({
            "regime.regime_type": regime.value,
            "tax_year": tax_year
        })
        
        documents = await cursor.to_list(length=None)
        return [self._convert_to_entity(doc) for doc in documents]

    async def delete_taxation_record(self,
                                   employee_id: str,
                                   tax_year: str,
                                   organisation_id: str) -> None:
        """
        Delete a taxation record.
        
        Args:
            employee_id: Employee ID
            tax_year: Tax year (e.g., "2025-26")
            organisation_id: Organisation ID for database selection
        """
        collection = await self._get_collection(organisation_id)
        await collection.delete_one({
            "employee_id": employee_id,
            "tax_year": tax_year
        })
    
    async def update_taxation_record(self, record: TaxationRecord, organisation_id: str) -> None:
        """
        Update a taxation record.
        
        Args:
            record: Taxation record to update
        """
        collection = await self._get_collection(organisation_id)
        document = self._convert_to_document(record)
        await collection.replace_one(
            {
                "employee_id": record.employee_id,
                "tax_year": record.tax_year
            },
            document
        )
    
    async def get_taxation_records_by_date_range(self,
                                               start_date: date,
                                               end_date: date,
                                               organization_id: str) -> List[TaxationRecord]:
        """
        Get taxation records by date range.
        
        Args:
            start_date: Start date
            end_date: End date
            organisation_id: Organisation ID for database selection
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        collection = await self._get_collection(organisation_id)
        cursor = collection.find({
            "created_at": {
                "$gte": start_date,
                "$lte": end_date
            }
        })
        
        documents = await cursor.to_list(length=None)
        return [self._convert_to_entity(doc) for doc in documents]
    
    async def get_taxation_records_by_tax_liability_range(self,
                                                        min_tax: float,
                                                        max_tax: float,
                                                        tax_year: str,
                                                        organisation_id: str = None) -> List[TaxationRecord]:
        """
        Get taxation records by tax liability range.
        
        Args:
            min_tax: Minimum tax liability
            max_tax: Maximum tax liability
            tax_year: Tax year (e.g., "2025-26")
            organisation_id: Organisation ID for database selection
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        collection = await self._get_collection(organisation_id)
        cursor = collection.find({
            "tax_liability": {
                "$gte": min_tax,
                "$lte": max_tax
            },
            "tax_year": tax_year
        })
        
        documents = await cursor.to_list(length=None)
        return [self._convert_to_entity(doc) for doc in documents]
    
    async def get_taxation_records_by_income_range(self,
                                                 min_income: float,
                                                 max_income: float,
                                                 tax_year: str,
                                                 organisation_id: str) -> List[TaxationRecord]:
        """
        Get taxation records by income range.
        
        Args:
            min_income: Minimum income
            max_income: Maximum income
            tax_year: Tax year (e.g., "2025-26")
            organisation_id: Organisation ID for database selection
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        collection = await self._get_collection(organisation_id)
        cursor = collection.find({
            "total_income": {
                "$gte": min_income,
                "$lte": max_income
            },
            "tax_year": tax_year
        })
        
        documents = await cursor.to_list(length=None)
        return [self._convert_to_entity(doc) for doc in documents]
    
    async def get_taxation_records_by_deduction_range(self,
                                                    min_deduction: float,
                                                    max_deduction: float,
                                                    tax_year: str,
                                                    organisation_id: str) -> List[TaxationRecord]:
        """
        Get taxation records by deduction range.
        
        Args:
            min_deduction: Minimum deduction
            max_deduction: Maximum deduction
            tax_year: Tax year (e.g., "2025-26")
            organisation_id: Organisation ID for database selection
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        collection = await self._get_collection(organisation_id)
        cursor = collection.find({
            "total_deductions": {
                "$gte": min_deduction,
                "$lte": max_deduction
            },
            "tax_year": tax_year
        })
        
        documents = await cursor.to_list(length=None)
        return [self._convert_to_entity(doc) for doc in documents]
    
    async def get_taxation_records_by_exemption_range(self,
                                                    min_exemption: float,
                                                    max_exemption: float,
                                                    tax_year: str,
                                                    organisation_id: str = None) -> List[TaxationRecord]:
        """
        Get taxation records by exemption range.
        
        Args:
            min_exemption: Minimum exemption
            max_exemption: Maximum exemption
            tax_year: Tax year (e.g., "2025-26")
            organisation_id: Organisation ID for database selection
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        collection = await self._get_collection(organisation_id)
        cursor = collection.find({
            "total_exemptions": {
                "$gte": min_exemption,
                "$lte": max_exemption
            },
            "tax_year": tax_year
        })
        
        documents = await cursor.to_list(length=None)
        return [self._convert_to_entity(doc) for doc in documents]
    
    def _convert_to_document(self, record: TaxationRecord) -> dict:
        """Convert taxation record to MongoDB document."""
        document = {
            # Core identification
            "taxation_id": record.taxation_id,
            "employee_id": str(record.employee_id),
            "organization_id": record.organization_id,
            "tax_year": str(record.tax_year),
            "age": record.age,
            
            # Core data - Salary income 
            "salary_income": self._serialize_salary_income(record.salary_income),
            
            # Core data - Tax deductions
            "deductions": self._serialize_deductions(record.deductions),
            
            # Tax regime
            "regime": {
                "regime_type": record.regime.regime_type.value
            },
            
            # Comprehensive income components (optional)
            "perquisites": self._serialize_perquisites(record.perquisites),
            "capital_gains_income": self._serialize_capital_gains_income(record.other_income.capital_gains_income),
            "retirement_benefits": self._serialize_retirement_benefits(record.retirement_benefits),
            "other_income": self._serialize_other_income(record.other_income),
            "monthly_payroll": self._serialize_monthly_payroll(record.monthly_payroll),
            
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
    
    def _serialize_salary_income(self, salary_income: SalaryIncome) -> dict:
        """Serialize salary income to document format."""
        return {
            "basic_salary": salary_income.basic_salary.to_float(),
            "dearness_allowance": salary_income.dearness_allowance.to_float(),
            "hra_received": salary_income.hra_received.to_float(),
            "hra_city_type": salary_income.hra_city_type,
            "actual_rent_paid": salary_income.actual_rent_paid.to_float(),
            "special_allowance": salary_income.special_allowance.to_float(),
            "bonus": salary_income.bonus.to_float(),
            "commission": salary_income.commission.to_float(),
            "overtime": salary_income.specific_allowances.overtime_allowance.to_float() if salary_income.specific_allowances else 0.0,
            "arrears": salary_income.arrears.to_float()
        }
    
    def _serialize_deductions(self, deductions: TaxDeductions) -> dict:
        """Serialize tax deductions to document format."""
        # Handle the nested structure by accessing actual fields
        return {
            "section_80c": self._serialize_section_80c(deductions.section_80c),
            "section_80ccc": self._serialize_section_80ccc(deductions.section_80ccc),
            "section_80ccd": self._serialize_section_80ccd(deductions.section_80ccd),
            "section_80eeb": self._serialize_section_80eeb(deductions.section_80eeb),
            "section_80ggc": self._serialize_section_80ggc(deductions.section_80ggc),
            "section_80u": self._serialize_section_80u(deductions.section_80u),
            "section_80dd": self._serialize_section_80dd(deductions.section_80dd),
            "section_80ddb": self._serialize_section_80ddb(deductions.section_80ddb),
            "section_80d": self._serialize_section_80d(deductions.section_80d),
            "section_80e": self._serialize_section_80e(deductions.section_80e),
            "section_80g": self._serialize_section_80g(deductions.section_80g),
            "section_80tta_ttb": self._serialize_section_80tta_ttb(deductions.section_80tta_ttb),
            "other_deductions": self._serialize_other_deductions(deductions.other_deductions)
        }
    
    def _serialize_section_80c(self, section_80c) -> Optional[dict]:
        """Serialize Section 80C deductions to document format."""
        if not section_80c:
            return None
        
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
    
    def _serialize_section_80ccc(self, section_80ccc) -> Optional[dict]:
        """Serialize Section 80CCC deductions to document format."""
        if not section_80ccc:
            return None
        
        return {
            "pension_fund_contribution": section_80ccc.pension_fund_contribution.to_float()
        }
    
    def _serialize_section_80ccd(self, section_80ccd) -> Optional[dict]:
        """Serialize Section 80CCD deductions to document format."""
        if not section_80ccd:
            return None
        
        return {
            "employee_nps_contribution": section_80ccd.employee_nps_contribution.to_float(),
            "additional_nps_contribution": section_80ccd.additional_nps_contribution.to_float(),
            "employer_nps_contribution": section_80ccd.employer_nps_contribution.to_float()
        }
    
    def _serialize_section_80d(self, section_80d) -> Optional[dict]:
        """Serialize Section 80D deductions to document format."""
        if not section_80d:
            return None
        
        return {
            "self_family_premium": section_80d.self_family_premium.to_float(),
            "parent_premium": section_80d.parent_premium.to_float(),
            "preventive_health_checkup": section_80d.preventive_health_checkup.to_float(),
            "parent_age": section_80d.parent_age
        }
    
    def _serialize_section_80dd(self, section_80dd) -> Optional[dict]:
        """Serialize Section 80DD deductions to document format."""
        if not section_80dd:
            return None
        
        return {
            "relation": section_80dd.relation.value,
            "disability_percentage": section_80dd.disability_percentage.value
        }
    
    def _serialize_section_80ddb(self, section_80ddb) -> Optional[dict]:
        """Serialize Section 80DDB deductions to document format."""
        if not section_80ddb:
            return None
        
        return {
            "dependent_age": section_80ddb.dependent_age,
            "medical_expenses": section_80ddb.medical_expenses.to_float(),
            "relation": section_80ddb.relation.value
        }
    
    def _serialize_section_80e(self, section_80e) -> Optional[dict]:
        """Serialize Section 80E deductions to document format."""
        if not section_80e:
            return None
        
        return {
            "education_loan_interest": section_80e.education_loan_interest.to_float(),
            "relation": section_80e.relation.value
        }
    
    def _serialize_section_80eeb(self, section_80eeb) -> Optional[dict]:
        """Serialize Section 80EEB deductions to document format."""
        if not section_80eeb:
            return None
        
        return {
            "ev_loan_interest": section_80eeb.ev_loan_interest.to_float(),
            "ev_purchase_date": section_80eeb.ev_purchase_date.isoformat() if section_80eeb.ev_purchase_date else None
        }
    
    def _serialize_section_80g(self, section_80g) -> Optional[dict]:
        """Serialize Section 80G deductions to document format."""
        if not section_80g:
            return None
        
        return {
            # 100% deduction without qualifying limit
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
            
            # 50% deduction without qualifying limit
            "jn_memorial_fund": section_80g.jn_memorial_fund.to_float(),
            "pm_drought_relief": section_80g.pm_drought_relief.to_float(),
            "indira_gandhi_memorial_trust": section_80g.indira_gandhi_memorial_trust.to_float(),
            "rajiv_gandhi_foundation": section_80g.rajiv_gandhi_foundation.to_float(),
            "other_50_percent_wo_limit": section_80g.other_50_percent_wo_limit.to_float(),
            
            # 100% deduction with qualifying limit (10% of income)
            "family_planning_donation": section_80g.family_planning_donation.to_float(),
            "indian_olympic_association": section_80g.indian_olympic_association.to_float(),
            "other_100_percent_w_limit": section_80g.other_100_percent_w_limit.to_float(),
            
            # 50% deduction with qualifying limit (10% of income)
            "govt_charitable_donations": section_80g.govt_charitable_donations.to_float(),
            "housing_authorities_donations": section_80g.housing_authorities_donations.to_float(),
            "religious_renovation_donations": section_80g.religious_renovation_donations.to_float(),
            "other_charitable_donations": section_80g.other_charitable_donations.to_float(),
            "other_50_percent_w_limit": section_80g.other_50_percent_w_limit.to_float(),
            
            # Summary fields
            "total_donations": section_80g.calculate_total_donations().to_float()
        }
    
    def _serialize_section_80ggc(self, section_80ggc) -> Optional[dict]:
        """Serialize Section 80GGC deductions to document format."""
        if not section_80ggc:
            return None
        
        return {
            "political_party_contribution": section_80ggc.political_party_contribution.to_float()
        }
    
    def _serialize_section_80u(self, section_80u) -> Optional[dict]:
        """Serialize Section 80U deductions to document format."""
        if not section_80u:
            return None
        
        return {
            "disability_percentage": section_80u.disability_percentage.value
        }
    
    def _serialize_section_80tta_ttb(self, section_80tta_ttb) -> Optional[dict]:
        """Serialize Section 80TTA/80TTB deductions to document format."""
        if not section_80tta_ttb:
            return None
        
        return {
            "savings_interest": section_80tta_ttb.savings_interest.to_float(),
            "fd_interest": section_80tta_ttb.fd_interest.to_float(),
            "rd_interest": section_80tta_ttb.rd_interest.to_float(),
            "post_office_interest": section_80tta_ttb.post_office_interest.to_float(),
            "age": section_80tta_ttb.age
        }
    
    def _serialize_other_deductions(self, other_deductions) -> Optional[dict]:
        """Serialize other deductions to document format."""
        if not other_deductions:
            return None
        
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
    
    def _serialize_house_property_income(self, house_property: Optional[HousePropertyIncome]) -> Optional[dict]:
        """Serialize house property income to document format."""
        if not house_property:
            return None
        
        return {
            "property_type": house_property.property_type.value,
            "annual_rent_received": house_property.annual_rent_received.to_float(),
            "municipal_taxes_paid": house_property.municipal_taxes_paid.to_float(),
            "home_loan_interest": house_property.home_loan_interest.to_float(),
            "pre_construction_interest": house_property.pre_construction_interest.to_float(),
            "fair_rental_value": house_property.fair_rental_value.to_float(),
            "standard_rent": house_property.standard_rent.to_float()
        }
    
    def _serialize_capital_gains_income(self, capital_gains: Optional[CapitalGainsIncome]) -> Optional[dict]:
        """Serialize capital gains income to document format."""
        if not capital_gains:
            return None
        
        return {
            "stcg_111a_equity_stt": capital_gains.stcg_111a_equity_stt.to_float(),
            "stcg_other_assets": capital_gains.stcg_other_assets.to_float(),
            "stcg_debt_mf": capital_gains.stcg_debt_mf.to_float(),
            "ltcg_112a_equity_stt": capital_gains.ltcg_112a_equity_stt.to_float(),
            "ltcg_other_assets": capital_gains.ltcg_other_assets.to_float(),
            "ltcg_debt_mf": capital_gains.ltcg_debt_mf.to_float()
        }
    
    def _serialize_retirement_benefits(self, retirement_benefits: Optional[RetirementBenefits]) -> Optional[dict]:
        """Serialize retirement benefits to document format."""
        if not retirement_benefits:
            return None
        
        return {
            "leave_encashment_amount": retirement_benefits.leave_encashment.leave_encashment_amount.to_float() if retirement_benefits.leave_encashment else 0.0,
            "gratuity_amount": retirement_benefits.gratuity.gratuity_amount.to_float() if retirement_benefits.gratuity else 0.0,
            "vrs_amount": retirement_benefits.vrs.vrs_amount.to_float() if retirement_benefits.vrs else 0.0,
            "pension_amount": retirement_benefits.pension.total_pension.to_float() if retirement_benefits.pension else 0.0,
            "retrenchment_compensation": retirement_benefits.retrenchment_compensation.retrenchment_amount.to_float() if retirement_benefits.retrenchment_compensation else 0.0
        }
    
    def _serialize_interest_income(self, interest_income) -> Optional[dict]:
        """Serialize interest income to document format."""
        if not interest_income:
            return None
        
        return {
            "savings_account_interest": interest_income.savings_account_interest.to_float(),
            "fixed_deposit_interest": interest_income.fixed_deposit_interest.to_float(),
            "recurring_deposit_interest": interest_income.recurring_deposit_interest.to_float(),
            "post_office_interest": interest_income.post_office_interest.to_float()
        }
    
    def _serialize_other_income(self, other_income: Optional[OtherIncome]) -> Optional[dict]:
        """Serialize other income to document format."""
        if not other_income:
            return None
        
        return {
            "interest_income": self._serialize_interest_income(other_income.interest_income),
            "house_property_income": self._serialize_house_property_income(other_income.house_property_income),
            "dividend_income": other_income.dividend_income.to_float(),
            "gifts_received": other_income.gifts_received.to_float(),
            "business_professional_income": other_income.business_professional_income.to_float(),
            "other_miscellaneous_income": other_income.other_miscellaneous_income.to_float()
        }
    
    def _serialize_monthly_payroll(self, monthly_payroll) -> Optional[dict]:
        """Serialize monthly payroll to document format."""
        if not monthly_payroll:
            return None
        
        from app.domain.entities.taxation.payout import PayoutBase, PayoutFrequency, PayoutStatus
        
        return {
            "employee_id": monthly_payroll.employee_id,
            "pay_period_start": monthly_payroll.pay_period_start.isoformat(),
            "pay_period_end": monthly_payroll.pay_period_end.isoformat(),
            "payout_date": monthly_payroll.payout_date.isoformat(),
            "frequency": monthly_payroll.frequency.value,
            
            # Salary components
            "basic_salary": monthly_payroll.basic_salary,
            "da": monthly_payroll.da,
            "hra": monthly_payroll.hra,
            "special_allowance": monthly_payroll.special_allowance,
            "overtime": monthly_payroll.overtime,
            "arrears": monthly_payroll.arrears,
            "bonus": monthly_payroll.bonus,
            "commission": monthly_payroll.commission,
            
            # Deductions
            "epf_employee": monthly_payroll.epf_employee,
            "epf_employer": monthly_payroll.epf_employer,
            "esi_employee": monthly_payroll.esi_employee,
            "esi_employer": monthly_payroll.esi_employer,
            "professional_tax": monthly_payroll.professional_tax,
            "tds": monthly_payroll.tds,
            "advance_deduction": monthly_payroll.advance_deduction,
            "loan_deduction": monthly_payroll.loan_deduction,
            "other_deductions": monthly_payroll.other_deductions,
            
            # Calculated totals
            "gross_salary": monthly_payroll.gross_salary,
            "total_deductions": monthly_payroll.total_deductions,
            "net_salary": monthly_payroll.net_salary,
            
            # Annual projections
            "annual_gross_salary": monthly_payroll.annual_gross_salary,
            "annual_tax_liability": monthly_payroll.annual_tax_liability,
            "monthly_tds": monthly_payroll.monthly_tds,
            
            # Tax details
            "tax_regime": monthly_payroll.tax_regime,
            "tax_exemptions": monthly_payroll.tax_exemptions,
            "standard_deduction": monthly_payroll.standard_deduction,
            "section_80c_claimed": monthly_payroll.section_80c_claimed,
            
            # Reimbursements
            "reimbursements": monthly_payroll.reimbursements,
            
            # Working days and status
            "total_days_in_month": monthly_payroll.total_days_in_month,
            "working_days_in_period": monthly_payroll.working_days_in_period,
            "lwp_days": monthly_payroll.lwp_days,
            "effective_working_days": monthly_payroll.effective_working_days,
            "status": monthly_payroll.status.value,
            "notes": monthly_payroll.notes,
            "remarks": monthly_payroll.remarks
        }
    
    def _serialize_calculation_result(self, calculation_result) -> Optional[dict]:
        """Serialize calculation result to document format."""
        if not calculation_result:
            return None
        
        return {
            "total_income": calculation_result.total_income.to_float(),
            "total_exemptions": calculation_result.total_exemptions.to_float(),
            "total_deductions": calculation_result.total_deductions.to_float(),
            "taxable_income": calculation_result.taxable_income.to_float(),
            "tax_liability": calculation_result.tax_liability.to_float(),
            "effective_tax_rate": calculation_result.effective_tax_rate,
            "monthly_tax_liability": calculation_result.monthly_tax_liability.to_float(),
            "tax_breakdown": calculation_result.tax_breakdown
        }
    
    def _convert_to_entity(self, document: dict) -> TaxationRecord:
        """Convert MongoDB document to taxation record."""
        from datetime import datetime
        
        # Deserialize salary income
        salary_income = self._deserialize_salary_income(document.get("salary_income", {}))
        
        # Deserialize tax deductions
        deductions = self._deserialize_deductions(document.get("deductions", {}))
        
        # Deserialize regime
        regime = TaxRegime(TaxRegimeType(document["regime"]["regime_type"]))
        
        # Deserialize calculation result if present
        calculation_result = self._deserialize_calculation_result(document.get("calculation_result"))
        
        # Create TaxationRecord with core required fields
        record = TaxationRecord(
            taxation_id=document.get("taxation_id", str(document.get("_id", ""))),
            employee_id=EmployeeId(document["employee_id"]),
            #organization_id=document["organization_id"],
            tax_year=TaxYear.from_string(document["tax_year"]),
            salary_income=salary_income,
            deductions=deductions,
            regime=regime,
            age=document["age"],
            
            # Optional comprehensive income components
            perquisites=self._deserialize_perquisites(document.get("perquisites")),
            retirement_benefits=self._deserialize_retirement_benefits(document.get("retirement_benefits")),
            other_income=self._deserialize_other_income(document.get("other_income"), document.get("house_property_income"), document.get("capital_gains_income")),
            monthly_payroll=self._deserialize_monthly_payroll(document.get("monthly_payroll")),
            
            # Calculated fields
            calculation_result=calculation_result,
            last_calculated_at=datetime.fromisoformat(document["last_calculated_at"]) if document.get("last_calculated_at") else None,
            
            # Metadata
            is_final=document.get("is_final", False),
            submitted_at=datetime.fromisoformat(document["submitted_at"]) if document.get("submitted_at") else None,
            
            # # Audit fields
            # created_at=datetime.fromisoformat(document["created_at"]),
            # updated_at=datetime.fromisoformat(document["updated_at"]),
            # version=document.get("version", 1)
        )
        
        return record
    
    def _deserialize_salary_income(self, salary_data: dict) -> SalaryIncome:
        """Deserialize salary income from document format."""
        from app.domain.entities.taxation.salary_income import SpecificAllowances
        
        # Create SpecificAllowances with overtime_allowance
        specific_allowances = SpecificAllowances(
            overtime_allowance=Money(salary_data.get("overtime", 0))
        )
        
        return SalaryIncome(
            basic_salary=Money(salary_data.get("basic_salary", 0)),
            dearness_allowance=Money(salary_data.get("dearness_allowance", 0)),
            hra_received=Money(salary_data.get("hra_received", 0)),
            hra_city_type=salary_data.get("hra_city_type", "metro"),
            actual_rent_paid=Money(salary_data.get("actual_rent_paid", 0)),
            special_allowance=Money(salary_data.get("special_allowance", 0)),
            bonus=Money(salary_data.get("bonus", 0)),
            commission=Money(salary_data.get("commission", 0)),
            arrears=Money(salary_data.get("arrears", 0)),
            specific_allowances=specific_allowances
        )
    
    def _deserialize_deductions(self, deductions_data: dict) -> TaxDeductions:
        """Deserialize tax deductions from document format."""
        from app.domain.entities.taxation.deductions import (
            DeductionSection80C, DeductionSection80D, DeductionSection80E, 
            DeductionSection80G, DeductionSection80TTA_TTB, OtherDeductions
        )
        
        # Create simplified structure for now
        section_80c = DeductionSection80C()
        section_80d = DeductionSection80D()
        section_80e = DeductionSection80E()
        section_80g = DeductionSection80G()
        section_80tta_ttb = DeductionSection80TTA_TTB()
        other_deductions = OtherDeductions()
        
        return TaxDeductions(
            section_80c=section_80c,
            section_80d=section_80d,
            section_80e=section_80e,
            section_80g=section_80g,
            section_80tta_ttb=section_80tta_ttb,
            other_deductions=other_deductions
        )
    
    def _deserialize_perquisites(self, perquisites_data: Optional[dict]) -> Optional[Perquisites]:
        """Deserialize perquisites from document format."""
        if not perquisites_data:
            return None
        
        # Create default empty perquisites for now
        return Perquisites()
    
    def _deserialize_house_property_income(self, house_property_data: Optional[dict]) -> Optional[HousePropertyIncome]:
        """Deserialize house property income from document format."""
        if not house_property_data:
            return None
        
        from app.domain.entities.taxation.house_property_income import PropertyType
        
        property_type = PropertyType(house_property_data.get("property_type", "SELF_OCCUPIED"))
        
        return HousePropertyIncome(
            property_type=property_type,
            annual_rent_received=Money(house_property_data.get("annual_rent_received", 0)),
            municipal_taxes_paid=Money(house_property_data.get("municipal_taxes_paid", 0)),
            home_loan_interest=Money(house_property_data.get("home_loan_interest", 0)),
            pre_construction_interest=Money(house_property_data.get("pre_construction_interest", 0)),
            fair_rental_value=Money(house_property_data.get("fair_rental_value", 0)),
            standard_rent=Money(house_property_data.get("standard_rent", 0))
        )
    
    def _deserialize_capital_gains_income(self, capital_gains_data: Optional[dict]) -> Optional[CapitalGainsIncome]:
        """Deserialize capital gains income from document format."""
        if not capital_gains_data:
            return None
        
        return CapitalGainsIncome(
            stcg_111a_equity_stt=Money(capital_gains_data.get("stcg_111a_equity_stt", 0)),
            stcg_other_assets=Money(capital_gains_data.get("stcg_other_assets", 0)),
            stcg_debt_mf=Money(capital_gains_data.get("stcg_debt_mf", 0)),
            ltcg_112a_equity_stt=Money(capital_gains_data.get("ltcg_112a_equity_stt", 0)),
            ltcg_other_assets=Money(capital_gains_data.get("ltcg_other_assets", 0)),
            ltcg_debt_mf=Money(capital_gains_data.get("ltcg_debt_mf", 0))
        )
    
    def _deserialize_retirement_benefits(self, retirement_data: Optional[dict]) -> Optional[RetirementBenefits]:
        """Deserialize retirement benefits from document format."""
        if not retirement_data:
            return None
        
        from app.domain.entities.taxation.retirement_benefits import (
            LeaveEncashment, Gratuity, VRS, Pension, RetrenchmentCompensation
        )
        
        # Create sub-entities with data from document
        leave_encashment = LeaveEncashment(
            leave_encashment_amount=Money(retirement_data.get("leave_encashment_amount", 0))
        ) if retirement_data.get("leave_encashment_amount", 0) > 0 else None
        
        gratuity = Gratuity(
            gratuity_amount=Money(retirement_data.get("gratuity_amount", 0))
        ) if retirement_data.get("gratuity_amount", 0) > 0 else None
        
        vrs = VRS(
            vrs_amount=Money(retirement_data.get("vrs_amount", 0))
        ) if retirement_data.get("vrs_amount", 0) > 0 else None
        
        pension = Pension(
            total_pension=Money(retirement_data.get("pension_amount", 0))
        ) if retirement_data.get("pension_amount", 0) > 0 else None
        
        retrenchment_compensation = RetrenchmentCompensation(
            retrenchment_amount=Money(retirement_data.get("retrenchment_compensation", 0))
        ) if retirement_data.get("retrenchment_compensation", 0) > 0 else None
        
        return RetirementBenefits(
            leave_encashment=leave_encashment,
            gratuity=gratuity,
            vrs=vrs,
            pension=pension,
            retrenchment_compensation=retrenchment_compensation
        )
    
    def _deserialize_other_income(self, other_income_data: Optional[dict], legacy_house_property_data: Optional[dict] = None, legacy_capital_gains_data: Optional[dict] = None) -> Optional[OtherIncome]:
        """Deserialize other income from document format."""
        if not other_income_data and not legacy_house_property_data and not legacy_capital_gains_data:
            return None
        
        from app.domain.entities.taxation.other_income import InterestIncome
        
        # Handle case where we only have legacy data
        if not other_income_data:
            other_income_data = {}
        
        # Deserialize interest income
        interest_data = other_income_data.get("interest_income", {})
        interest_income = InterestIncome(
            savings_account_interest=Money.from_float(interest_data.get("savings_account_interest", 0.0)),
            fixed_deposit_interest=Money.from_float(interest_data.get("fixed_deposit_interest", 0.0)),
            recurring_deposit_interest=Money.from_float(interest_data.get("recurring_deposit_interest", 0.0)),
            post_office_interest=Money.from_float(interest_data.get("post_office_interest", 0.0))
        ) if interest_data else InterestIncome()
        
        # Deserialize house property income
        house_property_income = None
        house_property_data = other_income_data.get("house_property_income") or legacy_house_property_data
        if house_property_data:
            house_property_income = self._deserialize_house_property_income(house_property_data)
        
        # Deserialize capital gains income
        capital_gains_income = None
        capital_gains_data = other_income_data.get("capital_gains_income") or legacy_capital_gains_data
        if capital_gains_data:
            capital_gains_income = self._deserialize_capital_gains_income(capital_gains_data)
        
        return OtherIncome(
            interest_income=interest_income,
            house_property_income=house_property_income,
            capital_gains_income=capital_gains_income,
            dividend_income=Money.from_float(other_income_data.get("dividend_income", 0.0)),
            gifts_received=Money.from_float(other_income_data.get("gifts_received", 0.0)),
            business_professional_income=Money.from_float(other_income_data.get("business_professional_income", 0.0)),
            other_miscellaneous_income=Money.from_float(other_income_data.get("other_miscellaneous_income", 0.0))
        )
    
    def _deserialize_monthly_payroll(self, payroll_data: Optional[dict]):
        """Deserialize monthly payroll from document format."""
        if not payroll_data:
            return None
        
        from app.domain.entities.taxation.payout import PayoutBase, PayoutFrequency, PayoutStatus
        from datetime import date
        
        try:
            return PayoutBase(
                employee_id=payroll_data.get("employee_id", ""),
                pay_period_start=date.fromisoformat(payroll_data.get("pay_period_start", date.today().isoformat())),
                pay_period_end=date.fromisoformat(payroll_data.get("pay_period_end", date.today().isoformat())),
                payout_date=date.fromisoformat(payroll_data.get("payout_date", date.today().isoformat())),
                frequency=PayoutFrequency(payroll_data.get("frequency", "monthly")),
                
                # Salary components
                basic_salary=payroll_data.get("basic_salary", 0.0),
                da=payroll_data.get("da", 0.0),
                hra=payroll_data.get("hra", 0.0),
                special_allowance=payroll_data.get("special_allowance", 0.0),
                bonus=payroll_data.get("bonus", 0.0),   
                commission=payroll_data.get("commission", 0.0),
                overtime=payroll_data.get("overtime", 0.0),
                arrears=payroll_data.get("arrears", 0.0),
                
                # Deductions
                epf_employee=payroll_data.get("epf_employee", 0.0),
                epf_employer=payroll_data.get("epf_employer", 0.0),
                esi_employee=payroll_data.get("esi_employee", 0.0),
                esi_employer=payroll_data.get("esi_employer", 0.0),
                professional_tax=payroll_data.get("professional_tax", 0.0),
                tds=payroll_data.get("tds", 0.0),
                advance_deduction=payroll_data.get("advance_deduction", 0.0),
                loan_deduction=payroll_data.get("loan_deduction", 0.0),
                other_deductions=payroll_data.get("other_deductions", 0.0),
                
                # Calculated totals
                gross_salary=payroll_data.get("gross_salary", 0.0),
                total_deductions=payroll_data.get("total_deductions", 0.0),
                net_salary=payroll_data.get("net_salary", 0.0),
                
                # Annual projections
                annual_gross_salary=payroll_data.get("annual_gross_salary", 0.0),
                annual_tax_liability=payroll_data.get("annual_tax_liability", 0.0),
                monthly_tds=payroll_data.get("monthly_tds", 0.0),
                
                # Tax details
                tax_regime=payroll_data.get("tax_regime", "new"),
                tax_exemptions=payroll_data.get("tax_exemptions", 0.0),
                standard_deduction=payroll_data.get("standard_deduction", 0.0),
                section_80c_claimed=payroll_data.get("section_80c_claimed", 0.0),
                
                # Reimbursements
                reimbursements=payroll_data.get("reimbursements", 0.0),
                
                # Working days and status
                total_days_in_month=payroll_data.get("total_days_in_month", 30),
                working_days_in_period=payroll_data.get("working_days_in_period", 22),
                lwp_days=payroll_data.get("lwp_days", 0),
                effective_working_days=payroll_data.get("effective_working_days", 22),
                status=PayoutStatus(payroll_data.get("status", "pending")),
                notes=payroll_data.get("notes"),
                remarks=payroll_data.get("remarks")
            )
        except Exception as e:
            # If deserialization fails, return None to prevent breaking the overall record loading
            return None
    
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

    async def save(self, taxation_record: TaxationRecord, organization_id: str) -> TaxationRecord:
        """
        Save or update a taxation record.
        
        Args:
            taxation_record: Taxation record to save
            
        Returns:
            TaxationRecord: Saved taxation record
        """
        collection = await self._get_collection(organization_id)
        document = self._convert_to_document(taxation_record)
        
        # Check if record already exists - convert value objects to strings for MongoDB query
        existing = await collection.find_one({
            "employee_id": str(taxation_record.employee_id),
            "tax_year": str(taxation_record.tax_year)
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
    
    async def get_by_id(self, taxation_id: str, organization_id: str) -> Optional[TaxationRecord]:
        """
        Get taxation record by ID.
        
        Args:
            taxation_id: Taxation record ID
            organization_id: Organization ID
            
        Returns:
            Optional[TaxationRecord]: Taxation record if found
        """
        collection = await self._get_collection(organization_id)
        try:
            document = await collection.find_one({"_id": ObjectId(taxation_id)})
            if document:
                return self._convert_to_entity(document)
        except Exception:
            # If ObjectId conversion fails, try string ID
            document = await collection.find_one({"taxation_id": taxation_id})
            if document:
                return self._convert_to_entity(document)
        return None
    
    async def get_by_user_and_year(self, 
                                 employee_id: EmployeeId, 
                                 tax_year: TaxYear,
                                 organization_id: str) -> Optional[TaxationRecord]:
        """
        Get taxation record by user and tax year.
        
        Args:
            employee_id: User ID
            tax_year: Tax year
            organization_id: Organization ID
            
        Returns:
            Optional[TaxationRecord]: Taxation record if found
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
                        offset: int = 0) -> List[TaxationRecord]:
        """
        Get all taxation records for a user.
        
        Args:
            employee_id: User ID
            organization_id: Organization ID
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        collection = await self._get_collection(organization_id)
        cursor = collection.find({
            "employee_id": str(employee_id),
            "organization_id": organization_id
        }).skip(offset).limit(limit).sort("created_at", -1)
        
        documents = await cursor.to_list(length=None)
        return [self._convert_to_entity(doc) for doc in documents]
    
    async def get_by_tax_year(self, 
                            tax_year: TaxYear,
                            organization_id: str,
                            limit: int = 100,
                            offset: int = 0) -> List[TaxationRecord]:
        """
        Get all taxation records for a tax year.
        
        Args:
            tax_year: Tax year
            organization_id: Organization ID
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        collection = await self._get_collection(organization_id)
        cursor = collection.find({
            "tax_year": str(tax_year)
        }).skip(offset).limit(limit).sort("created_at", -1)
        
        documents = await cursor.to_list(length=None)
        return [self._convert_to_entity(doc) for doc in documents]
    
    async def get_by_organization(self, 
                                organization_id: str,
                                limit: int = 100,
                                offset: int = 0) -> List[TaxationRecord]:
        """
        Get all taxation records for an organization.
        
        Args:
            organization_id: Organization ID
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        collection = await self._get_collection(organization_id)
        cursor = collection.find({
            "organization_id": organization_id
        }).skip(offset).limit(limit).sort("created_at", -1)
        
        documents = await cursor.to_list(length=None)
        return [self._convert_to_entity(doc) for doc in documents] 