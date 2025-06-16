#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from decimal import Decimal
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_salary_income_creation():
    """Test SalaryIncome entity creation step by step."""
    
    logger.info("🔍 Testing SalaryIncome entity creation...")
    
    try:
        # Import required modules
        logger.info("📦 Importing Money...")
        from app.domain.value_objects.money import Money
        logger.info("✅ Money imported successfully")
        
        logger.info("📦 Importing SalaryIncome...")
        from app.domain.entities.taxation.salary_income import SalaryIncome
        logger.info("✅ SalaryIncome imported successfully")
        
        logger.info("📦 Importing SalaryIncomeDTO...")
        from app.application.dto.taxation_dto import SalaryIncomeDTO
        logger.info("✅ SalaryIncomeDTO imported successfully")
        
        # Create test data
        logger.info("🔍 Creating test SalaryIncomeDTO...")
        salary_dto = SalaryIncomeDTO(
            basic_salary=Decimal('1500000'),
            hra_received=Decimal('900000'),
            hra_city_type='metro',
            dearness_allowance=Decimal('300000'),
            actual_rent_paid=Decimal('600000'),
            special_allowance=Decimal('1000'),
            bonus=Decimal('2000'),
            commission=Decimal('1000'),
            medical_allowance=Decimal('4000'),
            conveyance_allowance=Decimal('3200'),
            other_allowances=Decimal('100')
        )
        logger.info("✅ SalaryIncomeDTO created successfully")
        logger.info(f"   - basic_salary: {salary_dto.basic_salary}")
        logger.info(f"   - hra_received: {salary_dto.hra_received}")
        logger.info(f"   - hra_city_type: {salary_dto.hra_city_type}")
        
        # Test direct SalaryIncome creation
        logger.info("🔍 Creating SalaryIncome entity directly...")
        try:
            salary_entity = SalaryIncome(
                basic_salary=Money.from_decimal(salary_dto.basic_salary),
                dearness_allowance=Money.from_decimal(salary_dto.dearness_allowance),
                house_rent_allowance=Money.from_decimal(salary_dto.hra_received),
                hra_received=Money.from_decimal(salary_dto.hra_received),
                hra_city_type=salary_dto.hra_city_type,
                special_allowance=Money.from_decimal(salary_dto.special_allowance),
                conveyance_allowance=Money.from_decimal(salary_dto.conveyance_allowance),
                medical_allowance=Money.from_decimal(salary_dto.medical_allowance)
            )
            logger.info("✅ SalaryIncome entity created successfully!")
            logger.info(f"   - basic_salary: {salary_entity.basic_salary.to_float()}")
            logger.info(f"   - hra_received: {salary_entity.hra_received.to_float()}")
            logger.info(f"   - hra_city_type: {salary_entity.hra_city_type}")
        except Exception as e:
            logger.error(f"❌ Failed to create SalaryIncome entity: {str(e)}")
            logger.error(f"❌ Error type: {type(e)}")
            return False
        
        # Test controller conversion method
        logger.info("🔍 Testing controller conversion method...")
        try:
            from app.api.controllers.taxation_controller import UnifiedTaxationController
            controller = UnifiedTaxationController.__new__(UnifiedTaxationController)
            converted_entity = controller._convert_salary_dto_to_entity(salary_dto)
            logger.info("✅ Controller conversion successful!")
            logger.info(f"   - basic_salary: {converted_entity.basic_salary.to_float()}")
            logger.info(f"   - hra_received: {converted_entity.hra_received.to_float()}")
            logger.info(f"   - hra_city_type: {converted_entity.hra_city_type}")
        except Exception as e:
            logger.error(f"❌ Controller conversion failed: {str(e)}")
            logger.error(f"❌ Error type: {type(e)}")
            return False
        
        # Test command creation
        logger.info("🔍 Testing CreateTaxationRecordCommand creation...")
        try:
            from app.application.commands.taxation_commands import CreateTaxationRecordCommand
            from app.domain.entities.taxation.tax_deductions import TaxDeductions
            
            # Create minimal deductions
            deductions = TaxDeductions()
            
            command = CreateTaxationRecordCommand(
                employee_id="EMP005",
                organization_id="localhost",
                tax_year="2025-26",
                regime="old",
                age=43,
                salary_income=converted_entity,
                deductions=deductions
            )
            logger.info("✅ CreateTaxationRecordCommand created successfully!")
            logger.info(f"   - employee_id: {command.employee_id}")
            logger.info(f"   - salary_income type: {type(command.salary_income)}")
        except Exception as e:
            logger.error(f"❌ CreateTaxationRecordCommand creation failed: {str(e)}")
            logger.error(f"❌ Error type: {type(e)}")
            return False
        
        logger.info("🎉 All tests passed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {str(e)}")
        logger.error(f"❌ Error type: {type(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_salary_income_creation()
    if success:
        print("\n🎉 SUCCESS: All SalaryIncome tests passed!")
        sys.exit(0)
    else:
        print("\n❌ FAILURE: SalaryIncome tests failed!")
        sys.exit(1) 