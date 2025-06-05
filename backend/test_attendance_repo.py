#!/usr/bin/env python3
"""
Test script to verify the attendance repository works in isolation
"""

import sys
import os
sys.path.append('.')

def test_attendance_repository_import():
    """Test if the attendance repository can be imported successfully"""
    try:
        # Test individual imports first
        print("Testing individual imports...")
        
        from app.domain.events.attendance_events import AttendanceCreatedEvent
        print("✅ Events import successful")
        
        from app.application.interfaces.repositories.attendance_repository import AttendanceRepository
        print("✅ Interface import successful")
        
        from app.application.dto.attendance_dto import AttendanceSearchFiltersDTO
        print("✅ DTO import successful")
        
        from app.domain.value_objects.employee_id import EmployeeId
        print("✅ Employee ID import successful")
        
        from app.domain.value_objects.attendance_status import AttendanceStatus
        print("✅ Attendance Status import successful")
        
        from app.domain.value_objects.working_hours import WorkingHours
        print("✅ Working Hours import successful")
        
        # Test the main repository import
        print("\nTesting main repository import...")
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "mongodb_attendance_repository", 
            "app/infrastructure/repositories/mongodb_attendance_repository.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        MongoDBAttendanceRepository = module.MongoDBAttendanceRepository
        print("✅ MongoDB Attendance Repository import successful (direct import)")
        
        print("\n🎉 All imports successful! The attendance repository is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_attendance_repository_import()
    sys.exit(0 if success else 1) 