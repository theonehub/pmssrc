"""
MongoDB Taxation Repository
MongoDB implementation of the taxation repository
"""

from typing import List, Optional
from datetime import date
from decimal import Decimal
from motor.motor_asyncio import AsyncIOMotorClient
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


class MongoDBTaxationRepository(TaxationRepository):
    """MongoDB implementation of the taxation repository."""
    
    def __init__(self, client: AsyncIOMotorClient, database_name: str):
        """
        Initialize the repository.
        
        Args:
            client: MongoDB client
            database_name: Database name
        """
        self.client = client
        self.db = client[database_name]
        self.collection = self.db.taxation_records
    
    async def save_taxation_record(self, record: TaxationRecord) -> None:
        """
        Save a taxation record.
        
        Args:
            record: Taxation record to save
        """
        document = self._convert_to_document(record)
        await self.collection.insert_one(document)
    
    async def get_taxation_record(self, 
                                employee_id: str,
                                financial_year: int) -> Optional[TaxationRecord]:
        """
        Get a taxation record.
        
        Args:
            employee_id: Employee ID
            financial_year: Financial year
            
        Returns:
            Optional[TaxationRecord]: Taxation record if found, None otherwise
        """
        document = await self.collection.find_one({
            "employee_id": employee_id,
            "financial_year": financial_year
        })
        
        if document:
            return self._convert_to_entity(document)
        return None
    
    async def get_taxation_records(self,
                                 employee_id: str,
                                 start_year: Optional[int] = None,
                                 end_year: Optional[int] = None) -> List[TaxationRecord]:
        """
        Get taxation records for an employee.
        
        Args:
            employee_id: Employee ID
            start_year: Start financial year (optional)
            end_year: End financial year (optional)
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        query = {"employee_id": employee_id}
        
        if start_year and end_year:
            query["financial_year"] = {"$gte": start_year, "$lte": end_year}
        elif start_year:
            query["financial_year"] = {"$gte": start_year}
        elif end_year:
            query["financial_year"] = {"$lte": end_year}
        
        cursor = self.collection.find(query)
        documents = await cursor.to_list(length=None)
        
        return [self._convert_to_entity(doc) for doc in documents]
    
    async def get_taxation_records_by_regime(self,
                                           regime: TaxRegimeType,
                                           financial_year: int) -> List[TaxationRecord]:
        """
        Get taxation records by regime.
        
        Args:
            regime: Tax regime
            financial_year: Financial year
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        cursor = self.collection.find({
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
        cursor = self.collection.find({
            "organisation_id": organisation_id,
            "financial_year": financial_year
        })
        
        documents = await cursor.to_list(length=None)
        return [self._convert_to_entity(doc) for doc in documents]
    
    async def delete_taxation_record(self,
                                   employee_id: str,
                                   financial_year: int) -> None:
        """
        Delete a taxation record.
        
        Args:
            employee_id: Employee ID
            financial_year: Financial year
        """
        await self.collection.delete_one({
            "employee_id": employee_id,
            "financial_year": financial_year
        })
    
    async def update_taxation_record(self, record: TaxationRecord) -> None:
        """
        Update a taxation record.
        
        Args:
            record: Taxation record to update
        """
        document = self._convert_to_document(record)
        await self.collection.replace_one(
            {
                "employee_id": record.employee_id,
                "financial_year": record.financial_year
            },
            document
        )
    
    async def get_taxation_records_by_date_range(self,
                                               start_date: date,
                                               end_date: date) -> List[TaxationRecord]:
        """
        Get taxation records by date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        cursor = self.collection.find({
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
                                                        financial_year: int) -> List[TaxationRecord]:
        """
        Get taxation records by tax liability range.
        
        Args:
            min_tax: Minimum tax liability
            max_tax: Maximum tax liability
            financial_year: Financial year
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        cursor = self.collection.find({
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
                                                 financial_year: int) -> List[TaxationRecord]:
        """
        Get taxation records by income range.
        
        Args:
            min_income: Minimum income
            max_income: Maximum income
            financial_year: Financial year
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        cursor = self.collection.find({
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
                                                    financial_year: int) -> List[TaxationRecord]:
        """
        Get taxation records by deduction range.
        
        Args:
            min_deduction: Minimum deduction
            max_deduction: Maximum deduction
            financial_year: Financial year
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        cursor = self.collection.find({
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
                                                    financial_year: int) -> List[TaxationRecord]:
        """
        Get taxation records by exemption range.
        
        Args:
            min_exemption: Minimum exemption
            max_exemption: Maximum exemption
            financial_year: Financial year
            
        Returns:
            List[TaxationRecord]: List of taxation records
        """
        cursor = self.collection.find({
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
                "house_rent_allowance": record.salary_income.house_rent_allowance.to_float(),
                "special_allowance": record.salary_income.special_allowance.to_float(),
                "conveyance_allowance": record.salary_income.conveyance_allowance.to_float(),
                "medical_allowance": record.salary_income.medical_allowance.to_float(),
                "bonus": record.salary_income.bonus.to_float(),
                "commission": record.salary_income.commission.to_float(),
                "overtime": record.salary_income.overtime.to_float(),
                "arrears": record.salary_income.arrears.to_float(),
                "gratuity": record.salary_income.gratuity.to_float(),
                "leave_encashment": record.salary_income.leave_encashment.to_float(),
                "other_allowances": record.salary_income.other_allowances.to_float()
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
                "property_type": record.house_property_income.property_type,
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
                "gratuity_amount": record.retirement_benefits.gratuity_amount.to_float(),
                "years_of_service": record.retirement_benefits.years_of_service,
                "is_government_employee": record.retirement_benefits.is_government_employee,
                "leave_encashment_amount": record.retirement_benefits.leave_encashment_amount.to_float(),
                "leave_balance": record.retirement_benefits.leave_balance,
                "pension_amount": record.retirement_benefits.pension_amount.to_float(),
                "is_commuted_pension": record.retirement_benefits.is_commuted_pension,
                "commutation_percentage": float(record.retirement_benefits.commutation_percentage),
                "vrs_compensation": record.retirement_benefits.vrs_compensation.to_float(),
                "other_retirement_benefits": record.retirement_benefits.other_retirement_benefits.to_float()
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
            house_rent_allowance=Money(document["salary_income"]["house_rent_allowance"]),
            special_allowance=Money(document["salary_income"]["special_allowance"]),
            conveyance_allowance=Money(document["salary_income"]["conveyance_allowance"]),
            medical_allowance=Money(document["salary_income"]["medical_allowance"]),
            bonus=Money(document["salary_income"]["bonus"]),
            commission=Money(document["salary_income"]["commission"]),
            overtime=Money(document["salary_income"]["overtime"]),
            arrears=Money(document["salary_income"]["arrears"]),
            gratuity=Money(document["salary_income"]["gratuity"]),
            leave_encashment=Money(document["salary_income"]["leave_encashment"]),
            other_allowances=Money(document["salary_income"]["other_allowances"])
        )
        
        # Convert perquisites
        perquisites = Perquisites(
            rent_free_accommodation=Money(document["perquisites"]["rent_free_accommodation"]),
            concessional_accommodation=Money(document["perquisites"]["concessional_accommodation"]),
            car_perquisite=Money(document["perquisites"]["car_perquisite"]),
            driver_perquisite=Money(document["perquisites"]["driver_perquisite"]),
            fuel_perquisite=Money(document["perquisites"]["fuel_perquisite"]),
            education_perquisite=Money(document["perquisites"]["education_perquisite"]),
            domestic_servant_perquisite=Money(document["perquisites"]["domestic_servant_perquisite"]),
            utility_perquisite=Money(document["perquisites"]["utility_perquisite"]),
            loan_perquisite=Money(document["perquisites"]["loan_perquisite"]),
            esop_perquisite=Money(document["perquisites"]["esop_perquisite"]),
            club_membership_perquisite=Money(document["perquisites"]["club_membership_perquisite"]),
            other_perquisites=Money(document["perquisites"]["other_perquisites"])
        )
        
        # Convert house property income
        house_property_income = HousePropertyIncome(
            property_type=document["house_property_income"]["property_type"],
            municipal_value=Money(document["house_property_income"]["municipal_value"]),
            fair_rental_value=Money(document["house_property_income"]["fair_rental_value"]),
            standard_rent=Money(document["house_property_income"]["standard_rent"]),
            actual_rent=Money(document["house_property_income"]["actual_rent"]),
            municipal_tax=Money(document["house_property_income"]["municipal_tax"]),
            interest_on_loan=Money(document["house_property_income"]["interest_on_loan"]),
            pre_construction_interest=Money(document["house_property_income"]["pre_construction_interest"]),
            other_deductions=Money(document["house_property_income"]["other_deductions"])
        )
        
        # Convert capital gains income
        capital_gains_income = CapitalGainsIncome(
            asset_type=document["capital_gains_income"]["asset_type"],
            purchase_date=date.fromisoformat(document["capital_gains_income"]["purchase_date"]),
            sale_date=date.fromisoformat(document["capital_gains_income"]["sale_date"]),
            purchase_price=Money(document["capital_gains_income"]["purchase_price"]),
            sale_price=Money(document["capital_gains_income"]["sale_price"]),
            transfer_expenses=Money(document["capital_gains_income"]["transfer_expenses"]),
            improvement_cost=Money(document["capital_gains_income"]["improvement_cost"])
        )
        
        # Convert retirement benefits
        retirement_benefits = RetirementBenefits(
            gratuity_amount=Money(document["retirement_benefits"]["gratuity_amount"]),
            years_of_service=document["retirement_benefits"]["years_of_service"],
            is_government_employee=document["retirement_benefits"]["is_government_employee"],
            leave_encashment_amount=Money(document["retirement_benefits"]["leave_encashment_amount"]),
            leave_balance=document["retirement_benefits"]["leave_balance"],
            pension_amount=Money(document["retirement_benefits"]["pension_amount"]),
            is_commuted_pension=document["retirement_benefits"]["is_commuted_pension"],
            commutation_percentage=Decimal(str(document["retirement_benefits"]["commutation_percentage"])),
            vrs_compensation=Money(document["retirement_benefits"]["vrs_compensation"]),
            other_retirement_benefits=Money(document["retirement_benefits"]["other_retirement_benefits"])
        )
        
        # Convert other income
        other_income = OtherIncome(
            bank_interest=Money(document["other_income"]["bank_interest"]),
            fixed_deposit_interest=Money(document["other_income"]["fixed_deposit_interest"]),
            recurring_deposit_interest=Money(document["other_income"]["recurring_deposit_interest"]),
            post_office_interest=Money(document["other_income"]["post_office_interest"]),
            other_interest=Money(document["other_income"]["other_interest"]),
            equity_dividend=Money(document["other_income"]["equity_dividend"]),
            mutual_fund_dividend=Money(document["other_income"]["mutual_fund_dividend"]),
            other_dividend=Money(document["other_income"]["other_dividend"]),
            house_property_rent=Money(document["other_income"]["house_property_rent"]),
            commercial_property_rent=Money(document["other_income"]["commercial_property_rent"]),
            other_rental=Money(document["other_income"]["other_rental"]),
            business_income=Money(document["other_income"]["business_income"]),
            professional_income=Money(document["other_income"]["professional_income"]),
            short_term_capital_gains=Money(document["other_income"]["short_term_capital_gains"]),
            long_term_capital_gains=Money(document["other_income"]["long_term_capital_gains"]),
            lottery_winnings=Money(document["other_income"]["lottery_winnings"]),
            horse_race_winnings=Money(document["other_income"]["horse_race_winnings"]),
            crossword_puzzle_winnings=Money(document["other_income"]["crossword_puzzle_winnings"]),
            card_game_winnings=Money(document["other_income"]["card_game_winnings"]),
            other_speculative_income=Money(document["other_income"]["other_speculative_income"]),
            agricultural_income=Money(document["other_income"]["agricultural_income"]),
            share_of_profit_partnership=Money(document["other_income"]["share_of_profit_partnership"]),
            interest_on_tax_free_bonds=Money(document["other_income"]["interest_on_tax_free_bonds"]),
            other_exempt_income=Money(document["other_income"]["other_exempt_income"])
        )
        
        # Convert tax deductions
        tax_deductions = TaxDeductions(
            life_insurance_premium=Money(document["tax_deductions"]["life_insurance_premium"]),
            elss_investments=Money(document["tax_deductions"]["elss_investments"]),
            public_provident_fund=Money(document["tax_deductions"]["public_provident_fund"]),
            employee_provident_fund=Money(document["tax_deductions"]["employee_provident_fund"]),
            sukanya_samriddhi=Money(document["tax_deductions"]["sukanya_samriddhi"]),
            national_savings_certificate=Money(document["tax_deductions"]["national_savings_certificate"]),
            tax_saving_fixed_deposits=Money(document["tax_deductions"]["tax_saving_fixed_deposits"]),
            principal_repayment_home_loan=Money(document["tax_deductions"]["principal_repayment_home_loan"]),
            tuition_fees=Money(document["tax_deductions"]["tuition_fees"]),
            other_80c_deductions=Money(document["tax_deductions"]["other_80c_deductions"]),
            health_insurance_self=Money(document["tax_deductions"]["health_insurance_self"]),
            health_insurance_parents=Money(document["tax_deductions"]["health_insurance_parents"]),
            preventive_health_checkup=Money(document["tax_deductions"]["preventive_health_checkup"]),
            education_loan_interest=Money(document["tax_deductions"]["education_loan_interest"]),
            donations_80g=Money(document["tax_deductions"]["donations_80g"]),
            savings_account_interest=Money(document["tax_deductions"]["savings_account_interest"]),
            senior_citizen_interest=Money(document["tax_deductions"]["senior_citizen_interest"]),
            disability_deduction=Money(document["tax_deductions"]["disability_deduction"]),
            medical_treatment_deduction=Money(document["tax_deductions"]["medical_treatment_deduction"]),
            scientific_research_donation=Money(document["tax_deductions"]["scientific_research_donation"]),
            political_donation=Money(document["tax_deductions"]["political_donation"]),
            infrastructure_deduction=Money(document["tax_deductions"]["infrastructure_deduction"]),
            industrial_undertaking_deduction=Money(document["tax_deductions"]["industrial_undertaking_deduction"]),
            special_category_state_deduction=Money(document["tax_deductions"]["special_category_state_deduction"]),
            hotel_deduction=Money(document["tax_deductions"]["hotel_deduction"]),
            north_eastern_state_deduction=Money(document["tax_deductions"]["north_eastern_state_deduction"]),
            employment_deduction=Money(document["tax_deductions"]["employment_deduction"]),
            employment_generation_deduction=Money(document["tax_deductions"]["employment_generation_deduction"]),
            offshore_banking_deduction=Money(document["tax_deductions"]["offshore_banking_deduction"]),
            co_operative_society_deduction=Money(document["tax_deductions"]["co_operative_society_deduction"]),
            royalty_deduction=Money(document["tax_deductions"]["royalty_deduction"]),
            patent_deduction=Money(document["tax_deductions"]["patent_deduction"]),
            interest_on_savings_deduction=Money(document["tax_deductions"]["interest_on_savings_deduction"]),
            disability_deduction_amount=Money(document["tax_deductions"]["disability_deduction_amount"])
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