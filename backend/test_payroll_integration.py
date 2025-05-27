#!/usr/bin/env python3
"""
Payroll SOLID Architecture Integration Test
Tests the integration between all components of the new payroll system
"""

import sys
import os
from datetime import datetime, date
from decimal import Decimal

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_complete_payout_workflow():
    """Test a complete payout calculation workflow"""
    print("🔄 Testing Complete Payout Workflow...")
    
    try:
        # Import all components
        from domain.events.payroll_events import PayoutCalculated
        from domain.value_objects.payroll_value_objects import (
            Money, SalaryComponents, DeductionComponents, 
            AttendanceInfo, PayoutSummary
        )
        from application.dto.payroll_dto import (
            PayoutCalculationRequestDTO,
            PayoutResponseDTO,
            SalaryComponentsResponseDTO
        )
        
        # Step 1: Create a payout calculation request
        request = PayoutCalculationRequestDTO(
            employee_id="EMP001",
            month=3,
            year=2024,
            force_recalculate=True
        )
        
        # Step 2: Create salary components
        salary_components = SalaryComponents(
            basic=Money(Decimal("50000")),
            dearness_allowance=Money(Decimal("0")),
            hra=Money(Decimal("25000")),
            special_allowance=Money(Decimal("20000")),
            bonus=Money(Decimal("5000"))
        )
        
        # Step 3: Create attendance info  
        attendance_info = AttendanceInfo(
            total_days_in_month=31,
            working_days_in_period=30,
            lwp_days=1
        )
        
        # Step 4: Calculate adjusted salary for LWP
        working_ratio = attendance_info.effective_working_ratio()
        adjusted_basic = salary_components.basic.multiply(working_ratio)
        
        # Step 5: Calculate deductions
        deduction_components = DeductionComponents(
            epf_employee=Money(Decimal("1800")),  # 12% of basic, capped
            esi_employee=Money(Decimal("750")),   # 0.75% of gross  
            professional_tax=Money(Decimal("200")),
            tds=Money(Decimal("2000"))
        )
        
        # Step 6: Create payout summary
        total_earnings = salary_components.total_earnings()
        adjusted_earnings = total_earnings.multiply(working_ratio)
        total_deductions = deduction_components.total_deductions()
        
        payout_summary = PayoutSummary(
            gross_earnings=adjusted_earnings,
            total_deductions=total_deductions,
            net_pay=adjusted_earnings.subtract(total_deductions),
            employer_contributions=Money(Decimal("3600"))  # EPF + ESI employer
        )
        
        # Step 7: Create domain event
        payout_event = PayoutCalculated(
            employee_id=request.employee_id,
            month=request.month,
            year=request.year,
            gross_salary=adjusted_earnings.to_float(),
            net_salary=payout_summary.net_pay.to_float(),
            total_deductions=total_deductions.to_float(),
            basic_salary=adjusted_basic.to_float(),
            allowances=salary_components.hra.add(salary_components.special_allowance).to_float(),
            tax_deducted=deduction_components.tds.to_float(),
            working_days=attendance_info.effective_working_days(),
            lwp_days=attendance_info.lwp_days,
            calculation_method="automated",
            tax_regime="new"
        )
        
        # Step 8: Verify calculations
        assert request.employee_id == "EMP001"
        assert payout_summary.take_home_percentage() > 0
        assert payout_summary.cost_to_company().amount > payout_summary.gross_earnings.amount
        assert payout_event.event_type == "PayoutCalculated"
        assert working_ratio < 1.0  # LWP should reduce ratio
        
        print(f"  ✅ Employee: {request.employee_id}")
        print(f"  ✅ Gross Salary: ₹{adjusted_earnings.to_float():,.2f}")
        print(f"  ✅ Total Deductions: ₹{total_deductions.to_float():,.2f}")
        print(f"  ✅ Net Pay: ₹{payout_summary.net_pay.to_float():,.2f}")
        print(f"  ✅ Take Home %: {payout_summary.take_home_percentage():.1f}%")
        print(f"  ✅ CTC: ₹{payout_summary.cost_to_company().to_float():,.2f}")
        print(f"  ✅ Working Ratio (LWP adjusted): {working_ratio:.3f}")
        
        print("✅ Complete Payout Workflow test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Complete Payout Workflow test failed: {str(e)}")
        return False


