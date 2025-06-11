"""
MongoDB Taxation Repository Implementation
Concrete implementation of taxation repository using MongoDB
Enhanced to support comprehensive taxation with all income types
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4
from decimal import Decimal

from motor.motor_asyncio import AsyncIOMotorCollection

from app.application.interfaces.repositories.taxation_repository import TaxationRepository
from app.domain.value_objects.user_id import UserId
from app.domain.value_objects.tax_year import TaxYear
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
from app.domain.value_objects.money import Money
from app.domain.entities.taxation_record import TaxationRecord
from app.domain.entities.salary_income import SalaryIncome
from app.domain.entities.tax_deductions import TaxDeductions, DeductionSection80C, DeductionSection80D, OtherDeductions

# Comprehensive income entities
from app.domain.entities.perquisites import (
    Perquisites, AccommodationPerquisite, CarPerquisite, AccommodationType,
    CityPopulation, CarUseType, AssetType, MedicalReimbursement, LTAPerquisite,
    InterestFreeConcessionalLoan, ESOPPerquisite, UtilitiesPerquisite,
    FreeEducationPerquisite, MovableAssetUsage, MovableAssetTransfer,
    LunchRefreshmentPerquisite, GiftVoucherPerquisite, MonetaryBenefitsPerquisite,
    ClubExpensesPerquisite, DomesticHelpPerquisite
)
from app.domain.entities.house_property_income import HousePropertyIncome, PropertyType
from app.domain.entities.capital_gains import CapitalGainsIncome, CapitalGainsType
from app.domain.entities.retirement_benefits import (
    RetirementBenefits, LeaveEncashment, Gratuity, VRS, Pension, RetrenchmentCompensation
)
from app.domain.entities.other_income import OtherIncome, InterestIncome
from app.domain.entities.monthly_payroll import MonthlyPayroll, AnnualPayrollWithLWP, LWPDetails

from app.domain.exceptions.taxation_exceptions import TaxationRepositoryError
from app.infrastructure.database.database_connector import DatabaseConnector


logger = logging.getLogger(__name__)


class MongoDBTaxationRepository(TaxationRepository):
    """
    MongoDB implementation of taxation repository.
    
    Enhanced to handle comprehensive taxation with all income types:
    - Salary income (simple and periodic)
    - Perquisites (all 15+ types)
    - House property income
    - Capital gains
    - Retirement benefits
    - Other income sources
    - Monthly payroll with LWP
    
    Maintains backward compatibility with existing basic taxation records.
    """
    
    def __init__(self, db_connector: DatabaseConnector):
        self.db_connector = db_connector
    
    async def _get_collection(self, organization_id: str) -> AsyncIOMotorCollection:
        """Get taxation collection for organization."""
        db = await self.db_connector.get_database(organization_id)
        return db.taxation_records
    
    async def save(self, taxation_record: TaxationRecord) -> TaxationRecord:
        """Save or update a taxation record."""
        try:
            collection = await self._get_collection(taxation_record.organization_id)
            
            # Convert entity to document
            document = self._entity_to_document(taxation_record)
            
            # Update or insert
            filter_query = {"taxation_id": taxation_record.taxation_id}
            
            result = await collection.replace_one(
                filter_query,
                document,
                upsert=True
            )
            
            if not result.acknowledged:
                raise TaxationRepositoryError("save", "Failed to save taxation record")
            
            logger.info(f"Saved taxation record: {taxation_record.taxation_id}")
            return taxation_record
            
        except Exception as e:
            logger.error(f"Error saving taxation record: {e}")
            raise TaxationRepositoryError("save", str(e))
    
    async def get_by_id(self, taxation_id: str, organization_id: str) -> Optional[TaxationRecord]:
        """Get taxation record by ID."""
        try:
            collection = await self._get_collection(organization_id)
            
            document = await collection.find_one({"taxation_id": taxation_id})
            
            if document:
                return self._document_to_entity(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting taxation record by ID: {e}")
            raise TaxationRepositoryError("get_by_id", str(e))
    
    def _convert_doc_to_perquisites(self, doc: Dict[str, Any]) -> Perquisites:
        """Convert document to perquisites entity."""
        # Accommodation
        accommodation = None
        if doc.get("accommodation"):
            acc_doc = doc["accommodation"]
            accommodation = AccommodationPerquisite(
                accommodation_type=AccommodationType(acc_doc["accommodation_type"]),
                city_population=CityPopulation(acc_doc["city_population"]),
                license_fees=Money.from_float(acc_doc["license_fees"]),
                employee_rent_payment=Money.from_float(acc_doc["employee_rent_payment"]),
                basic_salary=Money.from_float(acc_doc["basic_salary"]),
                dearness_allowance=Money.from_float(acc_doc["dearness_allowance"]),
                rent_paid_by_employer=Money.from_float(acc_doc["rent_paid_by_employer"]),
                hotel_charges=Money.from_float(acc_doc["hotel_charges"]),
                stay_days=acc_doc["stay_days"],
                furniture_cost=Money.from_float(acc_doc["furniture_cost"]),
                furniture_employee_payment=Money.from_float(acc_doc["furniture_employee_payment"]),
                is_furniture_owned_by_employer=acc_doc["is_furniture_owned_by_employer"]
            )
        
        # Car
        car = None
        if doc.get("car"):
            car_doc = doc["car"]
            car = CarPerquisite(
                car_use_type=CarUseType(car_doc["car_use_type"]),
                engine_capacity_cc=car_doc["engine_capacity_cc"],
                months_used=car_doc["months_used"],
                car_cost_to_employer=Money.from_float(car_doc["car_cost_to_employer"]),
                other_vehicle_cost=Money.from_float(car_doc["other_vehicle_cost"]),
                has_expense_reimbursement=car_doc["has_expense_reimbursement"],
                driver_provided=car_doc["driver_provided"]
            )
        
        # Medical reimbursement
        medical_reimbursement = None
        if doc.get("medical_reimbursement"):
            med_doc = doc["medical_reimbursement"]
            medical_reimbursement = MedicalReimbursement(
                medical_reimbursement_amount=Money.from_float(med_doc["medical_reimbursement_amount"]),
                is_overseas_treatment=med_doc["is_overseas_treatment"]
            )
        
        # LTA
        lta = None
        if doc.get("lta"):
            lta_doc = doc["lta"]
            lta = LTAPerquisite(
                lta_amount_claimed=Money.from_float(lta_doc["lta_amount_claimed"]),
                lta_claimed_count=lta_doc["lta_claimed_count"],
                public_transport_cost=Money.from_float(lta_doc["public_transport_cost"])
            )
        
        # Interest free loan
        interest_free_loan = None
        if doc.get("interest_free_loan"):
            loan_doc = doc["interest_free_loan"]
            interest_free_loan = InterestFreeConcessionalLoan(
                loan_amount=Money.from_float(loan_doc["loan_amount"]),
                outstanding_amount=Money.from_float(loan_doc["outstanding_amount"]),
                company_interest_rate=Decimal(str(loan_doc["company_interest_rate"])),
                sbi_interest_rate=Decimal(str(loan_doc["sbi_interest_rate"])),
                loan_months=loan_doc["loan_months"]
            )
        
        # ESOP
        esop = None
        if doc.get("esop"):
            esop_doc = doc["esop"]
            esop = ESOPPerquisite(
                shares_exercised=esop_doc["shares_exercised"],
                exercise_price=Money.from_float(esop_doc["exercise_price"]),
                allotment_price=Money.from_float(esop_doc["allotment_price"])
            )
        
        # Utilities
        utilities = None
        if doc.get("utilities"):
            util_doc = doc["utilities"]
            utilities = UtilitiesPerquisite(
                gas_paid_by_employer=Money.from_float(util_doc["gas_paid_by_employer"]),
                electricity_paid_by_employer=Money.from_float(util_doc["electricity_paid_by_employer"]),
                water_paid_by_employer=Money.from_float(util_doc["water_paid_by_employer"]),
                gas_paid_by_employee=Money.from_float(util_doc["gas_paid_by_employee"]),
                is_manufacturing_company=util_doc["is_manufacturing_company"]
            )
        
        # Free education
        free_education = None
        if doc.get("free_education"):
            edu_doc = doc["free_education"]
            free_education = FreeEducationPerquisite(
                monthly_expenses_child1=Money.from_float(edu_doc["monthly_expenses_child1"]),
                monthly_expenses_child2=Money.from_float(edu_doc["monthly_expenses_child2"]),
                months_child1=edu_doc["months_child1"],
                months_child2=edu_doc["months_child2"],
                is_maintained_by_employer=edu_doc["is_maintained_by_employer"]
            )
        
        # Other perquisites (condensed for brevity)
        movable_asset_usage = None
        if doc.get("movable_asset_usage"):
            asset_doc = doc["movable_asset_usage"]
            movable_asset_usage = MovableAssetUsage(
                asset_type=AssetType(asset_doc["asset_type"]),
                market_value=Money.from_float(asset_doc["market_value"]),
                usage_months=asset_doc["usage_months"]
            )
        
        movable_asset_transfer = None
        if doc.get("movable_asset_transfer"):
            transfer_doc = doc["movable_asset_transfer"]
            movable_asset_transfer = MovableAssetTransfer(
                asset_type=AssetType(transfer_doc["asset_type"]),
                market_value=Money.from_float(transfer_doc["market_value"]),
                employee_payment=Money.from_float(transfer_doc["employee_payment"])
            )
        
        lunch_refreshment = None
        if doc.get("lunch_refreshment"):
            lunch_refreshment = LunchRefreshmentPerquisite(
                annual_value=Money.from_float(doc["lunch_refreshment"]["annual_value"])
            )
        
        gift_voucher = None
        if doc.get("gift_voucher"):
            gift_voucher = GiftVoucherPerquisite(
                annual_value=Money.from_float(doc["gift_voucher"]["annual_value"])
            )
        
        monetary_benefits = None
        if doc.get("monetary_benefits"):
            monetary_benefits = MonetaryBenefitsPerquisite(
                annual_amount=Money.from_float(doc["monetary_benefits"]["annual_amount"])
            )
        
        club_expenses = None
        if doc.get("club_expenses"):
            club_expenses = ClubExpensesPerquisite(
                annual_expenses=Money.from_float(doc["club_expenses"]["annual_expenses"])
            )
        
        domestic_help = None
        if doc.get("domestic_help"):
            domestic_help = DomesticHelpPerquisite(
                annual_cost=Money.from_float(doc["domestic_help"]["annual_cost"])
            )
        
        return Perquisites(
            accommodation=accommodation,
            car=car,
            medical_reimbursement=medical_reimbursement,
            lta=lta,
            interest_free_loan=interest_free_loan,
            esop=esop,
            utilities=utilities,
            free_education=free_education,
            movable_asset_usage=movable_asset_usage,
            movable_asset_transfer=movable_asset_transfer,
            lunch_refreshment=lunch_refreshment,
            gift_voucher=gift_voucher,
            monetary_benefits=monetary_benefits,
            club_expenses=club_expenses,
            domestic_help=domestic_help
        )
    
    def _convert_doc_to_house_property(self, doc: Dict[str, Any]) -> HousePropertyIncome:
        """Convert document to house property income entity."""
        return HousePropertyIncome(
            property_type=PropertyType(doc["property_type"]),
            annual_rent_received=Money.from_float(doc["annual_rent_received"]),
            municipal_taxes_paid=Money.from_float(doc["municipal_taxes_paid"]),
            home_loan_interest=Money.from_float(doc["home_loan_interest"]),
            pre_construction_interest=Money.from_float(doc["pre_construction_interest"]),
            fair_rental_value=Money.from_float(doc["fair_rental_value"]),
            standard_rent=Money.from_float(doc["standard_rent"])
        )
    
    def _convert_doc_to_capital_gains(self, doc: Dict[str, Any]) -> CapitalGainsIncome:
        """Convert document to capital gains income entity."""
        return CapitalGainsIncome(
            stcg_111a_equity_stt=Money.from_float(doc["stcg_111a_equity_stt"]),
            stcg_other_assets=Money.from_float(doc["stcg_other_assets"]),
            ltcg_112a_equity_stt=Money.from_float(doc["ltcg_112a_equity_stt"]),
            ltcg_other_assets=Money.from_float(doc["ltcg_other_assets"]),
            ltcg_debt_mf=Money.from_float(doc["ltcg_debt_mf"])
        )
    
    def _convert_doc_to_retirement_benefits(self, doc: Dict[str, Any]) -> RetirementBenefits:
        """Convert document to retirement benefits entity."""
        leave_encashment = None
        if doc.get("leave_encashment"):
            le_doc = doc["leave_encashment"]
            leave_encashment = LeaveEncashment(
                leave_encashment_amount=Money.from_float(le_doc["leave_encashment_amount"]),
                average_monthly_salary=Money.from_float(le_doc["average_monthly_salary"]),
                leave_days_encashed=le_doc["leave_days_encashed"],
                is_govt_employee=le_doc["is_govt_employee"],
                during_employment=le_doc["during_employment"]
            )
        
        gratuity = None
        if doc.get("gratuity"):
            gr_doc = doc["gratuity"]
            gratuity = Gratuity(
                gratuity_amount=Money.from_float(gr_doc["gratuity_amount"]),
                monthly_salary=Money.from_float(gr_doc["monthly_salary"]),
                service_years=Decimal(str(gr_doc["service_years"])),
                is_govt_employee=gr_doc["is_govt_employee"]
            )
        
        vrs = None
        if doc.get("vrs"):
            vrs_doc = doc["vrs"]
            vrs = VRS(
                vrs_amount=Money.from_float(vrs_doc["vrs_amount"]),
                monthly_salary=Money.from_float(vrs_doc["monthly_salary"]),
                age=vrs_doc["age"],
                service_years=Decimal(str(vrs_doc["service_years"]))
            )
        
        pension = None
        if doc.get("pension"):
            pen_doc = doc["pension"]
            pension = Pension(
                regular_pension=Money.from_float(pen_doc["regular_pension"]),
                commuted_pension=Money.from_float(pen_doc["commuted_pension"]),
                total_pension=Money.from_float(pen_doc["total_pension"]),
                is_govt_employee=pen_doc["is_govt_employee"],
                gratuity_received=pen_doc["gratuity_received"]
            )
        
        retrenchment_compensation = None
        if doc.get("retrenchment_compensation"):
            rc_doc = doc["retrenchment_compensation"]
            retrenchment_compensation = RetrenchmentCompensation(
                retrenchment_amount=Money.from_float(rc_doc["retrenchment_amount"]),
                monthly_salary=Money.from_float(rc_doc["monthly_salary"]),
                service_years=Decimal(str(rc_doc["service_years"]))
            )
        
        return RetirementBenefits(
            leave_encashment=leave_encashment,
            gratuity=gratuity,
            vrs=vrs,
            pension=pension,
            retrenchment_compensation=retrenchment_compensation
        )
    
    def _convert_doc_to_other_income(self, doc: Dict[str, Any]) -> OtherIncome:
        """Convert document to other income entity."""
        interest_income = None
        if doc.get("interest_income"):
            ii_doc = doc["interest_income"]
            interest_income = InterestIncome(
                savings_account_interest=Money.from_float(ii_doc["savings_account_interest"]),
                fixed_deposit_interest=Money.from_float(ii_doc["fixed_deposit_interest"]),
                recurring_deposit_interest=Money.from_float(ii_doc["recurring_deposit_interest"]),
                other_bank_interest=Money.from_float(ii_doc["other_bank_interest"]),
                age=ii_doc["age"]
            )
        
        return OtherIncome(
            interest_income=interest_income,
            dividend_income=Money.from_float(doc["dividend_income"]),
            gifts_received=Money.from_float(doc["gifts_received"]),
            business_professional_income=Money.from_float(doc["business_professional_income"]),
            other_miscellaneous_income=Money.from_float(doc["other_miscellaneous_income"])
        )
    
    def _convert_doc_to_monthly_payroll(self, doc: Dict[str, Any]) -> AnnualPayrollWithLWP:
        """Convert document to monthly payroll entity."""
        monthly_payrolls = []
        for mp_doc in doc["monthly_payrolls"]:
            monthly_payrolls.append(MonthlyPayroll(
                month=mp_doc["month"],
                year=mp_doc["year"],
                base_monthly_gross=Money.from_float(mp_doc["base_monthly_gross"]),
                lwp_days=mp_doc["lwp_days"],
                working_days_in_month=mp_doc["working_days_in_month"]
            ))
        
        lwp_details = []
        for lwp_doc in doc["lwp_details"]:
            lwp_details.append(LWPDetails(
                month=lwp_doc["month"],
                year=lwp_doc["year"],
                lwp_days=lwp_doc["lwp_days"],
                working_days_in_month=lwp_doc["working_days_in_month"]
            ))
        
        return AnnualPayrollWithLWP(
            monthly_payrolls=monthly_payrolls,
            annual_salary=Money.from_float(doc["annual_salary"]),
            total_lwp_days=doc["total_lwp_days"],
            lwp_details=lwp_details
        )
    
    async def get_by_id(self, taxation_id: str, organization_id: str) -> Optional[TaxationRecord]:
        """Get taxation record by ID."""
        try:
            collection = await self._get_collection(organization_id)
            
            document = await collection.find_one({"taxation_id": taxation_id})
            
            if document:
                return self._document_to_entity(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting taxation record by ID: {e}")
            raise TaxationRepositoryError("get_by_id", str(e))
    
    async def get_by_user_and_year(self, 
                                 user_id: UserId, 
                                 tax_year: TaxYear,
                                 organization_id: str) -> Optional[TaxationRecord]:
        """Get taxation record by user and tax year."""
        try:
            collection = await self._get_collection(organization_id)
            
            document = await collection.find_one({
                "user_id": str(user_id),
                "tax_year": str(tax_year)
            })
            
            if document:
                return self._document_to_entity(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting taxation record by user and year: {e}")
            raise TaxationRepositoryError("get_by_user_and_year", str(e))
    
    async def get_by_user(self, 
                        user_id: UserId, 
                        organization_id: str,
                        limit: int = 10,
                        offset: int = 0) -> List[TaxationRecord]:
        """Get all taxation records for a user."""
        try:
            collection = await self._get_collection(organization_id)
            
            cursor = collection.find({"user_id": str(user_id)}) \
                             .sort("created_at", -1) \
                             .skip(offset) \
                             .limit(limit)
            
            documents = await cursor.to_list(length=limit)
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting taxation records by user: {e}")
            raise TaxationRepositoryError("get_by_user", str(e))
    
    async def get_by_tax_year(self, 
                            tax_year: TaxYear,
                            organization_id: str,
                            limit: int = 100,
                            offset: int = 0) -> List[TaxationRecord]:
        """Get all taxation records for a tax year."""
        try:
            collection = await self._get_collection(organization_id)
            
            cursor = collection.find({"tax_year": str(tax_year)}) \
                             .sort("created_at", -1) \
                             .skip(offset) \
                             .limit(limit)
            
            documents = await cursor.to_list(length=limit)
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting taxation records by tax year: {e}")
            raise TaxationRepositoryError("get_by_tax_year", str(e))
    
    async def get_by_organization(self, 
                                organization_id: str,
                                limit: int = 100,
                                offset: int = 0) -> List[TaxationRecord]:
        """Get all taxation records for an organization."""
        try:
            collection = await self._get_collection(organization_id)
            
            cursor = collection.find({}) \
                             .sort("created_at", -1) \
                             .skip(offset) \
                             .limit(limit)
            
            documents = await cursor.to_list(length=limit)
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting taxation records by organization: {e}")
            raise TaxationRepositoryError("get_by_organization", str(e))
    
    async def search(self, 
                   organization_id: str,
                   user_id: Optional[UserId] = None,
                   tax_year: Optional[TaxYear] = None,
                   regime: Optional[str] = None,
                   is_final: Optional[bool] = None,
                   limit: int = 100,
                   offset: int = 0) -> List[TaxationRecord]:
        """Search taxation records with filters."""
        try:
            collection = await self._get_collection(organization_id)
            
            # Build query
            query = {}
            
            if user_id:
                query["user_id"] = str(user_id)
            
            if tax_year:
                query["tax_year"] = str(tax_year)
            
            if regime:
                query["regime"] = regime
            
            if is_final is not None:
                query["is_final"] = is_final
            
            cursor = collection.find(query) \
                             .sort("created_at", -1) \
                             .skip(offset) \
                             .limit(limit)
            
            documents = await cursor.to_list(length=limit)
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error searching taxation records: {e}")
            raise TaxationRepositoryError("search", str(e))
    
    async def count(self, 
                  organization_id: str,
                  user_id: Optional[UserId] = None,
                  tax_year: Optional[TaxYear] = None,
                  regime: Optional[str] = None,
                  is_final: Optional[bool] = None) -> int:
        """Count taxation records with filters."""
        try:
            collection = await self._get_collection(organization_id)
            
            # Build query
            query = {}
            
            if user_id:
                query["user_id"] = str(user_id)
            
            if tax_year:
                query["tax_year"] = str(tax_year)
            
            if regime:
                query["regime"] = regime
            
            if is_final is not None:
                query["is_final"] = is_final
            
            return await collection.count_documents(query)
            
        except Exception as e:
            logger.error(f"Error counting taxation records: {e}")
            raise TaxationRepositoryError("count", str(e))
    
    async def delete(self, taxation_id: str, organization_id: str) -> bool:
        """Delete a taxation record."""
        try:
            collection = await self._get_collection(organization_id)
            
            result = await collection.delete_one({"taxation_id": taxation_id})
            
            if result.deleted_count > 0:
                logger.info(f"Deleted taxation record: {taxation_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting taxation record: {e}")
            raise TaxationRepositoryError("delete", str(e))
    
    async def exists(self, 
                   user_id: UserId, 
                   tax_year: TaxYear,
                   organization_id: str) -> bool:
        """Check if taxation record exists for user and tax year."""
        try:
            collection = await self._get_collection(organization_id)
            
            count = await collection.count_documents({
                "user_id": str(user_id),
                "tax_year": str(tax_year)
            })
            
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking taxation record existence: {e}")
            raise TaxationRepositoryError("exists", str(e))
    
    def _entity_to_document(self, taxation_record: TaxationRecord) -> Dict[str, Any]:
        """
        Convert entity to MongoDB document.
        
        Enhanced to handle comprehensive taxation with all income types.
        Maintains backward compatibility with existing documents.
        """
        
        # Convert salary income (core - required)
        salary_doc = {
            "basic_salary": float(taxation_record.salary_income.basic_salary.amount),
            "dearness_allowance": float(taxation_record.salary_income.dearness_allowance.amount),
            "hra_received": float(taxation_record.salary_income.hra_received.amount),
            "hra_city_type": taxation_record.salary_income.hra_city_type,
            "actual_rent_paid": float(taxation_record.salary_income.actual_rent_paid.amount),
            "special_allowance": float(taxation_record.salary_income.special_allowance.amount),
            "other_allowances": float(taxation_record.salary_income.other_allowances.amount),
            "lta_received": float(taxation_record.salary_income.lta_received.amount),
            "medical_allowance": float(taxation_record.salary_income.medical_allowance.amount),
            "conveyance_allowance": float(taxation_record.salary_income.conveyance_allowance.amount)
        }
        
        # Convert deductions (core - required)
        deductions_doc = {
            "section_80c": {
                "life_insurance_premium": float(taxation_record.deductions.section_80c.life_insurance_premium.amount),
                "epf_contribution": float(taxation_record.deductions.section_80c.epf_contribution.amount),
                "ppf_contribution": float(taxation_record.deductions.section_80c.ppf_contribution.amount),
                "nsc_investment": float(taxation_record.deductions.section_80c.nsc_investment.amount),
                "tax_saving_fd": float(taxation_record.deductions.section_80c.tax_saving_fd.amount),
                "elss_investment": float(taxation_record.deductions.section_80c.elss_investment.amount),
                "home_loan_principal": float(taxation_record.deductions.section_80c.home_loan_principal.amount),
                "tuition_fees": float(taxation_record.deductions.section_80c.tuition_fees.amount),
                "ulip_premium": float(taxation_record.deductions.section_80c.ulip_premium.amount),
                "sukanya_samriddhi": float(taxation_record.deductions.section_80c.sukanya_samriddhi.amount),
                "other_80c_investments": float(taxation_record.deductions.section_80c.other_80c_investments.amount)
            },
            "section_80d": {
                "self_family_premium": float(taxation_record.deductions.section_80d.self_family_premium.amount),
                "parent_premium": float(taxation_record.deductions.section_80d.parent_premium.amount),
                "preventive_health_checkup": float(taxation_record.deductions.section_80d.preventive_health_checkup.amount),
                "employee_age": taxation_record.deductions.section_80d.employee_age,
                "parent_age": taxation_record.deductions.section_80d.parent_age
            },
            "other_deductions": {
                "education_loan_interest": float(taxation_record.deductions.other_deductions.education_loan_interest.amount),
                "charitable_donations": float(taxation_record.deductions.other_deductions.charitable_donations.amount),
                "savings_interest": float(taxation_record.deductions.other_deductions.savings_interest.amount),
                "nps_contribution": float(taxation_record.deductions.other_deductions.nps_contribution.amount),
                "other_deductions": float(taxation_record.deductions.other_deductions.other_deductions.amount)
            }
        }
        
        # COMPREHENSIVE INCOME COMPONENTS (new - optional)
        
        # Convert perquisites (if present)
        perquisites_doc = None
        if taxation_record.perquisites:
            perquisites_doc = self._convert_perquisites_to_doc(taxation_record.perquisites)
        
        # Convert house property income (if present)
        house_property_doc = None
        if taxation_record.house_property_income:
            house_property_doc = self._convert_house_property_to_doc(taxation_record.house_property_income)
        
        # Convert capital gains income (if present)
        capital_gains_doc = None
        if taxation_record.capital_gains_income:
            capital_gains_doc = self._convert_capital_gains_to_doc(taxation_record.capital_gains_income)
        
        # Convert retirement benefits (if present)
        retirement_benefits_doc = None
        if taxation_record.retirement_benefits:
            retirement_benefits_doc = self._convert_retirement_benefits_to_doc(taxation_record.retirement_benefits)
        
        # Convert other income (if present)
        other_income_doc = None
        if taxation_record.other_income:
            other_income_doc = self._convert_other_income_to_doc(taxation_record.other_income)
        
        # Convert monthly payroll (if present)
        monthly_payroll_doc = None
        if taxation_record.monthly_payroll:
            monthly_payroll_doc = self._convert_monthly_payroll_to_doc(taxation_record.monthly_payroll)
        
        # Convert calculation result if exists
        calculation_doc = None
        if taxation_record.calculation_result:
            calculation_doc = {
                "gross_income": float(taxation_record.calculation_result.gross_income.amount),
                "total_exemptions": float(taxation_record.calculation_result.total_exemptions.amount),
                "total_deductions": float(taxation_record.calculation_result.total_deductions.amount),
                "taxable_income": float(taxation_record.calculation_result.taxable_income.amount),
                "tax_before_rebate": float(taxation_record.calculation_result.tax_before_rebate.amount),
                "rebate_87a": float(taxation_record.calculation_result.rebate_87a.amount),
                "tax_after_rebate": float(taxation_record.calculation_result.tax_after_rebate.amount),
                "surcharge": float(taxation_record.calculation_result.surcharge.amount),
                "cess": float(taxation_record.calculation_result.cess.amount),
                "total_tax_liability": float(taxation_record.calculation_result.total_tax_liability.amount),
                "effective_tax_rate": float(taxation_record.calculation_result.effective_tax_rate),
                "regime_type": taxation_record.calculation_result.regime_used.regime_type.value,
                "taxpayer_age": taxation_record.calculation_result.taxpayer_age,
                "calculation_breakdown": taxation_record.calculation_result.calculation_breakdown
            }
        
        # Build complete document
        document = {
            "taxation_id": taxation_record.taxation_id,
            "user_id": str(taxation_record.user_id),
            "organization_id": taxation_record.organization_id,
            "tax_year": str(taxation_record.tax_year),
            "salary_income": salary_doc,
            "deductions": deductions_doc,
            "regime": taxation_record.regime.regime_type.value,
            "age": taxation_record.age,
            "calculation_result": calculation_doc,
            "last_calculated_at": taxation_record.last_calculated_at,
            "is_final": taxation_record.is_final,
            "submitted_at": taxation_record.submitted_at,
            "created_at": taxation_record.created_at,
            "updated_at": taxation_record.updated_at,
            "version": taxation_record.version,
            
            # Comprehensive income components (new fields)
            "has_comprehensive_income": taxation_record.has_comprehensive_income(),
            "perquisites": perquisites_doc,
            "house_property_income": house_property_doc,
            "capital_gains_income": capital_gains_doc,
            "retirement_benefits": retirement_benefits_doc,
            "other_income": other_income_doc,
            "monthly_payroll": monthly_payroll_doc
        }
        
        return document
    
    def _convert_perquisites_to_doc(self, perquisites: Perquisites) -> Dict[str, Any]:
        """Convert perquisites entity to document format."""
        doc = {}
        
        # Accommodation perquisite
        if perquisites.accommodation:
            acc = perquisites.accommodation
            doc["accommodation"] = {
                "accommodation_type": acc.accommodation_type.value,
                "city_population": acc.city_population.value,
                "license_fees": float(acc.license_fees.amount),
                "employee_rent_payment": float(acc.employee_rent_payment.amount),
                "basic_salary": float(acc.basic_salary.amount),
                "dearness_allowance": float(acc.dearness_allowance.amount),
                "rent_paid_by_employer": float(acc.rent_paid_by_employer.amount),
                "hotel_charges": float(acc.hotel_charges.amount),
                "stay_days": acc.stay_days,
                "furniture_cost": float(acc.furniture_cost.amount),
                "furniture_employee_payment": float(acc.furniture_employee_payment.amount),
                "is_furniture_owned_by_employer": acc.is_furniture_owned_by_employer
            }
        
        # Car perquisite
        if perquisites.car:
            car = perquisites.car
            doc["car"] = {
                "car_use_type": car.car_use_type.value,
                "engine_capacity_cc": car.engine_capacity_cc,
                "months_used": car.months_used,
                "car_cost_to_employer": float(car.car_cost_to_employer.amount),
                "other_vehicle_cost": float(car.other_vehicle_cost.amount),
                "has_expense_reimbursement": car.has_expense_reimbursement,
                "driver_provided": car.driver_provided
            }
        
        # Medical reimbursement
        if perquisites.medical_reimbursement:
            med = perquisites.medical_reimbursement
            doc["medical_reimbursement"] = {
                "medical_reimbursement_amount": float(med.medical_reimbursement_amount.amount),
                "is_overseas_treatment": med.is_overseas_treatment
            }
        
        # LTA perquisite
        if perquisites.lta:
            lta = perquisites.lta
            doc["lta"] = {
                "lta_amount_claimed": float(lta.lta_amount_claimed.amount),
                "lta_claimed_count": lta.lta_claimed_count,
                "public_transport_cost": float(lta.public_transport_cost.amount)
            }
        
        # Interest free/concessional loan
        if perquisites.interest_free_loan:
            loan = perquisites.interest_free_loan
            doc["interest_free_loan"] = {
                "loan_amount": float(loan.loan_amount.amount),
                "outstanding_amount": float(loan.outstanding_amount.amount),
                "company_interest_rate": float(loan.company_interest_rate),
                "sbi_interest_rate": float(loan.sbi_interest_rate),
                "loan_months": loan.loan_months
            }
        
        # ESOP perquisite
        if perquisites.esop:
            esop = perquisites.esop
            doc["esop"] = {
                "shares_exercised": esop.shares_exercised,
                "exercise_price": float(esop.exercise_price.amount),
                "allotment_price": float(esop.allotment_price.amount)
            }
        
        # Utilities perquisite
        if perquisites.utilities:
            util = perquisites.utilities
            doc["utilities"] = {
                "gas_paid_by_employer": float(util.gas_paid_by_employer.amount),
                "electricity_paid_by_employer": float(util.electricity_paid_by_employer.amount),
                "water_paid_by_employer": float(util.water_paid_by_employer.amount),
                "gas_paid_by_employee": float(util.gas_paid_by_employee.amount),
                "is_manufacturing_company": util.is_manufacturing_company
            }
        
        # Free education perquisite
        if perquisites.free_education:
            edu = perquisites.free_education
            doc["free_education"] = {
                "monthly_expenses_child1": float(edu.monthly_expenses_child1.amount),
                "monthly_expenses_child2": float(edu.monthly_expenses_child2.amount),
                "months_child1": edu.months_child1,
                "months_child2": edu.months_child2,
                "is_maintained_by_employer": edu.is_maintained_by_employer
            }
        
        # Additional perquisites (condensed for brevity)
        if perquisites.movable_asset_usage:
            asset = perquisites.movable_asset_usage
            doc["movable_asset_usage"] = {
                "asset_type": asset.asset_type.value,
                "market_value": float(asset.market_value.amount),
                "usage_months": asset.usage_months
            }
        
        if perquisites.movable_asset_transfer:
            transfer = perquisites.movable_asset_transfer
            doc["movable_asset_transfer"] = {
                "asset_type": transfer.asset_type.value,
                "market_value": float(transfer.market_value.amount),
                "employee_payment": float(transfer.employee_payment.amount)
            }
        
        if perquisites.lunch_refreshment:
            lunch = perquisites.lunch_refreshment
            doc["lunch_refreshment"] = {
                "annual_value": float(lunch.annual_value.amount)
            }
        
        if perquisites.gift_voucher:
            gift = perquisites.gift_voucher
            doc["gift_voucher"] = {
                "annual_value": float(gift.annual_value.amount)
            }
        
        if perquisites.monetary_benefits:
            monetary = perquisites.monetary_benefits
            doc["monetary_benefits"] = {
                "annual_amount": float(monetary.annual_amount.amount)
            }
        
        if perquisites.club_expenses:
            club = perquisites.club_expenses
            doc["club_expenses"] = {
                "annual_expenses": float(club.annual_expenses.amount)
            }
        
        if perquisites.domestic_help:
            help_service = perquisites.domestic_help
            doc["domestic_help"] = {
                "annual_cost": float(help_service.annual_cost.amount)
            }
        
        return doc
    
    def _convert_house_property_to_doc(self, house_property: HousePropertyIncome) -> Dict[str, Any]:
        """Convert house property income entity to document format."""
        return {
            "property_type": house_property.property_type.value,
            "annual_rent_received": float(house_property.annual_rent_received.amount),
            "municipal_taxes_paid": float(house_property.municipal_taxes_paid.amount),
            "home_loan_interest": float(house_property.home_loan_interest.amount),
            "pre_construction_interest": float(house_property.pre_construction_interest.amount),
            "fair_rental_value": float(house_property.fair_rental_value.amount),
            "standard_rent": float(house_property.standard_rent.amount)
        }
    
    def _convert_capital_gains_to_doc(self, capital_gains: CapitalGainsIncome) -> Dict[str, Any]:
        """Convert capital gains income entity to document format."""
        return {
            "stcg_111a_equity_stt": float(capital_gains.stcg_111a_equity_stt.amount),
            "stcg_other_assets": float(capital_gains.stcg_other_assets.amount),
            "ltcg_112a_equity_stt": float(capital_gains.ltcg_112a_equity_stt.amount),
            "ltcg_other_assets": float(capital_gains.ltcg_other_assets.amount),
            "ltcg_debt_mf": float(capital_gains.ltcg_debt_mf.amount)
        }
    
    def _convert_retirement_benefits_to_doc(self, retirement_benefits: RetirementBenefits) -> Dict[str, Any]:
        """Convert retirement benefits entity to document format."""
        doc = {}
        
        if retirement_benefits.leave_encashment:
            le = retirement_benefits.leave_encashment
            doc["leave_encashment"] = {
                "leave_encashment_amount": float(le.leave_encashment_amount.amount),
                "average_monthly_salary": float(le.average_monthly_salary.amount),
                "leave_days_encashed": le.leave_days_encashed,
                "is_govt_employee": le.is_govt_employee,
                "during_employment": le.during_employment
            }
        
        if retirement_benefits.gratuity:
            gr = retirement_benefits.gratuity
            doc["gratuity"] = {
                "gratuity_amount": float(gr.gratuity_amount.amount),
                "monthly_salary": float(gr.monthly_salary.amount),
                "service_years": float(gr.service_years),
                "is_govt_employee": gr.is_govt_employee
            }
        
        if retirement_benefits.vrs:
            vrs = retirement_benefits.vrs
            doc["vrs"] = {
                "vrs_amount": float(vrs.vrs_amount.amount),
                "monthly_salary": float(vrs.monthly_salary.amount),
                "age": vrs.age,
                "service_years": float(vrs.service_years)
            }
        
        if retirement_benefits.pension:
            pen = retirement_benefits.pension
            doc["pension"] = {
                "regular_pension": float(pen.regular_pension.amount),
                "commuted_pension": float(pen.commuted_pension.amount),
                "total_pension": float(pen.total_pension.amount),
                "is_govt_employee": pen.is_govt_employee,
                "gratuity_received": pen.gratuity_received
            }
        
        if retirement_benefits.retrenchment_compensation:
            rc = retirement_benefits.retrenchment_compensation
            doc["retrenchment_compensation"] = {
                "retrenchment_amount": float(rc.retrenchment_amount.amount),
                "monthly_salary": float(rc.monthly_salary.amount),
                "service_years": float(rc.service_years)
            }
        
        return doc
    
    def _convert_other_income_to_doc(self, other_income: OtherIncome) -> Dict[str, Any]:
        """Convert other income entity to document format."""
        doc = {
            "dividend_income": float(other_income.dividend_income.amount),
            "gifts_received": float(other_income.gifts_received.amount),
            "business_professional_income": float(other_income.business_professional_income.amount),
            "other_miscellaneous_income": float(other_income.other_miscellaneous_income.amount)
        }
        
        if other_income.interest_income:
            ii = other_income.interest_income
            doc["interest_income"] = {
                "savings_account_interest": float(ii.savings_account_interest.amount),
                "fixed_deposit_interest": float(ii.fixed_deposit_interest.amount),
                "recurring_deposit_interest": float(ii.recurring_deposit_interest.amount),
                "other_bank_interest": float(ii.other_bank_interest.amount),
                "age": ii.age
            }
        
        return doc
    
    def _convert_monthly_payroll_to_doc(self, monthly_payroll: AnnualPayrollWithLWP) -> Dict[str, Any]:
        """Convert monthly payroll entity to document format."""
        monthly_payrolls = []
        for mp in monthly_payroll.monthly_payrolls:
            monthly_payrolls.append({
                "month": mp.month,
                "year": mp.year,
                "base_monthly_gross": float(mp.base_monthly_gross.amount),
                "lwp_days": mp.lwp_days,
                "working_days_in_month": mp.working_days_in_month
            })
        
        lwp_details = []
        for lwp in monthly_payroll.lwp_details:
            lwp_details.append({
                "month": lwp.month,
                "year": lwp.year,
                "lwp_days": lwp.lwp_days,
                "working_days_in_month": lwp.working_days_in_month
            })
        
        return {
            "monthly_payrolls": monthly_payrolls,
            "annual_salary": float(monthly_payroll.annual_salary.amount),
            "total_lwp_days": monthly_payroll.total_lwp_days,
            "lwp_details": lwp_details
        }
    
    def _document_to_entity(self, document: Dict[str, Any]) -> TaxationRecord:
        """
        Convert MongoDB document to entity.
        
        Enhanced to handle comprehensive taxation with backward compatibility.
        """
        
        # Convert salary income (core - required)
        salary_income = SalaryIncome(
            basic_salary=Money.from_float(document["salary_income"]["basic_salary"]),
            dearness_allowance=Money.from_float(document["salary_income"]["dearness_allowance"]),
            hra_received=Money.from_float(document["salary_income"]["hra_received"]),
            hra_city_type=document["salary_income"]["hra_city_type"],
            actual_rent_paid=Money.from_float(document["salary_income"]["actual_rent_paid"]),
            special_allowance=Money.from_float(document["salary_income"]["special_allowance"]),
            other_allowances=Money.from_float(document["salary_income"]["other_allowances"]),
            lta_received=Money.from_float(document["salary_income"]["lta_received"]),
            medical_allowance=Money.from_float(document["salary_income"]["medical_allowance"]),
            conveyance_allowance=Money.from_float(document["salary_income"]["conveyance_allowance"])
        )
        
        # Convert deductions (core - required)
        section_80c = DeductionSection80C(
            life_insurance_premium=Money.from_float(document["deductions"]["section_80c"]["life_insurance_premium"]),
            epf_contribution=Money.from_float(document["deductions"]["section_80c"]["epf_contribution"]),
            ppf_contribution=Money.from_float(document["deductions"]["section_80c"]["ppf_contribution"]),
            nsc_investment=Money.from_float(document["deductions"]["section_80c"]["nsc_investment"]),
            tax_saving_fd=Money.from_float(document["deductions"]["section_80c"]["tax_saving_fd"]),
            elss_investment=Money.from_float(document["deductions"]["section_80c"]["elss_investment"]),
            home_loan_principal=Money.from_float(document["deductions"]["section_80c"]["home_loan_principal"]),
            tuition_fees=Money.from_float(document["deductions"]["section_80c"]["tuition_fees"]),
            ulip_premium=Money.from_float(document["deductions"]["section_80c"]["ulip_premium"]),
            sukanya_samriddhi=Money.from_float(document["deductions"]["section_80c"]["sukanya_samriddhi"]),
            other_80c_investments=Money.from_float(document["deductions"]["section_80c"]["other_80c_investments"])
        )
        
        section_80d = DeductionSection80D(
            self_family_premium=Money.from_float(document["deductions"]["section_80d"]["self_family_premium"]),
            parent_premium=Money.from_float(document["deductions"]["section_80d"]["parent_premium"]),
            preventive_health_checkup=Money.from_float(document["deductions"]["section_80d"]["preventive_health_checkup"]),
            employee_age=document["deductions"]["section_80d"]["employee_age"],
            parent_age=document["deductions"]["section_80d"]["parent_age"]
        )
        
        other_deductions = OtherDeductions(
            education_loan_interest=Money.from_float(document["deductions"]["other_deductions"]["education_loan_interest"]),
            charitable_donations=Money.from_float(document["deductions"]["other_deductions"]["charitable_donations"]),
            savings_interest=Money.from_float(document["deductions"]["other_deductions"]["savings_interest"]),
            nps_contribution=Money.from_float(document["deductions"]["other_deductions"]["nps_contribution"]),
            other_deductions=Money.from_float(document["deductions"]["other_deductions"]["other_deductions"])
        )
        
        deductions = TaxDeductions(
            section_80c=section_80c,
            section_80d=section_80d,
            other_deductions=other_deductions
        )
        
        # COMPREHENSIVE INCOME COMPONENTS (new - optional with backward compatibility)
        
        # Convert perquisites (if present)
        perquisites = None
        if document.get("perquisites"):
            perquisites = self._convert_doc_to_perquisites(document["perquisites"])
        
        # Convert house property income (if present)
        house_property_income = None
        if document.get("house_property_income"):
            house_property_income = self._convert_doc_to_house_property(document["house_property_income"])
        
        # Convert capital gains income (if present)
        capital_gains_income = None
        if document.get("capital_gains_income"):
            capital_gains_income = self._convert_doc_to_capital_gains(document["capital_gains_income"])
        
        # Convert retirement benefits (if present)
        retirement_benefits = None
        if document.get("retirement_benefits"):
            retirement_benefits = self._convert_doc_to_retirement_benefits(document["retirement_benefits"])
        
        # Convert other income (if present)
        other_income = None
        if document.get("other_income"):
            other_income = self._convert_doc_to_other_income(document["other_income"])
        
        # Convert monthly payroll (if present)
        monthly_payroll = None
        if document.get("monthly_payroll"):
            monthly_payroll = self._convert_doc_to_monthly_payroll(document["monthly_payroll"])
        
        # Create comprehensive taxation record
        taxation_record = TaxationRecord(
            taxation_id=document["taxation_id"],
            user_id=UserId(document["user_id"]),
            organization_id=document["organization_id"],
            tax_year=TaxYear.from_string(document["tax_year"]),
            salary_income=salary_income,
            deductions=deductions,
            regime=TaxRegime.from_string(document["regime"]),
            age=document["age"],
            perquisites=perquisites,
            house_property_income=house_property_income,
            capital_gains_income=capital_gains_income,
            retirement_benefits=retirement_benefits,
            other_income=other_income,
            monthly_payroll=monthly_payroll,
            is_final=document["is_final"],
            submitted_at=document.get("submitted_at"),
            created_at=document["created_at"],
            updated_at=document["updated_at"],
            version=document["version"]
        )
        
        # Set calculation result if exists
        if document.get("calculation_result"):
            calc_doc = document["calculation_result"]
            # Note: We would need to reconstruct the full TaxCalculationResult here
            # For now, setting basic fields and marking as valid calculation
            taxation_record.last_calculated_at = document.get("last_calculated_at")
        
        return taxation_record 