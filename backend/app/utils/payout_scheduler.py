import logging
import asyncio
from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional
import os
import sys

# Add the parent directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# MIGRATION NOTE: Legacy services have been moved to infrastructure layer
# This scheduler will need to be updated to use the new SOLID architecture
# from app.infrastructure.services.payroll_migration_service import PayrollMigrationService
# from app.infrastructure.services.organisation_migration_service import OrganisationMigrationService
from database.database_connector import connect_to_database

# Import centralized logger
from app.utils.logger import get_logger, LoggerConfig

logger = logging.getLogger(__name__)

class PayoutScheduler:
    """
    Utility class for scheduled payout processing
    Can be called from cron jobs or other scheduling systems
    """
    
    def __init__(self):
        self.org_service = OrganisationService()
    
    def get_all_active_organisations(self) -> List[str]:
        """Get all active organisation IDs"""
        try:
            # This is a simplified approach - you might need to implement
            # get_all_organisations in OrganisationService
            # For now, return a hardcoded list or implement based on your setup
            
            # TODO: Implement proper organisation listing
            # organisations = self.org_service.get_all_organisations()
            # return [org.id for org in organisations if org.is_active]
            
            # For now, we'll scan the database for company databases
            from pymongo import MongoClient
            from config import MONGO_URI
            
            client = MongoClient(MONGO_URI, tls=True)
            db_names = client.list_database_names()
            
            # Filter for PMS databases (assuming they follow pattern "pms_{company_id}")
            pms_dbs = [db for db in db_names if db.startswith("pms_") and db != "pms_"]
            company_ids = [db.replace("pms_", "") for db in pms_dbs]
            
            return company_ids
            
        except Exception as e:
            logger.error(f"Error getting active organisations: {str(e)}")
            return []
    
    def process_organisation_payouts(self, company_id: str, target_date: date = None) -> Dict[str, Any]:
        """Process payouts for a specific organisation"""
        try:
            logger.info(f"Processing payouts for organisation: {company_id}")
            
            if target_date is None:
                target_date = date.today()
            
            payout_service = PayoutService(company_id)
            result = payout_service.process_monthly_payout_schedule(target_date)
            
            return {
                "company_id": company_id,
                "success": True,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error processing payouts for organisation {company_id}: {str(e)}")
            return {
                "company_id": company_id,
                "success": False,
                "error": str(e)
            }
    
    def process_all_organisations(self, target_date: date = None) -> Dict[str, Any]:
        """
        Process payouts for all active organisations
        This is the main method to be called by cron jobs
        """
        try:
            if target_date is None:
                target_date = date.today()
            
            logger.info(f"Starting scheduled payout processing for all organisations on {target_date}")
            
            # Check if today is the 30th (or last day of month if month has < 30 days)
            if target_date.day != 30:
                import calendar
                last_day = calendar.monthrange(target_date.year, target_date.month)[1]
                if target_date.day != last_day:
                    logger.info(f"Not a payout processing day. Current day: {target_date.day}")
                    return {
                        "processed": False,
                        "reason": f"Not payout processing day (day {target_date.day})",
                        "target_date": str(target_date)
                    }
            
            # Get all active organisations
            company_ids = self.get_all_active_organisations()
            
            if not company_ids:
                logger.warning("No active organisations found")
                return {
                    "processed": False,
                    "reason": "No active organisations found",
                    "target_date": str(target_date)
                }
            
            # Process payouts for each organisation
            results = []
            successful_orgs = 0
            failed_orgs = 0
            
            for company_id in company_ids:
                result = self.process_organisation_payouts(company_id, target_date)
                results.append(result)
                
                if result["success"]:
                    successful_orgs += 1
                    if result["result"].get("processed", False):
                        logger.info(f"Successfully processed payouts for organisation {company_id}")
                    else:
                        logger.info(f"No payouts to process for organisation {company_id}: {result['result'].get('reason', 'Unknown')}")
                else:
                    failed_orgs += 1
                    logger.error(f"Failed to process payouts for organisation {company_id}: {result.get('error', 'Unknown error')}")
            
            summary = {
                "processed": True,
                "target_date": str(target_date),
                "total_organisations": len(company_ids),
                "successful_organisations": successful_orgs,
                "failed_organisations": failed_orgs,
                "results": results,
                "summary": {
                    "total_employees_processed": sum(
                        r["result"].get("total_employees", 0) 
                        for r in results 
                        if r["success"] and r["result"].get("processed", False)
                    ),
                    "total_successful_payouts": sum(
                        r["result"].get("successful_payouts", 0) 
                        for r in results 
                        if r["success"] and r["result"].get("processed", False)
                    ),
                    "total_failed_payouts": sum(
                        r["result"].get("failed_payouts", 0) 
                        for r in results 
                        if r["success"] and r["result"].get("processed", False)
                    )
                }
            }
            
            logger.info(f"Completed scheduled payout processing. Summary: {summary['summary']}")
            return summary
            
        except Exception as e:
            logger.error(f"Error in scheduled payout processing: {str(e)}")
            return {
                "processed": False,
                "error": str(e),
                "target_date": str(target_date) if target_date else None
            }

def main():
    """
    Main function to be called by cron job
    Usage: python payout_scheduler.py [YYYY-MM-DD]
    """
    try:
        # Configure custom file handler for payout scheduler
        logger_config = LoggerConfig()
        logger_config.add_custom_logger(
            'payout_scheduler',
            level='INFO',
            file_path='/var/log/payout_scheduler.log'
        )
        
        logger = get_logger('payout_scheduler')
        logger.info("Starting payout scheduler")
        
        # Parse target date from command line argument if provided
        target_date = None
        if len(sys.argv) > 1:
            try:
                target_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
                logger.info(f"Using target date from argument: {target_date}")
            except ValueError as e:
                logger.error(f"Invalid date format in argument: {sys.argv[1]}")
                print(f"Error: Invalid date format. Please use YYYY-MM-DD. Details: {e}")
                sys.exit(1)
        else:
            target_date = datetime.now().date()
            logger.info(f"Using current date as target: {target_date}")
        
        # Initialize services and repositories
        try:
            from app.config.dependency_container import get_dependency_container
            container = get_dependency_container()
            
            payout_service = container.get_payout_service()
            logger.info("Successfully initialized payout service")
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {str(e)}", exc_info=True)
            print(f"Error: Service initialization failed. Details: {e}")
            sys.exit(1)
        
        # Process payouts
        try:
            logger.info(f"Processing payouts for date: {target_date}")
            result = payout_service.process_payouts(target_date)
            
            logger.info(f"Payout processing completed. Results: {result}")
            print(f"Successfully processed payouts for {target_date}")
            
        except Exception as e:
            logger.error(f"Failed to process payouts: {str(e)}", exc_info=True)
            print(f"Error: Payout processing failed. Details: {e}")
            sys.exit(1)
        
    except Exception as e:
        print(f"Fatal error in payout scheduler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Example cron job entry (add to crontab):
# 0 10 30 * * /path/to/python /path/to/payout_scheduler.py >> /var/log/payout_cron.log 2>&1
# This runs every 30th of the month at 10:00 AM

# Alternative: Run on last day of month
# 0 10 28-31 * * [ $(date -d tomorrow +\%d) -eq 1 ] && /path/to/python /path/to/payout_scheduler.py >> /var/log/payout_cron.log 2>&1 