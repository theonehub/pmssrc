"""
Monthly Payout Repository Implementation
MongoDB-based repository for monthly payout operations
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING

from app.application.interfaces.repositories.monthly_payout_repository import MonthlyPayoutRepository
from app.domain.entities.taxation.monthly_payout import MonthlyPayoutRecord, MonthlyPayoutStatus
from app.domain.entities.taxation.salary_income import SalaryIncome
from app.domain.entities.taxation.monthly_payroll import LWPDetails
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime
from app.application.dto.payroll_dto import PayoutSearchFiltersDTO
from app.infrastructure.repositories.base_repository import BaseRepository
from decimal import Decimal

logger = logging.getLogger(__name__)


class MonthlyPayoutRepositoryImpl(MonthlyPayoutRepository, BaseRepository[MonthlyPayoutRecord]):
    """MongoDB implementation of monthly payout repository."""
    
    def __init__(self, database_connector):
        super().__init__(database_connector, "monthly_payouts")
    
    async def create_monthly_payout(
        self, 
        payout_record: MonthlyPayoutRecord, 
        organization_id: str
    ) -> MonthlyPayoutRecord:
        """Create a new monthly payout record."""
        try:
            # Check for duplicates
            existing = await self.check_duplicate_payout(
                str(payout_record.employee_id),
                payout_record.month,
                payout_record.year,
                organization_id
            )
            
            if existing:
                raise ValueError(f"Payout already exists for employee {payout_record.employee_id} for {payout_record.month}/{payout_record.year}")
            
            # Convert to document
            document = self._entity_to_document(payout_record)
            
            # Insert document
            document_id = await self._insert_document(document, organization_id)
            
            # Return the created record with ID
            payout_record.payout_id = document_id
            
            logger.info(f"Created monthly payout {document_id} for employee {payout_record.employee_id}")
            return payout_record
            
        except Exception as e:
            logger.error(f"Error creating monthly payout: {e}")
            raise
    
    async def get_monthly_payout(
        self, 
        employee_id: str, 
        month: int, 
        year: int, 
        organization_id: str
    ) -> Optional[MonthlyPayoutRecord]:
        """Get monthly payout by employee, month, and year."""
        try:
            filters = {
                "employee_id": employee_id,
                "month": month,
                "year": year
            }
            
            documents = await self._execute_query(filters, limit=1, organisation_id=organization_id)
            
            if not documents:
                return None
            
            return self._document_to_entity(documents[0])
            
        except Exception as e:
            logger.error(f"Error getting monthly payout for employee {employee_id}: {e}")
            raise
    
    async def update_monthly_payout(
        self, 
        payout_record: MonthlyPayoutRecord, 
        organization_id: str
    ) -> MonthlyPayoutRecord:
        """Update an existing monthly payout record."""
        try:
            if not payout_record.payout_id:
                raise ValueError("Payout ID is required for update")
            
            # Convert to document
            document = self._entity_to_document(payout_record)
            document.pop("_id", None)  # Remove ID from update data
            
            # Update document
            filters = {"_id": ObjectId(payout_record.payout_id)}
            updated = await self._update_document(
                filters, 
                {"$set": document}, 
                organization_id
            )
            
            if not updated:
                raise ValueError(f"Payout {payout_record.payout_id} not found")
            
            logger.info(f"Updated monthly payout {payout_record.payout_id}")
            return payout_record
            
        except Exception as e:
            logger.error(f"Error updating monthly payout {payout_record.payout_id}: {e}")
            raise
    
    async def delete_monthly_payout(
        self, 
        employee_id: str, 
        month: int, 
        year: int, 
        organization_id: str
    ) -> bool:
        """Delete a monthly payout record."""
        try:
            # First check if payout can be deleted
            payout = await self.get_monthly_payout(employee_id, month, year, organization_id)
            
            if not payout:
                raise ValueError(f"Payout not found for employee {employee_id} for {month}/{year}")
            
            if payout.status in [MonthlyPayoutStatus.PROCESSED, MonthlyPayoutStatus.PAID]:
                raise ValueError(f"Cannot delete payout in status: {payout.status}")
            
            filters = {
                "employee_id": employee_id,
                "month": month,
                "year": year
            }
            
            deleted = await self._delete_document(filters, organization_id)
            
            if deleted:
                logger.info(f"Deleted monthly payout for employee {employee_id} for {month}/{year}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting monthly payout for employee {employee_id}: {e}")
            raise
    
    async def get_monthly_payouts_by_period(
        self, 
        month: int, 
        year: int, 
        organization_id: str,
        status: Optional[MonthlyPayoutStatus] = None
    ) -> List[MonthlyPayoutRecord]:
        """Get all monthly payouts for a specific period."""
        try:
            filters = {
                "month": month,
                "year": year
            }
            
            if status:
                filters["status"] = status.value
            
            documents = await self._execute_query(
                filters, 
                limit=1000,  # Reasonable limit for monthly payouts
                sort_by="employee_id",
                sort_order=1,
                organisation_id=organization_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting monthly payouts for {month}/{year}: {e}")
            raise
    
    async def get_employee_payout_history(
        self, 
        employee_id: str, 
        year: int, 
        organization_id: str
    ) -> List[MonthlyPayoutRecord]:
        """Get payout history for an employee for a specific year."""
        try:
            filters = {
                "employee_id": employee_id,
                "year": year
            }
            
            documents = await self._execute_query(
                filters,
                limit=12,  # Maximum 12 months
                sort_by="month",
                sort_order=1,
                organisation_id=organization_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting payout history for employee {employee_id}: {e}")
            raise
    
    async def search_monthly_payouts(
        self, 
        filters: PayoutSearchFiltersDTO, 
        organization_id: str
    ) -> Dict[str, Any]:
        """Search monthly payouts with filters and pagination."""
        try:
            # Build query filters
            query_filters = {}
            
            if filters.employee_id:
                query_filters["employee_id"] = filters.employee_id
            
            if filters.month:
                query_filters["month"] = filters.month
            
            if filters.year:
                query_filters["year"] = filters.year
            
            if filters.status:
                query_filters["status"] = filters.status
            
            # Date range filters
            if filters.calculation_date_from or filters.calculation_date_to:
                date_filter = {}
                if filters.calculation_date_from:
                    date_filter["$gte"] = datetime.fromisoformat(filters.calculation_date_from)
                if filters.calculation_date_to:
                    date_filter["$lte"] = datetime.fromisoformat(filters.calculation_date_to)
                query_filters["calculation_date"] = date_filter
            
            # Calculate pagination
            skip = (filters.page - 1) * filters.page_size
            sort_order = 1 if filters.sort_order == "asc" else -1
            
            # Execute query
            documents = await self._execute_query(
                query_filters,
                skip=skip,
                limit=filters.page_size,
                sort_by=filters.sort_by,
                sort_order=sort_order,
                organisation_id=organization_id
            )
            
            # Get total count
            total_count = await self._count_documents(query_filters, organization_id)
            
            # Convert to entities
            payouts = [self._document_to_entity(doc) for doc in documents]
            
            return {
                "payouts": payouts,
                "total_count": total_count,
                "page": filters.page,
                "page_size": filters.page_size,
                "total_pages": (total_count + filters.page_size - 1) // filters.page_size
            }
            
        except Exception as e:
            logger.error(f"Error searching monthly payouts: {e}")
            raise
    
    async def get_payouts_by_status(
        self, 
        status: MonthlyPayoutStatus, 
        organization_id: str,
        limit: Optional[int] = None
    ) -> List[MonthlyPayoutRecord]:
        """Get payouts by status."""
        try:
            filters = {"status": status.value}
            
            documents = await self._execute_query(
                filters,
                limit=limit or 100,
                sort_by="calculation_date",
                sort_order=-1,
                organisation_id=organization_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting payouts by status {status}: {e}")
            raise
    
    async def bulk_update_status(
        self, 
        payout_ids: List[str], 
        new_status: MonthlyPayoutStatus, 
        organization_id: str,
        updated_by: str
    ) -> Dict[str, bool]:
        """Update status for multiple payouts."""
        try:
            results = {}
            
            for payout_id in payout_ids:
                try:
                    filters = {"_id": ObjectId(payout_id)}
                    update_data = {
                        "$set": {
                            "status": new_status.value,
                            "updated_at": datetime.utcnow().isoformat(),
                            "version": {"$inc": 1}
                        }
                    }
                    
                    if new_status == MonthlyPayoutStatus.APPROVED:
                        update_data["$set"]["approved_by"] = updated_by
                    elif new_status == MonthlyPayoutStatus.PROCESSED:
                        update_data["$set"]["processed_by"] = updated_by
                        update_data["$set"]["processed_date"] = datetime.utcnow().isoformat()
                    
                    updated = await self._update_document(filters, update_data, organization_id)
                    results[payout_id] = updated
                    
                except Exception as e:
                    logger.error(f"Error updating payout {payout_id}: {e}")
                    results[payout_id] = False
            
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk status update: {e}")
            raise
    
    async def get_payout_summary(
        self, 
        month: int, 
        year: int, 
        organization_id: str
    ) -> Dict[str, Any]:
        """Get summary statistics for monthly payouts."""
        try:
            collection = await self._get_collection(organization_id)
            
            pipeline = [
                {
                    "$match": {
                        "month": month,
                        "year": year
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_employees": {"$sum": 1},
                        "total_gross_amount": {"$sum": "$salary_breakdown.earnings.total_earnings"},
                        "total_net_amount": {"$sum": "$salary_breakdown.net_salary"},
                        "total_deductions": {"$sum": "$salary_breakdown.deductions.total_deductions"},
                        "total_lwp_deduction": {"$sum": "$lwp_impact.lwp_deduction_amount"},
                        "status_counts": {
                            "$push": "$status"
                        }
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "total_employees": 1,
                        "total_gross_amount": 1,
                        "total_net_amount": 1,
                        "total_deductions": 1,
                        "total_lwp_deduction": 1,
                        "status_breakdown": {
                            "$arrayToObject": {
                                "$map": {
                                    "input": {
                                        "$setUnion": ["$status_counts"]
                                    },
                                    "as": "status",
                                    "in": {
                                        "k": "$$status",
                                        "v": {
                                            "$size": {
                                                "$filter": {
                                                    "input": "$status_counts",
                                                    "cond": {"$eq": ["$$this", "$$status"]}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            ]
            
            results = await self._aggregate(pipeline, organization_id)
            
            if results:
                return results[0]
            else:
                return {
                    "total_employees": 0,
                    "total_gross_amount": 0.0,
                    "total_net_amount": 0.0,
                    "total_deductions": 0.0,
                    "total_lwp_deduction": 0.0,
                    "status_breakdown": {}
                }
                
        except Exception as e:
            logger.error(f"Error getting payout summary for {month}/{year}: {e}")
            raise
    
    async def get_lwp_analytics(
        self, 
        month: int, 
        year: int, 
        organization_id: str
    ) -> Dict[str, Any]:
        """Get LWP analytics for the specified period."""
        try:
            collection = await self._get_collection(organization_id)
            
            pipeline = [
                {
                    "$match": {
                        "month": month,
                        "year": year
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_employees": {"$sum": 1},
                        "employees_with_lwp": {
                            "$sum": {
                                "$cond": [{"$gt": ["$lwp_details.lwp_days", 0]}, 1, 0]
                            }
                        },
                        "total_lwp_days": {"$sum": "$lwp_details.lwp_days"},
                        "total_lwp_deduction": {"$sum": "$lwp_impact.lwp_deduction_amount"},
                        "total_base_gross": {"$sum": "$lwp_impact.base_monthly_gross"},
                        "total_adjusted_gross": {"$sum": "$lwp_impact.adjusted_monthly_gross"}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "total_employees": 1,
                        "employees_with_lwp": 1,
                        "total_lwp_days": 1,
                        "total_lwp_deduction": 1,
                        "lwp_impact_percentage": {
                            "$multiply": [
                                {"$divide": ["$total_lwp_deduction", "$total_base_gross"]},
                                100
                            ]
                        },
                        "average_lwp_days_per_employee": {
                            "$divide": ["$total_lwp_days", "$total_employees"]
                        }
                    }
                }
            ]
            
            results = await self._aggregate(pipeline, organization_id)
            
            if results:
                return results[0]
            else:
                return {
                    "total_employees": 0,
                    "employees_with_lwp": 0,
                    "total_lwp_days": 0,
                    "total_lwp_deduction": 0.0,
                    "lwp_impact_percentage": 0.0,
                    "average_lwp_days_per_employee": 0.0
                }
                
        except Exception as e:
            logger.error(f"Error getting LWP analytics for {month}/{year}: {e}")
            raise
    
    async def check_duplicate_payout(
        self, 
        employee_id: str, 
        month: int, 
        year: int, 
        organization_id: str
    ) -> bool:
        """Check if a payout already exists for employee/month/year."""
        try:
            filters = {
                "employee_id": employee_id,
                "month": month,
                "year": year
            }
            
            count = await self._count_documents(filters, organization_id)
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking duplicate payout: {e}")
            raise
    
    async def get_pending_approvals(
        self, 
        organization_id: str,
        approver_id: Optional[str] = None
    ) -> List[MonthlyPayoutRecord]:
        """Get payouts pending approval."""
        try:
            filters = {"status": MonthlyPayoutStatus.PENDING_APPROVAL.value}
            
            if approver_id:
                # Add logic for approver-specific filtering if needed
                pass
            
            documents = await self._execute_query(
                filters,
                limit=100,
                sort_by="calculation_date",
                sort_order=1,
                organisation_id=organization_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting pending approvals: {e}")
            raise
    
    async def get_department_wise_summary(
        self, 
        month: int, 
        year: int, 
        organization_id: str
    ) -> Dict[str, Dict[str, float]]:
        """Get department-wise payout summary."""
        try:
            # This would require joining with employee data
            # For now, return empty dict - can be enhanced later
            return {}
            
        except Exception as e:
            logger.error(f"Error getting department-wise summary: {e}")
            raise
    
    async def get_compliance_metrics(
        self, 
        month: int, 
        year: int, 
        organization_id: str
    ) -> Dict[str, Any]:
        """Get compliance metrics for payouts."""
        try:
            # Basic compliance metrics
            payouts = await self.get_monthly_payouts_by_period(month, year, organization_id)
            
            total_payouts = len(payouts)
            on_time_processed = sum(1 for p in payouts if p.status in [MonthlyPayoutStatus.PROCESSED, MonthlyPayoutStatus.PAID])
            
            return {
                "total_payouts": total_payouts,
                "on_time_processing_rate": (on_time_processed / total_payouts * 100) if total_payouts > 0 else 0,
                "pending_approvals": sum(1 for p in payouts if p.status == MonthlyPayoutStatus.PENDING_APPROVAL),
                "failed_payouts": sum(1 for p in payouts if p.status == MonthlyPayoutStatus.FAILED)
            }
            
        except Exception as e:
            logger.error(f"Error getting compliance metrics: {e}")
            raise
    
    async def archive_old_payouts(
        self, 
        cutoff_date: datetime, 
        organization_id: str
    ) -> int:
        """Archive old payout records."""
        try:
            # For now, just return 0 - archiving logic can be implemented later
            return 0
            
        except Exception as e:
            logger.error(f"Error archiving old payouts: {e}")
            raise
    
    def _entity_to_document(self, entity: MonthlyPayoutRecord) -> Dict[str, Any]:
        """Convert entity to MongoDB document."""
        document = entity.to_dict()
        
        # Convert payout_id to _id if present
        if entity.payout_id:
            try:
                document["_id"] = ObjectId(entity.payout_id)
            except:
                # If payout_id is not a valid ObjectId, keep it as is
                pass
        
        return document
    
    def _document_to_entity(self, document: Dict[str, Any]) -> MonthlyPayoutRecord:
        """Convert MongoDB document to entity."""
        # Convert _id to payout_id
        if "_id" in document:
            document["payout_id"] = str(document["_id"])
            del document["_id"]
        
        # Create basic salary income from document
        # This is a simplified conversion - in practice, you might need more sophisticated logic
        base_salary_income = SalaryIncome(
            basic_salary=Money(Decimal("50000")),  # Default values - should be loaded from actual data
            dearness_allowance=Money(Decimal("5000")),
            hra_received=Money(Decimal("15000")),
            special_allowance=Money(Decimal("10000")),
            conveyance_allowance=Money(Decimal("2000")),
            medical_allowance=Money(Decimal("1500")),
            bonus=Money.zero(),
            commission=Money.zero(),
            other_allowances=Money.zero()
        )
        
        # Create tax regime
        tax_regime = TaxRegime.new_regime()  # Default - should be loaded from document
        
        # Create entity using from_dict method
        entity = MonthlyPayoutRecord.from_dict(document, base_salary_income, tax_regime)
        
        return entity 