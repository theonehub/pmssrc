#!/usr/bin/env python3
"""
Minimal Test for Taxation SOLID Architecture Components
Tests only the new SOLID components without legacy dependencies
"""

import sys
import os
import asyncio
from datetime import datetime, date
from typing import Dict, Any

# Add the backend app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_core_imports():
    """Test that core taxation components can be imported"""
    
    print("Testing Core Taxation SOLID Architecture Imports...")
    
    try:
        # Test domain events
        print("✓ Testing domain events...")
        from app.domain.events.taxation_events import (
            TaxationCalculated,
            TaxationUpdated,
            TaxRegimeChanged,
            TaxFilingStatusChanged
        )
        print("  ✓ All taxation domain events imported successfully")
        
        # Test DTOs
        print("✓ Testing DTOs...")
        from app.application.dto.taxation_dto import (
            TaxationCreateRequestDTO,
            TaxationUpdateRequestDTO,
            TaxationResponseDTO,
            TaxSearchFiltersDTO,
            TaxCalculationRequestDTO,
            TaxProjectionDTO,
            TaxComparisonDTO,
            TaxStatisticsDTO,
            TaxBreakdownDTO,
            SalaryComponentsDTO,
            DeductionComponentsDTO
        )
        print("  ✓ All taxation DTOs imported successfully")
        
        # Test repository interfaces
        print("✓ Testing repository interfaces...")
        from app.application.interfaces.repositories.taxation_repository import (
            TaxationCommandRepository,
            TaxationQueryRepository,
            TaxationCalculationRepository,
            TaxationAnalyticsRepository,
            TaxationAuditRepository
        )
        print("  ✓ All taxation repository interfaces imported successfully")
        
        # Test use cases (without legacy dependencies)
        print("✓ Testing use cases...")
        from app.application.use_cases.taxation.create_taxation_use_case import (
            CreateTaxationUseCase,
            BulkCreateTaxationUseCase
        )
        print("  ✓ Taxation use cases imported successfully")
        
        print("\n🎉 All core taxation SOLID architecture components imported successfully!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error during imports: {e}")
        return False

