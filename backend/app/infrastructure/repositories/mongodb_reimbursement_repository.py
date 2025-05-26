"""
MongoDB Repository Implementation for Reimbursement System
Implements all reimbursement repository interfaces using MongoDB
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId

from domain.entities.reimbursement import Reimbursement, ReimbursementStatus, PaymentMethod
from domain.entities.reimbursement_type_entity import ReimbursementTypeEntity
from domain.value_objects.employee_id import EmployeeId
from domain.value_objects.reimbursement_type import ReimbursementType
from domain.value_objects.reimbursement_amount import ReimbursementAmount
from application.interfaces.repositories.reimbursement_repository import (
    ReimbursementCommandRepository,
    ReimbursementQueryRepository,
    ReimbursementTypeCommandRepository,
    ReimbursementTypeQueryRepository,
    ReimbursementAnalyticsRepository,
    ReimbursementReportRepository,
    ReimbursementRepository
)
from application.dto.reimbursement_dto import (
    ReimbursementSearchFiltersDTO,
    ReimbursementStatisticsDTO
)


logger = logging.getLogger(__name__)


class MongoDBReimbursementRepository(ReimbursementRepository):
    """
    MongoDB implementation of the complete reimbursement repository.
    
    Follows SOLID principles:
    - SRP: Each method has a single responsibility
    - OCP: Extensible through inheritance
    - LSP: Can be substituted with other implementations
    - ISP: Implements focused interfaces
    - DIP: Depends on abstractions (database interface)
    """
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.reimbursements_collection = database.reimbursements
        self.reimbursement_types_collection = database.reimbursement_types
        
        # Create indexes for better performance
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for optimal query performance"""
        try:
            # Reimbursements collection indexes
            self.reimbursements_collection.create_index([("employee_id", ASCENDING)])
            self.reimbursements_collection.create_index([("status", ASCENDING)])
            self.reimbursements_collection.create_index([("reimbursement_type.code", ASCENDING)])
            self.reimbursements_collection.create_index([("submitted_at", DESCENDING)])
            self.reimbursements_collection.create_index([("created_at", DESCENDING)])
            self.reimbursements_collection.create_index([
                ("employee_id", ASCENDING),
                ("status", ASCENDING),
                ("submitted_at", DESCENDING)
            ])
            
            # Reimbursement types collection indexes
            self.reimbursement_types_collection.create_index([("type_id", ASCENDING)], unique=True)
            self.reimbursement_types_collection.create_index([("reimbursement_type.code", ASCENDING)], unique=True)
            self.reimbursement_types_collection.create_index([("reimbursement_type.category", ASCENDING)])
            self.reimbursement_types_collection.create_index([("is_active", ASCENDING)])
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
    
    # ==================== REIMBURSEMENT COMMAND OPERATIONS ====================
    
    async def save(self, reimbursement: Reimbursement) -> Reimbursement:
        """Save a new reimbursement request"""
        try:
            document = self._reimbursement_to_document(reimbursement)
            result = await self.reimbursements_collection.insert_one(document)
            
            if result.inserted_id:
                logger.debug(f"Saved reimbursement: {reimbursement.request_id}")
                return reimbursement
            else:
                raise Exception("Failed to insert reimbursement document")
                
        except Exception as e:
            logger.error(f"Error saving reimbursement {reimbursement.request_id}: {e}")
            raise
    
    async def update(self, reimbursement: Reimbursement) -> Reimbursement:
        """Update an existing reimbursement request"""
        try:
            document = self._reimbursement_to_document(reimbursement)
            document["updated_at"] = datetime.utcnow()
            
            result = await self.reimbursements_collection.replace_one(
                {"request_id": reimbursement.request_id},
                document
            )
            
            if result.modified_count > 0 or result.matched_count > 0:
                logger.debug(f"Updated reimbursement: {reimbursement.request_id}")
                return reimbursement
            else:
                raise Exception(f"Reimbursement {reimbursement.request_id} not found for update")
                
        except Exception as e:
            logger.error(f"Error updating reimbursement {reimbursement.request_id}: {e}")
            raise
    
    async def submit(self, reimbursement: Reimbursement) -> Reimbursement:
        """Submit a reimbursement request"""
        return await self.update(reimbursement)
    
    async def approve(self, reimbursement: Reimbursement) -> Reimbursement:
        """Approve a reimbursement request"""
        return await self.update(reimbursement)
    
    async def reject(self, reimbursement: Reimbursement) -> Reimbursement:
        """Reject a reimbursement request"""
        return await self.update(reimbursement)
    
    async def cancel(self, reimbursement: Reimbursement) -> Reimbursement:
        """Cancel a reimbursement request"""
        return await self.update(reimbursement)
    
    async def process_payment(self, reimbursement: Reimbursement) -> Reimbursement:
        """Process payment for a reimbursement request"""
        return await self.update(reimbursement)
    
    async def upload_receipt(self, reimbursement: Reimbursement) -> Reimbursement:
        """Upload receipt for a reimbursement request"""
        return await self.update(reimbursement)
    
    async def bulk_approve(self, reimbursement_ids: List[str], approved_by: str) -> List[Reimbursement]:
        """Bulk approve multiple reimbursement requests"""
        try:
            approved_reimbursements = []
            
            for request_id in reimbursement_ids:
                reimbursement = await self.get_by_id(request_id)
                if reimbursement and reimbursement.is_pending_approval():
                    # This would need the actual approval logic from the use case
                    # For now, we'll just update the status
                    await self.reimbursements_collection.update_one(
                        {"request_id": request_id},
                        {
                            "$set": {
                                "status": "approved",
                                "approval.approved_by": approved_by,
                                "approval.approved_at": datetime.utcnow(),
                                "updated_at": datetime.utcnow()
                            }
                        }
                    )
                    
                    # Reload the updated reimbursement
                    updated_reimbursement = await self.get_by_id(request_id)
                    if updated_reimbursement:
                        approved_reimbursements.append(updated_reimbursement)
            
            logger.info(f"Bulk approved {len(approved_reimbursements)} reimbursements")
            return approved_reimbursements
            
        except Exception as e:
            logger.error(f"Error in bulk approve: {e}")
            raise
    
    # ==================== REIMBURSEMENT QUERY OPERATIONS ====================
    
    async def get_by_id(self, request_id: str) -> Optional[Reimbursement]:
        """Get reimbursement by ID"""
        try:
            document = await self.reimbursements_collection.find_one({"request_id": request_id})
            
            if document:
                return self._document_to_reimbursement(document)
            return None
            
        except Exception as e:
            logger.error(f"Error getting reimbursement by ID {request_id}: {e}")
            raise
    
    async def get_by_employee_id(self, employee_id: str) -> List[Reimbursement]:
        """Get reimbursements by employee ID"""
        try:
            cursor = self.reimbursements_collection.find(
                {"employee_id": employee_id}
            ).sort("created_at", DESCENDING)
            
            reimbursements = []
            async for document in cursor:
                reimbursement = self._document_to_reimbursement(document)
                if reimbursement:
                    reimbursements.append(reimbursement)
            
            return reimbursements
            
        except Exception as e:
            logger.error(f"Error getting reimbursements by employee ID {employee_id}: {e}")
            raise
    
    async def get_by_status(self, status: str) -> List[Reimbursement]:
        """Get reimbursements by status"""
        try:
            cursor = self.reimbursements_collection.find(
                {"status": status}
            ).sort("submitted_at", DESCENDING)
            
            reimbursements = []
            async for document in cursor:
                reimbursement = self._document_to_reimbursement(document)
                if reimbursement:
                    reimbursements.append(reimbursement)
            
            return reimbursements
            
        except Exception as e:
            logger.error(f"Error getting reimbursements by status {status}: {e}")
            raise
    
    async def get_pending_approval(self) -> List[Reimbursement]:
        """Get reimbursements pending approval"""
        return await self.get_by_status("under_review")
    
    async def get_all(self) -> List[Reimbursement]:
        """Get all reimbursements"""
        try:
            cursor = self.reimbursements_collection.find().sort("created_at", DESCENDING)
            
            reimbursements = []
            async for document in cursor:
                reimbursement = self._document_to_reimbursement(document)
                if reimbursement:
                    reimbursements.append(reimbursement)
            
            return reimbursements
            
        except Exception as e:
            logger.error(f"Error getting all reimbursements: {e}")
            raise
    
    async def search(self, filters: ReimbursementSearchFiltersDTO) -> List[Reimbursement]:
        """Search reimbursements with filters"""
        try:
            query = {}
            
            # Build query based on filters
            if filters.employee_id:
                query["employee_id"] = filters.employee_id
            
            if filters.status:
                query["status"] = filters.status
            
            if filters.reimbursement_type_code:
                query["reimbursement_type.code"] = filters.reimbursement_type_code
            
            if filters.start_date or filters.end_date:
                date_query = {}
                if filters.start_date:
                    date_query["$gte"] = filters.start_date
                if filters.end_date:
                    date_query["$lte"] = filters.end_date
                query["submitted_at"] = date_query
            
            if filters.min_amount or filters.max_amount:
                amount_query = {}
                if filters.min_amount:
                    amount_query["$gte"] = float(filters.min_amount)
                if filters.max_amount:
                    amount_query["$lte"] = float(filters.max_amount)
                query["amount.amount"] = amount_query
            
            # Execute query
            cursor = self.reimbursements_collection.find(query).sort("submitted_at", DESCENDING)
            
            if filters.limit:
                cursor = cursor.limit(filters.limit)
            
            reimbursements = []
            async for document in cursor:
                reimbursement = self._document_to_reimbursement(document)
                if reimbursement:
                    reimbursements.append(reimbursement)
            
            return reimbursements
            
        except Exception as e:
            logger.error(f"Error searching reimbursements: {e}")
            raise
    
    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Reimbursement]:
        """Get reimbursements within date range"""
        try:
            cursor = self.reimbursements_collection.find({
                "submitted_at": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }).sort("submitted_at", DESCENDING)
            
            reimbursements = []
            async for document in cursor:
                reimbursement = self._document_to_reimbursement(document)
                if reimbursement:
                    reimbursements.append(reimbursement)
            
            return reimbursements
            
        except Exception as e:
            logger.error(f"Error getting reimbursements by date range: {e}")
            raise
    
    async def get_total_amount_by_employee_and_type(
        self,
        employee_id: str,
        reimbursement_type_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Decimal:
        """Get total amount spent by employee for a specific type in date range"""
        try:
            pipeline = [
                {
                    "$match": {
                        "employee_id": employee_id,
                        "reimbursement_type.code": reimbursement_type_id,
                        "status": {"$in": ["approved", "paid"]},
                        "submitted_at": {
                            "$gte": start_date,
                            "$lte": end_date
                        }
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total": {"$sum": "$amount.amount"}
                    }
                }
            ]
            
            result = await self.reimbursements_collection.aggregate(pipeline).to_list(1)
            
            if result:
                return Decimal(str(result[0]["total"]))
            return Decimal("0")
            
        except Exception as e:
            logger.error(f"Error getting total amount: {e}")
            raise
    
    # ==================== REIMBURSEMENT TYPE OPERATIONS ====================
    
    async def save_reimbursement_type(self, reimbursement_type: ReimbursementTypeEntity) -> ReimbursementTypeEntity:
        """Save a new reimbursement type"""
        try:
            document = self._reimbursement_type_to_document(reimbursement_type)
            result = await self.reimbursement_types_collection.insert_one(document)
            
            if result.inserted_id:
                logger.debug(f"Saved reimbursement type: {reimbursement_type.type_id}")
                return reimbursement_type
            else:
                raise Exception("Failed to insert reimbursement type document")
                
        except Exception as e:
            logger.error(f"Error saving reimbursement type {reimbursement_type.type_id}: {e}")
            raise
    
    async def update_reimbursement_type(self, reimbursement_type: ReimbursementTypeEntity) -> ReimbursementTypeEntity:
        """Update an existing reimbursement type"""
        try:
            document = self._reimbursement_type_to_document(reimbursement_type)
            document["updated_at"] = datetime.utcnow()
            
            result = await self.reimbursement_types_collection.replace_one(
                {"type_id": reimbursement_type.type_id},
                document
            )
            
            if result.modified_count > 0 or result.matched_count > 0:
                logger.debug(f"Updated reimbursement type: {reimbursement_type.type_id}")
                return reimbursement_type
            else:
                raise Exception(f"Reimbursement type {reimbursement_type.type_id} not found for update")
                
        except Exception as e:
            logger.error(f"Error updating reimbursement type {reimbursement_type.type_id}: {e}")
            raise
    
    async def get_reimbursement_type_by_id(self, type_id: str) -> Optional[ReimbursementTypeEntity]:
        """Get reimbursement type by ID"""
        try:
            document = await self.reimbursement_types_collection.find_one({"type_id": type_id})
            
            if document:
                return self._document_to_reimbursement_type(document)
            return None
            
        except Exception as e:
            logger.error(f"Error getting reimbursement type by ID {type_id}: {e}")
            raise
    
    async def get_reimbursement_type_by_code(self, code: str) -> Optional[ReimbursementTypeEntity]:
        """Get reimbursement type by code"""
        try:
            document = await self.reimbursement_types_collection.find_one({"reimbursement_type.code": code})
            
            if document:
                return self._document_to_reimbursement_type(document)
            return None
            
        except Exception as e:
            logger.error(f"Error getting reimbursement type by code {code}: {e}")
            raise
    
    async def get_all_reimbursement_types(self) -> List[ReimbursementTypeEntity]:
        """Get all reimbursement types"""
        try:
            cursor = self.reimbursement_types_collection.find().sort("reimbursement_type.name", ASCENDING)
            
            types = []
            async for document in cursor:
                reimbursement_type = self._document_to_reimbursement_type(document)
                if reimbursement_type:
                    types.append(reimbursement_type)
            
            return types
            
        except Exception as e:
            logger.error(f"Error getting all reimbursement types: {e}")
            raise
    
    # ==================== ANALYTICS OPERATIONS ====================
    
    async def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> ReimbursementStatisticsDTO:
        """Get reimbursement statistics"""
        try:
            # Build date filter
            date_filter = {}
            if start_date or end_date:
                date_range = {}
                if start_date:
                    date_range["$gte"] = start_date
                if end_date:
                    date_range["$lte"] = end_date
                date_filter["submitted_at"] = date_range
            
            # Get total counts by status
            status_pipeline = [
                {"$match": date_filter},
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            
            status_results = await self.reimbursements_collection.aggregate(status_pipeline).to_list(None)
            status_counts = {result["_id"]: result["count"] for result in status_results}
            
            # Get total amounts
            amount_pipeline = [
                {"$match": {**date_filter, "status": {"$in": ["approved", "paid"]}}},
                {"$group": {"_id": None, "total": {"$sum": "$amount.amount"}}}
            ]
            
            amount_results = await self.reimbursements_collection.aggregate(amount_pipeline).to_list(1)
            total_amount = amount_results[0]["total"] if amount_results else 0
            
            return ReimbursementStatisticsDTO(
                total_requests=sum(status_counts.values()),
                pending_requests=status_counts.get("under_review", 0),
                approved_requests=status_counts.get("approved", 0),
                rejected_requests=status_counts.get("rejected", 0),
                paid_requests=status_counts.get("paid", 0),
                total_amount=float(total_amount),
                average_amount=float(total_amount) / max(status_counts.get("approved", 0) + status_counts.get("paid", 0), 1)
            )
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            raise
    
    # ==================== HELPER METHODS ====================
    
    def _reimbursement_to_document(self, reimbursement: Reimbursement) -> Dict[str, Any]:
        """Convert reimbursement entity to MongoDB document"""
        document = {
            "request_id": reimbursement.request_id,
            "employee_id": reimbursement.employee_id.value,
            "reimbursement_type": {
                "code": reimbursement.reimbursement_type.code,
                "name": reimbursement.reimbursement_type.name,
                "category": reimbursement.reimbursement_type.category.value,
                "description": reimbursement.reimbursement_type.description
            },
            "amount": {
                "amount": float(reimbursement.amount.amount),
                "currency": reimbursement.amount.currency
            },
            "description": reimbursement.description,
            "status": reimbursement.status.value,
            "created_at": reimbursement.created_at,
            "created_by": reimbursement.created_by,
            "submitted_at": reimbursement.submitted_at,
            "updated_at": datetime.utcnow()
        }
        
        # Add receipt information if present
        if reimbursement.receipt:
            document["receipt"] = {
                "file_path": reimbursement.receipt.file_path,
                "file_name": reimbursement.receipt.file_name,
                "file_size": reimbursement.receipt.file_size,
                "uploaded_at": reimbursement.receipt.uploaded_at,
                "uploaded_by": reimbursement.receipt.uploaded_by
            }
        
        # Add approval information if present
        if reimbursement.approval:
            document["approval"] = {
                "approved_by": reimbursement.approval.approved_by,
                "approved_at": reimbursement.approval.approved_at,
                "approved_amount": float(reimbursement.approval.approved_amount.amount) if reimbursement.approval.approved_amount else None,
                "approval_level": reimbursement.approval.approval_level,
                "comments": reimbursement.approval.comments
            }
        
        # Add payment information if present
        if reimbursement.payment:
            document["payment"] = {
                "paid_by": reimbursement.payment.paid_by,
                "paid_at": reimbursement.payment.paid_at,
                "payment_method": reimbursement.payment.payment_method.value,
                "payment_reference": reimbursement.payment.payment_reference,
                "bank_details": reimbursement.payment.bank_details
            }
        
        return document
    
    def _document_to_reimbursement(self, document: Dict[str, Any]) -> Optional[Reimbursement]:
        """Convert MongoDB document to reimbursement entity"""
        try:
            # Create value objects
            employee_id = EmployeeId.from_string(document["employee_id"])
            
            reimbursement_type = ReimbursementType(
                code=document["reimbursement_type"]["code"],
                name=document["reimbursement_type"]["name"],
                category=document["reimbursement_type"]["category"],
                description=document["reimbursement_type"]["description"]
            )
            
            amount = ReimbursementAmount(
                Decimal(str(document["amount"]["amount"])),
                document["amount"]["currency"]
            )
            
            status = ReimbursementStatus(document["status"])
            
            # Create reimbursement entity
            reimbursement = Reimbursement(
                request_id=document["request_id"],
                employee_id=employee_id,
                reimbursement_type=reimbursement_type,
                amount=amount,
                description=document["description"],
                status=status,
                created_at=document["created_at"],
                created_by=document["created_by"],
                submitted_at=document.get("submitted_at")
            )
            
            # Set receipt if present
            if "receipt" in document:
                receipt_data = document["receipt"]
                # This would need to be implemented based on the Receipt value object structure
                # For now, we'll skip this
            
            # Set approval if present
            if "approval" in document:
                approval_data = document["approval"]
                # This would need to be implemented based on the Approval value object structure
                # For now, we'll skip this
            
            # Set payment if present
            if "payment" in document:
                payment_data = document["payment"]
                # This would need to be implemented based on the Payment value object structure
                # For now, we'll skip this
            
            return reimbursement
            
        except Exception as e:
            logger.error(f"Error converting document to reimbursement: {e}")
            return None
    
    def _reimbursement_type_to_document(self, reimbursement_type: ReimbursementTypeEntity) -> Dict[str, Any]:
        """Convert reimbursement type entity to MongoDB document"""
        return {
            "type_id": reimbursement_type.type_id,
            "reimbursement_type": {
                "code": reimbursement_type.reimbursement_type.code,
                "name": reimbursement_type.reimbursement_type.name,
                "category": reimbursement_type.reimbursement_type.category.value,
                "description": reimbursement_type.reimbursement_type.description,
                "max_limit": float(reimbursement_type.reimbursement_type.max_limit) if reimbursement_type.reimbursement_type.max_limit else None,
                "frequency": reimbursement_type.reimbursement_type.frequency.value,
                "approval_level": reimbursement_type.reimbursement_type.approval_level.value,
                "requires_receipt": reimbursement_type.reimbursement_type.requires_receipt,
                "is_taxable": reimbursement_type.reimbursement_type.is_taxable
            },
            "is_active": reimbursement_type.is_active,
            "created_at": reimbursement_type.created_at,
            "created_by": reimbursement_type.created_by,
            "updated_at": datetime.utcnow()
        }
    
    def _document_to_reimbursement_type(self, document: Dict[str, Any]) -> Optional[ReimbursementTypeEntity]:
        """Convert MongoDB document to reimbursement type entity"""
        try:
            rt_data = document["reimbursement_type"]
            
            reimbursement_type = ReimbursementType(
                code=rt_data["code"],
                name=rt_data["name"],
                category=rt_data["category"],
                description=rt_data["description"],
                max_limit=Decimal(str(rt_data["max_limit"])) if rt_data.get("max_limit") else None,
                frequency=rt_data["frequency"],
                approval_level=rt_data["approval_level"],
                requires_receipt=rt_data["requires_receipt"],
                is_taxable=rt_data["is_taxable"]
            )
            
            return ReimbursementTypeEntity(
                type_id=document["type_id"],
                reimbursement_type=reimbursement_type,
                is_active=document["is_active"],
                created_at=document["created_at"],
                created_by=document["created_by"]
            )
            
        except Exception as e:
            logger.error(f"Error converting document to reimbursement type: {e}")
            return None 