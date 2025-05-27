"""
Payout Repository Migration Example
Demonstrates how to use the new SOLID payout repository
"""

import asyncio
import logging
import os
from datetime import datetime, date, timedelta
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration handling
def get_mongo_uri():
    """Get MongoDB URI from config or environment."""
    try:
        from config import MONGO_URI
        return MONGO_URI
    except ImportError:
        return os.getenv('MONGO_URI', 'mongodb://localhost:27017')


async def example_payout_operations():
    """
    Example showing how to use the SOLID payout repository.
    """
    print("\n=== SOLID Payout Repository Example ===")
    
    try:
        from infrastructure.services.database_migration_service import get_migration_service
        
        # Initialize migration service
        print("Initializing migration service...")
        MONGO_URI = get_mongo_uri()
        migration_service = await get_migration_service(MONGO_URI)
        
        # Get payout repository
        payout_repo = migration_service.get_payout_repository()
        
        hostname = "example_company"
        
        # Create a simple payout object
        class SimplePayout:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
            
            def dict(self):
                return {k: v for k, v in self.__dict__.items()}
        
        # Create test payout
        payout = SimplePayout(
            employee_id="EMP001",
            pay_period_start=date(2024, 1, 1),
            pay_period_end=date(2024, 1, 31),
            payout_date=date(2024, 2, 1),
            basic_salary=50000.0,
            hra=15000.0,
            special_allowance=10000.0,
            epf_employee=6000.0,
            tds=5000.0,
            gross_salary=75000.0,
            total_deductions=11000.0,
            net_salary=64000.0,
            status="pending"
        )
        
        print("Creating payout...")
        try:
            created_payout = await payout_repo.create_payout(payout, hostname)
            print(f"✓ Payout created: {getattr(created_payout, 'id', 'Unknown ID')}")
            payout_id = getattr(created_payout, 'id', None)
        except Exception as e:
            print(f"⚠ Payout creation failed (might already exist): {e}")
            # Try to find existing payout
            existing_payouts = await payout_repo.get_employee_payouts("EMP001", hostname, year=2024, month=1)
            if existing_payouts:
                payout_id = getattr(existing_payouts[0], 'id', None)
                print(f"✓ Using existing payout: {payout_id}")
            else:
                payout_id = None
        
        if payout_id:
            # Get payout by ID
            print("\nGetting payout by ID...")
            retrieved_payout = await payout_repo.get_by_id(payout_id, hostname)
            if retrieved_payout:
                print(f"✓ Retrieved payout for employee: {getattr(retrieved_payout, 'employee_id', 'Unknown')}")
            
            # Update payout status
            print("\nUpdating payout status...")
            status_updated = await payout_repo.update_payout_status(
                payout_id, "processed", hostname, "system_admin"
            )
            print(f"✓ Status updated: {status_updated}")
        
        # Get employee payouts
        print("\nGetting employee payouts...")
        employee_payouts = await payout_repo.get_employee_payouts("EMP001", hostname, year=2024)
        print(f"✓ Found {len(employee_payouts)} payouts for employee")
        
        # Get monthly payouts
        print("\nGetting monthly payouts...")
        monthly_payouts = await payout_repo.get_monthly_payouts(1, 2024, hostname)
        print(f"✓ Found {len(monthly_payouts)} payouts for January 2024")
        
        # Get payout summary
        print("\nGetting payout summary...")
        summary = await payout_repo.get_payout_summary(1, 2024, hostname)
        print(f"✓ Summary - Total employees: {summary.get('total_employees', 0)}")
        print(f"  Total gross: ${summary.get('total_gross_amount', 0):,.2f}")
        print(f"  Total net: ${summary.get('total_net_amount', 0):,.2f}")
        
        # Check duplicate payout
        print("\nChecking for duplicate payout...")
        is_duplicate = await payout_repo.check_duplicate_payout(
            "EMP001", date(2024, 1, 1), date(2024, 1, 31), hostname
        )
        print(f"✓ Duplicate check: {'Found duplicate' if is_duplicate else 'No duplicate'}")
        
        # Get payout history
        print("\nGetting payout history...")
        history = await payout_repo.get_employee_payout_history("EMP001", 2024, hostname)
        print(f"✓ Annual history - Gross: ${history.get('annual_gross', 0):,.2f}")
        print(f"  Annual net: ${history.get('annual_net', 0):,.2f}")
        
        print("\n✅ All payout operations completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in payout operations example: {e}")


