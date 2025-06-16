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
from app.domain.value_objects.taxation.tax_regime import TaxRegime, TaxRegimeType
from app.domain.entities.taxation.salary_income import SalaryIncome
from app.domain.entities.taxation.tax_deductions import TaxDeductions
from app.domain.entities.taxation.perquisites import Perquisites
from app.domain.entities.taxation.other_income import OtherIncome
from app.domain.entities.taxation.house_property_income import HousePropertyIncome
from app.domain.entities.taxation.capital_gains import CapitalGainsIncome
from app.domain.entities.taxation.retirement_benefits import RetirementBenefits
from app.domain.value_objects.money import Money
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.tax_year import TaxYear
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
                                financial_year: int,
                                organisation_id: str = None) -> Optional[TaxationRecord]:
        """
        Get a taxation record.
        
        Args:
            employee_id: Employee ID
            financial_year: Financial year
            organisation_id: Organisation ID for database selection
            
        Returns:
            Optional[TaxationRecord]: Taxation record if found, None otherwise
        """
        collection = await self._get_collection(organisation_id)
        document = await collection.find_one({
            "employee_id": employee_id,
            "financial_year": financial_year
        })
        
        if document:
            return self._convert_to_entity(document)
        return None
    
    async def get_taxation_records(self,
                                 employee_id: str,
                                 start_year: Optional[int] = None,
                                 end_year: Optional[int] = None,
                                 organisation_id: str = None) -> List[TaxationRecord]:
        """
        Get taxation records for an employee.
        
        Args:
            employee_id: Employee ID
            start_year: Start financial year (optional)
            end_year: End financial year (optional)
            organisation_id: Organisation ID for database selection
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        collection = await self._get_collection(organisation_id)
        query = {"employee_id": employee_id}
        
        if start_year and end_year:
            query["financial_year"] = {"$gte": start_year, "$lte": end_year}
        elif start_year:
            query["financial_year"] = {"$gte": start_year}
        elif end_year:
            query["financial_year"] = {"$lte": end_year}
        
        cursor = collection.find(query)
        documents = await cursor.to_list(length=None)
        
        return [self._convert_to_entity(doc) for doc in documents]
    
    async def get_taxation_records_by_regime(self,
                                           regime: TaxRegimeType,
                                           financial_year: int,
                                           organisation_id: str = None) -> List[TaxationRecord]:
        """
        Get taxation records by regime.
        
        Args:
            regime: Tax regime
            financial_year: Financial year
            organisation_id: Organisation ID for database selection
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        collection = await self._get_collection(organisation_id)
        cursor = collection.find({
            "regime.regime_type": regime.value,
            "financial_year": financial_year
        })
        
        documents = await cursor.to_list(length=None)
        return [self._convert_to_entity(doc) for doc in documents]
    
    async def get_taxation_records_by_organisation(self,
                                                 organisation_id: str,
                                                 financial_year: int) -> List[TaxationRecord]:
        """
        Get taxation records by organisation.
        
        Args:
            organisation_id: Organisation ID
            financial_year: Financial year
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        collection = await self._get_collection(organisation_id)
        cursor = collection.find({
            "organisation_id": organisation_id,
            "financial_year": financial_year
        })
        
        documents = await cursor.to_list(length=None)
        return [self._convert_to_entity(doc) for doc in documents]
    
    async def delete_taxation_record(self,
                                   employee_id: str,
                                   financial_year: int,
                                   organisation_id: str = None) -> None:
        """
        Delete a taxation record.
        
        Args:
            employee_id: Employee ID
            financial_year: Financial year
            organisation_id: Organisation ID for database selection
        """
        collection = await self._get_collection(organisation_id)
        await collection.delete_one({
            "employee_id": employee_id,
            "financial_year": financial_year
        })
    
    async def update_taxation_record(self, record: TaxationRecord, organization_id: str) -> None:
        """
        Update a taxation record.
        
        Args:
            record: Taxation record to update
        """
        collection = await self._get_collection(organization_id)
        document = self._convert_to_document(record)
        await collection.replace_one(
            {
                "employee_id": record.employee_id,
                "financial_year": record.financial_year
            },
            document
        )
    
    async def get_taxation_records_by_date_range(self,
                                               start_date: date,
                                               end_date: date,
                                               organisation_id: str = None) -> List[TaxationRecord]:
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
                                                        financial_year: int,
                                                        organisation_id: str = None) -> List[TaxationRecord]:
        """
        Get taxation records by tax liability range.
        
        Args:
            min_tax: Minimum tax liability
            max_tax: Maximum tax liability
            financial_year: Financial year
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
            "financial_year": financial_year
        })
        
        documents = await cursor.to_list(length=None)
        return [self._convert_to_entity(doc) for doc in documents]
    
    async def get_taxation_records_by_income_range(self,
                                                 min_income: float,
                                                 max_income: float,
                                                 financial_year: int,
                                                 organisation_id: str = None) -> List[TaxationRecord]:
        """
        Get taxation records by income range.
        
        Args:
            min_income: Minimum income
            max_income: Maximum income
            financial_year: Financial year
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
            "financial_year": financial_year
        })
        
        documents = await cursor.to_list(length=None)
        return [self._convert_to_entity(doc) for doc in documents]
    
    async def get_taxation_records_by_deduction_range(self,
                                                    min_deduction: float,
                                                    max_deduction: float,
                                                    financial_year: int,
                                                    organisation_id: str = None) -> List[TaxationRecord]:
        """
        Get taxation records by deduction range.
        
        Args:
            min_deduction: Minimum deduction
            max_deduction: Maximum deduction
            financial_year: Financial year
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
            "financial_year": financial_year
        })
        
        documents = await cursor.to_list(length=None)
        return [self._convert_to_entity(doc) for doc in documents]
    
    async def get_taxation_records_by_exemption_range(self,
                                                    min_exemption: float,
                                                    max_exemption: float,
                                                    financial_year: int,
                                                    organisation_id: str = None) -> List[TaxationRecord]:
        """
        Get taxation records by exemption range.
        
        Args:
            min_exemption: Minimum exemption
            max_exemption: Maximum exemption
            financial_year: Financial year
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
            "financial_year": financial_year
        })
        
        documents = await cursor.to_list(length=None)
        return [self._convert_to_entity(doc) for doc in documents]
    
    def _convert_to_document(self, record: TaxationRecord) -> dict:
        """Convert taxation record to MongoDB document."""
        return {
            "employee_id": record.employee_id,
            "financial_year": record.financial_year,
            "assessment_year": record.assessment_year,
            "salary_income": {
                "basic_salary": record.salary_income.basic_salary.to_float(),
                "dearness_allowance": record.salary_income.dearness_allowance.to_float(),
                "hra_received": record.salary_income.hra_received.to_float(),
                "hra_city_type": record.salary_income.hra_city_type,
                "actual_rent_paid": record.salary_income.actual_rent_paid.to_float(),
                "special_allowance": record.salary_income.special_allowance.to_float(),
                "other_allowances": record.salary_income.other_allowances.to_float(),
                "bonus": record.salary_income.bonus.to_float(),
                "commission": record.salary_income.commission.to_float(),
                "medical_allowance": record.salary_income.medical_allowance.to_float(),
                "conveyance_allowance": record.salary_income.conveyance_allowance.to_float(),
                "overtime_allowance": record.salary_income.overtime_allowance.to_float(),
                "arrears": record.salary_income.arrears.to_float(),
                "gratuity": record.salary_income.gratuity.to_float(),
                "leave_encashment": record.salary_income.leave_encashment.to_float()
            },
            "perquisites": {
                "rent_free_accommodation": record.perquisites.rent_free_accommodation.to_float(),
                "concessional_accommodation": record.perquisites.concessional_accommodation.to_float(),
                "car_perquisite": record.perquisites.car_perquisite.to_float(),
                "driver_perquisite": record.perquisites.driver_perquisite.to_float(),
                "fuel_perquisite": record.perquisites.fuel_perquisite.to_float(),
                "education_perquisite": record.perquisites.education_perquisite.to_float(),
                "domestic_servant_perquisite": record.perquisites.domestic_servant_perquisite.to_float(),
                "utility_perquisite": record.perquisites.utility_perquisite.to_float(),
                "loan_perquisite": record.perquisites.loan_perquisite.to_float(),
                "esop_perquisite": record.perquisites.esop_perquisite.to_float(),
                "club_membership_perquisite": record.perquisites.club_membership_perquisite.to_float(),
                "other_perquisites": record.perquisites.other_perquisites.to_float()
            },
            "house_property_income": {
                "property_type": record.house_property_income.property_type.value,
                "municipal_value": record.house_property_income.municipal_value.to_float(),
                "fair_rental_value": record.house_property_income.fair_rental_value.to_float(),
                "standard_rent": record.house_property_income.standard_rent.to_float(),
                "actual_rent": record.house_property_income.actual_rent.to_float(),
                "municipal_tax": record.house_property_income.municipal_tax.to_float(),
                "interest_on_loan": record.house_property_income.interest_on_loan.to_float(),
                "pre_construction_interest": record.house_property_income.pre_construction_interest.to_float(),
                "other_deductions": record.house_property_income.other_deductions.to_float()
            },
            "capital_gains_income": {
                "asset_type": record.capital_gains_income.asset_type,
                "purchase_date": record.capital_gains_income.purchase_date.isoformat(),
                "sale_date": record.capital_gains_income.sale_date.isoformat(),
                "purchase_price": record.capital_gains_income.purchase_price.to_float(),
                "sale_price": record.capital_gains_income.sale_price.to_float(),
                "transfer_expenses": record.capital_gains_income.transfer_expenses.to_float(),
                "improvement_cost": record.capital_gains_income.improvement_cost.to_float()
            },
            "retirement_benefits": {
                "gratuity_amount": record.retirement_benefits.gratuity.gratuity_amount.to_float() if record.retirement_benefits.gratuity else 0,
                "years_of_service": int(record.retirement_benefits.gratuity.service_years) if record.retirement_benefits.gratuity else 0,
                "is_government_employee": record.retirement_benefits.gratuity.is_govt_employee if record.retirement_benefits.gratuity else False,
                "leave_encashment_amount": record.retirement_benefits.leave_encashment.leave_encashment_amount.to_float() if record.retirement_benefits.leave_encashment else 0,
                "leave_balance": record.retirement_benefits.leave_encashment.leave_days_encashed if record.retirement_benefits.leave_encashment else 0,
                "pension_amount": record.retirement_benefits.pension.total_pension.to_float() if record.retirement_benefits.pension else 0,
                "is_commuted_pension": record.retirement_benefits.pension.is_govt_employee if record.retirement_benefits.pension else False,
                "commutation_percentage": 0.0,  # Not available in new structure, default to 0
                "vrs_compensation": record.retirement_benefits.vrs.vrs_amount.to_float() if record.retirement_benefits.vrs else 0,
                "other_retirement_benefits": record.retirement_benefits.retrenchment_compensation.compensation_amount.to_float() if record.retirement_benefits.retrenchment_compensation else 0
            },
            "other_income": {
                "bank_interest": record.other_income.bank_interest.to_float(),
                "fixed_deposit_interest": record.other_income.fixed_deposit_interest.to_float(),
                "recurring_deposit_interest": record.other_income.recurring_deposit_interest.to_float(),
                "post_office_interest": record.other_income.post_office_interest.to_float(),
                "other_interest": record.other_income.other_interest.to_float(),
                "equity_dividend": record.other_income.equity_dividend.to_float(),
                "mutual_fund_dividend": record.other_income.mutual_fund_dividend.to_float(),
                "other_dividend": record.other_income.other_dividend.to_float(),
                "house_property_rent": record.other_income.house_property_rent.to_float(),
                "commercial_property_rent": record.other_income.commercial_property_rent.to_float(),
                "other_rental": record.other_income.other_rental.to_float(),
                "business_income": record.other_income.business_income.to_float(),
                "professional_income": record.other_income.professional_income.to_float(),
                "short_term_capital_gains": record.other_income.short_term_capital_gains.to_float(),
                "long_term_capital_gains": record.other_income.long_term_capital_gains.to_float(),
                "lottery_winnings": record.other_income.lottery_winnings.to_float(),
                "horse_race_winnings": record.other_income.horse_race_winnings.to_float(),
                "crossword_puzzle_winnings": record.other_income.crossword_puzzle_winnings.to_float(),
                "card_game_winnings": record.other_income.card_game_winnings.to_float(),
                "other_speculative_income": record.other_income.other_speculative_income.to_float(),
                "agricultural_income": record.other_income.agricultural_income.to_float(),
                "share_of_profit_partnership": record.other_income.share_of_profit_partnership.to_float(),
                "interest_on_tax_free_bonds": record.other_income.interest_on_tax_free_bonds.to_float(),
                "other_exempt_income": record.other_income.other_exempt_income.to_float()
            },
            "tax_deductions": {
                "life_insurance_premium": record.tax_deductions.life_insurance_premium.to_float(),
                "elss_investments": record.tax_deductions.elss_investments.to_float(),
                "public_provident_fund": record.tax_deductions.public_provident_fund.to_float(),
                "employee_provident_fund": record.tax_deductions.employee_provident_fund.to_float(),
                "sukanya_samriddhi": record.tax_deductions.sukanya_samriddhi.to_float(),
                "national_savings_certificate": record.tax_deductions.national_savings_certificate.to_float(),
                "tax_saving_fixed_deposits": record.tax_deductions.tax_saving_fixed_deposits.to_float(),
                "principal_repayment_home_loan": record.tax_deductions.principal_repayment_home_loan.to_float(),
                "tuition_fees": record.tax_deductions.tuition_fees.to_float(),
                "other_80c_deductions": record.tax_deductions.other_80c_deductions.to_float(),
                "health_insurance_self": record.tax_deductions.health_insurance_self.to_float(),
                "health_insurance_parents": record.tax_deductions.health_insurance_parents.to_float(),
                "preventive_health_checkup": record.tax_deductions.preventive_health_checkup.to_float(),
                "education_loan_interest": record.tax_deductions.education_loan_interest.to_float(),
                "donations_80g": record.tax_deductions.donations_80g.to_float(),
                "savings_account_interest": record.tax_deductions.savings_account_interest.to_float(),
                "senior_citizen_interest": record.tax_deductions.senior_citizen_interest.to_float(),
                "disability_deduction": record.tax_deductions.disability_deduction.to_float(),
                "medical_treatment_deduction": record.tax_deductions.medical_treatment_deduction.to_float(),
                "scientific_research_donation": record.tax_deductions.scientific_research_donation.to_float(),
                "political_donation": record.tax_deductions.political_donation.to_float(),
                "infrastructure_deduction": record.tax_deductions.infrastructure_deduction.to_float(),
                "industrial_undertaking_deduction": record.tax_deductions.industrial_undertaking_deduction.to_float(),
                "special_category_state_deduction": record.tax_deductions.special_category_state_deduction.to_float(),
                "hotel_deduction": record.tax_deductions.hotel_deduction.to_float(),
                "north_eastern_state_deduction": record.tax_deductions.north_eastern_state_deduction.to_float(),
                "employment_deduction": record.tax_deductions.employment_deduction.to_float(),
                "employment_generation_deduction": record.tax_deductions.employment_generation_deduction.to_float(),
                "offshore_banking_deduction": record.tax_deductions.offshore_banking_deduction.to_float(),
                "co_operative_society_deduction": record.tax_deductions.co_operative_society_deduction.to_float(),
                "royalty_deduction": record.tax_deductions.royalty_deduction.to_float(),
                "patent_deduction": record.tax_deductions.patent_deduction.to_float(),
                "interest_on_savings_deduction": record.tax_deductions.interest_on_savings_deduction.to_float(),
                "disability_deduction_amount": record.tax_deductions.disability_deduction_amount.to_float()
            },
            "regime": {
                "regime_type": record.regime.regime_type.value
            },
            "age": record.age,
            "is_senior_citizen": record.is_senior_citizen,
            "is_super_senior_citizen": record.is_super_senior_citizen,
            "is_government_employee": record.is_government_employee,
            "created_at": record.created_at.isoformat() if hasattr(record, 'created_at') else None,
            "updated_at": record.updated_at.isoformat() if hasattr(record, 'updated_at') else None
        }
    
    def _convert_to_entity(self, document: dict) -> TaxationRecord:
        """Convert MongoDB document to taxation record."""
        # Convert salary income
        salary_income = SalaryIncome(
            basic_salary=Money(document["salary_income"]["basic_salary"]),
            dearness_allowance=Money(document["salary_income"]["dearness_allowance"]),
            hra_received=Money(document["salary_income"]["hra_received"]),
            hra_city_type=document["salary_income"]["hra_city_type"],
            actual_rent_paid=Money(document["salary_income"].get("actual_rent_paid", 0)),
            special_allowance=Money(document["salary_income"]["special_allowance"]),
            other_allowances=Money(document["salary_income"]["other_allowances"]),
            bonus=Money(document["salary_income"]["bonus"]),
            commission=Money(document["salary_income"]["commission"]),
            medical_allowance=Money(document["salary_income"]["medical_allowance"]),
            conveyance_allowance=Money(document["salary_income"]["conveyance_allowance"]),
            overtime_allowance=Money(document["salary_income"]["overtime_allowance"]),
            arrears=Money(document["salary_income"]["arrears"]),
            gratuity=Money(document["salary_income"]["gratuity"]),
            leave_encashment=Money(document["salary_income"]["leave_encashment"])
        )
        
        # Convert perquisites - create with new structure but handle legacy data
        perquisites = Perquisites(
            # Core perquisites
            accommodation=None,  # Will be populated from legacy data if available
            car=None,  # Will be populated from legacy data if available
            
            # Medical and travel perquisites
            medical_reimbursement=None,
            lta=None,
            
            # Financial perquisites
            interest_free_loan=None,
            esop=None,
            
            # Utilities and facilities
            utilities=None,
            free_education=None,
            lunch_refreshment=None,
            domestic_help=None,
            
            # Asset-related perquisites
            movable_asset_usage=None,
            movable_asset_transfer=None,
            
            # Miscellaneous perquisites
            gift_voucher=None,
            monetary_benefits=None,
            club_expenses=None
        )
        
        # Convert house property income - use new constructor signature
        from app.domain.entities.taxation.house_property_income import PropertyType
        
        # Map property type string to enum
        property_type_mapping = {
            "Self-Occupied": PropertyType.SELF_OCCUPIED,
            "Let-Out": PropertyType.LET_OUT,
            "Deemed Let-Out": PropertyType.DEEMED_LET_OUT
        }
        property_type = property_type_mapping.get(
            document["house_property_income"]["property_type"], 
            PropertyType.SELF_OCCUPIED
        )
        
        house_property_income = HousePropertyIncome(
            property_type=property_type,
            annual_rent_received=Money(document["house_property_income"].get("actual_rent", 0)),
            municipal_taxes_paid=Money(document["house_property_income"].get("municipal_tax", 0)),
            home_loan_interest=Money(document["house_property_income"].get("interest_on_loan", 0)),
            pre_construction_interest=Money(document["house_property_income"].get("pre_construction_interest", 0)),
            fair_rental_value=Money(document["house_property_income"].get("fair_rental_value", 0)),
            standard_rent=Money(document["house_property_income"].get("standard_rent", 0))
        )
        
        # Convert capital gains income - use new constructor signature
        capital_gains_income = CapitalGainsIncome(
            stcg_111a_equity_stt=Money(document["capital_gains_income"].get("stcg_111a_equity_stt", 0)),
            stcg_other_assets=Money(document["capital_gains_income"].get("stcg_other_assets", 0)),
            stcg_debt_mf=Money(document["capital_gains_income"].get("stcg_debt_mf", 0)),
            ltcg_112a_equity_stt=Money(document["capital_gains_income"].get("ltcg_112a_equity_stt", 0)),
            ltcg_other_assets=Money(document["capital_gains_income"].get("ltcg_other_assets", 0)),
            ltcg_debt_mf=Money(document["capital_gains_income"].get("ltcg_debt_mf", 0))
        )
        
        # Convert retirement benefits - use new nested structure
        from app.domain.entities.taxation.retirement_benefits import (
            LeaveEncashment, Gratuity, VRS, Pension, RetrenchmentCompensation
        )
        
        # Create nested objects from legacy data
        leave_encashment = LeaveEncashment(
            leave_encashment_amount=Money(document["retirement_benefits"].get("leave_encashment_amount", 0)),
            leave_days_encashed=document["retirement_benefits"].get("leave_balance", 0),
            is_govt_employee=document["retirement_benefits"].get("is_government_employee", False)
        )
        
        gratuity = Gratuity(
            gratuity_amount=Money(document["retirement_benefits"].get("gratuity_amount", 0)),
            service_years=Decimal(str(document["retirement_benefits"].get("years_of_service", 0))),
            is_govt_employee=document["retirement_benefits"].get("is_government_employee", False)
        )
        
        vrs = VRS(
            vrs_amount=Money(document["retirement_benefits"].get("vrs_compensation", 0))
        )
        
        pension = Pension(
            regular_pension=Money(document["retirement_benefits"].get("pension_amount", 0)),
            commuted_pension=Money.zero(),  # Default to zero for legacy data
            total_pension=Money(document["retirement_benefits"].get("pension_amount", 0)),
            is_govt_employee=document["retirement_benefits"].get("is_government_employee", False)
        )
        
        retrenchment_compensation = RetrenchmentCompensation(
            retrenchment_amount=Money(document["retirement_benefits"].get("other_retirement_benefits", 0))
        )
        
        retirement_benefits = RetirementBenefits(
            leave_encashment=leave_encashment,
            gratuity=gratuity,
            vrs=vrs,
            pension=pension,
            retrenchment_compensation=retrenchment_compensation
        )
        
        # Convert other income - use new constructor signature
        from app.domain.entities.taxation.other_income import InterestIncome
        
        # Create interest income from legacy fields
        interest_income = InterestIncome(
            savings_account_interest=Money(document["other_income"].get("bank_interest", 0)),
            fixed_deposit_interest=Money(document["other_income"].get("fixed_deposit_interest", 0)),
            recurring_deposit_interest=Money(document["other_income"].get("recurring_deposit_interest", 0)),
            other_bank_interest=Money(document["other_income"].get("other_interest", 0)),
            age=25  # Default age, will be overridden by actual age if available
        )
        
        other_income = OtherIncome(
            interest_income=interest_income,
            dividend_income=Money(document["other_income"].get("equity_dividend", 0)),
            gifts_received=Money.zero(),  # Not in legacy data
            business_professional_income=Money(document["other_income"].get("business_income", 0)),
            other_miscellaneous_income=Money(document["other_income"].get("other_speculative_income", 0))
        )
        
        # Convert tax deductions - use new nested structure
        from app.domain.entities.taxation.tax_deductions import (
            DeductionSection80C, DeductionSection80D, DeductionSection80E, 
            DeductionSection80G, DeductionSection80TTA_TTB, OtherDeductions
        )
        
        # Create Section 80C from legacy data
        section_80c = DeductionSection80C(
            life_insurance_premium=Money(document["tax_deductions"].get("life_insurance_premium", 0)),
            epf_contribution=Money(document["tax_deductions"].get("employee_provident_fund", 0)),
            ppf_contribution=Money(document["tax_deductions"].get("public_provident_fund", 0)),
            nsc_investment=Money(document["tax_deductions"].get("national_savings_certificate", 0)),
            tax_saving_fd=Money(document["tax_deductions"].get("tax_saving_fixed_deposits", 0)),
            elss_investment=Money(document["tax_deductions"].get("elss_investments", 0)),
            home_loan_principal=Money(document["tax_deductions"].get("principal_repayment_home_loan", 0)),
            tuition_fees=Money(document["tax_deductions"].get("tuition_fees", 0)),
            sukanya_samriddhi=Money(document["tax_deductions"].get("sukanya_samriddhi", 0)),
            other_80c_investments=Money(document["tax_deductions"].get("other_80c_deductions", 0))
        )
        
        # Create Section 80D from legacy data
        section_80d = DeductionSection80D(
            self_family_premium=Money(document["tax_deductions"].get("health_insurance_self", 0)),
            parent_premium=Money(document["tax_deductions"].get("health_insurance_parents", 0)),
            preventive_health_checkup=Money(document["tax_deductions"].get("preventive_health_checkup", 0))
        )
        
        # Create Section 80E from legacy data
        section_80e = DeductionSection80E(
            education_loan_interest=Money(document["tax_deductions"].get("education_loan_interest", 0))
        )
        
        # Create Section 80G from legacy data
        section_80g = DeductionSection80G(
            other_charitable_donations=Money(document["tax_deductions"].get("donations_80g", 0))
        )
        
        # Create Section 80TTA/TTB from legacy data
        section_80tta_ttb = DeductionSection80TTA_TTB(
            savings_interest=Money(document["tax_deductions"].get("savings_account_interest", 0)),
            fd_interest=Money(document["tax_deductions"].get("senior_citizen_interest", 0))
        )
        
        # Create other deductions from legacy data
        other_deductions = OtherDeductions(
            education_loan_interest=Money(document["tax_deductions"].get("education_loan_interest", 0)),
            charitable_donations=Money(document["tax_deductions"].get("donations_80g", 0)),
            savings_interest=Money(document["tax_deductions"].get("savings_account_interest", 0))
        )
        
        # Create TaxDeductions with nested objects
        tax_deductions = TaxDeductions(
            section_80c=section_80c,
            section_80d=section_80d,
            section_80e=section_80e,
            section_80g=section_80g,
            section_80tta_ttb=section_80tta_ttb,
            other_deductions=other_deductions
        )
        
        # Create taxation record
        return TaxationRecord(
            employee_id=document["employee_id"],
            financial_year=document["financial_year"],
            assessment_year=document["assessment_year"],
            salary_income=salary_income,
            perquisites=perquisites,
            house_property_income=house_property_income,
            capital_gains_income=capital_gains_income,
            retirement_benefits=retirement_benefits,
            other_income=other_income,
            tax_deductions=tax_deductions,
            regime=TaxRegime(TaxRegimeType(document["regime"]["regime_type"])),
            age=document["age"],
            is_senior_citizen=document["is_senior_citizen"],
            is_super_senior_citizen=document["is_super_senior_citizen"],
            is_government_employee=document["is_government_employee"]
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
        
        # Check if record already exists
        existing = await collection.find_one({
            "employee_id": taxation_record.employee_id,
            "financial_year": taxation_record.financial_year
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
                                 user_id: EmployeeId, 
                                 tax_year: TaxYear,
                                 organization_id: str) -> Optional[TaxationRecord]:
        """
        Get taxation record by user and tax year.
        
        Args:
            user_id: User ID
            tax_year: Tax year
            organization_id: Organization ID
            
        Returns:
            Optional[TaxationRecord]: Taxation record if found
        """
        collection = await self._get_collection(organization_id)
        document = await collection.find_one({
            "employee_id": str(user_id),
            "financial_year": tax_year.start_year
        })
        
        if document:
            return self._convert_to_entity(document)
        return None
    
    async def get_by_user(self, 
                        user_id: EmployeeId, 
                        organization_id: str,
                        limit: int = 10,
                        offset: int = 0) -> List[TaxationRecord]:
        """
        Get all taxation records for a user.
        
        Args:
            user_id: User ID
            organization_id: Organization ID
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        collection = await self._get_collection(organization_id)
        cursor = collection.find({
            "user_id": str(user_id),
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
            "tax_year": str(tax_year),
            "organization_id": organization_id
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