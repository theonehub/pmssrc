"""
MongoDB Company Leave Repository Implementation
Concrete implementation of company leave repositories using MongoDB
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId

from app.application.interfaces.repositories.company_leave_repository import (
    CompanyLeaveCommandRepository,
    CompanyLeaveQueryRepository,
    CompanyLeaveAnalyticsRepository
)
from app.domain.entities.company_leave import CompanyLeave
from app.domain.value_objects.leave_type import LeaveType, LeaveCategory, AccrualType
from app.domain.value_objects.leave_policy import LeavePolicy
from app.database.database_connector import connect_to_database
from decimal import Decimal


class MongoDBCompanyLeaveCommandRepository(CompanyLeaveCommandRepository):
    """
    MongoDB implementation of company leave command repository.
    
    Follows SOLID principles:
    - SRP: Only handles company leave write operations
    - OCP: Can be extended with new storage features
    - LSP: Can be substituted with other implementations
    - ISP: Implements only command operations
    - DIP: Depends on MongoDB abstractions
    """
    
    def __init__(self, hostname: str):
        self._hostname = hostname
        self._logger = logging.getLogger(__name__)
        self._db = connect_to_database(hostname)
        self._collection: Collection = self._db["company_leaves"]
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Ensure necessary indexes exist"""
        try:
            self._collection.create_index([("company_leave_id", ASCENDING)], unique=True)
            self._collection.create_index([("leave_type.code", ASCENDING)], unique=True)
            self._collection.create_index([("is_active", ASCENDING)])
            self._collection.create_index([("created_at", DESCENDING)])
            self._collection.create_index([("policy.gender_specific", ASCENDING)])
            self._collection.create_index([("policy.available_during_probation", ASCENDING)])
        except Exception as e:
            self._logger.warning(f"Error creating indexes: {e}")
    
    def save(self, company_leave: CompanyLeave) -> bool:
        """Save company leave record"""
        try:
            document = self._entity_to_document(company_leave)
            result = self._collection.insert_one(document)
            
            if result.inserted_id:
                self._logger.info(f"Saved company leave: {company_leave.company_leave_id}")
                return True
            return False
            
        except Exception as e:
            self._logger.error(f"Error saving company leave: {e}")
            return False
    
    def update(self, company_leave: CompanyLeave) -> bool:
        """Update existing company leave record"""
        try:
            document = self._entity_to_document(company_leave)
            # Remove _id to avoid update conflicts
            document.pop('_id', None)
            
            result = self._collection.replace_one(
                {"company_leave_id": company_leave.company_leave_id},
                document
            )
            
            if result.matched_count > 0:
                self._logger.info(f"Updated company leave: {company_leave.company_leave_id}")
                return True
            return False
            
        except Exception as e:
            self._logger.error(f"Error updating company leave: {e}")
            return False
    
    def delete(self, company_leave_id: str) -> bool:
        """Delete company leave record (soft delete)"""
        try:
            result = self._collection.update_one(
                {"company_leave_id": company_leave_id},
                {
                    "$set": {
                        "is_active": False,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.matched_count > 0:
                self._logger.info(f"Deleted company leave: {company_leave_id}")
                return True
            return False
            
        except Exception as e:
            self._logger.error(f"Error deleting company leave: {e}")
            return False
    
    def _entity_to_document(self, company_leave: CompanyLeave) -> Dict[str, Any]:
        """Convert CompanyLeave entity to MongoDB document"""
        return {
            "company_leave_id": company_leave.company_leave_id,
            "leave_type": {
                "code": company_leave.leave_type.code,
                "name": company_leave.leave_type.name,
                "category": company_leave.leave_type.category.value,
                "description": company_leave.leave_type.description
            },
            "policy": {
                "annual_allocation": company_leave.policy.annual_allocation,
                "accrual_type": company_leave.policy.accrual_type.value,
                "accrual_rate": float(company_leave.policy.accrual_rate) if company_leave.policy.accrual_rate else None,
                "max_carryover_days": company_leave.policy.max_carryover_days,
                "carryover_expiry_months": company_leave.policy.carryover_expiry_months,
                "min_advance_notice_days": company_leave.policy.min_advance_notice_days,
                "max_advance_application_days": company_leave.policy.max_advance_application_days,
                "min_application_days": company_leave.policy.min_application_days,
                "max_continuous_days": company_leave.policy.max_continuous_days,
                "requires_approval": company_leave.policy.requires_approval,
                "auto_approve_threshold": company_leave.policy.auto_approve_threshold,
                "requires_medical_certificate": company_leave.policy.requires_medical_certificate,
                "medical_certificate_threshold": company_leave.policy.medical_certificate_threshold,
                "is_encashable": company_leave.policy.is_encashable,
                "max_encashment_days": company_leave.policy.max_encashment_days,
                "encashment_percentage": float(company_leave.policy.encashment_percentage),
                "available_during_probation": company_leave.policy.available_during_probation,
                "probation_allocation": company_leave.policy.probation_allocation,
                "gender_specific": company_leave.policy.gender_specific,
                "employee_category_specific": company_leave.policy.employee_category_specific
            },
            "is_active": company_leave.is_active,
            "description": company_leave.description,
            "effective_from": company_leave.effective_from,
            "effective_until": company_leave.effective_until,
            "created_at": company_leave.created_at,
            "updated_at": company_leave.updated_at,
            "created_by": company_leave.created_by,
            "updated_by": company_leave.updated_by
        }


class MongoDBCompanyLeaveQueryRepository(CompanyLeaveQueryRepository):
    """
    MongoDB implementation of company leave query repository.
    """
    
    def __init__(self, hostname: str):
        self._hostname = hostname
        self._logger = logging.getLogger(__name__)
        self._db = connect_to_database(hostname)
        self._collection: Collection = self._db["company_leaves"]
    
    def get_by_id(self, company_leave_id: str) -> Optional[CompanyLeave]:
        """Get company leave by ID"""
        try:
            document = self._collection.find_one({"company_leave_id": company_leave_id})
            if document:
                return self._document_to_entity(document)
            return None
            
        except Exception as e:
            self._logger.error(f"Error retrieving company leave by ID: {e}")
            return None
    
    def get_by_leave_type_code(self, leave_type_code: str) -> Optional[CompanyLeave]:
        """Get company leave by leave type code"""
        try:
            document = self._collection.find_one({
                "leave_type.code": leave_type_code.upper(),
                "is_active": True
            })
            if document:
                return self._document_to_entity(document)
            return None
            
        except Exception as e:
            self._logger.error(f"Error retrieving company leave by type code: {e}")
            return None
    
    def get_all_active(self) -> List[CompanyLeave]:
        """Get all active company leaves"""
        try:
            documents = list(self._collection.find({"is_active": True}).sort("created_at", DESCENDING))
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            self._logger.error(f"Error retrieving active company leaves: {e}")
            return []
    
    def get_all(self, include_inactive: bool = False) -> List[CompanyLeave]:
        """Get all company leaves"""
        try:
            query = {} if include_inactive else {"is_active": True}
            documents = list(self._collection.find(query).sort("created_at", DESCENDING))
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            self._logger.error(f"Error retrieving company leaves: {e}")
            return []
    
    def get_applicable_for_employee(
        self,
        employee_gender: Optional[str] = None,
        employee_category: Optional[str] = None,
        is_on_probation: bool = False
    ) -> List[CompanyLeave]:
        """Get company leaves applicable for employee"""
        try:
            query = {"is_active": True}
            
            # Build query for applicable leaves
            if employee_gender:
                query["$or"] = [
                    {"policy.gender_specific": None},
                    {"policy.gender_specific": employee_gender}
                ]
            
            if is_on_probation:
                query["policy.available_during_probation"] = True
            
            if employee_category:
                query["$or"] = query.get("$or", []) + [
                    {"policy.employee_category_specific": None},
                    {"policy.employee_category_specific": {"$in": [employee_category]}}
                ]
            
            documents = list(self._collection.find(query).sort("leave_type.name", ASCENDING))
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            self._logger.error(f"Error retrieving applicable leaves: {e}")
            return []
    
    def exists_by_leave_type_code(self, leave_type_code: str) -> bool:
        """Check if company leave exists for leave type code"""
        try:
            count = self._collection.count_documents({
                "leave_type.code": leave_type_code.upper(),
                "is_active": True
            })
            return count > 0
            
        except Exception as e:
            self._logger.error(f"Error checking leave type existence: {e}")
            return False
    
    def count_active(self) -> int:
        """Count active company leaves"""
        try:
            return self._collection.count_documents({"is_active": True})
            
        except Exception as e:
            self._logger.error(f"Error counting active leaves: {e}")
            return 0
    
    def _document_to_entity(self, document: Dict[str, Any]) -> CompanyLeave:
        """Convert MongoDB document to CompanyLeave entity"""
        # Create LeaveType value object
        leave_type = LeaveType(
            code=document["leave_type"]["code"],
            name=document["leave_type"]["name"],
            category=LeaveCategory(document["leave_type"]["category"]),
            description=document["leave_type"].get("description")
        )
        
        # Create LeavePolicy value object
        policy_data = document["policy"]
        leave_policy = LeavePolicy(
            leave_type=leave_type,
            annual_allocation=policy_data["annual_allocation"],
            accrual_type=AccrualType(policy_data["accrual_type"]),
            accrual_rate=Decimal(str(policy_data["accrual_rate"])) if policy_data.get("accrual_rate") else None,
            max_carryover_days=policy_data["max_carryover_days"],
            carryover_expiry_months=policy_data["carryover_expiry_months"],
            min_advance_notice_days=policy_data["min_advance_notice_days"],
            max_advance_application_days=policy_data["max_advance_application_days"],
            min_application_days=policy_data["min_application_days"],
            max_continuous_days=policy_data.get("max_continuous_days"),
            requires_approval=policy_data["requires_approval"],
            auto_approve_threshold=policy_data.get("auto_approve_threshold"),
            requires_medical_certificate=policy_data["requires_medical_certificate"],
            medical_certificate_threshold=policy_data.get("medical_certificate_threshold"),
            is_encashable=policy_data["is_encashable"],
            max_encashment_days=policy_data["max_encashment_days"],
            encashment_percentage=Decimal(str(policy_data["encashment_percentage"])),
            available_during_probation=policy_data["available_during_probation"],
            probation_allocation=policy_data.get("probation_allocation"),
            gender_specific=policy_data.get("gender_specific"),
            employee_category_specific=policy_data.get("employee_category_specific")
        )
        
        # Create CompanyLeave entity
        company_leave = CompanyLeave(
            company_leave_id=document["company_leave_id"],
            leave_type=leave_type,
            policy=leave_policy,
            is_active=document["is_active"],
            created_at=document["created_at"],
            updated_at=document["updated_at"],
            created_by=document.get("created_by"),
            updated_by=document.get("updated_by"),
            description=document.get("description"),
            effective_from=document.get("effective_from"),
            effective_until=document.get("effective_until")
        )
        
        return company_leave


class MongoDBCompanyLeaveAnalyticsRepository(CompanyLeaveAnalyticsRepository):
    """
    MongoDB implementation of company leave analytics repository.
    """
    
    def __init__(self, hostname: str):
        self._hostname = hostname
        self._logger = logging.getLogger(__name__)
        self._db = connect_to_database(hostname)
        self._collection: Collection = self._db["company_leaves"]
        self._employee_leaves_collection: Collection = self._db["employee_leaves"]
    
    def get_leave_type_usage_stats(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get leave type usage statistics"""
        try:
            # This would typically aggregate from employee leave applications
            # For now, return basic stats from company leaves
            pipeline = [
                {"$match": {"is_active": True}},
                {
                    "$group": {
                        "_id": "$leave_type.category",
                        "leave_types": {"$push": "$leave_type.name"},
                        "total_allocation": {"$sum": "$policy.annual_allocation"},
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            results = list(self._collection.aggregate(pipeline))
            return results
            
        except Exception as e:
            self._logger.error(f"Error getting usage stats: {e}")
            return []
    
    def get_policy_compliance_report(self) -> List[Dict[str, Any]]:
        """Get policy compliance report"""
        try:
            pipeline = [
                {"$match": {"is_active": True}},
                {
                    "$group": {
                        "_id": None,
                        "total_policies": {"$sum": 1},
                        "encashable_policies": {
                            "$sum": {"$cond": ["$policy.is_encashable", 1, 0]}
                        },
                        "auto_approval_policies": {
                            "$sum": {"$cond": [{"$ne": ["$policy.auto_approve_threshold", None]}, 1, 0]}
                        },
                        "medical_cert_required": {
                            "$sum": {"$cond": ["$policy.requires_medical_certificate", 1, 0]}
                        },
                        "probation_restricted": {
                            "$sum": {"$cond": [{"$eq": ["$policy.available_during_probation", False]}, 1, 0]}
                        }
                    }
                }
            ]
            
            results = list(self._collection.aggregate(pipeline))
            return results
            
        except Exception as e:
            self._logger.error(f"Error getting compliance report: {e}")
            return []
    
    def get_leave_trends(
        self,
        period: str = "monthly"
    ) -> List[Dict[str, Any]]:
        """Get leave application trends"""
        try:
            # This would typically analyze employee leave applications over time
            # For now, return creation trends of company leaves
            group_format = {
                "daily": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "weekly": {"$dateToString": {"format": "%Y-W%U", "date": "$created_at"}},
                "monthly": {"$dateToString": {"format": "%Y-%m", "date": "$created_at"}},
                "quarterly": {"$dateToString": {"format": "%Y-Q%q", "date": "$created_at"}}
            }
            
            pipeline = [
                {"$match": {"is_active": True}},
                {
                    "$group": {
                        "_id": group_format.get(period, group_format["monthly"]),
                        "policies_created": {"$sum": 1},
                        "total_allocation": {"$sum": "$policy.annual_allocation"}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            results = list(self._collection.aggregate(pipeline))
            return results
            
        except Exception as e:
            self._logger.error(f"Error getting leave trends: {e}")
            return [] 