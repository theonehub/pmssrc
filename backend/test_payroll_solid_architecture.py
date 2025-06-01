#!/usr/bin/env python3
"""
Comprehensive Test for Payroll SOLID Architecture Migration
Tests all core components of the new payroll system architecture
"""

import sys
import os
from datetime import datetime, date
from decimal import Decimal

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_payroll_domain_events():
    """Test payroll domain events creation and validation"""
    print("🔄 Testing Payroll Domain Events...")
    
    try:
        from app.domain.events.payroll_events import (
            PayoutCalculated,
            PayoutStatusChanged,
            PayslipGenerated,
            PayoutStatus
        )
        
        # Test PayoutCalculated event
        payout_calculated = PayoutCalculated(
            employee_id="EMP001",
            month=3,
            year=2024,
            gross_salary=100000.0,
            net_salary=75000.0,
            total_deductions=25000.0,
            basic_salary=50000.0,
            allowances=50000.0,
            tax_deducted=5000.0,
            working_days=30,
            lwp_days=0,
            calculation_method="automated",
            tax_regime="new"
        )
        
        assert payout_calculated.employee_id == "EMP001"
        assert payout_calculated.month == 3
        assert payout_calculated.gross_salary == 100000.0
        print("  ✅ PayoutCalculated event created successfully")
        
        print("✅ All Payroll Domain Events tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Payroll Domain Events test failed: {str(e)}")
        return False


def test_payroll_value_objects():
    """Test payroll value objects creation and business logic"""
    print("🔄 Testing Payroll Value Objects...")
    
    try:
        from app.domain.value_objects.payroll_value_objects import (
            Money, SalaryComponents, DeductionComponents, AttendanceInfo
        )
        
        # Test Money value object
        money1 = Money(Decimal("50000"))
        money2 = Money(Decimal("25000"))
        
        total = money1.add(money2)
        assert total.amount == Decimal("75000")
        print("  ✅ Money value object operations working correctly")
        
        # Test SalaryComponents
        salary_components = SalaryComponents(
            basic=Money(Decimal("50000")),
            dearness_allowance=Money(Decimal("0")),
            hra=Money(Decimal("25000")),
            special_allowance=Money(Decimal("20000")),
            bonus=Money(Decimal("5000"))
        )
        
        total_earnings = salary_components.total_earnings()
        assert total_earnings.amount == Decimal("100000")
        print("  ✅ SalaryComponents calculations working correctly")
        
        print("✅ All Payroll Value Objects tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Payroll Value Objects test failed: {str(e)}")
        return False


def test_payroll_dtos():
    """Test payroll DTOs creation and validation"""
    print("🔄 Testing Payroll DTOs...")
    
    try:
        from app.application.dto.payroll_dto import (
            PayoutCalculationRequestDTO,
            PayoutCreateRequestDTO
        )
        
        # Test PayoutCalculationRequestDTO
        calculation_request = PayoutCalculationRequestDTO(
            employee_id="EMP001",
            month=3,
            year=2024,
            force_recalculate=False
        )
        
        assert calculation_request.employee_id == "EMP001"
        assert calculation_request.month == 3
        print("  ✅ PayoutCalculationRequestDTO created successfully")
        
        print("✅ All Payroll DTOs tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Payroll DTOs test failed: {str(e)}")
        return False


def test_repository_interfaces():
    """Test repository interfaces can be imported"""
    print("🔄 Testing Repository Interfaces...")
    
    try:
        from app.application.interfaces.repositories.payout_repository import (
            PayoutCommandRepository,
            PayoutQueryRepository
        )
        from app.application.interfaces.repositories.payslip_repository import (
            PayslipCommandRepository,
            PayslipQueryRepository
        )
        
        # Check that interfaces have the expected methods
        assert hasattr(PayoutCommandRepository, 'create_payout')
        assert hasattr(PayoutQueryRepository, 'get_by_id')
        assert hasattr(PayslipCommandRepository, 'save_generated_payslip')
        assert hasattr(PayslipQueryRepository, 'get_by_id')
        
        print("  ✅ All repository interfaces imported successfully")
        print("✅ All Repository Interfaces tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Repository Interfaces test failed: {str(e)}")
        return False


def run_all_tests():
    """Run all payroll SOLID architecture tests"""
    print("🚀 Starting Payroll SOLID Architecture Migration Tests\n")
    
    test_results = []
    
    # Domain Layer Tests
    test_results.append(("Domain Events", test_payroll_domain_events()))
    test_results.append(("Value Objects", test_payroll_value_objects()))
    test_results.append(("DTOs", test_payroll_dtos()))
    test_results.append(("Repository Interfaces", test_repository_interfaces()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 PAYROLL SOLID ARCHITECTURE TEST SUMMARY")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-"*60)
    print(f"Total Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(test_results)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Payroll SOLID architecture is ready!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 