"""
MongoDB Reporting Repository Implementation
Concrete implementation of reporting repository using MongoDB
"""

import logging
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from pymongo.errors import PyMongoError

from app.application.interfaces.repositories.reporting_repository import ReportingRepository
from app.domain.entities.report import Report, ReportType, ReportFormat, ReportStatus
from app.domain.value_objects.report_id import ReportId
from app.application.dto.reporting_dto import ReportSearchFiltersDTO
from app.infrastructure.database.database_connector import DatabaseConnector

logger = logging.getLogger(__name__)


class MongoDBReportingRepository(ReportingRepository):
    """
    MongoDB implementation of reporting repository.
    
    Handles persistence of reports in organisation-specific MongoDB collections.
    """
    
    def __init__(self, database_connector: DatabaseConnector):
        """Initialize repository with database connector."""
        self.database_connector = database_connector
        self.collection_name = "reports"
    
    async def save(self, report: Report, hostname: str) -> Report:
        """Save report to organisation-specific database."""
        try:
            logger.info(f"Saving report {report.id.value} for organisation: {hostname}")
            
            # Get organisation-specific database
            db = await self.database_connector.get_database(hostname)
            collection = db[self.collection_name]
            
            # Convert entity to document
            document = self._entity_to_document(report)
            
            if report.is_new():
                # Insert new report
                result = await collection.insert_one(document)
                logger.info(f"Inserted new report with ID: {result.inserted_id}")
            else:
                # Update existing report
                await collection.replace_one(
                    {"_id": ObjectId(report.id.value)},
                    document
                )
                logger.info(f"Updated report with ID: {report.id.value}")
            
            return report
            
        except PyMongoError as e:
            logger.error(f"MongoDB error saving report {report.id.value}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error saving report {report.id.value}: {e}")
            raise
    
    async def get_by_id(self, report_id: ReportId, hostname: str) -> Optional[Report]:
        """Get report by ID from organisation-specific database."""
        try:
            logger.info(f"Getting report {report_id.value} for organisation: {hostname}")
            
            # Get organisation-specific database
            db = await self.database_connector.get_database(hostname)
            collection = db[self.collection_name]
            
            # Find document
            document = await collection.find_one({"_id": ObjectId(report_id.value)})
            
            if document:
                return self._document_to_entity(document)
            
            logger.info(f"Report {report_id.value} not found")
            return None
            
        except PyMongoError as e:
            logger.error(f"MongoDB error getting report {report_id.value}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting report {report_id.value}: {e}")
            raise
    
    async def find_with_filters(
        self, 
        filters: ReportSearchFiltersDTO, 
        hostname: str
    ) -> Tuple[List[Report], int]:
        """Find reports with filters from organisation-specific database."""
        try:
            logger.info(f"Finding reports with filters for organisation: {hostname}")
            
            # Get organisation-specific database
            db = await self.database_connector.get_database(hostname)
            collection = db[self.collection_name]
            
            # Build query
            query = {}
            
            if filters.report_type:
                query["report_type"] = filters.report_type
            
            if filters.status:
                query["status"] = filters.status
            
            if filters.created_by:
                query["created_by"] = filters.created_by
            
            if filters.start_date or filters.end_date:
                date_query = {}
                if filters.start_date:
                    date_query["$gte"] = datetime.fromisoformat(filters.start_date.replace('Z', '+00:00'))
                if filters.end_date:
                    date_query["$lte"] = datetime.fromisoformat(filters.end_date.replace('Z', '+00:00'))
                query["created_at"] = date_query
            
            # Get total count
            total_count = await collection.count_documents(query)
            
            # Build sort
            sort_direction = 1 if filters.sort_order == "asc" else -1
            sort_criteria = [(filters.sort_by, sort_direction)]
            
            # Calculate skip
            skip = (filters.page - 1) * filters.page_size
            
            # Find documents
            cursor = collection.find(query).sort(sort_criteria).skip(skip).limit(filters.page_size)
            documents = await cursor.to_list(length=filters.page_size)
            
            # Convert to entities
            reports = [self._document_to_entity(doc) for doc in documents]
            
            logger.info(f"Found {len(reports)} reports out of {total_count} total")
            return reports, total_count
            
        except PyMongoError as e:
            logger.error(f"MongoDB error finding reports: {e}")
            raise
        except Exception as e:
            logger.error(f"Error finding reports: {e}")
            raise
    
    async def delete(self, report_id: ReportId, hostname: str) -> bool:
        """Delete report from organisation-specific database."""
        try:
            logger.info(f"Deleting report {report_id.value} for organisation: {hostname}")
            
            # Get organisation-specific database
            db = await self.database_connector.get_database(hostname)
            collection = db[self.collection_name]
            
            # Delete document
            result = await collection.delete_one({"_id": ObjectId(report_id.value)})
            
            success = result.deleted_count > 0
            if success:
                logger.info(f"Successfully deleted report {report_id.value}")
            else:
                logger.warning(f"Report {report_id.value} not found for deletion")
            
            return success
            
        except PyMongoError as e:
            logger.error(f"MongoDB error deleting report {report_id.value}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error deleting report {report_id.value}: {e}")
            raise
    
    async def get_reports_by_type(
        self, 
        report_type: str, 
        hostname: str,
        limit: int = 10
    ) -> List[Report]:
        """Get recent reports by type."""
        try:
            logger.info(f"Getting reports by type {report_type} for organisation: {hostname}")
            
            # Get organisation-specific database
            db = await self.database_connector.get_database(hostname)
            collection = db[self.collection_name]
            
            # Find documents
            cursor = collection.find({"report_type": report_type}).sort("created_at", -1).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            # Convert to entities
            reports = [self._document_to_entity(doc) for doc in documents]
            
            logger.info(f"Found {len(reports)} reports of type {report_type}")
            return reports
            
        except PyMongoError as e:
            logger.error(f"MongoDB error getting reports by type: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting reports by type: {e}")
            raise
    
    async def get_reports_by_status(
        self, 
        status: str, 
        hostname: str,
        limit: int = 10
    ) -> List[Report]:
        """Get reports by status."""
        try:
            logger.info(f"Getting reports by status {status} for organisation: {hostname}")
            
            # Get organisation-specific database
            db = await self.database_connector.get_database(hostname)
            collection = db[self.collection_name]
            
            # Find documents
            cursor = collection.find({"status": status}).sort("created_at", -1).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            # Convert to entities
            reports = [self._document_to_entity(doc) for doc in documents]
            
            logger.info(f"Found {len(reports)} reports with status {status}")
            return reports
            
        except PyMongoError as e:
            logger.error(f"MongoDB error getting reports by status: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting reports by status: {e}")
            raise
    
    async def get_user_reports(
        self, 
        created_by: str, 
        hostname: str,
        limit: int = 10
    ) -> List[Report]:
        """Get reports created by specific user."""
        try:
            logger.info(f"Getting reports by user {created_by} for organisation: {hostname}")
            
            # Get organisation-specific database
            db = await self.database_connector.get_database(hostname)
            collection = db[self.collection_name]
            
            # Find documents
            cursor = collection.find({"created_by": created_by}).sort("created_at", -1).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            # Convert to entities
            reports = [self._document_to_entity(doc) for doc in documents]
            
            logger.info(f"Found {len(reports)} reports created by {created_by}")
            return reports
            
        except PyMongoError as e:
            logger.error(f"MongoDB error getting user reports: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting user reports: {e}")
            raise
    
    async def cleanup_old_reports(
        self, 
        hostname: str,
        days_old: int = 30
    ) -> int:
        """Clean up old completed reports."""
        try:
            logger.info(f"Cleaning up reports older than {days_old} days for organisation: {hostname}")
            
            # Get organisation-specific database
            db = await self.database_connector.get_database(hostname)
            collection = db[self.collection_name]
            
            # Calculate cutoff date
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Delete old completed reports
            result = await collection.delete_many({
                "status": ReportStatus.COMPLETED.value,
                "completed_at": {"$lt": cutoff_date}
            })
            
            deleted_count = result.deleted_count
            logger.info(f"Cleaned up {deleted_count} old reports")
            return deleted_count
            
        except PyMongoError as e:
            logger.error(f"MongoDB error cleaning up reports: {e}")
            raise
        except Exception as e:
            logger.error(f"Error cleaning up reports: {e}")
            raise
    
    def _entity_to_document(self, report: Report) -> Dict[str, Any]:
        """Convert report entity to MongoDB document."""
        document = {
            "name": report.name,
            "description": report.description,
            "report_type": report.report_type.value,
            "format": report.format.value,
            "status": report.status.value,
            "parameters": report.parameters,
            "data": report.data,
            "file_path": report.file_path,
            "error_message": report.error_message,
            "created_at": report.created_at,
            "updated_at": report.updated_at,
            "completed_at": report.completed_at,
            "created_by": report.created_by,
            "organisation_id": report.organisation_id
        }
        
        # Add _id if not new
        if not report.is_new():
            document["_id"] = ObjectId(report.id.value)
        
        return document
    
    def _document_to_entity(self, document: Dict[str, Any]) -> Report:
        """Convert MongoDB document to report entity."""
        return Report(
            id=ReportId(str(document["_id"])),
            name=document["name"],
            description=document["description"],
            report_type=ReportType(document["report_type"]),
            format=ReportFormat(document["format"]),
            status=ReportStatus(document["status"]),
            parameters=document.get("parameters", {}),
            data=document.get("data"),
            file_path=document.get("file_path"),
            error_message=document.get("error_message"),
            created_at=document.get("created_at"),
            updated_at=document.get("updated_at"),
            completed_at=document.get("completed_at"),
            created_by=document.get("created_by"),
            organisation_id=document.get("organisation_id")
        ) 