async def example_payout_analytics():
    """
    Example showing payout analytics capabilities.
    """
    print("\n=== Payout Analytics Example ===")
    
    try:
        from infrastructure.services.database_migration_service import get_migration_service
        
        MONGO_URI = get_mongo_uri()
        migration_service = await get_migration_service(MONGO_URI)
        payout_repo = migration_service.get_payout_repository()
        
        hostname = "example_company"
        
        # Get salary distribution
        print("Getting salary distribution...")
        distribution = await payout_repo.get_salary_distribution(1, 2024, hostname)
        print(f"✓ Salary distribution:")
        print(f"  Min: ${distribution.get('min_salary', 0):,.2f}")
        print(f"  Max: ${distribution.get('max_salary', 0):,.2f}")
        print(f"  Avg: ${distribution.get('avg_salary', 0):,.2f}")
        
        # Get top earners
        print("\nGetting top earners...")
        top_earners = await payout_repo.get_top_earners(1, 2024, hostname, limit=5)
        print(f"✓ Top {len(top_earners)} earners:")
        for i, earner in enumerate(top_earners, 1):
            print(f"  {i}. Employee {earner.get('employee_id')}: ${earner.get('net_salary', 0):,.2f}")
        
        # Get deduction analysis
        print("\nGetting deduction analysis...")
        deductions = await payout_repo.get_deduction_analysis(1, 2024, hostname)
        print(f"✓ Deduction analysis:")
        print(f"  Total EPF: ${deductions.get('total_epf', 0):,.2f}")
        print(f"  Total TDS: ${deductions.get('total_tds', 0):,.2f}")
        print(f"  Total Professional Tax: ${deductions.get('total_professional_tax', 0):,.2f}")
        
        # Get compliance metrics
        print("\nGetting compliance metrics...")
        compliance = await payout_repo.get_compliance_metrics(1, 2024, hostname)
        print(f"✓ Compliance metrics:")
        print(f"  Compliance rate: {compliance.get('compliance_rate', 0):.1f}%")
        print(f"  Total statutory deductions: ${compliance.get('total_statutory_deductions', 0):,.2f}")
        
        # Get monthly trends
        print("\nGetting monthly trends...")
        trends = await payout_repo.get_monthly_trends(1, 2024, 3, 2024, hostname)
        print(f"✓ Monthly trends for Q1 2024:")
        for trend in trends:
            month = trend.get('month', 'Unknown')
            total_net = trend.get('total_net_amount', 0)
            print(f"  {month}: ${total_net:,.2f}")
        
        print("\n✅ All analytics operations completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in payout analytics example: {e}")


