#!/usr/bin/env python3
"""
Test script to verify MonthlySalary entity works with perquisites_payouts field.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.domain.entities.monthly_salary import MonthlySalary
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.tax_year import TaxYear
from app.domain.value_objects.tax_regime import TaxRegime
from app.domain.value_objects.money import Money
from app.domain.entities.taxation.salary_income import SalaryIncome
from app.domain.entities.taxation.perquisites import MonthlyPerquisitesPayouts, MonthlyPerquisitesComponents
from app.domain.entities.taxation.deductions import TaxDeductions
from app.domain.entities.taxation.retirement_benefits import RetirementBenefits
from app.domain.entities.taxation.lwp_details import LWPDetails
from app.infrastructure.repositories.mongodb_monthly_salary_repository import MongoDBMonthlySalaryRepository

def test_monthly_salary_creation():
    """Test that MonthlySalary can be created with perquisites_payouts."""
    print("Testing MonthlySalary entity creation...")
    
    # Create test components
    employee_id = EmployeeId("EMP001")
    tax_year = TaxYear.from_string("2024-25")
    tax_regime = TaxRegime("new")
    
    # Create salary income
    salary_income = SalaryIncome(
        basic_salary=Money.from_float(50000.0),
        dearness_allowance=Money.from_float(5000.0),
        hra_provided=Money.from_float(20000.0),
        special_allowance=Money.from_float(10000.0),
        bonus=Money.from_float(0.0),
        commission=Money.from_float(0.0),
        arrears=Money.from_float(0.0),
        effective_from=datetime(2024, 7, 1),
        effective_till=datetime(2024, 7, 1)
    )
    
    # Create perquisites payouts
    components = [
        MonthlyPerquisitesComponents("accommodation", "Accommodation", Money.from_float(5000.0)),
        MonthlyPerquisitesComponents("car", "Car", Money.from_float(3000.0))
    ]
    perquisites_payouts = MonthlyPerquisitesPayouts(
        components=components,
        total=Money.from_float(8000.0)
    )
    
    # Create other components
    deductions = TaxDeductions()
    retirement = RetirementBenefits()
    lwp = LWPDetails(lwp_days=0, total_working_days=26, month=7, year=2024)
    
    # Create MonthlySalary entity
    monthly_salary = MonthlySalary(
        employee_id=employee_id,
        month=7,
        year=2024,
        salary=salary_income,
        perquisites_payouts=perquisites_payouts,
        deductions=deductions,
        retirement=retirement,
        lwp=lwp,
        tax_year=tax_year,
        tax_regime=tax_regime,
        tax_amount=Money.from_float(5000.0),
        net_salary=Money.from_float(75000.0)
    )
    
    print(f"✓ MonthlySalary created successfully")
    print(f"  - Employee ID: {monthly_salary.employee_id}")
    print(f"  - Month/Year: {monthly_salary.month}/{monthly_salary.year}")
    print(f"  - Perquisites Payouts: {len(monthly_salary.perquisites_payouts.components)} components")
    print(f"  - Total Perquisites: ₹{monthly_salary.perquisites_payouts.total.to_float():,.2f}")
    
    return monthly_salary

def test_serialization_deserialization(monthly_salary):
    """Test that MonthlySalary can be serialized and deserialized correctly."""
    print("\nTesting serialization/deserialization...")
    
    # Create repository instance (without database connection for testing)
    from app.infrastructure.database.database_connector import DatabaseConnector
    db_connector = DatabaseConnector()
    repository = MongoDBMonthlySalaryRepository(db_connector)
    
    # Test serialization
    try:
        document = repository._entity_to_document(monthly_salary, "test_org")
        print("✓ Entity to document serialization successful")
        print(f"  - Document keys: {list(document.keys())}")
        print(f"  - Has perquisites_payouts: {'perquisites_payouts' in document}")
        
        # Test deserialization
        recreated_entity = repository._document_to_entity(document)
        print("✓ Document to entity deserialization successful")
        print(f"  - Recreated employee ID: {recreated_entity.employee_id}")
        print(f"  - Recreated perquisites components: {len(recreated_entity.perquisites_payouts.components)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Serialization/deserialization failed: {e}")
        return False

async def main():
    """Main test function."""
    print("=" * 60)
    print("Testing MonthlySalary perquisites_payouts fix")
    print("=" * 60)
    
    # Test entity creation
    monthly_salary = test_monthly_salary_creation()
    
    # Test serialization/deserialization
    success = test_serialization_deserialization(monthly_salary)
    
    print("\n" + "=" * 60)
    if success:
        print("✓ All tests passed! The perquisites_payouts fix is working correctly.")
    else:
        print("✗ Some tests failed. Please check the implementation.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 