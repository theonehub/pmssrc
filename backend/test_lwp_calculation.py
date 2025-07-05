#!/usr/bin/env python3
"""
Test script for LWP calculation service
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.infrastructure.services.lwp_calculation_service import LWPCalculationService
from app.infrastructure.services.attendance_service_impl import AttendanceServiceImpl
from app.infrastructure.repositories.employee_leave_repository_impl import EmployeeLeaveRepositoryImpl
from app.infrastructure.repositories.mongodb_public_holiday_repository import MongoDBPublicHolidayRepository
from app.infrastructure.database.mongodb_connector import MongoDBConnector


async def test_lwp_calculation():
    """Test the LWP calculation service."""
    print("Testing LWP Calculation Service...")
    
    try:
        # Create dependencies
        db_connector = MongoDBConnector()
        attendance_service = AttendanceServiceImpl(db_connector)
        employee_leave_repository = EmployeeLeaveRepositoryImpl(db_connector)
        public_holiday_repository = MongoDBPublicHolidayRepository(db_connector)
        
        # Create LWP calculation service
        lwp_service = LWPCalculationService(
            attendance_service=attendance_service,
            employee_leave_repository=employee_leave_repository,
            public_holiday_repository=public_holiday_repository
        )
        
        # Test LWP calculation for a sample employee
        employee_id = "EMP001"
        month = 12
        year = 2024
        organisation_id = "test_org"
        
        print(f"Calculating LWP for employee {employee_id} in {month}/{year}...")
        
        result = await lwp_service.calculate_lwp_for_month(
            employee_id, month, year, organisation_id
        )
        
        print("LWP Calculation Result:")
        print(f"  Employee ID: {result.employee_id}")
        print(f"  Month: {result.month}")
        print(f"  Year: {result.year}")
        print(f"  LWP Days: {result.lwp_days}")
        print(f"  Working Days: {result.working_days}")
        print(f"  LWP Amount: {result.lwp_amount}")
        print(f"  Calculation Details: {result.calculation_details}")
        
        # Test LWP factor calculation
        lwp_factor = lwp_service.calculate_lwp_factor(result.lwp_days, result.working_days)
        paid_days = lwp_service.calculate_paid_days(result.lwp_days, result.working_days)
        
        print(f"  LWP Factor: {lwp_factor}")
        print(f"  Paid Days: {paid_days}")
        
        print("✅ LWP calculation test completed successfully!")
        
    except Exception as e:
        print(f"❌ LWP calculation test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_lwp_calculation()) 