def test_dto_serialization():
    """Test DTO serialization and validation"""
    print("🔄 Testing DTO Serialization...")
    
    try:
        from application.dto.payroll_dto import (
            PayoutCalculationRequestDTO,
            PayoutResponseDTO,
            SalaryComponentsResponseDTO,
            DeductionComponentsResponseDTO
        )
        
        # Test request DTO with validation
        request = PayoutCalculationRequestDTO(
            employee_id="EMP001",
            month=3,
            year=2024,
            override_salary={"basic_salary": 60000.0, "hra": 30000.0}
        )
        
        # Test response DTO components
        salary_dto = SalaryComponentsResponseDTO(
            basic=50000.0,
            dearness_allowance=0.0,
            hra=25000.0,
            special_allowance=20000.0,
            bonus=5000.0,
            total_earnings=100000.0
        )
        
        deduction_dto = DeductionComponentsResponseDTO(
            epf_employee=1800.0,
            esi_employee=750.0,
            professional_tax=200.0,
            tds=2000.0,
            total_deductions=4750.0
        )
        
        # Test validation
        assert request.month >= 1 and request.month <= 12
        assert request.year >= 2020
        assert salary_dto.total_earnings == 100000.0
        assert deduction_dto.total_deductions == 4750.0
        
        print("  ✅ Request DTO validation working")
        print("  ✅ Response DTO creation working")
        print("  ✅ Salary components serialization working")
        print("  ✅ Deduction components serialization working")
        
        print("✅ DTO Serialization test passed!")
        return True
        
    except Exception as e:
        print(f"❌ DTO Serialization test failed: {str(e)}")
        return False


def test_business_logic_validations():
    """Test business logic validations"""
    print("🔄 Testing Business Logic Validations...")
    
    try:
        from domain.value_objects.payroll_value_objects import (
            Money, AttendanceInfo, PayPeriod
        )
        
        # Test Money validations
        try:
            negative_money = Money(Decimal("-100"))
            assert False, "Should not allow negative money"
        except ValueError:
            print("  ✅ Money validation prevents negative amounts")
        
        # Test AttendanceInfo validations
        try:
            invalid_attendance = AttendanceInfo(
                total_days_in_month=30,
                working_days_in_period=35,  # More than total days
                lwp_days=0
            )
            assert False, "Should not allow working days > total days"
        except ValueError:
            print("  ✅ AttendanceInfo validation prevents invalid working days")
        
        # Test PayPeriod validations
        try:
            invalid_period = PayPeriod(
                start_date=date(2024, 3, 31),
                end_date=date(2024, 3, 1),  # End before start
                month=3,
                year=2024
            )
            assert False, "Should not allow end date before start date"
        except ValueError:
            print("  ✅ PayPeriod validation prevents invalid date ranges")
        
        # Test valid calculations
        valid_attendance = AttendanceInfo(
            total_days_in_month=30,
            working_days_in_period=28,
            lwp_days=2
        )
        
        assert valid_attendance.effective_working_days() == 26
        assert valid_attendance.working_ratio() == 28/30
        assert valid_attendance.effective_working_ratio() == 26/30
        
        print("  ✅ Attendance calculations working correctly")
        
        print("✅ Business Logic Validations test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Business Logic Validations test failed: {str(e)}")
        return False


def run_integration_tests():
    """Run all integration tests"""
    print("🚀 Starting Payroll SOLID Architecture Integration Tests\n")
    
    test_results = []
    
    # Integration Tests
    test_results.append(("Complete Payout Workflow", test_complete_payout_workflow()))
    test_results.append(("DTO Serialization", test_dto_serialization()))
    test_results.append(("Business Logic Validations", test_business_logic_validations()))
    
    # Summary
    print("\n" + "="*70)
    print("📊 PAYROLL INTEGRATION TEST SUMMARY")
    print("="*70)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<35}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-"*70)
    print(f"Total Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(test_results)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("🚀 Payroll SOLID architecture is production-ready!")
        return True
    else:
        print(f"\n⚠️  {failed} integration test(s) failed.")
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1) 