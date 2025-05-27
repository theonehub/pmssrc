"""
Employee Leave Repository Implementation
MongoDB implementation of employee leave repositories following SOLID principles
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId

from application.interfaces.repositories.employee_leave_repository import (
    EmployeeLeaveCommandRepository,
    EmployeeLeaveQueryRepository,
    EmployeeLeaveAnalyticsRepository,
    EmployeeLeaveBalanceRepository
)
from domain.entities.employee_leave import EmployeeLeave
from domain.value_objects.employee_id import EmployeeId
from domain.value_objects.leave_type import LeaveType, LeaveCategory
from domain.value_objects.date_range import DateRange
from models.leave_model import LeaveStatus
from database.database_connector import connect_to_database
from infrastructure.services.legacy_migration_service import (
    get_user_by_emp_id, get_users_by_manager_id, is_public_holiday_sync
)
from services.attendance_service import get_employee_attendance_by_month


class EmployeeLeaveCommandRepositoryImpl(EmployeeLeaveCommandRepository):
    """
    MongoDB implementation of employee leave command repository.
    
    Follows SOLID principles:
    - SRP: Only handles write operations for employee leaves
    - OCP: Can be extended with new write operations
    - LSP: Can be substituted with other command repositories
    - ISP: Implements only command operations interface
    - DIP: Depends on database abstraction
    """
    
    def __init__(self, database_connector):
        self._database_connector = database_connector
        self._logger = logging.getLogger(__name__)
    
    def _get_collection(self, hostname: str) -> Collection:
        """Get employee leave collection for hostname"""
        db = connect_to_database(hostname)
        return db["employee_leave"]
    
    def save(self, employee_leave: EmployeeLeave) -> bool:
        """Save employee leave application"""
        try:
            # For now, use default hostname - this will be improved with proper hostname handling
            hostname = "default"
            collection = self._get_collection(hostname)
            
            # Convert entity to document
            document = self._entity_to_document(employee_leave)
            
            # Insert document
            result = collection.insert_one(document)
            
            if result.inserted_id:
                self._logger.info(f"Saved employee leave: {employee_leave.leave_id}")
                return True
            
            return False
            
        except Exception as e:
            self._logger.error(f"Error saving employee leave: {e}")
            return False
    
    def update(self, employee_leave: EmployeeLeave) -> bool:
        """Update existing employee leave application"""
        try:
            hostname = "default"
            collection = self._get_collection(hostname)
            
            # Convert entity to document
            document = self._entity_to_document(employee_leave)
            document["updated_at"] = datetime.utcnow()
            
            # Update document
            result = collection.update_one(
                {"leave_id": employee_leave.leave_id},
                {"$set": document}
            )
            
            if result.modified_count > 0:
                self._logger.info(f"Updated employee leave: {employee_leave.leave_id}")
                return True
            
            return False
            
        except Exception as e:
            self._logger.error(f"Error updating employee leave: {e}")
            return False
    
    def delete(self, leave_id: str) -> bool:
        """Delete employee leave application"""
        try:
            hostname = "default"
            collection = self._get_collection(hostname)
            
            result = collection.delete_one({"leave_id": leave_id})
            
            if result.deleted_count > 0:
                self._logger.info(f"Deleted employee leave: {leave_id}")
                return True
            
            return False
            
        except Exception as e:
            self._logger.error(f"Error deleting employee leave: {e}")
            return False
    
    def update_status(
        self, 
        leave_id: str, 
        status: LeaveStatus, 
        approved_by: str,
        comments: Optional[str] = None
    ) -> bool:
        """Update leave application status"""
        try:
            hostname = "default"
            collection = self._get_collection(hostname)
            
            update_data = {
                "status": status.value,
                "approved_by": approved_by,
                "approved_date": datetime.now().strftime("%Y-%m-%d"),
                "updated_at": datetime.utcnow()
            }
            
            if comments:
                update_data["approval_comments"] = comments
            
            result = collection.update_one(
                {"leave_id": leave_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                self._logger.info(f"Updated leave status: {leave_id} to {status}")
                return True
            
            return False
            
        except Exception as e:
            self._logger.error(f"Error updating leave status: {e}")
            return False
    
    def _entity_to_document(self, employee_leave: EmployeeLeave) -> Dict[str, Any]:
        """Convert EmployeeLeave entity to MongoDB document"""
        return {
            "leave_id": employee_leave.leave_id,
            "emp_id": str(employee_leave.employee_id),
            "emp_name": employee_leave.employee_name,
            "emp_email": employee_leave.employee_email,
            "leave_name": employee_leave.leave_type.code,
            "start_date": employee_leave.date_range.start_date.strftime("%Y-%m-%d"),
            "end_date": employee_leave.date_range.end_date.strftime("%Y-%m-%d"),
            "leave_count": employee_leave.working_days_count,
            "status": employee_leave.status.value,
            "applied_date": employee_leave.applied_date.strftime("%Y-%m-%d"),
            "approved_by": employee_leave.approved_by,
            "approved_date": employee_leave.approved_date.strftime("%Y-%m-%d") if employee_leave.approved_date else None,
            "reason": employee_leave.reason,
            "approval_comments": employee_leave.approval_comments,
            "created_at": employee_leave.created_at,
            "updated_at": employee_leave.updated_at,
            "created_by": employee_leave.created_by,
            "updated_by": employee_leave.updated_by
        }


class EmployeeLeaveQueryRepositoryImpl(EmployeeLeaveQueryRepository):
    """
    MongoDB implementation of employee leave query repository.
    """
    
    def __init__(self, database_connector):
        self._database_connector = database_connector
        self._logger = logging.getLogger(__name__)
    
    def _get_collection(self, hostname: str) -> Collection:
        """Get employee leave collection for hostname"""
        db = connect_to_database(hostname)
        return db["employee_leave"]
    
    def get_by_id(self, leave_id: str) -> Optional[EmployeeLeave]:
        """Get employee leave by ID"""
        try:
            hostname = "default"
            collection = self._get_collection(hostname)
            document = collection.find_one({"leave_id": leave_id})
            
            if document:
                return self._document_to_entity(document)
            
            return None
            
        except Exception as e:
            self._logger.error(f"Error retrieving employee leave by ID: {e}")
            return None
    
    def get_by_employee_id(
        self, 
        employee_id: EmployeeId,
        status_filter: Optional[LeaveStatus] = None,
        limit: Optional[int] = None,
        hostname: str = "default"
    ) -> List[EmployeeLeave]:
        """Get employee leaves by employee ID"""
        try:
            collection = self._get_collection(hostname)
            
            query = {"emp_id": str(employee_id)}
            if status_filter:
                query["status"] = status_filter.value
            
            cursor = collection.find(query).sort("applied_date", DESCENDING)
            
            if limit:
                cursor = cursor.limit(limit)
            
            documents = list(cursor)
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            self._logger.error(f"Error retrieving leaves for employee: {e}")
            return []
    
    def get_by_manager_id(
        self, 
        manager_id: str,
        status_filter: Optional[LeaveStatus] = None,
        limit: Optional[int] = None,
        hostname: str = "default"
    ) -> List[EmployeeLeave]:
        """Get employee leaves by manager ID"""
        try:
            # Get employees under this manager
            users = get_users_by_manager_id(manager_id, hostname)
            emp_ids = [user["emp_id"] for user in users]
            
            if not emp_ids:
                return []
            
            collection = self._get_collection(hostname)
            
            query = {"emp_id": {"$in": emp_ids}}
            if status_filter:
                query["status"] = status_filter.value
            
            cursor = collection.find(query).sort("applied_date", DESCENDING)
            
            if limit:
                cursor = cursor.limit(limit)
            
            documents = list(cursor)
            leaves = [self._document_to_entity(doc) for doc in documents]
            
            # Add employee details
            user_map = {user["emp_id"]: user for user in users}
            for leave in leaves:
                user = user_map.get(str(leave.employee_id))
                if user:
                    leave.employee_name = user.get("name")
                    leave.employee_email = user.get("email")
            
            return leaves
            
        except Exception as e:
            self._logger.error(f"Error retrieving leaves for manager: {e}")
            return []
    
    def get_by_date_range(
        self, 
        date_range: DateRange,
        employee_id: Optional[EmployeeId] = None,
        status_filter: Optional[LeaveStatus] = None,
        hostname: str = "default"
    ) -> List[EmployeeLeave]:
        """Get employee leaves by date range"""
        try:
            collection = self._get_collection(hostname)
            
            start_str = date_range.start_date.strftime("%Y-%m-%d")
            end_str = date_range.end_date.strftime("%Y-%m-%d")
            
            query = {
                "$or": [
                    {"start_date": {"$gte": start_str, "$lte": end_str}},
                    {"end_date": {"$gte": start_str, "$lte": end_str}},
                    {"$and": [
                        {"start_date": {"$lt": start_str}},
                        {"end_date": {"$gt": end_str}}
                    ]}
                ]
            }
            
            if employee_id:
                query["emp_id"] = str(employee_id)
            
            if status_filter:
                query["status"] = status_filter.value
            
            documents = list(collection.find(query).sort("start_date", ASCENDING))
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            self._logger.error(f"Error retrieving leaves by date range: {e}")
            return []
    
    def get_by_month(
        self, 
        employee_id: EmployeeId,
        month: int,
        year: int,
        hostname: str = "default"
    ) -> List[EmployeeLeave]:
        """Get employee leaves for a specific month"""
        try:
            collection = self._get_collection(hostname)
            
            # Calculate month boundaries
            month_start = date(year, month, 1)
            if month == 12:
                month_end = date(year + 1, 1, 1) - datetime.timedelta(days=1)
            else:
                month_end = date(year, month + 1, 1) - datetime.timedelta(days=1)
            
            month_start_str = month_start.strftime("%Y-%m-%d")
            month_end_str = month_end.strftime("%Y-%m-%d")
            
            query = {
                "emp_id": str(employee_id),
                "$or": [
                    {"start_date": {"$gte": month_start_str, "$lte": month_end_str}},
                    {"end_date": {"$gte": month_start_str, "$lte": month_end_str}},
                    {"$and": [
                        {"start_date": {"$lt": month_start_str}},
                        {"end_date": {"$gt": month_end_str}}
                    ]}
                ]
            }
            
            documents = list(collection.find(query).sort("start_date", ASCENDING))
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            self._logger.error(f"Error retrieving monthly leaves: {e}")
            return []
    
    def get_overlapping_leaves(
        self, 
        employee_id: EmployeeId,
        date_range: DateRange,
        exclude_leave_id: Optional[str] = None,
        hostname: str = "default"
    ) -> List[EmployeeLeave]:
        """Get leaves that overlap with the given date range"""
        try:
            collection = self._get_collection(hostname)
            
            start_str = date_range.start_date.strftime("%Y-%m-%d")
            end_str = date_range.end_date.strftime("%Y-%m-%d")
            
            query = {
                "emp_id": str(employee_id),
                "status": {"$in": [LeaveStatus.PENDING.value, LeaveStatus.APPROVED.value]},
                "$or": [
                    {"start_date": {"$gte": start_str, "$lte": end_str}},
                    {"end_date": {"$gte": start_str, "$lte": end_str}},
                    {"$and": [
                        {"start_date": {"$lt": start_str}},
                        {"end_date": {"$gt": end_str}}
                    ]}
                ]
            }
            
            if exclude_leave_id:
                query["leave_id"] = {"$ne": exclude_leave_id}
            
            documents = list(collection.find(query))
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            self._logger.error(f"Error retrieving overlapping leaves: {e}")
            return []
    
    def get_pending_approvals(
        self, 
        manager_id: Optional[str] = None,
        limit: Optional[int] = None,
        hostname: str = "default"
    ) -> List[EmployeeLeave]:
        """Get pending leave approvals"""
        try:
            collection = self._get_collection(hostname)
            
            query = {"status": LeaveStatus.PENDING.value}
            
            if manager_id:
                # Get employees under this manager
                users = get_users_by_manager_id(manager_id, hostname)
                emp_ids = [user["emp_id"] for user in users]
                if emp_ids:
                    query["emp_id"] = {"$in": emp_ids}
                else:
                    return []
            
            cursor = collection.find(query).sort("applied_date", ASCENDING)
            
            if limit:
                cursor = cursor.limit(limit)
            
            documents = list(cursor)
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            self._logger.error(f"Error retrieving pending approvals: {e}")
            return []
    
    def search(
        self,
        employee_id: Optional[EmployeeId] = None,
        manager_id: Optional[str] = None,
        leave_type: Optional[str] = None,
        status: Optional[LeaveStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
        hostname: str = "default"
    ) -> List[EmployeeLeave]:
        """Search employee leaves with filters"""
        try:
            collection = self._get_collection(hostname)
            
            query = {}
            
            # Employee filter
            if employee_id:
                query["emp_id"] = str(employee_id)
            
            # Manager filter
            if manager_id:
                users = get_users_by_manager_id(manager_id, hostname)
                emp_ids = [user["emp_id"] for user in users]
                if emp_ids:
                    query["emp_id"] = {"$in": emp_ids}
                else:
                    return []
            
            # Leave type filter
            if leave_type:
                query["leave_name"] = leave_type
            
            # Status filter
            if status:
                query["status"] = status.value
            
            # Date range filter
            if start_date and end_date:
                start_str = start_date.strftime("%Y-%m-%d")
                end_str = end_date.strftime("%Y-%m-%d")
                query["$or"] = [
                    {"start_date": {"$gte": start_str, "$lte": end_str}},
                    {"end_date": {"$gte": start_str, "$lte": end_str}},
                    {"$and": [
                        {"start_date": {"$lt": start_str}},
                        {"end_date": {"$gt": end_str}}
                    ]}
                ]
            
            # Month/year filter
            if month and year:
                month_start = date(year, month, 1)
                if month == 12:
                    month_end = date(year + 1, 1, 1) - datetime.timedelta(days=1)
                else:
                    month_end = date(year, month + 1, 1) - datetime.timedelta(days=1)
                
                month_start_str = month_start.strftime("%Y-%m-%d")
                month_end_str = month_end.strftime("%Y-%m-%d")
                
                query["$or"] = [
                    {"start_date": {"$gte": month_start_str, "$lte": month_end_str}},
                    {"end_date": {"$gte": month_start_str, "$lte": month_end_str}},
                    {"$and": [
                        {"start_date": {"$lt": month_start_str}},
                        {"end_date": {"$gt": month_end_str}}
                    ]}
                ]
            
            cursor = collection.find(query).sort("applied_date", DESCENDING).skip(skip).limit(limit)
            documents = list(cursor)
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            self._logger.error(f"Error searching employee leaves: {e}")
            return []
    
    def count_by_filters(
        self,
        employee_id: Optional[EmployeeId] = None,
        manager_id: Optional[str] = None,
        leave_type: Optional[str] = None,
        status: Optional[LeaveStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        hostname: str = "default"
    ) -> int:
        """Count employee leaves matching filters"""
        try:
            collection = self._get_collection(hostname)
            
            query = {}
            
            # Apply same filters as search method
            if employee_id:
                query["emp_id"] = str(employee_id)
            
            if manager_id:
                users = get_users_by_manager_id(manager_id, hostname)
                emp_ids = [user["emp_id"] for user in users]
                if emp_ids:
                    query["emp_id"] = {"$in": emp_ids}
                else:
                    return 0
            
            if leave_type:
                query["leave_name"] = leave_type
            
            if status:
                query["status"] = status.value
            
            if start_date and end_date:
                start_str = start_date.strftime("%Y-%m-%d")
                end_str = end_date.strftime("%Y-%m-%d")
                query["$or"] = [
                    {"start_date": {"$gte": start_str, "$lte": end_str}},
                    {"end_date": {"$gte": start_str, "$lte": end_str}},
                    {"$and": [
                        {"start_date": {"$lt": start_str}},
                        {"end_date": {"$gt": end_str}}
                    ]}
                ]
            
            if month and year:
                month_start = date(year, month, 1)
                if month == 12:
                    month_end = date(year + 1, 1, 1) - datetime.timedelta(days=1)
                else:
                    month_end = date(year, month + 1, 1) - datetime.timedelta(days=1)
                
                month_start_str = month_start.strftime("%Y-%m-%d")
                month_end_str = month_end.strftime("%Y-%m-%d")
                
                query["$or"] = [
                    {"start_date": {"$gte": month_start_str, "$lte": month_end_str}},
                    {"end_date": {"$gte": month_start_str, "$lte": month_end_str}},
                    {"$and": [
                        {"start_date": {"$lt": month_start_str}},
                        {"end_date": {"$gt": month_end_str}}
                    ]}
                ]
            
            return collection.count_documents(query)
            
        except Exception as e:
            self._logger.error(f"Error counting employee leaves: {e}")
            return 0
    
    def _document_to_entity(self, document: Dict[str, Any]) -> EmployeeLeave:
        """Convert MongoDB document to EmployeeLeave entity"""
        try:
            # Create value objects
            employee_id = EmployeeId(document["emp_id"])
            
            leave_type = LeaveType(
                code=document["leave_name"],
                name=document["leave_name"],
                category=LeaveCategory.GENERAL,
                description=f"{document['leave_name']} leave"
            )
            
            start_date = datetime.strptime(document["start_date"], "%Y-%m-%d").date()
            end_date = datetime.strptime(document["end_date"], "%Y-%m-%d").date()
            date_range = DateRange(start_date=start_date, end_date=end_date)
            
            applied_date = datetime.strptime(document["applied_date"], "%Y-%m-%d").date()
            approved_date = None
            if document.get("approved_date"):
                approved_date = datetime.strptime(document["approved_date"], "%Y-%m-%d").date()
            
            # Create entity
            return EmployeeLeave(
                leave_id=document["leave_id"],
                employee_id=employee_id,
                leave_type=leave_type,
                date_range=date_range,
                working_days_count=document["leave_count"],
                reason=document.get("reason"),
                status=LeaveStatus(document["status"]),
                applied_date=applied_date,
                approved_by=document.get("approved_by"),
                approved_date=approved_date,
                approval_comments=document.get("approval_comments"),
                employee_name=document.get("emp_name"),
                employee_email=document.get("emp_email"),
                created_at=document.get("created_at", datetime.utcnow()),
                updated_at=document.get("updated_at", datetime.utcnow()),
                created_by=document.get("created_by"),
                updated_by=document.get("updated_by")
            )
            
        except Exception as e:
            self._logger.error(f"Error converting document to entity: {e}")
            raise


class EmployeeLeaveAnalyticsRepositoryImpl(EmployeeLeaveAnalyticsRepository):
    """
    MongoDB implementation of employee leave analytics repository.
    """
    
    def __init__(self, database_connector):
        self._database_connector = database_connector
        self._logger = logging.getLogger(__name__)
    
    def _get_collection(self, hostname: str) -> Collection:
        """Get employee leave collection for hostname"""
        db = connect_to_database(hostname)
        return db["employee_leave"]
    
    def get_leave_statistics(
        self,
        employee_id: Optional[EmployeeId] = None,
        manager_id: Optional[str] = None,
        year: Optional[int] = None,
        hostname: str = "default"
    ) -> Dict[str, Any]:
        """Get leave statistics"""
        try:
            collection = self._get_collection(hostname)
            
            # Build match query
            match_query = {}
            
            if employee_id:
                match_query["emp_id"] = str(employee_id)
            
            if manager_id:
                users = get_users_by_manager_id(manager_id, hostname)
                emp_ids = [user["emp_id"] for user in users]
                if emp_ids:
                    match_query["emp_id"] = {"$in": emp_ids}
                else:
                    return self._empty_statistics()
            
            if year:
                match_query["applied_date"] = {
                    "$gte": f"{year}-01-01",
                    "$lte": f"{year}-12-31"
                }
            
            # Aggregation pipeline
            pipeline = [
                {"$match": match_query},
                {
                    "$group": {
                        "_id": None,
                        "total_applications": {"$sum": 1},
                        "approved_applications": {
                            "$sum": {"$cond": [{"$eq": ["$status", "APPROVED"]}, 1, 0]}
                        },
                        "rejected_applications": {
                            "$sum": {"$cond": [{"$eq": ["$status", "REJECTED"]}, 1, 0]}
                        },
                        "pending_applications": {
                            "$sum": {"$cond": [{"$eq": ["$status", "PENDING"]}, 1, 0]}
                        },
                        "total_days_taken": {
                            "$sum": {"$cond": [{"$eq": ["$status", "APPROVED"]}, "$leave_count", 0]}
                        }
                    }
                }
            ]
            
            results = list(collection.aggregate(pipeline))
            
            if results:
                stats = results[0]
                return {
                    "total_applications": stats.get("total_applications", 0),
                    "approved_applications": stats.get("approved_applications", 0),
                    "rejected_applications": stats.get("rejected_applications", 0),
                    "pending_applications": stats.get("pending_applications", 0),
                    "total_days_taken": stats.get("total_days_taken", 0)
                }
            
            return self._empty_statistics()
            
        except Exception as e:
            self._logger.error(f"Error getting leave statistics: {e}")
            return self._empty_statistics()
    
    def get_leave_type_breakdown(
        self,
        employee_id: Optional[EmployeeId] = None,
        manager_id: Optional[str] = None,
        year: Optional[int] = None,
        hostname: str = "default"
    ) -> Dict[str, int]:
        """Get leave type breakdown"""
        try:
            collection = self._get_collection(hostname)
            
            # Build match query
            match_query = {}
            
            if employee_id:
                match_query["emp_id"] = str(employee_id)
            
            if manager_id:
                users = get_users_by_manager_id(manager_id, hostname)
                emp_ids = [user["emp_id"] for user in users]
                if emp_ids:
                    match_query["emp_id"] = {"$in": emp_ids}
                else:
                    return {}
            
            if year:
                match_query["applied_date"] = {
                    "$gte": f"{year}-01-01",
                    "$lte": f"{year}-12-31"
                }
            
            # Aggregation pipeline
            pipeline = [
                {"$match": match_query},
                {
                    "$group": {
                        "_id": "$leave_name",
                        "count": {"$sum": 1},
                        "total_days": {
                            "$sum": {"$cond": [{"$eq": ["$status", "APPROVED"]}, "$leave_count", 0]}
                        }
                    }
                }
            ]
            
            results = list(collection.aggregate(pipeline))
            
            return {result["_id"]: result["total_days"] for result in results}
            
        except Exception as e:
            self._logger.error(f"Error getting leave type breakdown: {e}")
            return {}
    
    def get_monthly_leave_trends(
        self,
        employee_id: Optional[EmployeeId] = None,
        manager_id: Optional[str] = None,
        year: Optional[int] = None,
        hostname: str = "default"
    ) -> Dict[str, int]:
        """Get monthly leave trends"""
        try:
            collection = self._get_collection(hostname)
            
            # Build match query
            match_query = {}
            
            if employee_id:
                match_query["emp_id"] = str(employee_id)
            
            if manager_id:
                users = get_users_by_manager_id(manager_id, hostname)
                emp_ids = [user["emp_id"] for user in users]
                if emp_ids:
                    match_query["emp_id"] = {"$in": emp_ids}
                else:
                    return {}
            
            if year:
                match_query["applied_date"] = {
                    "$gte": f"{year}-01-01",
                    "$lte": f"{year}-12-31"
                }
            
            # Aggregation pipeline
            pipeline = [
                {"$match": match_query},
                {
                    "$addFields": {
                        "month": {"$substr": ["$applied_date", 5, 2]}
                    }
                },
                {
                    "$group": {
                        "_id": "$month",
                        "count": {"$sum": 1},
                        "total_days": {
                            "$sum": {"$cond": [{"$eq": ["$status", "APPROVED"]}, "$leave_count", 0]}
                        }
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            results = list(collection.aggregate(pipeline))
            
            # Convert to month names
            month_names = {
                "01": "January", "02": "February", "03": "March", "04": "April",
                "05": "May", "06": "June", "07": "July", "08": "August",
                "09": "September", "10": "October", "11": "November", "12": "December"
            }
            
            return {
                month_names.get(result["_id"], result["_id"]): result["total_days"] 
                for result in results
            }
            
        except Exception as e:
            self._logger.error(f"Error getting monthly trends: {e}")
            return {}
    
    def get_team_leave_summary(
        self,
        manager_id: str,
        month: Optional[int] = None,
        year: Optional[int] = None,
        hostname: str = "default"
    ) -> List[Dict[str, Any]]:
        """Get team leave summary for a manager"""
        try:
            # Get team members
            users = get_users_by_manager_id(manager_id, hostname)
            if not users:
                return []
            
            collection = self._get_collection(hostname)
            
            # Build date filter
            date_filter = {}
            if month and year:
                month_start = date(year, month, 1)
                if month == 12:
                    month_end = date(year + 1, 1, 1) - datetime.timedelta(days=1)
                else:
                    month_end = date(year, month + 1, 1) - datetime.timedelta(days=1)
                
                month_start_str = month_start.strftime("%Y-%m-%d")
                month_end_str = month_end.strftime("%Y-%m-%d")
                
                date_filter = {
                    "$or": [
                        {"start_date": {"$gte": month_start_str, "$lte": month_end_str}},
                        {"end_date": {"$gte": month_start_str, "$lte": month_end_str}},
                        {"$and": [
                            {"start_date": {"$lt": month_start_str}},
                            {"end_date": {"$gt": month_end_str}}
                        ]}
                    ]
                }
            
            team_summary = []
            
            for user in users:
                emp_id = user["emp_id"]
                
                # Build query for this employee
                query = {"emp_id": emp_id}
                if date_filter:
                    query.update(date_filter)
                
                # Get leave statistics for this employee
                pipeline = [
                    {"$match": query},
                    {
                        "$group": {
                            "_id": None,
                            "total_leaves": {"$sum": 1},
                            "approved_leaves": {
                                "$sum": {"$cond": [{"$eq": ["$status", "APPROVED"]}, 1, 0]}
                            },
                            "pending_leaves": {
                                "$sum": {"$cond": [{"$eq": ["$status", "PENDING"]}, 1, 0]}
                            },
                            "total_days": {
                                "$sum": {"$cond": [{"$eq": ["$status", "APPROVED"]}, "$leave_count", 0]}
                            }
                        }
                    }
                ]
                
                results = list(collection.aggregate(pipeline))
                
                if results:
                    stats = results[0]
                    team_summary.append({
                        "employee_id": emp_id,
                        "employee_name": user.get("name", ""),
                        "employee_email": user.get("email", ""),
                        "total_leaves": stats.get("total_leaves", 0),
                        "approved_leaves": stats.get("approved_leaves", 0),
                        "pending_leaves": stats.get("pending_leaves", 0),
                        "total_days_taken": stats.get("total_days", 0)
                    })
                else:
                    team_summary.append({
                        "employee_id": emp_id,
                        "employee_name": user.get("name", ""),
                        "employee_email": user.get("email", ""),
                        "total_leaves": 0,
                        "approved_leaves": 0,
                        "pending_leaves": 0,
                        "total_days_taken": 0
                    })
            
            return team_summary
            
        except Exception as e:
            self._logger.error(f"Error getting team leave summary: {e}")
            return []
    
    def calculate_lwp_for_employee(
        self,
        employee_id: EmployeeId,
        month: int,
        year: int,
        hostname: str = "default"
    ) -> int:
        """Calculate Leave Without Pay (LWP) for an employee"""
        try:
            # Get month boundaries
            month_start = datetime(year, month, 1)
            if month == 12:
                month_end = datetime(year + 1, 1, 1) - datetime.timedelta(days=1)
            else:
                month_end = datetime(year, month + 1, 1) - datetime.timedelta(days=1)

            # Get attendance records for the month
            attendance_records = get_employee_attendance_by_month(str(employee_id), month, year, hostname)
            
            # Get leaves for the month
            leaves = self.get_by_month(employee_id, month, year, hostname)

            lwp_days = 0
            current_date = month_start

            while current_date <= month_end:
                current_date_obj = current_date.date()
                
                # Skip weekends and public holidays
                if self._is_weekend(current_date) or is_public_holiday_sync(current_date.strftime("%Y-%m-%d"), hostname):
                    current_date += datetime.timedelta(days=1)
                    continue

                # Check if present on this day
                is_present = any(
                    att.checkin_time.date() == current_date_obj
                    for att in attendance_records
                )

                if not is_present:
                    # Check if on approved leave
                    has_approved_leave = any(
                        leave.date_range.start_date <= current_date_obj <= leave.date_range.end_date and
                        leave.status == LeaveStatus.APPROVED
                        for leave in leaves
                    )

                    if not has_approved_leave:
                        # Check if day has pending or rejected leave
                        has_pending_rejected_leave = any(
                            leave.date_range.start_date <= current_date_obj <= leave.date_range.end_date and
                            leave.status in [LeaveStatus.PENDING, LeaveStatus.REJECTED]
                            for leave in leaves
                        )

                        # Count as LWP if absent without approved leave
                        if not has_approved_leave or has_pending_rejected_leave:
                            lwp_days += 1

                current_date += datetime.timedelta(days=1)

            return lwp_days
            
        except Exception as e:
            self._logger.error(f"Error calculating LWP: {e}")
            return 0
    
    def _is_weekend(self, date_obj: datetime) -> bool:
        """Check if a date is a weekend (Saturday or Sunday)"""
        return date_obj.weekday() >= 5  # 5 is Saturday, 6 is Sunday
    
    def _empty_statistics(self) -> Dict[str, Any]:
        """Return empty statistics"""
        return {
            "total_applications": 0,
            "approved_applications": 0,
            "rejected_applications": 0,
            "pending_applications": 0,
            "total_days_taken": 0
        }


class EmployeeLeaveBalanceRepositoryImpl(EmployeeLeaveBalanceRepository):
    """
    MongoDB implementation of employee leave balance repository.
    """
    
    def __init__(self, database_connector):
        self._database_connector = database_connector
        self._logger = logging.getLogger(__name__)
    
    def _get_user_collection(self, hostname: str) -> Collection:
        """Get user collection for hostname"""
        db = connect_to_database(hostname)
        return db["users"]
    
    def get_leave_balance(self, employee_id: EmployeeId, hostname: str = "default") -> Dict[str, int]:
        """Get leave balance for an employee"""
        try:
            user = get_user_by_emp_id(str(employee_id), hostname)
            if user:
                return user.get("leave_balance", {})
            return {}
            
        except Exception as e:
            self._logger.error(f"Error getting leave balance: {e}")
            return {}
    
    def update_leave_balance(
        self, 
        employee_id: EmployeeId, 
        leave_type: str, 
        balance_change: int,
        hostname: str = "default"
    ) -> bool:
        """Update leave balance for an employee"""
        try:
            collection = self._get_user_collection(hostname)
            
            result = collection.update_one(
                {"emp_id": str(employee_id)},
                {"$inc": {f"leave_balance.{leave_type}": balance_change}}
            )
            
            if result.modified_count > 0:
                self._logger.info(f"Updated leave balance for {employee_id}: {leave_type} by {balance_change}")
                return True
            
            return False
            
        except Exception as e:
            self._logger.error(f"Error updating leave balance: {e}")
            return False
    
    def set_leave_balance(
        self, 
        employee_id: EmployeeId, 
        leave_balances: Dict[str, int],
        hostname: str = "default"
    ) -> bool:
        """Set leave balances for an employee"""
        try:
            collection = self._get_user_collection(hostname)
            
            result = collection.update_one(
                {"emp_id": str(employee_id)},
                {"$set": {"leave_balance": leave_balances}}
            )
            
            if result.modified_count > 0:
                self._logger.info(f"Set leave balances for {employee_id}: {leave_balances}")
                return True
            
            return False
            
        except Exception as e:
            self._logger.error(f"Error setting leave balances: {e}")
            return False
    
    def get_team_leave_balances(self, manager_id: str, hostname: str = "default") -> List[Dict[str, Any]]:
        """Get leave balances for all team members under a manager"""
        try:
            users = get_users_by_manager_id(manager_id, hostname)
            
            team_balances = []
            for user in users:
                team_balances.append({
                    "employee_id": user["emp_id"],
                    "employee_name": user.get("name", ""),
                    "employee_email": user.get("email", ""),
                    "leave_balances": user.get("leave_balance", {})
                })
            
            return team_balances
            
        except Exception as e:
            self._logger.error(f"Error getting team leave balances: {e}")
            return [] 