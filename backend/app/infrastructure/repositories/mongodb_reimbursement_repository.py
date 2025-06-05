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

from app.domain.entities.reimbursement import Reimbursement, ReimbursementStatus, PaymentMethod
from app.domain.entities.reimbursement_type_entity import ReimbursementTypeEntity
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.reimbursement_type import ReimbursementType
from app.domain.value_objects.reimbursement_amount import ReimbursementAmount
from app.application.interfaces.repositories.reimbursement_repository import (
    ReimbursementCommandRepository,
    ReimbursementQueryRepository,
    ReimbursementTypeCommandRepository,
    ReimbursementTypeQueryRepository,
    ReimbursementAnalyticsRepository,
    ReimbursementReportRepository,
    ReimbursementRepository
)
from app.application.dto.reimbursement_dto import (
    ReimbursementSearchFiltersDTO,
    ReimbursementStatisticsDTO
)
from app.infrastructure.database.mongodb_connector import MongoDBConnector
from app.config.mongodb_config import get_mongodb_connection_string, get_mongodb_client_options


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
    
    def __init__(self, database_connector: MongoDBConnector):
        self.db_connector = database_connector
        self._collection_name = "reimbursements"
        self._types_collection_name = "reimbursement_types"
        self._connection_string = None
        self._client_options = None
        
        # Create indexes for better performance
        # Note: Indexes will be created when collections are accessed
    
    def set_connection_config(self, connection_string: str, client_options: Dict[str, Any]):
        """Set connection configuration - called by dependency container."""
        self._connection_string = connection_string
        self._client_options = client_options
    
    async def _get_collection(self, organisation_id: Optional[str] = None, collection_name: Optional[str] = None):
        """
        Get collection for specific organisation or global.
        
        Ensures database connection is established in the correct event loop.
        Uses global database for reimbursement data.
        """
        db_name = "pms_global_database"
        actual_collection_name = collection_name or self._collection_name
        
        # Ensure database is connected in the current event loop
        if not self.db_connector.is_connected:
            logger.debug("Database not connected, establishing connection...")
            
            try:
                # Use stored connection configuration or fallback to config functions
                if self._connection_string and self._client_options:
                    logger.debug("Using stored connection parameters from repository configuration")
                    connection_string = self._connection_string
                    options = self._client_options
                else:
                    # Fallback to config functions if connection config not set
                    logger.debug("Loading connection parameters from mongodb_config")
                    connection_string = get_mongodb_connection_string()
                    options = get_mongodb_client_options()
                
                await self.db_connector.connect(connection_string, **options)
                logger.info("MongoDB connection established successfully in current event loop")
                
            except Exception as e:
                logger.error(f"Failed to establish database connection: {e}")
                raise RuntimeError(f"Database connection failed: {e}")
        
        # Verify connection and get collection
        try:
            db = self.db_connector.get_database(db_name)
            collection = db[actual_collection_name]
            logger.debug(f"Successfully retrieved collection: {actual_collection_name} from database: {db_name}")
            return collection
            
        except Exception as e:
            logger.error(f"Failed to get collection {actual_collection_name}: {e}")
            # Reset connection state to force reconnection on next call
            if hasattr(self.db_connector, '_client'):
                self.db_connector._client = None
            raise RuntimeError(f"Collection access failed: {e}")
    
    async def _get_reimbursements_collection(self, organisation_id: Optional[str] = None):
        """Get the reimbursements collection."""
        return await self._get_collection(organisation_id, self._collection_name)
    
    async def _get_reimbursement_types_collection(self, organisation_id: Optional[str] = None):
        """Get the reimbursement types collection."""
        return await self._get_collection(organisation_id, self._types_collection_name)

    async def _create_indexes(self, organisation_id: Optional[str] = None):
        """Create database indexes for optimal query performance"""
        try:
            # Get collections
            reimbursements_collection = await self._get_reimbursements_collection(organisation_id)
            reimbursement_types_collection = await self._get_reimbursement_types_collection(organisation_id)
            
            # Reimbursements collection indexes
            await reimbursements_collection.create_index([("employee_id", ASCENDING)])
            await reimbursements_collection.create_index([("status", ASCENDING)])
            await reimbursements_collection.create_index([("reimbursement_type.code", ASCENDING)])
            await reimbursements_collection.create_index([("submitted_at", DESCENDING)])
            await reimbursements_collection.create_index([("created_at", DESCENDING)])
            await reimbursements_collection.create_index([
                ("employee_id", ASCENDING),
                ("status", ASCENDING),
                ("submitted_at", DESCENDING)
            ])
            
            # Reimbursement types collection indexes
            await reimbursement_types_collection.create_index([("type_id", ASCENDING)], unique=True)
            await reimbursement_types_collection.create_index([("reimbursement_type.code", ASCENDING)], unique=True)
            await reimbursement_types_collection.create_index([("reimbursement_type.category", ASCENDING)])
            await reimbursement_types_collection.create_index([("is_active", ASCENDING)])
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
    
    # ==================== REIMBURSEMENT COMMAND OPERATIONS ====================
    
    async def save(self, reimbursement: Reimbursement) -> Reimbursement:
        """Save a new reimbursement request"""
        try:
            document = self._reimbursement_to_document(reimbursement)
            collection = await self._get_reimbursements_collection()
            result = await collection.insert_one(document)
            
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
            
            collection = await self._get_reimbursements_collection()
            result = await collection.replace_one(
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
    
    async def bulk_approve(
        self,
        request_ids: List[str],
        approved_by: str,
        approval_criteria: str
    ) -> Dict[str, bool]:
        """Bulk approve multiple reimbursement requests"""
        try:
            results = {}
            
            for request_id in request_ids:
                try:
                    # Use the approve_request method we implemented
                    success = await self.approve_request(
                        request_id=request_id,
                        approved_by=approved_by,
                        approval_level="manager",
                        comments=f"Bulk approval: {approval_criteria}"
                    )
                    results[request_id] = success
                    
                except Exception as e:
                    logger.error(f"Error approving request {request_id}: {e}")
                    results[request_id] = False
            
            approved_count = sum(1 for success in results.values() if success)
            logger.info(f"Bulk approved {approved_count}/{len(request_ids)} reimbursements")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk approve: {e}")
            # Return False for all request IDs on error
            return {request_id: False for request_id in request_ids}
    
    # ==================== REIMBURSEMENT QUERY OPERATIONS ====================
    
    async def get_by_id(self, request_id: str) -> Optional[Reimbursement]:
        """Get reimbursement by ID"""
        try:
            collection = await self._get_reimbursements_collection()
            document = await collection.find_one({"request_id": request_id})
            
            if document:
                return self._document_to_reimbursement(document)
            return None
            
        except Exception as e:
            logger.error(f"Error getting reimbursement by ID {request_id}: {e}")
            raise
    
    async def get_by_employee_id(self, employee_id: str) -> List[Reimbursement]:
        """Get reimbursements by employee ID"""
        try:
            collection = await self._get_reimbursements_collection()
            cursor = collection.find(
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
            collection = await self._get_reimbursements_collection()
            cursor = collection.find(
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
            collection = await self._get_reimbursements_collection()
            cursor = collection.find().sort("created_at", DESCENDING)
            
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
                query["amount"] = amount_query
            
            # Execute query
            collection = await self._get_reimbursements_collection()
            cursor = collection.find(query).sort("submitted_at", DESCENDING)
            
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
            collection = await self._get_reimbursements_collection()
            cursor = collection.find({
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
        """Get total reimbursement amount for employee and type within date range"""
        try:
            pipeline = [
                {
                    "$match": {
                        "employee_id": employee_id,
                        "reimbursement_type.type_id": reimbursement_type_id,
                        "submitted_at": {
                            "$gte": start_date,
                            "$lte": end_date
                        },
                        "status": {"$in": ["approved", "paid"]}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total": {"$sum": "$amount"}
                    }
                }
            ]
            
            collection = await self._get_reimbursements_collection()
            result = await collection.aggregate(pipeline).to_list(1)
            
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
            collection = await self._get_reimbursement_types_collection()
            result = await collection.insert_one(document)
            
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
            
            collection = await self._get_reimbursement_types_collection()
            result = await collection.replace_one(
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
            collection = await self._get_reimbursement_types_collection()
            document = await collection.find_one({"type_id": type_id})
            
            if document:
                return self._document_to_reimbursement_type(document)
            return None
            
        except Exception as e:
            logger.error(f"Error getting reimbursement type by ID {type_id}: {e}")
            raise
    
    async def get_reimbursement_type_by_code(self, code: str) -> Optional[ReimbursementTypeEntity]:
        """Get reimbursement type by code"""
        try:
            collection = await self._get_reimbursement_types_collection()
            document = await collection.find_one({"reimbursement_type.code": code})
            
            if document:
                return self._document_to_reimbursement_type(document)
            return None
            
        except Exception as e:
            logger.error(f"Error getting reimbursement type by code {code}: {e}")
            raise
    
    async def get_all_reimbursement_types(self) -> List[ReimbursementTypeEntity]:
        """Get all reimbursement types"""
        try:
            collection = await self._get_reimbursement_types_collection()
            cursor = collection.find().sort("reimbursement_type.name", ASCENDING)
            
            types = []
            async for document in cursor:
                reimbursement_type = self._document_to_reimbursement_type(document)
                if reimbursement_type:
                    types.append(reimbursement_type)
            
            return types
            
        except Exception as e:
            logger.error(f"Error getting all reimbursement types: {e}")
            raise
    
    async def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> ReimbursementStatisticsDTO:
        """Get reimbursement statistics"""
        try:
            date_filter = {}
            if start_date or end_date:
                if start_date:
                    date_filter["$gte"] = start_date
                if end_date:
                    date_filter["$lte"] = end_date
            
            # Get status counts
            status_pipeline = [
                {"$match": {"submitted_at": date_filter} if date_filter else {"$match": {}}},
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            
            collection = await self._get_reimbursements_collection()
            status_results = await collection.aggregate(status_pipeline).to_list(None)
            status_counts = {result["_id"]: result["count"] for result in status_results}
            
            # Get total amount
            amount_pipeline = [
                {"$match": {"submitted_at": date_filter} if date_filter else {"$match": {}}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]
            
            amount_results = await collection.aggregate(amount_pipeline).to_list(1)
            total_amount = amount_results[0]["total"] if amount_results else 0
            
            return ReimbursementStatisticsDTO(
                total_requests=sum(status_counts.values()),
                pending_requests=status_counts.get("pending", 0),
                approved_requests=status_counts.get("approved", 0),
                rejected_requests=status_counts.get("rejected", 0),
                paid_requests=status_counts.get("paid", 0),
                total_amount=Decimal(str(total_amount)),
                average_amount=Decimal(str(total_amount / sum(status_counts.values()))) if sum(status_counts.values()) > 0 else Decimal("0")
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

    # Missing Abstract Methods Implementation
    
    # ReimbursementTypeCommandRepository Methods
    async def activate(self, type_id: str, updated_by: str) -> bool:
        """Activate a reimbursement type."""
        try:
            result = await self._get_reimbursement_types_collection().update_one(
                {"type_id": type_id},
                {
                    "$set": {
                        "is_active": True,
                        "updated_by": updated_by,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Activated reimbursement type: {type_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error activating reimbursement type {type_id}: {e}")
            return False

    async def deactivate(self, type_id: str, updated_by: str, reason: Optional[str] = None) -> bool:
        """Deactivate a reimbursement type."""
        try:
            update_data = {
                "is_active": False,
                "updated_by": updated_by,
                "updated_at": datetime.utcnow()
            }
            
            if reason:
                update_data["deactivation_reason"] = reason
            
            result = await self._get_reimbursement_types_collection().update_one(
                {"type_id": type_id},
                {"$set": update_data}
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Deactivated reimbursement type: {type_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error deactivating reimbursement type {type_id}: {e}")
            return False

    # ReimbursementTypeQueryRepository Methods
    async def get_by_code(self, code: str) -> Optional[ReimbursementTypeEntity]:
        """Get reimbursement type by code."""
        try:
            document = await self._get_reimbursement_types_collection().find_one(
                {"reimbursement_type.code": code}
            )
            
            if document:
                return self._document_to_reimbursement_type(document)
            return None
            
        except Exception as e:
            logger.error(f"Error getting reimbursement type by code {code}: {e}")
            return None

    async def get_active(self) -> List[ReimbursementTypeEntity]:
        """Get all active reimbursement types."""
        try:
            cursor = await self._get_reimbursement_types_collection().find({"is_active": True})
            documents = await cursor.to_list(length=None)
            
            types = []
            for doc in documents:
                reimbursement_type = self._document_to_reimbursement_type(doc)
                if reimbursement_type:
                    types.append(reimbursement_type)
            
            return types
            
        except Exception as e:
            logger.error(f"Error getting active reimbursement types: {e}")
            return []

    async def get_by_category(self, category: str) -> List[ReimbursementTypeEntity]:
        """Get reimbursement types by category."""
        try:
            cursor = await self._get_reimbursement_types_collection().find(
                {"reimbursement_type.category": category}
            )
            documents = await cursor.to_list(length=None)
            
            types = []
            for doc in documents:
                reimbursement_type = self._document_to_reimbursement_type(doc)
                if reimbursement_type:
                    types.append(reimbursement_type)
            
            return types
            
        except Exception as e:
            logger.error(f"Error getting reimbursement types by category {category}: {e}")
            return []

    async def exists_by_code(self, code: str, exclude_id: Optional[str] = None) -> bool:
        """Check if reimbursement type exists by code."""
        try:
            query = {"reimbursement_type.code": code}
            
            if exclude_id:
                query["type_id"] = {"$ne": exclude_id}
            
            count = await self._get_reimbursement_types_collection().count_documents(query)
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking reimbursement type code existence {code}: {e}")
            return False

    # ReimbursementCommandRepository Methods
    async def delete(self, request_id: str) -> bool:
        """Delete a reimbursement request (soft delete)."""
        try:
            result = await self._get_reimbursements_collection().update_one(
                {"request_id": request_id},
                {
                    "$set": {
                        "is_deleted": True,
                        "deleted_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Soft deleted reimbursement: {request_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error deleting reimbursement {request_id}: {e}")
            return False

    async def submit_request(self, request_id: str, submitted_by: str) -> bool:
        """Submit a reimbursement request."""
        try:
            result = await self._get_reimbursements_collection().update_one(
                {"request_id": request_id},
                {
                    "$set": {
                        "status": "submitted",
                        "submitted_by": submitted_by,
                        "submitted_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Submitted reimbursement request: {request_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error submitting reimbursement request {request_id}: {e}")
            return False

    async def approve_request(
        self,
        request_id: str,
        approved_by: str,
        approved_amount: Optional[Decimal] = None,
        approval_level: str = "manager",
        comments: Optional[str] = None
    ) -> bool:
        """Approve a reimbursement request."""
        try:
            update_data = {
                "status": "approved",
                "approval.approved_by": approved_by,
                "approval.approved_at": datetime.utcnow(),
                "approval.approval_level": approval_level,
                "updated_at": datetime.utcnow()
            }
            
            if approved_amount is not None:
                update_data["approval.approved_amount"] = float(approved_amount)
            
            if comments:
                update_data["approval.comments"] = comments
            
            result = await self._get_reimbursements_collection().update_one(
                {"request_id": request_id},
                {"$set": update_data}
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Approved reimbursement request: {request_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error approving reimbursement request {request_id}: {e}")
            return False

    async def reject_request(
        self,
        request_id: str,
        rejected_by: str,
        rejection_reason: str
    ) -> bool:
        """Reject a reimbursement request."""
        try:
            result = await self._get_reimbursements_collection().update_one(
                {"request_id": request_id},
                {
                    "$set": {
                        "status": "rejected",
                        "rejection.rejected_by": rejected_by,
                        "rejection.rejected_at": datetime.utcnow(),
                        "rejection.reason": rejection_reason,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Rejected reimbursement request: {request_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error rejecting reimbursement request {request_id}: {e}")
            return False

    async def cancel_request(
        self,
        request_id: str,
        cancelled_by: str,
        cancellation_reason: Optional[str] = None
    ) -> bool:
        """Cancel a reimbursement request."""
        try:
            update_data = {
                "status": "cancelled",
                "cancellation.cancelled_by": cancelled_by,
                "cancellation.cancelled_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            if cancellation_reason:
                update_data["cancellation.reason"] = cancellation_reason
            
            result = await self._get_reimbursements_collection().update_one(
                {"request_id": request_id},
                {"$set": update_data}
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Cancelled reimbursement request: {request_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error cancelling reimbursement request {request_id}: {e}")
            return False

    async def process_payment(
        self,
        request_id: str,
        paid_by: str,
        payment_method: str,
        payment_reference: Optional[str] = None,
        bank_details: Optional[str] = None
    ) -> bool:
        """Process payment for a reimbursement request."""
        try:
            update_data = {
                "status": "paid",
                "payment.paid_by": paid_by,
                "payment.paid_at": datetime.utcnow(),
                "payment.method": payment_method,
                "updated_at": datetime.utcnow()
            }
            
            if payment_reference:
                update_data["payment.reference"] = payment_reference
            
            if bank_details:
                update_data["payment.bank_details"] = bank_details
            
            result = await self._get_reimbursements_collection().update_one(
                {"request_id": request_id},
                {"$set": update_data}
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Processed payment for reimbursement: {request_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error processing payment for reimbursement {request_id}: {e}")
            return False

    async def upload_receipt(
        self,
        request_id: str,
        file_path: str,
        file_name: str,
        file_size: int,
        uploaded_by: str
    ) -> bool:
        """Upload receipt for a reimbursement request."""
        try:
            receipt_data = {
                "file_path": file_path,
                "file_name": file_name,
                "file_size": file_size,
                "uploaded_by": uploaded_by,
                "uploaded_at": datetime.utcnow()
            }
            
            result = await self._get_reimbursements_collection().update_one(
                {"request_id": request_id},
                {
                    "$push": {"receipts": receipt_data},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Uploaded receipt for reimbursement: {request_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error uploading receipt for reimbursement {request_id}: {e}")
            return False

    # ReimbursementQueryRepository Methods
    async def get_approved(self) -> List[Reimbursement]:
        """Get all approved reimbursements."""
        try:
            cursor = await self._get_reimbursements_collection().find(
                {"status": "approved"}
            ).sort("approval.approved_at", DESCENDING)
            
            documents = await cursor.to_list(length=None)
            
            reimbursements = []
            for doc in documents:
                reimbursement = self._document_to_reimbursement(doc)
                if reimbursement:
                    reimbursements.append(reimbursement)
            
            return reimbursements
            
        except Exception as e:
            logger.error(f"Error getting approved reimbursements: {e}")
            return []

    async def get_paid(self) -> List[Reimbursement]:
        """Get all paid reimbursements."""
        try:
            cursor = await self._get_reimbursements_collection().find(
                {"status": "paid"}
            ).sort("payment.paid_at", DESCENDING)
            
            documents = await cursor.to_list(length=None)
            
            reimbursements = []
            for doc in documents:
                reimbursement = self._document_to_reimbursement(doc)
                if reimbursement:
                    reimbursements.append(reimbursement)
            
            return reimbursements
            
        except Exception as e:
            logger.error(f"Error getting paid reimbursements: {e}")
            return []

    async def get_by_reimbursement_type(self, type_id: str) -> List[Reimbursement]:
        """Get reimbursements by type."""
        try:
            cursor = await self._get_reimbursements_collection().find(
                {"reimbursement_type.type_id": type_id}
            ).sort("created_at", DESCENDING)
            
            documents = await cursor.to_list(length=None)
            
            reimbursements = []
            for doc in documents:
                reimbursement = self._document_to_reimbursement(doc)
                if reimbursement:
                    reimbursements.append(reimbursement)
            
            return reimbursements
            
        except Exception as e:
            logger.error(f"Error getting reimbursements by type {type_id}: {e}")
            return []

    async def get_employee_reimbursements_by_period(
        self,
        employee_id: str,
        start_date: datetime,
        end_date: datetime,
        reimbursement_type_id: Optional[str] = None
    ) -> List[Reimbursement]:
        """Get employee reimbursements for a specific period."""
        try:
            query = {
                "employee_id": employee_id,
                "created_at": {"$gte": start_date, "$lte": end_date}
            }
            
            if reimbursement_type_id:
                query["reimbursement_type.type_id"] = reimbursement_type_id
            
            cursor = await self._get_reimbursements_collection().find(query).sort("created_at", DESCENDING)
            documents = await cursor.to_list(length=None)
            
            reimbursements = []
            for doc in documents:
                reimbursement = self._document_to_reimbursement(doc)
                if reimbursement:
                    reimbursements.append(reimbursement)
            
            return reimbursements
            
        except Exception as e:
            logger.error(f"Error getting employee reimbursements by period: {e}")
            return []

    # ReimbursementAnalyticsRepository Methods
    async def get_employee_statistics(
        self,
        employee_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get statistics for specific employee."""
        try:
            query = {"employee_id": employee_id}
            
            if start_date and end_date:
                query["created_at"] = {"$gte": start_date, "$lte": end_date}
            
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": None,
                        "total_requests": {"$sum": 1},
                        "total_amount": {"$sum": "$amount.value"},
                        "approved_requests": {
                            "$sum": {"$cond": [{"$eq": ["$status", "approved"]}, 1, 0]}
                        },
                        "approved_amount": {
                            "$sum": {"$cond": [{"$eq": ["$status", "approved"]}, "$amount.value", 0]}
                        },
                        "paid_amount": {
                            "$sum": {"$cond": [{"$eq": ["$status", "paid"]}, "$amount.value", 0]}
                        },
                        "pending_amount": {
                            "$sum": {"$cond": [{"$in": ["$status", ["submitted", "pending"]]}, "$amount.value", 0]}
                        },
                        "rejected_amount": {
                            "$sum": {"$cond": [{"$eq": ["$status", "rejected"]}, "$amount.value", 0]}
                        }
                    }
                }
            ]
            
            cursor = await self._get_reimbursements_collection().aggregate(pipeline)
            results = await cursor.to_list(length=1)
            
            if results:
                return results[0]
            
            return {
                "total_requests": 0,
                "total_amount": 0,
                "approved_requests": 0,
                "approved_amount": 0,
                "paid_amount": 0,
                "pending_amount": 0,
                "rejected_amount": 0
            }
            
        except Exception as e:
            logger.error(f"Error getting employee statistics: {e}")
            return {}

    async def get_category_wise_spending(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Decimal]:
        """Get spending breakdown by category."""
        try:
            query = {"status": {"$in": ["approved", "paid"]}}
            
            if start_date and end_date:
                query["created_at"] = {"$gte": start_date, "$lte": end_date}
            
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$reimbursement_type.category",
                        "total_amount": {"$sum": "$amount.value"}
                    }
                }
            ]
            
            cursor = await self._get_reimbursements_collection().aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            category_spending = {}
            for result in results:
                category = result["_id"] or "uncategorized"
                amount = Decimal(str(result["total_amount"]))
                category_spending[category] = amount
            
            return category_spending
            
        except Exception as e:
            logger.error(f"Error getting category wise spending: {e}")
            return {}

    async def get_monthly_trends(self, months: int = 12) -> Dict[str, Dict[str, Any]]:
        """Get monthly spending trends."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date.replace(month=end_date.month-months) if end_date.month > months else end_date.replace(year=end_date.year-1, month=12+end_date.month-months)
            
            pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$created_at"},
                            "month": {"$month": "$created_at"}
                        },
                        "total_amount": {"$sum": "$amount.value"},
                        "total_requests": {"$sum": 1},
                        "approved_amount": {
                            "$sum": {"$cond": [{"$eq": ["$status", "approved"]}, "$amount.value", 0]}
                        },
                        "approved_requests": {
                            "$sum": {"$cond": [{"$eq": ["$status", "approved"]}, 1, 0]}
                        }
                    }
                },
                {"$sort": {"_id.year": 1, "_id.month": 1}}
            ]
            
            cursor = await self._get_reimbursements_collection().aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            trends = {}
            for result in results:
                month_key = f"{result['_id']['year']}-{result['_id']['month']:02d}"
                trends[month_key] = {
                    "total_amount": result["total_amount"],
                    "total_requests": result["total_requests"],
                    "approved_amount": result["approved_amount"],
                    "approved_requests": result["approved_requests"]
                }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting monthly trends: {e}")
            return {}

    async def get_approval_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get approval metrics and turnaround times."""
        try:
            query = {}
            
            if start_date and end_date:
                query["created_at"] = {"$gte": start_date, "$lte": end_date}
            
            pipeline = [
                {"$match": query},
                {
                    "$project": {
                        "status": 1,
                        "created_at": 1,
                        "approved_at": "$approval.approved_at",
                        "rejected_at": "$rejection.rejected_at",
                        "turnaround_time": {
                            "$cond": [
                                {"$ne": ["$approval.approved_at", None]},
                                {"$subtract": ["$approval.approved_at", "$created_at"]},
                                {"$cond": [
                                    {"$ne": ["$rejection.rejected_at", None]},
                                    {"$subtract": ["$rejection.rejected_at", "$created_at"]},
                                    None
                                ]}
                            ]
                        }
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_requests": {"$sum": 1},
                        "approved_requests": {
                            "$sum": {"$cond": [{"$eq": ["$status", "approved"]}, 1, 0]}
                        },
                        "rejected_requests": {
                            "$sum": {"$cond": [{"$eq": ["$status", "rejected"]}, 1, 0]}
                        },
                        "avg_turnaround_ms": {"$avg": "$turnaround_time"}
                    }
                }
            ]
            
            cursor = await self._get_reimbursements_collection().aggregate(pipeline)
            results = await cursor.to_list(length=1)
            
            if results:
                stats = results[0]
                avg_turnaround_ms = stats.get("avg_turnaround_ms", 0)
                avg_turnaround_days = (avg_turnaround_ms / (1000 * 60 * 60 * 24)) if avg_turnaround_ms else 0
                
                return {
                    "total_requests": stats.get("total_requests", 0),
                    "approved_requests": stats.get("approved_requests", 0),
                    "rejected_requests": stats.get("rejected_requests", 0),
                    "approval_rate": (stats.get("approved_requests", 0) / max(stats.get("total_requests", 1), 1)) * 100,
                    "rejection_rate": (stats.get("rejected_requests", 0) / max(stats.get("total_requests", 1), 1)) * 100,
                    "average_turnaround_days": round(avg_turnaround_days, 2)
                }
            
            return {
                "total_requests": 0,
                "approved_requests": 0,
                "rejected_requests": 0,
                "approval_rate": 0,
                "rejection_rate": 0,
                "average_turnaround_days": 0
            }
            
        except Exception as e:
            logger.error(f"Error getting approval metrics: {e}")
            return {}

    async def get_top_spenders(
        self,
        limit: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get top spending employees."""
        try:
            query = {"status": {"$in": ["approved", "paid"]}}
            
            if start_date and end_date:
                query["created_at"] = {"$gte": start_date, "$lte": end_date}
            
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$employee_id",
                        "total_amount": {"$sum": "$amount.value"},
                        "total_requests": {"$sum": 1}
                    }
                },
                {"$sort": {"total_amount": -1}},
                {"$limit": limit}
            ]
            
            cursor = await self._get_reimbursements_collection().aggregate(pipeline)
            results = await cursor.to_list(length=limit)
            
            top_spenders = []
            for result in results:
                top_spenders.append({
                    "employee_id": result["_id"],
                    "total_amount": result["total_amount"],
                    "total_requests": result["total_requests"]
                })
            
            return top_spenders
            
        except Exception as e:
            logger.error(f"Error getting top spenders: {e}")
            return []

    async def get_compliance_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get compliance report with policy violations."""
        try:
            query = {}
            
            if start_date and end_date:
                query["created_at"] = {"$gte": start_date, "$lte": end_date}
            
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": None,
                        "total_requests": {"$sum": 1},
                        "requests_without_receipts": {
                            "$sum": {"$cond": [{"$eq": [{"$size": {"$ifNull": ["$receipts", []]}}, 0]}, 1, 0]}
                        },
                        "high_value_requests": {
                            "$sum": {"$cond": [{"$gt": ["$amount.value", 10000]}, 1, 0]}
                        },
                        "requests_over_limit": {
                            "$sum": {"$cond": [{"$gt": ["$amount.value", 50000]}, 1, 0]}
                        }
                    }
                }
            ]
            
            cursor = await self._get_reimbursements_collection().aggregate(pipeline)
            results = await cursor.to_list(length=1)
            
            if results:
                stats = results[0]
                total = stats.get("total_requests", 1)
                compliance_rate = ((total - stats.get("requests_without_receipts", 0) - stats.get("requests_over_limit", 0)) / total) * 100
                
                return {
                    "total_requests": total,
                    "requests_without_receipts": stats.get("requests_without_receipts", 0),
                    "high_value_requests": stats.get("high_value_requests", 0),
                    "requests_over_limit": stats.get("requests_over_limit", 0),
                    "compliance_rate": round(compliance_rate, 2)
                }
            
            return {
                "total_requests": 0,
                "requests_without_receipts": 0,
                "high_value_requests": 0,
                "requests_over_limit": 0,
                "compliance_rate": 100
            }
            
        except Exception as e:
            logger.error(f"Error getting compliance report: {e}")
            return {}

    async def get_payment_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get payment method analytics."""
        try:
            query = {"status": "paid"}
            
            if start_date and end_date:
                query["payment.paid_at"] = {"$gte": start_date, "$lte": end_date}
            
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$payment.method",
                        "count": {"$sum": 1},
                        "total_amount": {"$sum": "$amount.value"}
                    }
                }
            ]
            
            cursor = await self._get_reimbursements_collection().aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            payment_methods = {}
            total_paid_requests = 0
            total_paid_amount = 0
            
            for result in results:
                method = result["_id"] or "unknown"
                count = result["count"]
                amount = result["total_amount"]
                
                payment_methods[method] = {
                    "count": count,
                    "total_amount": amount
                }
                
                total_paid_requests += count
                total_paid_amount += amount
            
            return {
                "payment_methods": payment_methods,
                "total_paid_requests": total_paid_requests,
                "total_paid_amount": total_paid_amount
            }
            
        except Exception as e:
            logger.error(f"Error getting payment analytics: {e}")
            return {}

    # ReimbursementReportRepository Methods
    async def generate_employee_report(
        self,
        employee_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate detailed employee reimbursement report."""
        try:
            reimbursements = await self.get_employee_reimbursements_by_period(
                employee_id, start_date, end_date
            )
            stats = await self.get_employee_statistics(employee_id, start_date, end_date)
            
            return {
                "employee_id": employee_id,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "statistics": stats,
                "reimbursements": [
                    self._reimbursement_to_document(r) for r in reimbursements
                ],
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating employee report: {e}")
            return {}

    async def generate_department_report(
        self,
        department: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate department-wise reimbursement report."""
        try:
            pipeline = [
                {
                    "$match": {
                        "department": department,
                        "created_at": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$employee_id",
                        "total_amount": {"$sum": "$amount.value"},
                        "total_requests": {"$sum": 1},
                        "approved_amount": {
                            "$sum": {"$cond": [{"$eq": ["$status", "approved"]}, "$amount.value", 0]}
                        }
                    }
                }
            ]
            
            cursor = await self._get_reimbursements_collection().aggregate(pipeline)
            employee_stats = await cursor.to_list(length=None)
            
            total_department_amount = sum(emp["total_amount"] for emp in employee_stats)
            total_department_requests = sum(emp["total_requests"] for emp in employee_stats)
            
            return {
                "department": department,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "total_amount": total_department_amount,
                "total_requests": total_department_requests,
                "employee_breakdown": employee_stats,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating department report: {e}")
            return {}

    async def generate_tax_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate tax-related reimbursement report."""
        try:
            pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": start_date, "$lte": end_date},
                        "status": {"$in": ["approved", "paid"]}
                    }
                },
                {
                    "$group": {
                        "_id": "$reimbursement_type.type_id",
                        "total_amount": {"$sum": "$amount.value"},
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            cursor = await self._get_reimbursements_collection().aggregate(pipeline)
            type_breakdown = await cursor.to_list(length=None)
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "type_breakdown": type_breakdown,
                "total_taxable_amount": sum(item["total_amount"] for item in type_breakdown),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating tax report: {e}")
            return {}

    async def generate_audit_trail(self, request_id: str) -> List[Dict[str, Any]]:
        """Generate audit trail for a reimbursement request."""
        try:
            reimbursement = await self.get_by_id(request_id)
            
            if not reimbursement:
                return []
            
            reimbursement_doc = self._reimbursement_to_document(reimbursement)
            audit_trail = []
            
            # Creation event
            audit_trail.append({
                "timestamp": reimbursement_doc.get("created_at"),
                "event": "created",
                "user": reimbursement_doc.get("employee_id"),
                "details": {
                    "amount": reimbursement_doc.get("amount", {}).get("value"),
                    "type": reimbursement_doc.get("reimbursement_type", {}).get("type_id")
                }
            })
            
            # Submission event
            if reimbursement_doc.get("submitted_at"):
                audit_trail.append({
                    "timestamp": reimbursement_doc.get("submitted_at"),
                    "event": "submitted",
                    "user": reimbursement_doc.get("submitted_by"),
                    "details": {}
                })
            
            # Approval event
            approval = reimbursement_doc.get("approval", {})
            if approval.get("approved_at"):
                audit_trail.append({
                    "timestamp": approval.get("approved_at"),
                    "event": "approved",
                    "user": approval.get("approved_by"),
                    "details": {
                        "approved_amount": approval.get("approved_amount"),
                        "comments": approval.get("comments")
                    }
                })
            
            # Rejection event
            rejection = reimbursement_doc.get("rejection", {})
            if rejection.get("rejected_at"):
                audit_trail.append({
                    "timestamp": rejection.get("rejected_at"),
                    "event": "rejected",
                    "user": rejection.get("rejected_by"),
                    "details": {"reason": rejection.get("reason")}
                })
            
            # Payment event
            payment = reimbursement_doc.get("payment", {})
            if payment.get("paid_at"):
                audit_trail.append({
                    "timestamp": payment.get("paid_at"),
                    "event": "paid",
                    "user": payment.get("paid_by"),
                    "details": {
                        "payment_method": payment.get("method"),
                        "payment_reference": payment.get("reference")
                    }
                })
            
            # Sort by timestamp
            audit_trail.sort(key=lambda x: x["timestamp"] or datetime.min)
            
            return audit_trail
            
        except Exception as e:
            logger.error(f"Error generating audit trail: {e}")
            return []

    async def export_to_excel(
        self,
        filters: ReimbursementSearchFiltersDTO,
        file_path: str
    ) -> str:
        """Export reimbursement data to Excel."""
        try:
            import pandas as pd
            
            # Get reimbursements based on filters
            reimbursements = await self.search(filters)
            
            if not reimbursements:
                return "No data to export"
            
            # Convert to DataFrame
            data = []
            for reimbursement in reimbursements:
                reimbursement_doc = self._reimbursement_to_document(reimbursement)
                # Flatten the document for Excel export
                flat_data = {
                    "request_id": reimbursement_doc.get("request_id"),
                    "employee_id": reimbursement_doc.get("employee_id"),
                    "amount": reimbursement_doc.get("amount", {}).get("value"),
                    "currency": reimbursement_doc.get("amount", {}).get("currency"),
                    "status": reimbursement_doc.get("status"),
                    "type": reimbursement_doc.get("reimbursement_type", {}).get("name"),
                    "description": reimbursement_doc.get("description"),
                    "created_at": reimbursement_doc.get("created_at"),
                    "submitted_at": reimbursement_doc.get("submitted_at"),
                    "approved_at": reimbursement_doc.get("approval", {}).get("approved_at"),
                    "paid_at": reimbursement_doc.get("payment", {}).get("paid_at")
                }
                data.append(flat_data)
            
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            
            return f"Data exported successfully to {file_path}"
            
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            return f"Export failed: {str(e)}"

    # ReimbursementTypeAnalyticsRepository Methods
    async def get_usage_statistics(self) -> Dict[str, Any]:
        """Get reimbursement type usage statistics."""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$reimbursement_type.type_id",
                        "count": {"$sum": 1},
                        "total_amount": {"$sum": "$amount.value"}
                    }
                },
                {"$sort": {"count": -1}}
            ]
            
            cursor = await self._get_reimbursements_collection().aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            return {
                "type_usage": results,
                "total_types": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error getting usage statistics: {e}")
            return {}

    async def get_category_breakdown(self) -> Dict[str, int]:
        """Get breakdown by category."""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$reimbursement_type.category",
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            cursor = await self._get_reimbursement_types_collection().aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            return {
                result["_id"] or "uncategorized": result["count"]
                for result in results
            }
            
        except Exception as e:
            logger.error(f"Error getting category breakdown: {e}")
            return {}

    async def get_approval_level_distribution(self) -> Dict[str, int]:
        """Get approval level distribution."""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$approval_level",
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            cursor = await self._get_reimbursement_types_collection().aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            return {
                result["_id"] or "manager": result["count"]
                for result in results
            }
            
        except Exception as e:
            logger.error(f"Error getting approval level distribution: {e}")
            return {}

    # Composite Repository Properties Implementation
    @property
    def reimbursement_types(self) -> 'ReimbursementTypeQueryRepository':
        """Get reimbursement type query repository"""
        return self

    @property
    def reimbursement_type_commands(self) -> 'ReimbursementTypeCommandRepository':
        """Get reimbursement type command repository"""
        return self

    @property
    def reimbursements(self) -> 'ReimbursementQueryRepository':
        """Get reimbursement query repository"""
        return self

    @property
    def reimbursement_commands(self) -> 'ReimbursementCommandRepository':
        """Get reimbursement command repository"""
        return self

    @property
    def analytics(self) -> 'ReimbursementAnalyticsRepository':
        """Get analytics repository"""
        return self

    @property
    def reports(self) -> 'ReimbursementReportRepository':
        """Get reports repository"""
        return self 