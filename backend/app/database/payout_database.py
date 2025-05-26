import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, date, timedelta
from bson import ObjectId
from pymongo import DESCENDING, ASCENDING
from database.database_connector import connect_to_database
from models.payout import (
    PayoutCreate, PayoutUpdate, PayoutInDB, PayoutStatus, 
    BulkPayoutRequest, BulkPayoutResponse, PayoutSummary,
    PayoutSchedule, PayoutHistory, PayslipData
)

logger = logging.getLogger(__name__)

class PayoutDatabase:
    def __init__(self, hostname: str):
        self.db = connect_to_database(hostname)
        self.collection = self.db.payouts
        self.schedule_collection = self.db.payout_schedules
        self._ensure_indexes()
    
    def _convert_dates_to_datetime(self, data: dict) -> dict:
        """Convert date objects to datetime objects for MongoDB compatibility"""
        converted_data = data.copy()
        date_fields = ['pay_period_start', 'pay_period_end', 'payout_date']
        
        for field in date_fields:
            if field in converted_data and isinstance(converted_data[field], date):
                # Convert date to datetime at start of day
                converted_data[field] = datetime.combine(converted_data[field], datetime.min.time())
        
        return converted_data
    
    def _convert_datetime_to_date(self, data: dict) -> dict:
        """Convert datetime objects back to date objects for model compatibility"""
        converted_data = data.copy()
        date_fields = ['pay_period_start', 'pay_period_end', 'payout_date']
        
        for field in date_fields:
            if field in converted_data and isinstance(converted_data[field], datetime):
                # Convert datetime back to date
                converted_data[field] = converted_data[field].date()
        
        return converted_data
    
    def _ensure_indexes(self):
        """Ensure necessary indexes for optimal query performance"""
        try:
            # Index for employee and pay period queries
            self.collection.create_index([
                ("employee_id", ASCENDING),
                ("pay_period_start", DESCENDING)
            ])
            
            # Index for status and date queries
            self.collection.create_index([
                ("status", ASCENDING),
                ("payout_date", DESCENDING)
            ])
            
            # Index for bulk operations
            self.collection.create_index([
                ("pay_period_start", ASCENDING),
                ("pay_period_end", ASCENDING)
            ])
            
            # Schedule collection indexes
            self.schedule_collection.create_index([
                ("month", ASCENDING),
                ("year", ASCENDING)
            ], unique=True)
            
            logger.info("Payout database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating payout indexes: {str(e)}")
    
    def create_payout(self, payout_data: PayoutCreate) -> PayoutInDB:
        """Create a new payout record"""
        try:
            payout_dict = payout_data.dict()
            payout_dict["created_at"] = datetime.now()
            payout_dict["updated_at"] = datetime.now()
            
            # Convert date objects to datetime for MongoDB
            payout_dict = self._convert_dates_to_datetime(payout_dict)
            
            result = self.collection.insert_one(payout_dict)
            
            # Retrieve the created payout
            created_payout = self.collection.find_one({"_id": result.inserted_id})
            
            # Convert datetime back to date for model compatibility
            created_payout = self._convert_datetime_to_date(created_payout)
            
            created_payout["id"] = str(created_payout["_id"])
            del created_payout["_id"]
            
            logger.info(f"Payout created successfully for employee {payout_data.employee_id}")
            return PayoutInDB(**created_payout)
            
        except Exception as e:
            logger.error(f"Error creating payout: {str(e)}")
            raise
    
    def get_payout_by_id(self, payout_id: str) -> Optional[PayoutInDB]:
        """Get payout by ID"""
        try:
            payout = self.collection.find_one({"_id": ObjectId(payout_id)})
            if payout:
                # Convert datetime back to date for model compatibility
                payout = self._convert_datetime_to_date(payout)
                payout["id"] = str(payout["_id"])
                del payout["_id"]
                return PayoutInDB(**payout)
            return None
        except Exception as e:
            logger.error(f"Error retrieving payout {payout_id}: {str(e)}")
            return None
    
    def get_employee_payouts(
        self, 
        employee_id: str, 
        year: Optional[int] = None,
        month: Optional[int] = None,
        limit: int = 12
    ) -> List[PayoutInDB]:
        """Get payouts for a specific employee"""
        try:
            query = {"employee_id": employee_id}
            
            if year:
                start_date = datetime.combine(date(year, 1, 1), datetime.min.time())
                end_date = datetime.combine(date(year, 12, 31), datetime.min.time())
                query["pay_period_start"] = {"$gte": start_date, "$lte": end_date}
            
            if month and year:
                start_date = datetime.combine(date(year, month, 1), datetime.min.time())
                if month == 12:
                    end_date = datetime.combine(date(year + 1, 1, 1) - timedelta(days=1), datetime.min.time())
                else:
                    end_date = datetime.combine(date(year, month + 1, 1) - timedelta(days=1), datetime.min.time())
                query["pay_period_start"] = {"$gte": start_date, "$lte": end_date}
            
            payouts = self.collection.find(query).sort("pay_period_start", DESCENDING).limit(limit)
            
            result = []
            for payout in payouts:
                # Convert datetime back to date for model compatibility
                payout = self._convert_datetime_to_date(payout)
                payout["id"] = str(payout["_id"])
                del payout["_id"]
                result.append(PayoutInDB(**payout))
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving employee payouts: {str(e)}")
            return []
    
    def get_monthly_payouts(
        self, 
        month: int, 
        year: int, 
        status: Optional[PayoutStatus] = None
    ) -> List[PayoutInDB]:
        """Get all payouts for a specific month"""
        try:
            start_date = datetime.combine(date(year, month, 1), datetime.min.time())
            if month == 12:
                end_date = datetime.combine(date(year + 1, 1, 1) - timedelta(days=1), datetime.min.time())
            else:
                end_date = datetime.combine(date(year, month + 1, 1) - timedelta(days=1), datetime.min.time())
            
            query = {
                "pay_period_start": {"$gte": start_date, "$lte": end_date}
            }
            
            if status:
                query["status"] = status.value
            
            payouts = self.collection.find(query).sort("employee_id", ASCENDING)
            
            result = []
            for payout in payouts:
                # Convert datetime back to date for model compatibility
                payout = self._convert_datetime_to_date(payout)
                payout["id"] = str(payout["_id"])
                del payout["_id"]
                result.append(PayoutInDB(**payout))
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving monthly payouts: {str(e)}")
            return []
    
    def update_payout(self, payout_id: str, update_data: PayoutUpdate) -> Optional[PayoutInDB]:
        """Update a payout record"""
        try:
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            update_dict["updated_at"] = datetime.now()
            
            # Convert any date objects to datetime for MongoDB
            update_dict = self._convert_dates_to_datetime(update_dict)
            
            result = self.collection.update_one(
                {"_id": ObjectId(payout_id)},
                {"$set": update_dict}
            )
            
            if result.modified_count > 0:
                return self.get_payout_by_id(payout_id)
            return None
            
        except Exception as e:
            logger.error(f"Error updating payout {payout_id}: {str(e)}")
            return None
    
    def update_payout_status(
        self, 
        payout_id: str, 
        status: PayoutStatus, 
        updated_by: Optional[str] = None
    ) -> bool:
        """Update payout status with timestamp"""
        try:
            update_data = {
                "status": status.value,
                "updated_at": datetime.now()
            }
            
            if status == PayoutStatus.PROCESSED:
                update_data["processed_at"] = datetime.now()
                if updated_by:
                    update_data["processed_by"] = updated_by
            elif status == PayoutStatus.APPROVED:
                update_data["approved_at"] = datetime.now()
                if updated_by:
                    update_data["approved_by"] = updated_by
            
            result = self.collection.update_one(
                {"_id": ObjectId(payout_id)},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating payout status: {str(e)}")
            return False
    
    def bulk_update_status(
        self, 
        payout_ids: List[str], 
        status: PayoutStatus,
        updated_by: Optional[str] = None
    ) -> int:
        """Bulk update payout status"""
        try:
            object_ids = [ObjectId(pid) for pid in payout_ids]
            
            update_data = {
                "status": status.value,
                "updated_at": datetime.now()
            }
            
            if status == PayoutStatus.PROCESSED:
                update_data["processed_at"] = datetime.now()
                if updated_by:
                    update_data["processed_by"] = updated_by
            elif status == PayoutStatus.APPROVED:
                update_data["approved_at"] = datetime.now()
                if updated_by:
                    update_data["approved_by"] = updated_by
            
            result = self.collection.update_many(
                {"_id": {"$in": object_ids}},
                {"$set": update_data}
            )
            
            return result.modified_count
            
        except Exception as e:
            logger.error(f"Error bulk updating payout status: {str(e)}")
            return 0
    
    def delete_payout(self, payout_id: str) -> bool:
        """Delete a payout record"""
        try:
            result = self.collection.delete_one({"_id": ObjectId(payout_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting payout {payout_id}: {str(e)}")
            return False
    
    def check_duplicate_payout(
        self, 
        employee_id: str, 
        pay_period_start: date, 
        pay_period_end: date
    ) -> bool:
        """Check if payout already exists for the period"""
        try:
            # Convert dates to datetime for MongoDB query
            start_datetime = datetime.combine(pay_period_start, datetime.min.time())
            end_datetime = datetime.combine(pay_period_end, datetime.min.time())
            
            existing = self.collection.find_one({
                "employee_id": employee_id,
                "pay_period_start": start_datetime,
                "pay_period_end": end_datetime
            })
            return existing is not None
        except Exception as e:
            logger.error(f"Error checking duplicate payout: {str(e)}")
            return False
    
    def get_payout_summary(self, month: int, year: int) -> PayoutSummary:
        """Get payout summary for a month"""
        try:
            start_date = datetime.combine(date(year, month, 1), datetime.min.time())
            if month == 12:
                end_date = datetime.combine(date(year + 1, 1, 1) - timedelta(days=1), datetime.min.time())
            else:
                end_date = datetime.combine(date(year, month + 1, 1) - timedelta(days=1), datetime.min.time())
            
            pipeline = [
                {
                    "$match": {
                        "pay_period_start": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_employees": {"$sum": 1},
                        "total_gross_amount": {"$sum": "$gross_salary"},
                        "total_net_amount": {"$sum": "$net_salary"},
                        "total_tax_deducted": {"$sum": "$tds"},
                        "pending_payouts": {
                            "$sum": {"$cond": [{"$eq": ["$status", "pending"]}, 1, 0]}
                        },
                        "processed_payouts": {
                            "$sum": {"$cond": [{"$eq": ["$status", "processed"]}, 1, 0]}
                        },
                        "approved_payouts": {
                            "$sum": {"$cond": [{"$eq": ["$status", "approved"]}, 1, 0]}
                        },
                        "paid_payouts": {
                            "$sum": {"$cond": [{"$eq": ["$status", "paid"]}, 1, 0]}
                        }
                    }
                }
            ]
            
            result = list(self.collection.aggregate(pipeline))
            
            if result:
                summary_data = result[0]
                return PayoutSummary(
                    month=f"{year}-{month:02d}",
                    year=year,
                    total_employees=summary_data.get("total_employees", 0),
                    total_gross_amount=summary_data.get("total_gross_amount", 0.0),
                    total_net_amount=summary_data.get("total_net_amount", 0.0),
                    total_tax_deducted=summary_data.get("total_tax_deducted", 0.0),
                    pending_payouts=summary_data.get("pending_payouts", 0),
                    processed_payouts=summary_data.get("processed_payouts", 0),
                    approved_payouts=summary_data.get("approved_payouts", 0),
                    paid_payouts=summary_data.get("paid_payouts", 0)
                )
            else:
                return PayoutSummary(
                    month=f"{year}-{month:02d}",
                    year=year,
                    total_employees=0,
                    total_gross_amount=0.0,
                    total_net_amount=0.0,
                    total_tax_deducted=0.0,
                    pending_payouts=0,
                    processed_payouts=0,
                    approved_payouts=0,
                    paid_payouts=0
                )
                
        except Exception as e:
            logger.error(f"Error getting payout summary: {str(e)}")
            return PayoutSummary(
                month=f"{year}-{month:02d}",
                year=year,
                total_employees=0,
                total_gross_amount=0.0,
                total_net_amount=0.0,
                total_tax_deducted=0.0,
                pending_payouts=0,
                processed_payouts=0,
                approved_payouts=0,
                paid_payouts=0
            )
    
    # Payout Schedule Methods
    def create_payout_schedule(self, schedule: PayoutSchedule) -> bool:
        """Create or update payout schedule"""
        try:
            schedule_dict = schedule.dict()
            
            # Upsert schedule
            result = self.schedule_collection.update_one(
                {"month": schedule.month, "year": schedule.year},
                {"$set": schedule_dict},
                upsert=True
            )
            
            return True
        except Exception as e:
            logger.error(f"Error creating payout schedule: {str(e)}")
            return False
    
    def get_payout_schedule(self, month: int, year: int) -> Optional[PayoutSchedule]:
        """Get payout schedule for a month"""
        try:
            schedule = self.schedule_collection.find_one({"month": month, "year": year})
            if schedule:
                del schedule["_id"]
                return PayoutSchedule(**schedule)
            return None
        except Exception as e:
            logger.error(f"Error retrieving payout schedule: {str(e)}")
            return None
    
    def get_active_schedules(self) -> List[PayoutSchedule]:
        """Get all active payout schedules"""
        try:
            schedules = self.schedule_collection.find({"is_active": True})
            
            result = []
            for schedule in schedules:
                del schedule["_id"]
                result.append(PayoutSchedule(**schedule))
            
            return result
        except Exception as e:
            logger.error(f"Error retrieving active schedules: {str(e)}")
            return []
    
    def get_employee_payout_history(self, employee_id: str, year: int) -> PayoutHistory:
        """Get annual payout history for an employee"""
        try:
            payouts = self.get_employee_payouts(employee_id, year=year, limit=12)
            
            annual_gross = sum(payout.gross_salary for payout in payouts)
            annual_net = sum(payout.net_salary for payout in payouts)
            annual_tax_deducted = sum(payout.tds for payout in payouts)
            
            return PayoutHistory(
                employee_id=employee_id,
                year=year,
                payouts=payouts,
                annual_gross=annual_gross,
                annual_net=annual_net,
                annual_tax_deducted=annual_tax_deducted
            )
            
        except Exception as e:
            logger.error(f"Error retrieving payout history: {str(e)}")
            return PayoutHistory(
                employee_id=employee_id,
                year=year,
                payouts=[],
                annual_gross=0.0,
                annual_net=0.0,
                annual_tax_deducted=0.0
            ) 