"""
SOLID-Compliant Payout Repository Implementation
Replaces the procedural PayoutDatabase class with proper SOLID architecture
"""

import logging
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date, timedelta
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

# Import domain entities
try:
    from app.domain.entities.payout import (
        PayoutCreate, PayoutUpdate, PayoutInDB, PayoutStatus, 
        PayoutSummary, PayoutSchedule, PayoutHistory, PayslipData,
        BulkPayoutRequest, BulkPayoutResponse
    )
except ImportError:
    # Fallback classes for migration compatibility
    class PayoutCreate:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        def dict(self):
            return {k: v for k, v in self.__dict__.items()}
    
    class PayoutUpdate:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        def dict(self):
            return {k: v for k, v in self.__dict__.items() if v is not None}
    
    class PayoutInDB:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class PayoutStatus:
        PENDING = "pending"
        PROCESSED = "processed"
        APPROVED = "approved"
        PAID = "paid"
        FAILED = "failed"
        CANCELLED = "cancelled"
    
    class PayoutSummary:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class PayoutSchedule:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        def dict(self):
            return {k: v for k, v in self.__dict__.items()}
    
    class PayoutHistory:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

# Import application interfaces
try:
    from app.application.interfaces.repositories.payout_repository import (
        PayoutCommandRepository, PayoutQueryRepository, PayoutAnalyticsRepository,
        PayoutScheduleRepository, PayoutAuditRepository
    )
except ImportError:
    # Fallback interfaces
    from abc import ABC, abstractmethod
    
    class PayoutCommandRepository(ABC):
        pass
    
    class PayoutQueryRepository(ABC):
        pass
    
    class PayoutAnalyticsRepository(ABC):
        pass
    
    class PayoutScheduleRepository(ABC):
        pass
    
    class PayoutAuditRepository(ABC):
        pass

# Import DTOs
try:
    from app.application.dto.payroll_dto import PayoutSearchFiltersDTO
except ImportError:
    class PayoutSearchFiltersDTO:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

from .base_repository import BaseRepository
from ..database.database_connector import DatabaseConnector

logger = logging.getLogger(__name__)