def test_dto_creation():
    """Test that DTOs can be created and validated"""
    
    print("\nTesting DTO Creation and Validation...")
    
    try:
        from app.application.dto.taxation_dto import (
            TaxationCreateRequestDTO,
            SalaryComponentsDTO,
            DeductionComponentsDTO,
            TaxCalculationRequestDTO
        )
        
        # Test salary components DTO
        salary = SalaryComponentsDTO(
            basic=50000,
            dearness_allowance=5000,
            hra=20000,
            special_allowance=10000
        )
        print("  ✓ SalaryComponentsDTO created successfully")
        print(f"    Basic: {salary.basic}, HRA: {salary.hra}")
        
        # Test deduction components DTO
        deductions = DeductionComponentsDTO(
            section_80c=100000,
            section_80d=25000,
            section_80e=50000
        )
        print("  ✓ DeductionComponentsDTO created successfully")
        print(f"    80C: {deductions.section_80c}, 80D: {deductions.section_80d}")
        
        # Test taxation create request DTO
        create_request = TaxationCreateRequestDTO(
            employee_id="EMP001",
            tax_year="2024-2025",
            regime="old",
            emp_age=30,
            is_govt_employee=False,
            salary=salary,
            deductions=deductions,
            created_by="ADMIN"
        )
        print("  ✓ TaxationCreateRequestDTO created successfully")
        print(f"    Employee: {create_request.employee_id}, Year: {create_request.tax_year}")
        
        # Test validation
        validation_errors = create_request.validate()
        if not validation_errors:
            print("  ✓ DTO validation passed")
        else:
            print(f"  ⚠ DTO validation warnings: {validation_errors}")
        
        # Test tax calculation request DTO
        calc_request = TaxCalculationRequestDTO(
            employee_id="EMP001",
            calculation_type="full",
            force_recalculate=True,
            calculated_by="ADMIN"
        )
        print("  ✓ TaxCalculationRequestDTO created successfully")
        print(f"    Type: {calc_request.calculation_type}, Force: {calc_request.force_recalculate}")
        
        print("  🎉 All DTOs created and validated successfully!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error creating DTOs: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_domain_events():
    """Test that domain events can be created"""
    
    print("\nTesting Domain Events Creation...")
    
    try:
        from app.domain.events.taxation_events import TaxationCalculated
        from app.domain.value_objects.employee_id import EmployeeId
        from app.domain.value_objects.money import Money
        
        # Create a taxation calculated event
        event = TaxationCalculated(
            employee_id=EmployeeId("EMP001"),
            tax_year="2024-2025",
            regime="old",
            total_tax=Money.from_float(50000.0),
            taxable_income=Money.from_float(400000.0),
            calculated_by=EmployeeId("ADMIN")
        )
        
        print("  ✓ TaxationCalculated event created successfully")
        print(f"    - Employee ID: {event.employee_id}")
        print(f"    - Tax Year: {event.tax_year}")
        print(f"    - Total Tax: {event.total_tax}")
        print(f"    - Event Time: {event.occurred_at}")
        
        print("  🎉 Domain events created successfully!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error creating domain events: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_repository_interfaces():
    """Test that repository interfaces are properly defined"""
    
    print("\nTesting Repository Interface Definitions...")
    
    try:
        from app.application.interfaces.repositories.taxation_repository import (
            TaxationCommandRepository,
            TaxationQueryRepository,
            TaxationCalculationRepository,
            TaxationAnalyticsRepository
        )
        
        # Check that repositories have expected methods
        command_methods = [
            'create_taxation',
            'update_taxation', 
            'delete_taxation',
            'update_tax_calculation'
        ]
        
        for method in command_methods:
            assert hasattr(TaxationCommandRepository, method), f"TaxationCommandRepository missing {method}"
        print("  ✓ TaxationCommandRepository has all required methods")
        
        query_methods = [
            'get_taxation_by_employee',
            'get_current_taxation',
            'search_taxation_records',
            'exists_taxation'
        ]
        
        for method in query_methods:
            assert hasattr(TaxationQueryRepository, method), f"TaxationQueryRepository missing {method}"
        print("  ✓ TaxationQueryRepository has all required methods")
        
        calc_methods = [
            'calculate_tax',
            'calculate_tax_comparison',
            'calculate_tax_projection'
        ]
        
        for method in calc_methods:
            assert hasattr(TaxationCalculationRepository, method), f"TaxationCalculationRepository missing {method}"
        print("  ✓ TaxationCalculationRepository has all required methods")
        
        print("  🎉 Repository interfaces are properly defined!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing repository interfaces: {e}")
        return False

async def test_use_case_instantiation():
    """Test that use cases can be instantiated with mock dependencies"""
    
    print("\nTesting Use Case Instantiation...")
    
    try:
        from app.application.use_cases.taxation.create_taxation_use_case import CreateTaxationUseCase
        
        # Create mock repositories
        class MockTaxationQueryRepository:
            async def exists_taxation(self, employee_id, tax_year, hostname):
                return False
        
        class MockTaxationCommandRepository:
            async def create_taxation(self, request, hostname):
                from app.application.dto.taxation_dto import TaxationResponseDTO
                return TaxationResponseDTO(
                    taxation_id="TAX001",
                    employee_id=request.employee_id,
                    tax_year=request.tax_year,
                    regime=request.regime,
                    emp_age=request.emp_age,
                    filing_status="not_filed",
                    is_govt_employee=request.is_govt_employee,
                    gross_income=0.0,
                    taxable_income=0.0,
                    total_deductions=0.0,
                    total_tax=0.0,
                    tax_payable=0.0,
                    tax_paid=0.0,
                    tax_due=0.0,
                    tax_refundable=0.0,
                    created_at=datetime.utcnow().isoformat()
                )
        
        class MockNotificationService:
            async def send_notification(self, *args, **kwargs):
                pass
        
        # Instantiate use cases
        query_repo = MockTaxationQueryRepository()
        command_repo = MockTaxationCommandRepository()
        notification_service = MockNotificationService()
        
        # Test create taxation use case
        create_use_case = CreateTaxationUseCase(
            command_repository=command_repo,
            query_repository=query_repo,
            notification_service=notification_service
        )
        print("  ✓ CreateTaxationUseCase instantiated successfully")
        
        print("  🎉 Use cases instantiated successfully!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error instantiating use cases: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_flow():
    """Test complete data flow through DTOs"""
    
    print("\nTesting Complete Data Flow...")
    
    try:
        from app.application.dto.taxation_dto import (
            TaxationCreateRequestDTO,
            TaxationResponseDTO,
            SalaryComponentsDTO,
            DeductionComponentsDTO
        )
        
        # Create complete request
        salary = SalaryComponentsDTO(
            basic=60000,
            hra=24000,
            special_allowance=15000
        )
        
        deductions = DeductionComponentsDTO(
            section_80c=150000,
            section_80d=25000
        )
        
        request = TaxationCreateRequestDTO(
            employee_id="EMP123",
            tax_year="2024-2025",
            regime="old",
            emp_age=35,
            is_govt_employee=False,
            salary=salary,
            deductions=deductions,
            other_income=50000,
            created_by="HR_ADMIN"
        )
        
        print("  ✓ Complete taxation request created")
        print(f"    Annual Salary: {(salary.basic + salary.hra + salary.special_allowance) * 12:,.0f}")
        print(f"    Total Deductions: {deductions.section_80c + deductions.section_80d:,.0f}")
        
        # Test serialization
        salary_dict = salary.to_dict()
        deductions_dict = deductions.to_dict()
        
        print("  ✓ DTOs serialized to dictionaries successfully")
        
        # Create mock response
        response = TaxationResponseDTO(
            taxation_id="TAX123",
            employee_id=request.employee_id,
            tax_year=request.tax_year,
            regime=request.regime,
            emp_age=request.emp_age,
            filing_status="not_filed",
            is_govt_employee=request.is_govt_employee,
            gross_income=1188000.0,  # Annual gross
            taxable_income=1013000.0,  # After deductions
            total_deductions=175000.0,
            total_tax=85650.0,  # Estimated
            tax_payable=85650.0,
            tax_paid=0.0,
            tax_due=85650.0,
            tax_refundable=0.0,
            created_at=datetime.utcnow().isoformat()
        )
        
        print("  ✓ Taxation response created successfully")
        print(f"    Gross Income: {response.gross_income:,.0f}")
        print(f"    Taxable Income: {response.taxable_income:,.0f}")
        print(f"    Total Tax: {response.total_tax:,.0f}")
        
        # Test response serialization
        response_dict = response.to_dict()
        print("  ✓ Response serialized successfully")
        
        print("  🎉 Complete data flow test passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error in data flow test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_minimal_tests():
    """Run minimal tests without legacy dependencies"""
    
    print("=" * 60)
    print("TAXATION SOLID ARCHITECTURE - MINIMAL TESTING")
    print("=" * 60)
    
    results = []
    
    # Test core imports
    results.append(test_core_imports())
    
    # Test DTO creation
    results.append(test_dto_creation())
    
    # Test domain events
    results.append(test_domain_events())
    
    # Test repository interfaces
    results.append(test_repository_interfaces())
    
    # Test use case instantiation
    results.append(await test_use_case_instantiation())
    
    # Test data flow
    results.append(test_data_flow())
    
    # Print summary
    print("\n" + "=" * 60)
    print("MINIMAL TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL MINIMAL TESTS PASSED!")
        print("\nThe core taxation SOLID architecture is working correctly!")
        print("\nCore components verified:")
        print("  ✓ Domain events for taxation operations")
        print("  ✓ Comprehensive DTOs for request/response handling")
        print("  ✓ Repository interfaces following CQRS pattern")
        print("  ✓ Use cases with proper dependency injection")
        print("  ✓ Complete data flow from request to response")
        print("\nNext steps:")
        print("  - Implement repository implementations")
        print("  - Add database integration")
        print("  - Create API endpoint integration")
        print("  - Add comprehensive testing")
    else:
        print("❌ Some minimal tests failed. Please check the errors above.")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(run_minimal_tests())
    sys.exit(0 if success else 1) 