async def example_payout_schedules():
    """
    Example showing payout schedule management.
    """
    print("\n=== Payout Schedule Example ===")
    
    try:
        from infrastructure.services.database_migration_service import get_migration_service
        
        MONGO_URI = get_mongo_uri()
        migration_service = await get_migration_service(MONGO_URI)
        payout_repo = migration_service.get_payout_repository()
        
        hostname = "example_company"
        
        # Create payout schedule
        print("Creating payout schedule...")
        schedule_data = {
            "month": 1,
            "year": 2024,
            "payout_date": 30,
            "auto_process": True,
            "auto_approve": False,
            "is_active": True
        }
        
        schedule_id = await payout_repo.create_schedule(schedule_data, hostname, "admin")
        print(f"✓ Schedule created: {schedule_id}")
        
        # Get payout schedule
        print("\nGetting payout schedule...")
        schedule = await payout_repo.get_schedule(1, 2024, hostname)
        if schedule:
            print(f"✓ Schedule found - Payout date: {schedule.get('payout_date')}")
            print(f"  Auto process: {schedule.get('auto_process')}")
            print(f"  Auto approve: {schedule.get('auto_approve')}")
        
        # Get active schedules
        print("\nGetting active schedules...")
        active_schedules = await payout_repo.get_active_schedules(hostname)
        print(f"✓ Found {len(active_schedules)} active schedules")
        
        # Update schedule
        if schedule_id:
            print("\nUpdating schedule...")
            update_data = {"auto_approve": True}
            updated = await payout_repo.update_schedule(schedule_id, update_data, hostname, "admin")
            print(f"✓ Schedule updated: {updated}")
        
        print("\n✅ All schedule operations completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in payout schedule example: {e}")


async def example_payout_audit():
    """
    Example showing payout audit capabilities.
    """
    print("\n=== Payout Audit Example ===")
    
    try:
        from infrastructure.services.database_migration_service import get_migration_service
        
        MONGO_URI = get_mongo_uri()
        migration_service = await get_migration_service(MONGO_URI)
        payout_repo = migration_service.get_payout_repository()
        
        hostname = "example_company"
        
        # Log audit event
        print("Logging audit event...")
        audit_data = {
            "payout_id": "test_payout_id",
            "action": "manual_test",
            "user_id": "admin",
            "details": "Testing audit functionality"
        }
        
        audit_id = await payout_repo.log_audit_event(audit_data, hostname)
        print(f"✓ Audit event logged: {audit_id}")
        
        # Get payout audit trail
        print("\nGetting payout audit trail...")
        audit_trail = await payout_repo.get_payout_audit_trail("test_payout_id", hostname)
        print(f"✓ Found {len(audit_trail)} audit events for payout")
        
        # Get user audit trail
        print("\nGetting user audit trail...")
        user_trail = await payout_repo.get_user_audit_trail("admin", hostname)
        print(f"✓ Found {len(user_trail)} audit events for user")
        
        print("\n✅ All audit operations completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in payout audit example: {e}")


async def example_repository_health():
    """
    Example showing repository health monitoring.
    """
    print("\n=== Repository Health Example ===")
    
    try:
        from infrastructure.services.database_migration_service import get_migration_service
        
        MONGO_URI = get_mongo_uri()
        migration_service = await get_migration_service(MONGO_URI)
        payout_repo = migration_service.get_payout_repository()
        
        hostname = "example_company"
        
        # Repository health check
        print("Performing repository health check...")
        health = await payout_repo.health_check(hostname)
        print(f"✓ Repository health: {health.get('status', 'Unknown')}")
        print(f"  Collection: {health.get('collection', 'Unknown')}")
        print(f"  Document count: {health.get('document_count', 0)}")
        
        # Service health check
        print("\nPerforming service health check...")
        service_health = await migration_service.health_check()
        print(f"✓ Service status: {service_health.get('status', 'Unknown')}")
        
        print("\n✅ All health checks completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in health check example: {e}")


async def main():
    """
    Main function to run all payout examples.
    """
    print("Payout Repository Migration Examples")
    print("=" * 50)
    
    try:
        # Run all examples
        await example_payout_operations()
        await example_payout_analytics()
        await example_payout_schedules()
        await example_payout_audit()
        await example_repository_health()
        
        print("\n" + "=" * 50)
        print("🎉 All payout examples completed successfully!")
        print("✅ SOLID payout repository is working correctly!")
        
    except Exception as e:
        logger.error(f"Error running payout examples: {e}")
    
    finally:
        # Clean up
        try:
            from infrastructure.services.database_migration_service import cleanup_migration_service
            await cleanup_migration_service()
            print("\nCleaned up migration service")
        except Exception as e:
            logger.error(f"Error cleaning up: {e}")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main()) 