class SolidPayoutRepository(
    BaseRepository[PayoutInDB],
    PayoutCommandRepository,
    PayoutQueryRepository,
    PayoutAnalyticsRepository,
    PayoutScheduleRepository,
    PayoutAuditRepository
):
    """
    SOLID-compliant payout repository implementation.
    
    Replaces the procedural PayoutDatabase class with proper SOLID architecture:
    - Single Responsibility: Only handles payout data persistence
    - Open/Closed: Can be extended without modification
    - Liskov Substitution: Implements all payout repository interfaces
    - Interface Segregation: Implements focused payout repository interfaces
    - Dependency Inversion: Depends on DatabaseConnector abstraction
    """
    
    def __init__(self, database_connector: DatabaseConnector):
        """
        Initialize payout repository.
        
        Args:
            database_connector: Database connection abstraction
        """
        super().__init__(database_connector, "payouts")
        self._schedule_collection_name = "payout_schedules"
        self._audit_collection_name = "payout_audit"
        
    def _get_schedule_collection(self, organization_id: Optional[str] = None):
        """Get payout schedules collection."""
        db_name = f"pms_{organization_id}" if organization_id else "global_database"
        return self._db_connector.get_collection(db_name, self._schedule_collection_name)
    
    def _get_audit_collection(self, organization_id: Optional[str] = None):
        """Get payout audit collection."""
        db_name = f"pms_{organization_id}" if organization_id else "global_database"
        return self._db_connector.get_collection(db_name, self._audit_collection_name)
    
    def _convert_dates_to_datetime(self, data: dict) -> dict:
        """Convert date objects to datetime objects for MongoDB compatibility."""
        converted_data = data.copy()
        date_fields = ['pay_period_start', 'pay_period_end', 'payout_date']
        
        for field in date_fields:
            if field in converted_data and isinstance(converted_data[field], date):
                # Convert date to datetime at start of day
                converted_data[field] = datetime.combine(converted_data[field], datetime.min.time())
        
        return converted_data
    
    def _convert_datetime_to_date(self, data: dict) -> dict:
        """Convert datetime objects back to date objects for model compatibility."""
        converted_data = data.copy()
        date_fields = ['pay_period_start', 'pay_period_end', 'payout_date']
        
        for field in date_fields:
            if field in converted_data and isinstance(converted_data[field], datetime):
                # Convert datetime back to date
                converted_data[field] = converted_data[field].date()
        
        return converted_data
    
    def _entity_to_document(self, payout: PayoutInDB) -> Dict[str, Any]:
        """
        Convert Payout entity to database document.
        
        Args:
            payout: Payout entity to convert
            
        Returns:
            Database document representation
        """
        if hasattr(payout, 'dict'):
            document = payout.dict()
        else:
            document = {k: v for k, v in payout.__dict__.items()}
        
        # Remove the 'id' field if present (MongoDB uses '_id')
        if 'id' in document:
            del document['id']
        
        # Convert dates to datetime for MongoDB
        document = self._convert_dates_to_datetime(document)
        
        return document
    
    def _document_to_entity(self, document: Dict[str, Any]) -> PayoutInDB:
        """
        Convert database document to Payout entity.
        
        Args:
            document: Database document to convert
            
        Returns:
            Payout entity instance
        """
        # Convert datetime back to date for model compatibility
        document = self._convert_datetime_to_date(document)
        
        # Convert MongoDB _id to id
        if '_id' in document:
            document['id'] = str(document['_id'])
            del document['_id']
        
        return PayoutInDB(**document)
    
    async def _ensure_indexes(self, organization_id: str) -> None:
        """Ensure necessary indexes for optimal query performance."""
        try:
            collection = self._get_collection(organization_id)
            
            # Index for employee and pay period queries
            await collection.create_index([
                ("employee_id", 1),
                ("pay_period_start", -1)
            ])
            
            # Index for status and date queries
            await collection.create_index([
                ("status", 1),
                ("payout_date", -1)
            ])
            
            # Index for bulk operations
            await collection.create_index([
                ("pay_period_start", 1),
                ("pay_period_end", 1)
            ])
            
            # Schedule collection indexes
            schedule_collection = self._get_schedule_collection(organization_id)
            await schedule_collection.create_index([
                ("month", 1),
                ("year", 1)
            ], unique=True)
            
            logger.info(f"Payout indexes ensured for organization: {organization_id}")
            
        except Exception as e:
            logger.error(f"Error ensuring payout indexes: {e}")
    
    # Command Repository Implementation
    async def create_payout(self, payout: PayoutCreate, hostname: str) -> PayoutInDB:
        """
        Create a new payout record.
        
        Replaces: PayoutDatabase.create_payout()
        """
        try:
            # Check for duplicates
            if await self.check_duplicate_payout(
                payout.employee_id, 
                payout.pay_period_start, 
                payout.pay_period_end, 
                hostname
            ):
                raise DuplicateKeyError("Payout already exists for this period")
            
            # Ensure indexes
            await self._ensure_indexes(hostname)
            
            # Prepare document
            if hasattr(payout, 'dict'):
                payout_dict = payout.dict()
            else:
                payout_dict = {k: v for k, v in payout.__dict__.items()}
            
            payout_dict["created_at"] = datetime.utcnow()
            payout_dict["updated_at"] = datetime.utcnow()
            
            # Convert dates to datetime for MongoDB
            payout_dict = self._convert_dates_to_datetime(payout_dict)
            
            # Insert document
            document_id = await self._insert_document(payout_dict, hostname)
            
            # Retrieve and return created payout
            created_payout = await self.get_by_id(document_id, hostname)
            
            logger.info(f"Payout created successfully for employee {payout.employee_id}")
            return created_payout
            
        except Exception as e:
            logger.error(f"Error creating payout: {e}")
            raise
    
    async def update_payout(self, payout_id: str, update: PayoutUpdate, 
                           hostname: str, updated_by: str) -> PayoutInDB:
        """
        Update an existing payout record.
        
        Replaces: PayoutDatabase.update_payout()
        """
        try:
            if hasattr(update, 'dict'):
                update_dict = {k: v for k, v in update.dict().items() if v is not None}
            else:
                update_dict = {k: v for k, v in update.__dict__.items() if v is not None}
            
            update_dict["updated_at"] = datetime.utcnow()
            update_dict["updated_by"] = updated_by
            
            # Convert any date objects to datetime for MongoDB
            update_dict = self._convert_dates_to_datetime(update_dict)
            
            filters = {"_id": ObjectId(payout_id)}
            success = await self._update_document(
                filters=filters,
                update_data=update_dict,
                organization_id=hostname
            )
            
            if success:
                return await self.get_by_id(payout_id, hostname)
            else:
                raise ValueError(f"Payout {payout_id} not found or no changes made")
                
        except Exception as e:
            logger.error(f"Error updating payout {payout_id}: {e}")
            raise
    
    async def update_payout_status(self, payout_id: str, status: PayoutStatus,
                                  hostname: str, updated_by: str, 
                                  reason: Optional[str] = None) -> bool:
        """
        Update payout status with timestamp.
        
        Replaces: PayoutDatabase.update_payout_status()
        """
        try:
            status_value = status.value if hasattr(status, 'value') else str(status)
            
            update_data = {
                "status": status_value,
                "updated_at": datetime.utcnow(),
                "updated_by": updated_by
            }
            
            if reason:
                update_data["status_reason"] = reason
            
            if status_value == "processed":
                update_data["processed_at"] = datetime.utcnow()
                update_data["processed_by"] = updated_by
            elif status_value == "approved":
                update_data["approved_at"] = datetime.utcnow()
                update_data["approved_by"] = updated_by
            
            filters = {"_id": ObjectId(payout_id)}
            success = await self._update_document(
                filters=filters,
                update_data=update_data,
                organization_id=hostname
            )
            
            if success:
                # Log audit event
                await self._log_audit_event({
                    "payout_id": payout_id,
                    "action": "status_update",
                    "old_status": None,  # Could be fetched if needed
                    "new_status": status_value,
                    "updated_by": updated_by,
                    "reason": reason,
                    "timestamp": datetime.utcnow()
                }, hostname)
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating payout status: {e}")
            return False
    
    async def bulk_create_payouts(self, payouts: List[PayoutCreate], 
                                 hostname: str, created_by: str) -> List[PayoutInDB]:
        """
        Create multiple payout records in bulk.
        
        Provides bulk operations not available in original procedural code.
        """
        try:
            created_payouts = []
            
            for payout in payouts:
                try:
                    created_payout = await self.create_payout(payout, hostname)
                    created_payouts.append(created_payout)
                except Exception as e:
                    logger.error(f"Error creating payout for employee {payout.employee_id}: {e}")
                    # Continue with other payouts
            
            logger.info(f"Bulk created {len(created_payouts)} payouts")
            return created_payouts
            
        except Exception as e:
            logger.error(f"Error in bulk create payouts: {e}")
            raise
    
    async def bulk_update_status(self, payout_ids: List[str], status: PayoutStatus,
                                hostname: str, updated_by: str) -> Dict[str, bool]:
        """
        Update status for multiple payouts.
        
        Replaces: PayoutDatabase.bulk_update_status()
        """
        try:
            results = {}
            
            for payout_id in payout_ids:
                try:
                    success = await self.update_payout_status(
                        payout_id, status, hostname, updated_by
                    )
                    results[payout_id] = success
                except Exception as e:
                    logger.error(f"Error updating payout {payout_id}: {e}")
                    results[payout_id] = False
            
            successful_updates = sum(1 for success in results.values() if success)
            logger.info(f"Bulk updated {successful_updates}/{len(payout_ids)} payouts")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk update status: {e}")
            raise
    
    async def delete_payout(self, payout_id: str, hostname: str, 
                           deleted_by: str) -> bool:
        """
        Soft delete a payout record.
        
        Replaces: PayoutDatabase.delete_payout()
        """
        try:
            # Check if payout can be deleted (not in processed/paid state)
            payout = await self.get_by_id(payout_id, hostname)
            if not payout:
                return False
            
            status = getattr(payout, 'status', '')
            if status in ['processed', 'paid']:
                raise ValueError("Cannot delete processed or paid payouts")
            
            filters = {"_id": ObjectId(payout_id)}
            success = await self._delete_document(
                filters=filters,
                organization_id=hostname,
                soft_delete=True
            )
            
            if success:
                # Log audit event
                await self._log_audit_event({
                    "payout_id": payout_id,
                    "action": "delete",
                    "deleted_by": deleted_by,
                    "timestamp": datetime.utcnow()
                }, hostname)
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting payout {payout_id}: {e}")
            return False
    
    # Query Repository Implementation
    async def get_by_id(self, payout_id: str, hostname: str) -> Optional[PayoutInDB]:
        """
        Get payout by ID.
        
        Replaces: PayoutDatabase.get_payout_by_id()
        """
        try:
            filters = {"_id": ObjectId(payout_id)}
            documents = await self._execute_query(
                filters=filters,
                limit=1,
                organization_id=hostname
            )
            
            if documents:
                return self._document_to_entity(documents[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving payout {payout_id}: {e}")
            return None
    
    async def get_employee_payouts(self, employee_id: str, hostname: str,
                                  year: Optional[int] = None,
                                  month: Optional[int] = None) -> List[PayoutInDB]:
        """
        Get payouts for a specific employee.
        
        Replaces: PayoutDatabase.get_employee_payouts()
        """
        try:
            filters = {"employee_id": employee_id}
            
            if year:
                start_date = datetime.combine(date(year, 1, 1), datetime.min.time())
                end_date = datetime.combine(date(year, 12, 31), datetime.min.time())
                filters["pay_period_start"] = {"$gte": start_date, "$lte": end_date}
            
            if month and year:
                start_date = datetime.combine(date(year, month, 1), datetime.min.time())
                if month == 12:
                    end_date = datetime.combine(date(year + 1, 1, 1) - timedelta(days=1), datetime.min.time())
                else:
                    end_date = datetime.combine(date(year, month + 1, 1) - timedelta(days=1), datetime.min.time())
                filters["pay_period_start"] = {"$gte": start_date, "$lte": end_date}
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="pay_period_start",
                sort_order=-1,
                limit=12,
                organization_id=hostname
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving employee payouts: {e}")
            return []
    
    async def get_monthly_payouts(self, month: int, year: int, hostname: str,
                                 status: Optional[PayoutStatus] = None) -> List[PayoutInDB]:
        """
        Get all payouts for a specific month.
        
        Replaces: PayoutDatabase.get_monthly_payouts()
        """
        try:
            start_date = datetime.combine(date(year, month, 1), datetime.min.time())
            if month == 12:
                end_date = datetime.combine(date(year + 1, 1, 1) - timedelta(days=1), datetime.min.time())
            else:
                end_date = datetime.combine(date(year, month + 1, 1) - timedelta(days=1), datetime.min.time())
            
            filters = {
                "pay_period_start": {"$gte": start_date, "$lte": end_date}
            }
            
            if status:
                status_value = status.value if hasattr(status, 'value') else str(status)
                filters["status"] = status_value
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="employee_id",
                sort_order=1,
                limit=1000,  # Large limit for monthly data
                organization_id=hostname
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving monthly payouts: {e}")
            return []
    
    async def search_payouts(self, filters: PayoutSearchFiltersDTO,
                           hostname: str) -> Dict[str, Any]:
        """
        Search payouts with filters and pagination.
        
        Provides advanced search not available in original procedural code.
        """
        try:
            # Build query filters
            query_filters = {}
            
            if hasattr(filters, 'employee_id') and filters.employee_id:
                query_filters["employee_id"] = filters.employee_id
            
            if hasattr(filters, 'status') and filters.status:
                query_filters["status"] = filters.status
            
            if hasattr(filters, 'start_date') and filters.start_date:
                query_filters["pay_period_start"] = {"$gte": filters.start_date}
            
            if hasattr(filters, 'end_date') and filters.end_date:
                if "pay_period_start" in query_filters:
                    query_filters["pay_period_start"]["$lte"] = filters.end_date
                else:
                    query_filters["pay_period_start"] = {"$lte": filters.end_date}
            
            # Get pagination parameters
            page = getattr(filters, 'page', 1)
            page_size = getattr(filters, 'page_size', 50)
            skip = (page - 1) * page_size
            
            # Execute query
            documents = await self._execute_query(
                filters=query_filters,
                skip=skip,
                limit=page_size,
                sort_by="pay_period_start",
                sort_order=-1,
                organization_id=hostname
            )
            
            # Get total count
            total_count = await self._count_documents(query_filters, hostname)
            
            payouts = [self._document_to_entity(doc) for doc in documents]
            
            return {
                "payouts": payouts,
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size
            }
            
        except Exception as e:
            logger.error(f"Error searching payouts: {e}")
            return {
                "payouts": [],
                "total_count": 0,
                "page": 1,
                "page_size": 50,
                "total_pages": 0
            }
    
    async def check_duplicate_payout(self, employee_id: str, pay_period_start: date,
                                   pay_period_end: date, hostname: str) -> bool:
        """
        Check if payout already exists for the period.
        
        Replaces: PayoutDatabase.check_duplicate_payout()
        """
        try:
            # Convert dates to datetime for MongoDB query
            start_datetime = datetime.combine(pay_period_start, datetime.min.time())
            end_datetime = datetime.combine(pay_period_end, datetime.min.time())
            
            filters = {
                "employee_id": employee_id,
                "pay_period_start": start_datetime,
                "pay_period_end": end_datetime
            }
            
            count = await self._count_documents(filters, hostname)
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking duplicate payout: {e}")
            return False
    
    async def get_payout_summary(self, month: int, year: int, 
                                hostname: str) -> Dict[str, Any]:
        """
        Get payout summary for a month.
        
        Replaces: PayoutDatabase.get_payout_summary()
        """
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
            
            results = await self._aggregate(pipeline, hostname)
            
            if results:
                summary_data = results[0]
                return {
                    "month": f"{year}-{month:02d}",
                    "year": year,
                    "total_employees": summary_data.get("total_employees", 0),
                    "total_gross_amount": summary_data.get("total_gross_amount", 0.0),
                    "total_net_amount": summary_data.get("total_net_amount", 0.0),
                    "total_tax_deducted": summary_data.get("total_tax_deducted", 0.0),
                    "pending_payouts": summary_data.get("pending_payouts", 0),
                    "processed_payouts": summary_data.get("processed_payouts", 0),
                    "approved_payouts": summary_data.get("approved_payouts", 0),
                    "paid_payouts": summary_data.get("paid_payouts", 0)
                }
            else:
                return {
                    "month": f"{year}-{month:02d}",
                    "year": year,
                    "total_employees": 0,
                    "total_gross_amount": 0.0,
                    "total_net_amount": 0.0,
                    "total_tax_deducted": 0.0,
                    "pending_payouts": 0,
                    "processed_payouts": 0,
                    "approved_payouts": 0,
                    "paid_payouts": 0
                }
                
        except Exception as e:
            logger.error(f"Error getting payout summary: {e}")
            return {
                "month": f"{year}-{month:02d}",
                "year": year,
                "total_employees": 0,
                "total_gross_amount": 0.0,
                "total_net_amount": 0.0,
                "total_tax_deducted": 0.0,
                "pending_payouts": 0,
                "processed_payouts": 0,
                "approved_payouts": 0,
                "paid_payouts": 0
            }
    
    async def get_employee_payout_history(self, employee_id: str, year: int,
                                        hostname: str) -> Dict[str, Any]:
        """
        Get annual payout history for an employee.
        
        Replaces: PayoutDatabase.get_employee_payout_history()
        """
        try:
            payouts = await self.get_employee_payouts(employee_id, hostname, year=year)
            
            annual_gross = sum(getattr(payout, 'gross_salary', 0) for payout in payouts)
            annual_net = sum(getattr(payout, 'net_salary', 0) for payout in payouts)
            annual_tax_deducted = sum(getattr(payout, 'tds', 0) for payout in payouts)
            
            return {
                "employee_id": employee_id,
                "year": year,
                "payouts": payouts,
                "annual_gross": annual_gross,
                "annual_net": annual_net,
                "annual_tax_deducted": annual_tax_deducted
            }
            
        except Exception as e:
            logger.error(f"Error retrieving payout history: {e}")
            return {
                "employee_id": employee_id,
                "year": year,
                "payouts": [],
                "annual_gross": 0.0,
                "annual_net": 0.0,
                "annual_tax_deducted": 0.0
            }
    
    async def get_payouts_by_status(self, status: PayoutStatus, hostname: str,
                                   limit: Optional[int] = None) -> List[PayoutInDB]:
        """Get payouts by status."""
        try:
            status_value = status.value if hasattr(status, 'value') else str(status)
            filters = {"status": status_value}
            
            documents = await self._execute_query(
                filters=filters,
                limit=limit or 100,
                sort_by="updated_at",
                sort_order=-1,
                organization_id=hostname
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting payouts by status: {e}")
            return []
    
    async def get_pending_approvals(self, hostname: str, 
                                   approver_id: Optional[str] = None) -> List[PayoutInDB]:
        """Get payouts pending approval."""
        try:
            filters = {"status": "processed"}  # Processed payouts need approval
            
            documents = await self._execute_query(
                filters=filters,
                limit=100,
                sort_by="processed_at",
                sort_order=1,  # Oldest first
                organization_id=hostname
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting pending approvals: {e}")
            return []
    
    # Analytics Repository Implementation
    async def get_department_wise_summary(self, month: int, year: int,
                                        hostname: str) -> Dict[str, Dict[str, float]]:
        """Get department-wise payout summary."""
        try:
            start_date = datetime.combine(date(year, month, 1), datetime.min.time())
            if month == 12:
                end_date = datetime.combine(date(year + 1, 1, 1) - timedelta(days=1), datetime.min.time())
            else:
                end_date = datetime.combine(date(year, month + 1, 1) - timedelta(days=1), datetime.min.time())
            
            # This would require joining with user data to get department
            # For now, return empty dict as it needs user repository integration
            logger.warning("Department-wise summary requires user data integration")
            return {}
            
        except Exception as e:
            logger.error(f"Error getting department-wise summary: {e}")
            return {}
    
    async def get_monthly_trends(self, start_month: int, start_year: int,
                               end_month: int, end_year: int,
                               hostname: str) -> List[Dict[str, Any]]:
        """Get monthly payout trends."""
        try:
            trends = []
            
            current_month = start_month
            current_year = start_year
            
            while (current_year < end_year) or (current_year == end_year and current_month <= end_month):
                summary = await self.get_payout_summary(current_month, current_year, hostname)
                trends.append(summary)
                
                current_month += 1
                if current_month > 12:
                    current_month = 1
                    current_year += 1
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting monthly trends: {e}")
            return []
    
    async def get_salary_distribution(self, month: int, year: int,
                                    hostname: str) -> Dict[str, Any]:
        """Get salary distribution analysis."""
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
                        "min_salary": {"$min": "$net_salary"},
                        "max_salary": {"$max": "$net_salary"},
                        "avg_salary": {"$avg": "$net_salary"},
                        "median_salary": {"$avg": "$net_salary"},  # Simplified median
                        "total_employees": {"$sum": 1}
                    }
                }
            ]
            
            results = await self._aggregate(pipeline, hostname)
            
            if results:
                return results[0]
            else:
                return {
                    "min_salary": 0,
                    "max_salary": 0,
                    "avg_salary": 0,
                    "median_salary": 0,
                    "total_employees": 0
                }
                
        except Exception as e:
            logger.error(f"Error getting salary distribution: {e}")
            return {}
    
    async def get_top_earners(self, month: int, year: int, hostname: str,
                            limit: int = 10) -> List[Dict[str, Any]]:
        """Get top earners for a month."""
        try:
            start_date = datetime.combine(date(year, month, 1), datetime.min.time())
            if month == 12:
                end_date = datetime.combine(date(year + 1, 1, 1) - timedelta(days=1), datetime.min.time())
            else:
                end_date = datetime.combine(date(year, month + 1, 1) - timedelta(days=1), datetime.min.time())
            
            filters = {
                "pay_period_start": {"$gte": start_date, "$lte": end_date}
            }
            
            documents = await self._execute_query(
                filters=filters,
                limit=limit,
                sort_by="net_salary",
                sort_order=-1,  # Highest first
                organization_id=hostname
            )
            
            return [
                {
                    "employee_id": doc.get("employee_id"),
                    "net_salary": doc.get("net_salary", 0),
                    "gross_salary": doc.get("gross_salary", 0)
                }
                for doc in documents
            ]
            
        except Exception as e:
            logger.error(f"Error getting top earners: {e}")
            return []
    
    async def get_deduction_analysis(self, month: int, year: int,
                                   hostname: str) -> Dict[str, float]:
        """Get deduction analysis for a month."""
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
                        "total_epf": {"$sum": "$epf_employee"},
                        "total_esi": {"$sum": "$esi_employee"},
                        "total_tds": {"$sum": "$tds"},
                        "total_professional_tax": {"$sum": "$professional_tax"},
                        "total_other_deductions": {"$sum": "$other_deductions"}
                    }
                }
            ]
            
            results = await self._aggregate(pipeline, hostname)
            
            if results:
                return results[0]
            else:
                return {
                    "total_epf": 0.0,
                    "total_esi": 0.0,
                    "total_tds": 0.0,
                    "total_professional_tax": 0.0,
                    "total_other_deductions": 0.0
                }
                
        except Exception as e:
            logger.error(f"Error getting deduction analysis: {e}")
            return {}
    
    async def get_compliance_metrics(self, month: int, year: int,
                                   hostname: str) -> Dict[str, Any]:
        """Get compliance metrics for a month."""
        try:
            summary = await self.get_payout_summary(month, year, hostname)
            deductions = await self.get_deduction_analysis(month, year, hostname)
            
            return {
                "total_employees": summary.get("total_employees", 0),
                "payouts_processed": summary.get("processed_payouts", 0),
                "payouts_approved": summary.get("approved_payouts", 0),
                "payouts_paid": summary.get("paid_payouts", 0),
                "compliance_rate": (
                    summary.get("paid_payouts", 0) / max(summary.get("total_employees", 1), 1) * 100
                ),
                "total_statutory_deductions": (
                    deductions.get("total_epf", 0) + 
                    deductions.get("total_esi", 0) + 
                    deductions.get("total_professional_tax", 0)
                ),
                "total_tax_deducted": deductions.get("total_tds", 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting compliance metrics: {e}")
            return {}
    
    # Schedule Repository Implementation
    async def create_schedule(self, schedule_data: Dict[str, Any],
                            hostname: str, created_by: str) -> str:
        """Create or update payout schedule."""
        try:
            schedule_data["created_by"] = created_by
            schedule_data["created_at"] = datetime.utcnow()
            schedule_data["updated_at"] = datetime.utcnow()
            
            collection = self._get_schedule_collection(hostname)
            
            # Upsert schedule
            result = await collection.update_one(
                {"month": schedule_data["month"], "year": schedule_data["year"]},
                {"$set": schedule_data},
                upsert=True
            )
            
            if result.upserted_id:
                return str(result.upserted_id)
            else:
                # Find existing document
                existing = await collection.find_one({
                    "month": schedule_data["month"], 
                    "year": schedule_data["year"]
                })
                return str(existing["_id"]) if existing else ""
                
        except Exception as e:
            logger.error(f"Error creating payout schedule: {e}")
            raise
    
    async def get_schedule(self, month: int, year: int,
                         hostname: str) -> Optional[Dict[str, Any]]:
        """Get payout schedule for a month."""
        try:
            collection = self._get_schedule_collection(hostname)
            schedule = await collection.find_one({"month": month, "year": year})
            
            if schedule:
                schedule["id"] = str(schedule["_id"])
                del schedule["_id"]
                return schedule
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving payout schedule: {e}")
            return None
    
    async def update_schedule(self, schedule_id: str, update_data: Dict[str, Any],
                            hostname: str, updated_by: str) -> bool:
        """Update payout schedule."""
        try:
            update_data["updated_by"] = updated_by
            update_data["updated_at"] = datetime.utcnow()
            
            collection = self._get_schedule_collection(hostname)
            result = await collection.update_one(
                {"_id": ObjectId(schedule_id)},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating payout schedule: {e}")
            return False
    
    async def get_active_schedules(self, hostname: str) -> List[Dict[str, Any]]:
        """Get all active payout schedules."""
        try:
            collection = self._get_schedule_collection(hostname)
            cursor = collection.find({"is_active": True})
            schedules = await cursor.to_list(length=None)
            
            result = []
            for schedule in schedules:
                schedule["id"] = str(schedule["_id"])
                del schedule["_id"]
                result.append(schedule)
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving active schedules: {e}")
            return []
    
    # Audit Repository Implementation
    async def log_audit_event(self, event_data: Dict[str, Any],
                            hostname: str) -> str:
        """Log audit event."""
        return await self._log_audit_event(event_data, hostname)
    
    async def _log_audit_event(self, event_data: Dict[str, Any],
                             hostname: str) -> str:
        """Internal method to log audit events."""
        try:
            event_data["timestamp"] = datetime.utcnow()
            
            collection = self._get_audit_collection(hostname)
            result = await collection.insert_one(event_data)
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
            return ""
    
    async def get_payout_audit_trail(self, payout_id: str,
                                   hostname: str) -> List[Dict[str, Any]]:
        """Get audit trail for a payout."""
        try:
            collection = self._get_audit_collection(hostname)
            cursor = collection.find({"payout_id": payout_id}).sort("timestamp", -1)
            events = await cursor.to_list(length=None)
            
            for event in events:
                event["id"] = str(event["_id"])
                del event["_id"]
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting payout audit trail: {e}")
            return []
    
    async def get_user_audit_trail(self, employee_id: str, hostname: str,
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get audit trail for a user."""
        try:
            filters = {
                "$or": [
                    {"updated_by": employee_id},
                    {"created_by": employee_id},
                    {"processed_by": employee_id},
                    {"approved_by": employee_id}
                ]
            }
            
            if start_date:
                filters["timestamp"] = {"$gte": start_date}
            
            if end_date:
                if "timestamp" in filters:
                    filters["timestamp"]["$lte"] = end_date
                else:
                    filters["timestamp"] = {"$lte": end_date}
            
            collection = self._get_audit_collection(hostname)
            cursor = collection.find(filters).sort("timestamp", -1).limit(100)
            events = await cursor.to_list(length=None)
            
            for event in events:
                event["id"] = str(event["_id"])
                del event["_id"]
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting user audit trail: {e}")
            return [] 