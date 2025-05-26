"""
MongoDB Database Service for Taxation System
Handles all database operations for the re-architected taxation system
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
import uuid
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database
from bson import ObjectId
import logging

from models.taxation import Taxation
from models.salary_management import SalaryChange, SalaryProjection
from events.tax_events import TaxEvent
from strategies.tax_calculation_strategies import TaxCalculationResult

logger = logging.getLogger(__name__)

class MongoDBTaxationDatabase:
    """MongoDB database service for taxation system"""
    
    def __init__(self, connection_string: str, database_name: str):
        """Initialize MongoDB connection"""
        self.client = MongoClient(connection_string)
        self.db: Database = self.client[database_name]
        
        # Collection references
        self.taxation_collection: Collection = self.db.taxation
        self.tax_events_collection: Collection = self.db.tax_events
        self.salary_changes_collection: Collection = self.db.salary_change_records
        self.tax_results_collection: Collection = self.db.tax_calculation_results
        self.salary_projections_collection: Collection = self.db.salary_projections
        
        # Create indexes
        self._create_indexes()
    
    def _create_indexes(self):
        """Create necessary indexes for optimal performance"""
        try:
            # Taxation collection indexes
            self.taxation_collection.create_index([("emp_id", ASCENDING)])
            self.taxation_collection.create_index([("tax_year", ASCENDING)])
            self.taxation_collection.create_index([("regime", ASCENDING)])
            
            # Tax events collection indexes
            self.tax_events_collection.create_index([("employee_id", ASCENDING)])
            self.tax_events_collection.create_index([("event_type", ASCENDING)])
            self.tax_events_collection.create_index([("status", ASCENDING)])
            self.tax_events_collection.create_index([("event_date", DESCENDING)])
            self.tax_events_collection.create_index([("priority", ASCENDING)])
            
            # Salary changes collection indexes
            self.salary_changes_collection.create_index([("employee_id", ASCENDING)])
            self.salary_changes_collection.create_index([("effective_date", DESCENDING)])
            self.salary_changes_collection.create_index([("status", ASCENDING)])
            
            # Tax results collection indexes
            self.tax_results_collection.create_index([("employee_id", ASCENDING)])
            self.tax_results_collection.create_index([("tax_year", ASCENDING)])
            self.tax_results_collection.create_index([("regime", ASCENDING)])
            self.tax_results_collection.create_index([("calculation_date", DESCENDING)])
            
            # Salary projections collection indexes
            self.salary_projections_collection.create_index([("employee_id", ASCENDING)])
            self.salary_projections_collection.create_index([("tax_year", ASCENDING)])
            
            logger.info("MongoDB indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")
    
    # ========== TAXATION OPERATIONS ==========
    
    def save_taxation(self, taxation_data: Dict[str, Any], hostname: str) -> Dict[str, Any]:
        """Save or update taxation data"""
        try:
            # Add hostname and timestamps
            taxation_data["hostname"] = hostname
            taxation_data["updated_at"] = datetime.now()
            
            if "created_at" not in taxation_data:
                taxation_data["created_at"] = datetime.now()
            
            # Convert date strings to datetime objects
            taxation_data = self._convert_dates_for_storage(taxation_data)
            
            # Upsert based on emp_id and hostname
            filter_query = {
                "emp_id": taxation_data["emp_id"],
                "hostname": hostname
            }
            
            result = self.taxation_collection.replace_one(
                filter_query,
                taxation_data,
                upsert=True
            )
            
            if result.upserted_id:
                taxation_data["_id"] = result.upserted_id
                logger.info(f"Created new taxation record for {taxation_data['emp_id']}")
            else:
                logger.info(f"Updated taxation record for {taxation_data['emp_id']}")
            
            return taxation_data
            
        except Exception as e:
            logger.error(f"Error saving taxation data: {str(e)}")
            raise
    
    def get_taxation_by_emp_id(self, emp_id: str, hostname: str) -> Dict[str, Any]:
        """Get taxation data by employee ID"""
        try:
            result = self.taxation_collection.find_one({
                "emp_id": emp_id,
                "hostname": hostname
            })
            
            if not result:
                raise ValueError(f"Taxation data not found for employee {emp_id}")
            
            # Convert ObjectId to string and dates back to strings
            result = self._convert_dates_from_storage(result)
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving taxation data: {str(e)}")
            raise
    
    def get_all_taxation_records(self, hostname: str, 
                               tax_year: Optional[str] = None,
                               regime: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all taxation records with optional filters"""
        try:
            filter_query = {"hostname": hostname}
            
            if tax_year:
                filter_query["tax_year"] = tax_year
            if regime:
                filter_query["regime"] = regime
            
            results = list(self.taxation_collection.find(filter_query))
            
            # Convert dates and ObjectIds
            return [self._convert_dates_from_storage(record) for record in results]
            
        except Exception as e:
            logger.error(f"Error retrieving taxation records: {str(e)}")
            raise
    
    # ========== TAX EVENTS OPERATIONS ==========
    
    def save_tax_event(self, event: TaxEvent) -> bool:
        """Save tax event to database"""
        try:
            event_data = event.to_dict()
            event_data["created_at"] = datetime.now()
            event_data["updated_at"] = datetime.now()
            
            # Convert date strings to datetime objects
            event_data = self._convert_dates_for_storage(event_data)
            
            result = self.tax_events_collection.insert_one(event_data)
            
            logger.info(f"Saved tax event {event.id} for employee {event.employee_id}")
            return bool(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error saving tax event: {str(e)}")
            return False
    
    def get_events_by_employee(self, employee_id: str, 
                             event_types: Optional[List[str]] = None) -> List[TaxEvent]:
        """Get tax events for an employee"""
        try:
            filter_query = {"employee_id": employee_id}
            
            if event_types:
                filter_query["event_type"] = {"$in": event_types}
            
            results = list(self.tax_events_collection.find(filter_query).sort("event_date", DESCENDING))
            
            # Convert to TaxEvent objects
            events = []
            for result in results:
                result = self._convert_dates_from_storage(result)
                events.append(TaxEvent.from_dict(result))
            
            return events
            
        except Exception as e:
            logger.error(f"Error retrieving tax events: {str(e)}")
            return []
    
    def get_pending_events(self) -> List[TaxEvent]:
        """Get all pending tax events"""
        try:
            results = list(self.tax_events_collection.find({
                "status": "pending"
            }).sort("priority", ASCENDING).sort("created_at", ASCENDING))
            
            # Convert to TaxEvent objects
            events = []
            for result in results:
                result = self._convert_dates_from_storage(result)
                events.append(TaxEvent.from_dict(result))
            
            return events
            
        except Exception as e:
            logger.error(f"Error retrieving pending events: {str(e)}")
            return []
    
    def update_event_status(self, event_id: str, status: str, 
                          error_message: Optional[str] = None) -> bool:
        """Update event status"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now()
            }
            
            if status == "completed":
                update_data["processed_at"] = datetime.now()
            
            if error_message:
                update_data["error_message"] = error_message
            
            result = self.tax_events_collection.update_one(
                {"id": event_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating event status: {str(e)}")
            return False
    
    # ========== SALARY CHANGE OPERATIONS ==========
    
    def save_salary_change(self, salary_change: SalaryChange) -> bool:
        """Save salary change record"""
        try:
            change_data = salary_change.to_dict()
            change_data["created_at"] = datetime.now()
            change_data["updated_at"] = datetime.now()
            
            # Convert date strings to datetime objects
            change_data = self._convert_dates_for_storage(change_data)
            
            result = self.salary_changes_collection.insert_one(change_data)
            
            logger.info(f"Saved salary change {salary_change.id} for employee {salary_change.employee_id}")
            return bool(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error saving salary change: {str(e)}")
            return False
    
    def get_salary_changes_by_employee(self, employee_id: str, 
                                     tax_year: Optional[str] = None) -> List[SalaryChange]:
        """Get salary changes for an employee"""
        try:
            filter_query = {"employee_id": employee_id}
            
            if tax_year:
                # Parse tax year to get date range
                start_year = int(tax_year.split('-')[0])
                start_date = datetime(start_year, 4, 1)  # April 1st
                end_date = datetime(start_year + 1, 3, 31)  # March 31st
                
                filter_query["effective_date"] = {
                    "$gte": start_date,
                    "$lte": end_date
                }
            
            results = list(self.salary_changes_collection.find(filter_query).sort("effective_date", DESCENDING))
            
            # Convert to SalaryChange objects
            changes = []
            for result in results:
                result = self._convert_dates_from_storage(result)
                changes.append(SalaryChange.from_dict(result))
            
            return changes
            
        except Exception as e:
            logger.error(f"Error retrieving salary changes: {str(e)}")
            return []
    
    # ========== TAX CALCULATION RESULTS OPERATIONS ==========
    
    def save_tax_calculation_result(self, result: TaxCalculationResult) -> bool:
        """Save tax calculation result"""
        try:
            result_data = result.to_dict()
            result_data["created_at"] = datetime.now()
            
            # Convert date strings to datetime objects
            result_data = self._convert_dates_for_storage(result_data)
            
            # Upsert based on employee_id, tax_year, and regime
            filter_query = {
                "employee_id": result.employee_id,
                "tax_year": result_data.get("tax_year", ""),
                "regime": result.regime
            }
            
            db_result = self.tax_results_collection.replace_one(
                filter_query,
                result_data,
                upsert=True
            )
            
            logger.info(f"Saved tax calculation result for employee {result.employee_id}")
            return bool(db_result.upserted_id or db_result.modified_count)
            
        except Exception as e:
            logger.error(f"Error saving tax calculation result: {str(e)}")
            return False
    
    def get_tax_calculation_results(self, employee_id: str, 
                                  tax_year: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get tax calculation results for an employee"""
        try:
            filter_query = {"employee_id": employee_id}
            
            if tax_year:
                filter_query["tax_year"] = tax_year
            
            results = list(self.tax_results_collection.find(filter_query).sort("calculation_date", DESCENDING))
            
            # Convert dates and ObjectIds
            return [self._convert_dates_from_storage(record) for record in results]
            
        except Exception as e:
            logger.error(f"Error retrieving tax calculation results: {str(e)}")
            return []
    
    # ========== SALARY PROJECTION OPERATIONS ==========
    
    def save_salary_projection(self, projection: SalaryProjection) -> bool:
        """Save salary projection"""
        try:
            projection_data = projection.to_dict()
            projection_data["created_at"] = datetime.now()
            projection_data["updated_at"] = datetime.now()
            
            # Convert date strings to datetime objects
            projection_data = self._convert_dates_for_storage(projection_data)
            
            # Upsert based on employee_id and tax_year
            filter_query = {
                "employee_id": projection.employee_id,
                "tax_year": projection.tax_year
            }
            
            result = self.salary_projections_collection.replace_one(
                filter_query,
                projection_data,
                upsert=True
            )
            
            logger.info(f"Saved salary projection for employee {projection.employee_id}")
            return bool(result.upserted_id or result.modified_count)
            
        except Exception as e:
            logger.error(f"Error saving salary projection: {str(e)}")
            return False
    
    def get_salary_projection(self, employee_id: str, tax_year: str) -> Optional[SalaryProjection]:
        """Get salary projection for an employee"""
        try:
            result = self.salary_projections_collection.find_one({
                "employee_id": employee_id,
                "tax_year": tax_year
            })
            
            if not result:
                return None
            
            # Convert dates and create SalaryProjection object
            result = self._convert_dates_from_storage(result)
            return SalaryProjection.from_dict(result)
            
        except Exception as e:
            logger.error(f"Error retrieving salary projection: {str(e)}")
            return None
    
    # ========== UTILITY METHODS ==========
    
    def _convert_dates_for_storage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert date strings to datetime objects for MongoDB storage"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and self._is_date_string(value):
                    try:
                        data[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    except ValueError:
                        pass  # Keep as string if conversion fails
                elif isinstance(value, dict):
                    data[key] = self._convert_dates_for_storage(value)
                elif isinstance(value, list):
                    data[key] = [self._convert_dates_for_storage(item) if isinstance(item, dict) else item for item in value]
        return data
    
    def _convert_dates_from_storage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert datetime objects back to strings for API responses"""
        if isinstance(data, dict):
            # Convert ObjectId to string
            if "_id" in data:
                data["_id"] = str(data["_id"])
            
            for key, value in data.items():
                if isinstance(value, datetime):
                    data[key] = value.isoformat()
                elif isinstance(value, dict):
                    data[key] = self._convert_dates_from_storage(value)
                elif isinstance(value, list):
                    data[key] = [self._convert_dates_from_storage(item) if isinstance(item, dict) else item for item in value]
        return data
    
    def _is_date_string(self, value: str) -> bool:
        """Check if string looks like a date"""
        date_patterns = [
            'T',  # ISO format with time
            '-',  # Date format
        ]
        return any(pattern in value for pattern in date_patterns) and len(value) >= 10
    
    # ========== ANALYTICS AND REPORTING ==========
    
    def get_tax_analytics(self, hostname: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get tax analytics data"""
        try:
            base_filter = {"hostname": hostname}
            if filters:
                base_filter.update(filters)
            
            # Total employees
            total_employees = self.taxation_collection.count_documents(base_filter)
            
            # Regime distribution
            regime_pipeline = [
                {"$match": base_filter},
                {"$group": {"_id": "$regime", "count": {"$sum": 1}}}
            ]
            regime_distribution = {doc["_id"]: doc["count"] for doc in self.taxation_collection.aggregate(regime_pipeline)}
            
            # Average tax liability
            tax_pipeline = [
                {"$match": base_filter},
                {"$group": {
                    "_id": None,
                    "avg_tax": {"$avg": "$total_tax"},
                    "total_tax": {"$sum": "$total_tax"},
                    "min_tax": {"$min": "$total_tax"},
                    "max_tax": {"$max": "$total_tax"}
                }}
            ]
            tax_stats = list(self.taxation_collection.aggregate(tax_pipeline))
            tax_data = tax_stats[0] if tax_stats else {}
            
            return {
                "total_employees": total_employees,
                "regime_distribution": regime_distribution,
                "tax_statistics": tax_data,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating tax analytics: {str(e)}")
            return {}
    
    def get_compliance_metrics(self, hostname: str, tax_year: str) -> Dict[str, Any]:
        """Get compliance metrics for a tax year"""
        try:
            base_filter = {"hostname": hostname, "tax_year": tax_year}
            
            # Form 16 generation status
            form16_pipeline = [
                {"$match": base_filter},
                {"$group": {
                    "_id": "$filing_status",
                    "count": {"$sum": 1}
                }}
            ]
            filing_status = {doc["_id"]: doc["count"] for doc in self.taxation_collection.aggregate(form16_pipeline)}
            
            # TDS compliance
            tds_pipeline = [
                {"$match": base_filter},
                {"$group": {
                    "_id": None,
                    "total_tax_due": {"$sum": "$tax_due"},
                    "total_tax_paid": {"$sum": "$tax_paid"},
                    "employees_with_pending_tax": {"$sum": {"$cond": [{"$gt": ["$tax_due", 0]}, 1, 0]}}
                }}
            ]
            tds_stats = list(self.taxation_collection.aggregate(tds_pipeline))
            tds_data = tds_stats[0] if tds_stats else {}
            
            return {
                "tax_year": tax_year,
                "filing_status_distribution": filing_status,
                "tds_compliance": tds_data,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating compliance metrics: {str(e)}")
            return {}
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed") 