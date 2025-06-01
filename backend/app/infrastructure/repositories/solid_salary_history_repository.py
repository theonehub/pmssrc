"""
SOLID Salary History Repository Implementation

This module implements the salary history repository following SOLID principles:
- Single Responsibility: Handles only salary history data operations
- Open/Closed: Extensible through interfaces without modification
- Liskov Substitution: Implements consistent interfaces
- Interface Segregation: Focused interfaces for specific operations
- Dependency Inversion: Depends on abstractions, not concretions

Author: System Architecture Team
Date: 2024
"""

import logging
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from bson import ObjectId

from app.infrastructure.database.database_connector import DatabaseConnector
from app.infrastructure.repositories.base_repository import BaseRepository
from app.application.interfaces.repositories.salary_history_repository_interface import (
    SalaryHistoryCommandRepository,
    SalaryHistoryQueryRepository,
    SalaryHistoryAnalyticsRepository
)
from app.domain.entities.salary_history import SalaryHistoryInDB
from app.application.dto.salary_history_dto import (
    SalaryHistoryCreateDTO,
    SalaryHistoryUpdateDTO,
    SalaryHistoryResponseDTO
)

logger = logging.getLogger(__name__)

class SolidSalaryHistoryRepository(
    BaseRepository,
    SalaryHistoryCommandRepository,
    SalaryHistoryQueryRepository,
    SalaryHistoryAnalyticsRepository
):
    """
    SOLID-compliant salary history repository implementation.
    
    Provides comprehensive salary history management with:
    - CRUD operations
    - Employee salary tracking
    - Tax recalculation management
    - Performance optimization
    """
    
    def __init__(self, db_connector: DatabaseConnector):
        """
        Initialize the repository with database connector.
        
        Args:
            db_connector: Database connector following DIP
        """
        super().__init__(db_connector, "salary_history")
        self.logger = logging.getLogger(__name__)
    
    async def _ensure_indexes(self, company_id: str) -> None:
        """
        Ensure necessary indexes for optimal query performance.
        
        Args:
            company_id: Company identifier
        """
        try:
            collection = await self._get_collection(company_id)
            
            # Index for employee and effective date queries
            await collection.create_index([
                ("employee_id", 1),
                ("effective_date", -1)
            ])
            
            # Index for tax recalculation queries
            await collection.create_index([
                ("tax_recalculation_required", 1),
                ("tax_recalculated_at", 1)
            ])
            
            # Index for date range queries
            await collection.create_index([
                ("effective_date", 1)
            ])
            
            # Index for salary history ID queries
            await collection.create_index([
                ("salary_history_id", 1)
            ], unique=True)
            
            self.logger.info(f"Salary history indexes ensured for company: {company_id}")
            
        except Exception as e:
            self.logger.error(f"Error ensuring salary history indexes: {str(e)}")
    
    # Command Repository Implementation
    
    async def create_salary_history(
        self, 
        salary_data: SalaryHistoryCreateDTO, 
        company_id: str
    ) -> str:
        """
        Create a new salary history entry.
        
        Args:
            salary_data: Salary history creation data
            company_id: Company identifier
            
        Returns:
            str: Created salary history ID
            
        Raises:
            ValueError: If data validation fails
            RuntimeError: If creation fails
        """
        try:
            self.logger.info(f"Creating salary history for employee {salary_data.employee_id}")
            
            # Validate required fields
            if not salary_data.employee_id:
                raise ValueError("Employee ID is required")
            if not salary_data.effective_date:
                raise ValueError("Effective date is required")
            if salary_data.basic_salary is None or salary_data.basic_salary < 0:
                raise ValueError("Valid basic salary is required")
            
            # Ensure indexes
            await self._ensure_indexes(company_id)
            
            # Prepare document
            doc = salary_data.model_dump()
            doc.update({
                "salary_history_id": str(ObjectId()),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "tax_recalculation_required": False,
                "tax_recalculated_at": None
            })
            
            # Insert document
            collection = await self._get_collection(company_id)
            result = await collection.insert_one(doc)
            
            self.logger.info(f"Created salary history {doc['salary_history_id']}")
            return doc["salary_history_id"]
            
        except Exception as e:
            self.logger.error(f"Error creating salary history: {str(e)}")
            raise RuntimeError(f"Failed to create salary history: {str(e)}")
    
    async def update_salary_history(
        self, 
        salary_history_id: str, 
        update_data: SalaryHistoryUpdateDTO, 
        company_id: str
    ) -> bool:
        """
        Update an existing salary history entry.
        
        Args:
            salary_history_id: Salary history identifier
            update_data: Update data
            company_id: Company identifier
            
        Returns:
            bool: True if update successful
            
        Raises:
            ValueError: If salary history not found
            RuntimeError: If update fails
        """
        try:
            self.logger.info(f"Updating salary history {salary_history_id}")
            
            # Check if salary history exists
            existing = await self.get_salary_history_by_id(salary_history_id, company_id)
            if not existing:
                raise ValueError(f"Salary history {salary_history_id} not found")
            
            # Prepare update document
            update_doc = update_data.model_dump(exclude_unset=True)
            update_doc["updated_at"] = datetime.now()
            
            # Update document
            collection = await self._get_collection(company_id)
            result = await collection.update_one(
                {"salary_history_id": salary_history_id},
                {"$set": update_doc}
            )
            
            if result.modified_count == 0:
                raise RuntimeError("No documents were updated")
            
            self.logger.info(f"Updated salary history {salary_history_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating salary history: {str(e)}")
            raise RuntimeError(f"Failed to update salary history: {str(e)}")
    
    async def delete_salary_history(self, salary_history_id: str, company_id: str) -> bool:
        """
        Delete a salary history entry.
        
        Args:
            salary_history_id: Salary history identifier
            company_id: Company identifier
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            ValueError: If salary history not found
            RuntimeError: If deletion fails
        """
        try:
            self.logger.info(f"Deleting salary history {salary_history_id}")
            
            # Check if salary history exists
            existing = await self.get_salary_history_by_id(salary_history_id, company_id)
            if not existing:
                raise ValueError(f"Salary history {salary_history_id} not found")
            
            # Delete document
            collection = await self._get_collection(company_id)
            result = await collection.delete_one({"salary_history_id": salary_history_id})
            
            if result.deleted_count == 0:
                raise RuntimeError("No documents were deleted")
            
            self.logger.info(f"Deleted salary history {salary_history_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting salary history: {str(e)}")
            raise RuntimeError(f"Failed to delete salary history: {str(e)}")
    
    async def mark_for_tax_recalculation(
        self, 
        employee_id: str, 
        effective_from: date, 
        company_id: str
    ) -> int:
        """
        Mark salary history entries for tax recalculation.
        
        Args:
            employee_id: Employee identifier
            effective_from: Date from which to mark for recalculation
            company_id: Company identifier
            
        Returns:
            int: Number of records marked for recalculation
        """
        try:
            collection = await self._get_collection(company_id)
            
            result = await collection.update_many(
                {
                    "employee_id": employee_id,
                    "effective_date": {"$gte": effective_from}
                },
                {
                    "$set": {
                        "tax_recalculation_required": True,
                        "updated_at": datetime.now()
                    }
                }
            )
            
            self.logger.info(f"Marked {result.modified_count} salary history records for tax recalculation")
            return result.modified_count
            
        except Exception as e:
            self.logger.error(f"Error marking for tax recalculation: {str(e)}")
            raise RuntimeError(f"Failed to mark for tax recalculation: {str(e)}")
    
    async def complete_tax_recalculation(
        self, 
        salary_history_id: str, 
        company_id: str
    ) -> bool:
        """
        Mark tax recalculation as completed for a salary history entry.
        
        Args:
            salary_history_id: Salary history identifier
            company_id: Company identifier
            
        Returns:
            bool: True if successful
        """
        try:
            collection = await self._get_collection(company_id)
            
            result = await collection.update_one(
                {"salary_history_id": salary_history_id},
                {
                    "$set": {
                        "tax_recalculation_required": False,
                        "tax_recalculated_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            self.logger.error(f"Error completing tax recalculation: {str(e)}")
            return False
    
    # Query Repository Implementation
    
    async def get_salary_history_by_id(
        self, 
        salary_history_id: str, 
        company_id: str
    ) -> Optional[SalaryHistoryResponseDTO]:
        """
        Get salary history by ID.
        
        Args:
            salary_history_id: Salary history identifier
            company_id: Company identifier
            
        Returns:
            Optional[SalaryHistoryResponseDTO]: Salary history if found
        """
        try:
            collection = await self._get_collection(company_id)
            doc = await collection.find_one({"salary_history_id": salary_history_id})
            
            if doc:
                return SalaryHistoryResponseDTO(**doc)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting salary history by ID: {str(e)}")
            raise RuntimeError(f"Failed to get salary history: {str(e)}")
    
    async def get_salary_history_by_employee(
        self, 
        employee_id: str, 
        company_id: str,
        limit: Optional[int] = None
    ) -> List[SalaryHistoryResponseDTO]:
        """
        Get salary history for an employee.
        
        Args:
            employee_id: Employee identifier
            company_id: Company identifier
            limit: Optional limit on number of records
            
        Returns:
            List[SalaryHistoryResponseDTO]: List of salary history records
        """
        try:
            collection = await self._get_collection(company_id)
            cursor = collection.find({"employee_id": employee_id}).sort("effective_date", -1)
            
            if limit:
                cursor = cursor.limit(limit)
            
            histories = []
            async for doc in cursor:
                histories.append(SalaryHistoryResponseDTO(**doc))
            
            return histories
            
        except Exception as e:
            self.logger.error(f"Error getting salary history by employee: {str(e)}")
            raise RuntimeError(f"Failed to get salary history: {str(e)}")
    
    async def get_current_salary(
        self, 
        employee_id: str, 
        as_of_date: Optional[date] = None, 
        company_id: str = "default"
    ) -> Optional[SalaryHistoryResponseDTO]:
        """
        Get current salary for an employee as of a specific date.
        
        Args:
            employee_id: Employee identifier
            as_of_date: Date to check salary as of (defaults to today)
            company_id: Company identifier
            
        Returns:
            Optional[SalaryHistoryResponseDTO]: Current salary if found
        """
        try:
            if as_of_date is None:
                as_of_date = date.today()
            
            collection = await self._get_collection(company_id)
            doc = await collection.find_one(
                {
                    "employee_id": employee_id,
                    "effective_date": {"$lte": as_of_date}
                },
                sort=[("effective_date", -1)]
            )
            
            if doc:
                return SalaryHistoryResponseDTO(**doc)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting current salary: {str(e)}")
            raise RuntimeError(f"Failed to get current salary: {str(e)}")
    
    async def get_salary_history_by_date_range(
        self, 
        employee_id: str, 
        start_date: date, 
        end_date: date, 
        company_id: str
    ) -> List[SalaryHistoryResponseDTO]:
        """
        Get salary history within a date range.
        
        Args:
            employee_id: Employee identifier
            start_date: Start date
            end_date: End date
            company_id: Company identifier
            
        Returns:
            List[SalaryHistoryResponseDTO]: List of salary history records
        """
        try:
            collection = await self._get_collection(company_id)
            cursor = collection.find({
                "employee_id": employee_id,
                "effective_date": {"$gte": start_date, "$lte": end_date}
            }).sort("effective_date", 1)
            
            histories = []
            async for doc in cursor:
                histories.append(SalaryHistoryResponseDTO(**doc))
            
            return histories
            
        except Exception as e:
            self.logger.error(f"Error getting salary history by date range: {str(e)}")
            raise RuntimeError(f"Failed to get salary history: {str(e)}")
    
    async def get_pending_tax_recalculations(
        self, 
        company_id: str,
        limit: Optional[int] = None
    ) -> List[SalaryHistoryResponseDTO]:
        """
        Get salary history entries pending tax recalculation.
        
        Args:
            company_id: Company identifier
            limit: Optional limit on number of records
            
        Returns:
            List[SalaryHistoryResponseDTO]: List of pending recalculations
        """
        try:
            collection = await self._get_collection(company_id)
            cursor = collection.find({"tax_recalculation_required": True}).sort("effective_date", 1)
            
            if limit:
                cursor = cursor.limit(limit)
            
            histories = []
            async for doc in cursor:
                histories.append(SalaryHistoryResponseDTO(**doc))
            
            return histories
            
        except Exception as e:
            self.logger.error(f"Error getting pending tax recalculations: {str(e)}")
            raise RuntimeError(f"Failed to get pending tax recalculations: {str(e)}")
    
    # Analytics Repository Implementation
    
    async def get_salary_statistics(
        self, 
        company_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get salary statistics.
        
        Args:
            company_id: Company identifier
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dict[str, Any]: Salary statistics
        """
        try:
            collection = await self._get_collection(company_id)
            
            match_stage = {}
            if start_date and end_date:
                match_stage["effective_date"] = {"$gte": start_date, "$lte": end_date}
            
            pipeline = []
            if match_stage:
                pipeline.append({"$match": match_stage})
            
            pipeline.extend([
                {
                    "$group": {
                        "_id": None,
                        "total_records": {"$sum": 1},
                        "unique_employees": {"$addToSet": "$employee_id"},
                        "avg_basic_salary": {"$avg": "$basic_salary"},
                        "min_basic_salary": {"$min": "$basic_salary"},
                        "max_basic_salary": {"$max": "$basic_salary"},
                        "total_basic_salary": {"$sum": "$basic_salary"},
                        "pending_recalculations": {
                            "$sum": {"$cond": [{"$eq": ["$tax_recalculation_required", True]}, 1, 0]}
                        }
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "total_records": 1,
                        "unique_employees_count": {"$size": "$unique_employees"},
                        "avg_basic_salary": {"$round": ["$avg_basic_salary", 2]},
                        "min_basic_salary": 1,
                        "max_basic_salary": 1,
                        "total_basic_salary": 1,
                        "pending_recalculations": 1
                    }
                }
            ])
            
            result = await collection.aggregate(pipeline).to_list(1)
            
            if result:
                return result[0]
            
            return {
                "total_records": 0,
                "unique_employees_count": 0,
                "avg_basic_salary": 0,
                "min_basic_salary": 0,
                "max_basic_salary": 0,
                "total_basic_salary": 0,
                "pending_recalculations": 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting salary statistics: {str(e)}")
            raise RuntimeError(f"Failed to get salary statistics: {str(e)}")
    
    async def get_employee_salary_trends(
        self, 
        employee_id: str, 
        company_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get salary trends for a specific employee.
        
        Args:
            employee_id: Employee identifier
            company_id: Company identifier
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dict[str, Any]: Employee salary trends
        """
        try:
            collection = await self._get_collection(company_id)
            
            match_stage = {"employee_id": employee_id}
            if start_date and end_date:
                match_stage["effective_date"] = {"$gte": start_date, "$lte": end_date}
            
            pipeline = [
                {"$match": match_stage},
                {"$sort": {"effective_date": 1}},
                {
                    "$group": {
                        "_id": None,
                        "salary_history": {
                            "$push": {
                                "effective_date": "$effective_date",
                                "basic_salary": "$basic_salary",
                                "total_salary": {"$add": ["$basic_salary", {"$ifNull": ["$allowances", 0]}]}
                            }
                        },
                        "total_changes": {"$sum": 1},
                        "avg_salary": {"$avg": "$basic_salary"},
                        "current_salary": {"$last": "$basic_salary"},
                        "initial_salary": {"$first": "$basic_salary"}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "employee_id": employee_id,
                        "salary_history": 1,
                        "total_changes": 1,
                        "avg_salary": {"$round": ["$avg_salary", 2]},
                        "current_salary": 1,
                        "initial_salary": 1,
                        "salary_growth": {
                            "$subtract": ["$current_salary", "$initial_salary"]
                        }
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(1)
            
            if result:
                return result[0]
            
            return {
                "employee_id": employee_id,
                "salary_history": [],
                "total_changes": 0,
                "avg_salary": 0,
                "current_salary": 0,
                "initial_salary": 0,
                "salary_growth": 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting employee salary trends: {str(e)}")
            raise RuntimeError(f"Failed to get employee salary trends: {str(e)}")
    
    async def get_salary_distribution(
        self, 
        company_id: str,
        as_of_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get salary distribution across all employees.
        
        Args:
            company_id: Company identifier
            as_of_date: Date to check salary as of (defaults to today)
            
        Returns:
            Dict[str, Any]: Salary distribution data
        """
        try:
            if as_of_date is None:
                as_of_date = date.today()
            
            collection = await self._get_collection(company_id)
            
            # Get current salary for each employee
            pipeline = [
                {"$match": {"effective_date": {"$lte": as_of_date}}},
                {"$sort": {"employee_id": 1, "effective_date": -1}},
                {
                    "$group": {
                        "_id": "$employee_id",
                        "current_salary": {"$first": "$basic_salary"}
                    }
                },
                {
                    "$bucket": {
                        "groupBy": "$current_salary",
                        "boundaries": [0, 25000, 50000, 75000, 100000, 150000, 200000, float('inf')],
                        "default": "Other",
                        "output": {
                            "count": {"$sum": 1},
                            "employees": {"$push": "$_id"}
                        }
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(None)
            
            return {
                "as_of_date": as_of_date.isoformat(),
                "salary_ranges": result
            }
            
        except Exception as e:
            self.logger.error(f"Error getting salary distribution: {str(e)}")
            raise RuntimeError(f"Failed to get salary distribution: {str(e)}")
    
    # Health Check Methods
    
    async def health_check(self, company_id: str) -> Dict[str, Any]:
        """
        Perform health check on the salary history repository.
        
        Args:
            company_id: Company identifier
            
        Returns:
            Dict[str, Any]: Health check results
        """
        try:
            collection = await self._get_collection(company_id)
            
            # Test basic operations
            count = await collection.count_documents({})
            
            # Test index performance
            explain_result = await collection.find({"employee_id": "test"}).explain()
            
            return {
                "status": "healthy",
                "total_documents": count,
                "collection_name": self.collection_name,
                "indexes_used": len(explain_result.get("executionStats", {}).get("allPlansExecution", [])),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            } 