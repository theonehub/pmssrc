"""
Company Perquisites Policy Configuration
Wrapper entity for company-controlled perquisites
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from decimal import Decimal

from app.domain.value_objects.money import Money
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.entities.taxation.perquisites import (
    Perquisites, AccommodationPerquisite, CarPerquisite, MedicalReimbursement,
    LTAPerquisite, InterestFreeConcessionalLoan, ESOPPerquisite,
    UtilitiesPerquisite, FreeEducationPerquisite, LunchRefreshmentPerquisite,
    DomesticHelpPerquisite, MovableAssetUsage, MovableAssetTransfer,
    GiftVoucherPerquisite, MonetaryBenefitsPerquisite, ClubExpensesPerquisite,
    AccommodationType, CityPopulation, CarUseType, AssetType
)


@dataclass
class CompanyPerquisitesPolicy:
    """
    Company-defined perquisites policy that admins can configure.
    Uses existing Perquisites computation logic.
    """
    
    # Company identifiers
    organization_id: str
    policy_name: str
    effective_from_date: str
    
    # Company accommodation policy
    accommodation_policy_enabled: bool = False
    default_accommodation_type: Optional[AccommodationType] = None
    default_city_population: Optional[CityPopulation] = None
    
    # Company car policy
    car_policy_enabled: bool = False
    default_car_use_type: Optional[CarUseType] = None
    default_engine_capacity: int = 1600
    
    # Company medical policy
    medical_reimbursement_enabled: bool = False
    medical_reimbursement_limit: Money = Money.zero()
    
    # Company LTA policy
    lta_policy_enabled: bool = False
    lta_annual_limit: Money = Money.zero()
    
    # Company loan policy
    loan_policy_enabled: bool = False
    max_loan_amount: Money = Money.zero()
    company_loan_rate: Decimal = Decimal('0')
    
    # Company ESOP policy
    esop_policy_enabled: bool = False
    
    # Company utilities policy
    utilities_policy_enabled: bool = False
    
    # Company education policy
    education_policy_enabled: bool = False
    education_allowance_per_child: Money = Money.zero()
    
    # Company meal policy
    meal_policy_enabled: bool = False
    meal_subsidy_per_day: Money = Money.zero()
    
    # Company domestic help policy
    domestic_help_policy_enabled: bool = False
    
    # Company club membership policy
    club_membership_enabled: bool = False
    
    # Company gift voucher policy
    gift_voucher_enabled: bool = False
    annual_gift_voucher_limit: Money = Money.zero()
    
    # Metadata
    created_by: str = ""
    updated_by: str = ""
    is_active: bool = True
    
    def create_employee_perquisites(
        self,
        employee_id: EmployeeId,
        **perquisite_data
    ) -> Perquisites:
        """
        Create Perquisites entity using existing computation logic.
        Company policy provides defaults and limits.
        """
        
        # Initialize perquisites based on company policy
        perquisites = Perquisites()
        
        # Accommodation (if enabled by company policy)
        if self.accommodation_policy_enabled and 'accommodation' in perquisite_data:
            accommodation_data = perquisite_data['accommodation']
            perquisites.accommodation = AccommodationPerquisite(
                accommodation_type=accommodation_data.get('type', self.default_accommodation_type),
                city_population=accommodation_data.get('city_population', self.default_city_population),
                **{k: v for k, v in accommodation_data.items() if k not in ['type', 'city_population']}
            )
        
        # Car (if enabled by company policy)
        if self.car_policy_enabled and 'car' in perquisite_data:
            car_data = perquisite_data['car']
            perquisites.car = CarPerquisite(
                car_use_type=car_data.get('use_type', self.default_car_use_type),
                engine_capacity_cc=car_data.get('engine_capacity', self.default_engine_capacity),
                **{k: v for k, v in car_data.items() if k not in ['use_type', 'engine_capacity']}
            )
        
        # Medical reimbursement (if enabled)
        if self.medical_reimbursement_enabled and 'medical' in perquisite_data:
            medical_data = perquisite_data['medical']
            # Apply company limit
            medical_amount = Money.from_float(medical_data.get('amount', 0))
            if medical_amount.is_greater_than(self.medical_reimbursement_limit):
                medical_amount = self.medical_reimbursement_limit
            
            perquisites.medical_reimbursement = MedicalReimbursement(
                medical_reimbursement_amount=medical_amount,
                **{k: v for k, v in medical_data.items() if k != 'amount'}
            )
        
        # LTA (if enabled)
        if self.lta_policy_enabled and 'lta' in perquisite_data:
            lta_data = perquisite_data['lta']
            lta_amount = Money.from_float(lta_data.get('amount', 0))
            if lta_amount.is_greater_than(self.lta_annual_limit):
                lta_amount = self.lta_annual_limit
                
            perquisites.lta = LTAPerquisite(
                lta_amount_claimed=lta_amount,
                **{k: v for k, v in lta_data.items() if k != 'amount'}
            )
        
        # Interest-free loan (if enabled)
        if self.loan_policy_enabled and 'loan' in perquisite_data:
            loan_data = perquisite_data['loan']
            loan_amount = Money.from_float(loan_data.get('amount', 0))
            if loan_amount.is_greater_than(self.max_loan_amount):
                loan_amount = self.max_loan_amount
                
            perquisites.interest_free_loan = InterestFreeConcessionalLoan(
                loan_amount=loan_amount,
                company_interest_rate=self.company_loan_rate,
                **{k: v for k, v in loan_data.items() if k != 'amount'}
            )
        
        # ESOP (if enabled)
        if self.esop_policy_enabled and 'esop' in perquisite_data:
            esop_data = perquisite_data['esop']
            perquisites.esop = ESOPPerquisite(**esop_data)
        
        # Utilities (if enabled)
        if self.utilities_policy_enabled and 'utilities' in perquisite_data:
            utilities_data = perquisite_data['utilities']
            perquisites.utilities = UtilitiesPerquisite(**utilities_data)
        
        # Free education (if enabled)
        if self.education_policy_enabled and 'education' in perquisite_data:
            education_data = perquisite_data['education']
            perquisites.free_education = FreeEducationPerquisite(**education_data)
        
        # Lunch/refreshment (if enabled)
        if self.meal_policy_enabled and 'meals' in perquisite_data:
            meal_data = perquisite_data['meals']
            perquisites.lunch_refreshment = LunchRefreshmentPerquisite(
                employer_cost=self.meal_subsidy_per_day.multiply(meal_data.get('days', 250)),
                **{k: v for k, v in meal_data.items() if k != 'days'}
            )
        
        # Domestic help (if enabled)
        if self.domestic_help_policy_enabled and 'domestic_help' in perquisite_data:
            help_data = perquisite_data['domestic_help']
            perquisites.domestic_help = DomesticHelpPerquisite(**help_data)
        
        # Gift voucher (if enabled)
        if self.gift_voucher_enabled and 'gift_voucher' in perquisite_data:
            voucher_data = perquisite_data['gift_voucher']
            voucher_amount = Money.from_float(voucher_data.get('amount', 0))
            if voucher_amount.is_greater_than(self.annual_gift_voucher_limit):
                voucher_amount = self.annual_gift_voucher_limit
                
            perquisites.gift_voucher = GiftVoucherPerquisite(
                gift_voucher_amount=voucher_amount
            )
        
        # Club expenses (if enabled)
        if self.club_membership_enabled and 'club' in perquisite_data:
            club_data = perquisite_data['club']
            perquisites.club_expenses = ClubExpensesPerquisite(**club_data)
        
        # Movable assets (if provided)
        if 'movable_asset_usage' in perquisite_data:
            asset_data = perquisite_data['movable_asset_usage']
            perquisites.movable_asset_usage = MovableAssetUsage(**asset_data)
        
        if 'movable_asset_transfer' in perquisite_data:
            transfer_data = perquisite_data['movable_asset_transfer']
            perquisites.movable_asset_transfer = MovableAssetTransfer(**transfer_data)
        
        # Monetary benefits (if provided)
        if 'monetary_benefits' in perquisite_data:
            monetary_data = perquisite_data['monetary_benefits']
            perquisites.monetary_benefits = MonetaryBenefitsPerquisite(**monetary_data)
        
        return perquisites
    
    def get_policy_configuration(self) -> Dict[str, Any]:
        """Get company perquisites policy configuration for admin."""
        return {
            "policy_metadata": {
                "organization_id": self.organization_id,
                "policy_name": self.policy_name,
                "effective_from": self.effective_from_date,
                "is_active": self.is_active,
                "created_by": self.created_by,
                "updated_by": self.updated_by
            },
            "accommodation_policy": {
                "enabled": self.accommodation_policy_enabled,
                "default_type": self.default_accommodation_type.value if self.default_accommodation_type else None,
                "default_city_population": self.default_city_population.value if self.default_city_population else None
            },
            "car_policy": {
                "enabled": self.car_policy_enabled,
                "default_use_type": self.default_car_use_type.value if self.default_car_use_type else None,
                "default_engine_capacity": self.default_engine_capacity
            },
            "medical_policy": {
                "enabled": self.medical_reimbursement_enabled,
                "annual_limit": self.medical_reimbursement_limit.to_float()
            },
            "lta_policy": {
                "enabled": self.lta_policy_enabled,
                "annual_limit": self.lta_annual_limit.to_float()
            },
            "loan_policy": {
                "enabled": self.loan_policy_enabled,
                "max_amount": self.max_loan_amount.to_float(),
                "company_rate": float(self.company_loan_rate)
            },
            "esop_policy": {
                "enabled": self.esop_policy_enabled
            },
            "utilities_policy": {
                "enabled": self.utilities_policy_enabled
            },
            "education_policy": {
                "enabled": self.education_policy_enabled,
                "allowance_per_child": self.education_allowance_per_child.to_float()
            },
            "meal_policy": {
                "enabled": self.meal_policy_enabled,
                "subsidy_per_day": self.meal_subsidy_per_day.to_float()
            },
            "domestic_help_policy": {
                "enabled": self.domestic_help_policy_enabled
            },
            "club_membership_policy": {
                "enabled": self.club_membership_enabled
            },
            "gift_voucher_policy": {
                "enabled": self.gift_voucher_enabled,
                "annual_limit": self.annual_gift_voucher_limit.to_float()
            }
        }
    
    def update_policy_limits(self, policy_updates: Dict[str, Any]) -> List[str]:
        """Update policy limits and return validation messages."""
        messages = []
        
        if 'medical_limit' in policy_updates:
            self.medical_reimbursement_limit = Money.from_float(policy_updates['medical_limit'])
            messages.append("Medical reimbursement limit updated")
        
        if 'lta_limit' in policy_updates:
            self.lta_annual_limit = Money.from_float(policy_updates['lta_limit'])
            messages.append("LTA annual limit updated")
        
        if 'loan_limit' in policy_updates:
            self.max_loan_amount = Money.from_float(policy_updates['loan_limit'])
            messages.append("Maximum loan amount updated")
        
        if 'gift_voucher_limit' in policy_updates:
            self.annual_gift_voucher_limit = Money.from_float(policy_updates['gift_voucher_limit'])
            messages.append("Gift voucher annual limit updated")
        
        return messages
    
    def validate_policy(self) -> List[str]:
        """Validate company perquisites policy."""
        warnings = []
        
        if not self.organization_id:
            warnings.append("Organization ID required")
        
        if not self.policy_name:
            warnings.append("Policy name required")
        
        if self.accommodation_policy_enabled and not self.default_accommodation_type:
            warnings.append("Default accommodation type required when accommodation policy is enabled")
        
        if self.car_policy_enabled and not self.default_car_use_type:
            warnings.append("Default car use type required when car policy is enabled")
        
        return warnings


@dataclass
class EmployeePerquisiteAssignment:
    """
    Individual employee perquisite assignment based on company policy.
    Links company policy to specific employee perquisites.
    """
    
    employee_id: EmployeeId
    organization_id: str
    perquisites_policy_id: str
    
    # Employee-specific perquisite data
    perquisite_assignments: Dict[str, Any] = field(default_factory=dict)
    
    # Assignment metadata
    effective_from: str = ""
    assigned_by: str = ""
    is_active: bool = True
    
    def get_assignment_summary(self) -> Dict[str, Any]:
        """Get employee perquisite assignment summary."""
        return {
            "employee_id": str(self.employee_id),
            "organization_id": self.organization_id,
            "perquisites_policy_id": self.perquisites_policy_id,
            "assignments": self.perquisite_assignments,
            "assignment_metadata": {
                "effective_from": self.effective_from,
                "assigned_by": self.assigned_by,
                "is_active": self.is_active
            }
        } 