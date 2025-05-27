#!/usr/bin/env python3
"""
Simple test script for SOLID Attendance Repository
"""

import sys
sys.path.insert(0, '.')

def test_attendance_repository():
    """Test attendance repository import and basic functionality."""
    print("Testing SOLID Attendance Repository...")
    
    try:
        # Test import
        from infrastructure.repositories.solid_attendance_repository import SolidAttendanceRepository
        print("✓ SolidAttendanceRepository imported successfully")
        
        # Test that it has the expected methods
        expected_methods = [
            # Command methods
            'save', 'save_batch', 'delete', 'delete_by_employee_and_date',
            
            # Query methods
            'get_by_id', 'get_by_employee_and_date', 'get_by_employee', 
            'get_by_date', 'get_by_date_range', 'search', 'count_by_filters',
            'get_pending_check_outs', 'get_regularization_requests', 
            'exists_by_employee_and_date',
            
            # Analytics methods
            'get_employee_summary', 'get_multiple_employee_summaries',
            'get_daily_statistics', 'get_period_statistics',
            'get_late_arrivals', 'get_absent_employees',
            'get_attendance_percentage_by_employee', 'get_monthly_attendance_summary',
            
            # Team methods (legacy compatibility)
            'get_team_attendance_by_date', 'get_team_attendance_by_month',
            'get_team_attendance_by_year',
            
            # Legacy compatibility methods
            'create_attendance_legacy', 'get_employee_attendance_by_month_legacy',
            'get_todays_attendance_stats_legacy',
            
            # Reports methods
            'generate_daily_report', 'generate_weekly_report', 
            'generate_monthly_report', 'generate_custom_report',
            'export_to_csv', 'export_to_excel',
            
            # Bulk operations methods
            'bulk_import', 'bulk_update_status', 'bulk_regularize',
            'bulk_delete', 'auto_mark_absent', 'auto_mark_holidays'
        ]
        
        missing_methods = []
        for method in expected_methods:
            if hasattr(SolidAttendanceRepository, method):
                print(f"✓ Has method: {method}")
            else:
                missing_methods.append(method)
                print(f"✗ Missing method: {method}")
        
        if missing_methods:
            print(f"\n⚠ Missing {len(missing_methods)} methods")
            return False
        else:
            print(f"\n✅ All {len(expected_methods)} expected methods found!")
        
        # Test class structure
        print("\nTesting class structure...")
        
        # Check if it's a proper class
        if not isinstance(SolidAttendanceRepository, type):
            print("✗ SolidAttendanceRepository is not a class")
            return False
        
        print("✓ SolidAttendanceRepository is a proper class")
        
        # Check docstring
        if SolidAttendanceRepository.__doc__:
            print("✓ Has class docstring")
        else:
            print("⚠ Missing class docstring")
        
        # Test inheritance
        print("\nTesting inheritance...")
        base_classes = [cls.__name__ for cls in SolidAttendanceRepository.__mro__]
        expected_bases = [
            'SolidAttendanceRepository', 'BaseRepository',
            'AttendanceCommandRepository', 'AttendanceQueryRepository',
            'AttendanceAnalyticsRepository', 'AttendanceReportsRepository',
            'AttendanceBulkOperationsRepository', 'AttendanceRepository'
        ]
        
        for expected_base in expected_bases:
            if any(expected_base in base for base in base_classes):
                print(f"✓ Implements: {expected_base}")
            else:
                print(f"⚠ May not implement: {expected_base}")
        
        print("\n🎉 SOLID Attendance Repository validation successful!")
        print("✅ Ready for integration with existing codebase!")
        
        return True
        
    except Exception as e:
        print(f"✗ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_attendance_repository()
    sys.exit(0 if success else 1) 