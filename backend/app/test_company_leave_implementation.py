"""
Test script for Company Leave Implementation
Tests the complete end-to-end functionality of the company leave system
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from application.dto.company_leave_dto import CompanyLeaveCreateRequestDTO
from application.use_cases.company_leave.create_company_leave_use_case import CreateCompanyLeaveUseCase
from application.use_cases.company_leave.get_company_leaves_use_case import GetCompanyLeavesUseCase
from infrastructure.repositories.mongodb_company_leave_repository import (
    MongoDBCompanyLeaveCommandRepository,
    MongoDBCompanyLeaveQueryRepository
)
from infrastructure.services.mongodb_event_publisher import MongoDBEventPublisher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompanyLeaveTestSuite:
    """Test suite for company leave functionality"""
    
    def __init__(self, hostname: str = "test_company"):
        self.hostname = hostname
        self.command_repo = MongoDBCompanyLeaveCommandRepository(hostname)
        self.query_repo = MongoDBCompanyLeaveQueryRepository(hostname)
        self.event_publisher = MongoDBEventPublisher(hostname)
    
    def test_create_casual_leave(self) -> Dict[str, Any]:
        """Test creating a casual leave policy"""
        logger.info("Testing casual leave creation...")
        
        try:
            # Create request DTO
            request_data = {
                "leave_type_code": "CL",
                "leave_type_name": "Casual Leave",
                "leave_category": "casual",
                "annual_allocation": 12,
                "accrual_type": "monthly",
                "description": "Leave for personal reasons and emergencies",
                "max_carryover_days": 5,
                "min_advance_notice_days": 1,
                "max_continuous_days": 3,
                "requires_approval": True,
                "auto_approve_threshold": 2,
                "requires_medical_certificate": False,
                "is_encashable": False,
                "available_during_probation": True,
                "created_by": "test_admin"
            }
            
            create_request = CompanyLeaveCreateRequestDTO.from_dict(request_data)
            
            # Execute use case
            use_case = CreateCompanyLeaveUseCase(
                command_repository=self.command_repo,
                query_repository=self.query_repo,
                event_publisher=self.event_publisher
            )
            
            response = use_case.execute(create_request)
            
            logger.info(f"✅ Casual leave created successfully: {response.company_leave_id}")
            return response.to_dict()
            
        except Exception as e:
            logger.error(f"❌ Failed to create casual leave: {e}")
            raise
    
    def test_create_sick_leave(self) -> Dict[str, Any]:
        """Test creating a sick leave policy"""
        logger.info("Testing sick leave creation...")
        
        try:
            request_data = {
                "leave_type_code": "SL",
                "leave_type_name": "Sick Leave",
                "leave_category": "sick",
                "annual_allocation": 12,
                "accrual_type": "monthly",
                "description": "Leave for medical reasons and health issues",
                "max_carryover_days": 12,
                "min_advance_notice_days": 0,
                "max_continuous_days": 7,
                "requires_approval": True,
                "auto_approve_threshold": 3,
                "requires_medical_certificate": True,
                "medical_certificate_threshold": 3,
                "is_encashable": False,
                "available_during_probation": True,
                "created_by": "test_admin"
            }
            
            create_request = CompanyLeaveCreateRequestDTO.from_dict(request_data)
            
            use_case = CreateCompanyLeaveUseCase(
                command_repository=self.command_repo,
                query_repository=self.query_repo,
                event_publisher=self.event_publisher
            )
            
            response = use_case.execute(create_request)
            
            logger.info(f"✅ Sick leave created successfully: {response.company_leave_id}")
            return response.to_dict()
            
        except Exception as e:
            logger.error(f"❌ Failed to create sick leave: {e}")
            raise
    
    def test_create_annual_leave(self) -> Dict[str, Any]:
        """Test creating an annual leave policy"""
        logger.info("Testing annual leave creation...")
        
        try:
            request_data = {
                "leave_type_code": "AL",
                "leave_type_name": "Annual Leave",
                "leave_category": "annual",
                "annual_allocation": 21,
                "accrual_type": "monthly",
                "description": "Yearly vacation leave for rest and recreation",
                "max_carryover_days": 10,
                "min_advance_notice_days": 7,
                "max_continuous_days": 15,
                "requires_approval": True,
                "auto_approve_threshold": None,
                "requires_medical_certificate": False,
                "is_encashable": True,
                "max_encashment_days": 10,
                "available_during_probation": False,
                "created_by": "test_admin"
            }
            
            create_request = CompanyLeaveCreateRequestDTO.from_dict(request_data)
            
            use_case = CreateCompanyLeaveUseCase(
                command_repository=self.command_repo,
                query_repository=self.query_repo,
                event_publisher=self.event_publisher
            )
            
            response = use_case.execute(create_request)
            
            logger.info(f"✅ Annual leave created successfully: {response.company_leave_id}")
            return response.to_dict()
            
        except Exception as e:
            logger.error(f"❌ Failed to create annual leave: {e}")
            raise
    
    def test_create_maternity_leave(self) -> Dict[str, Any]:
        """Test creating a maternity leave policy"""
        logger.info("Testing maternity leave creation...")
        
        try:
            request_data = {
                "leave_type_code": "ML",
                "leave_type_name": "Maternity Leave",
                "leave_category": "maternity",
                "annual_allocation": 180,
                "accrual_type": "immediate",
                "description": "Leave for childbirth and post-natal care",
                "max_carryover_days": 0,
                "min_advance_notice_days": 30,
                "requires_approval": True,
                "requires_medical_certificate": True,
                "is_encashable": False,
                "available_during_probation": False,
                "gender_specific": "female",
                "created_by": "test_admin"
            }
            
            create_request = CompanyLeaveCreateRequestDTO.from_dict(request_data)
            
            use_case = CreateCompanyLeaveUseCase(
                command_repository=self.command_repo,
                query_repository=self.query_repo,
                event_publisher=self.event_publisher
            )
            
            response = use_case.execute(create_request)
            
            logger.info(f"✅ Maternity leave created successfully: {response.company_leave_id}")
            return response.to_dict()
            
        except Exception as e:
            logger.error(f"❌ Failed to create maternity leave: {e}")
            raise
    
    def test_get_all_leaves(self) -> Dict[str, Any]:
        """Test retrieving all company leaves"""
        logger.info("Testing get all leaves...")
        
        try:
            use_case = GetCompanyLeavesUseCase(query_repository=self.query_repo)
            leaves = use_case.get_all_company_leaves()
            
            logger.info(f"✅ Retrieved {len(leaves)} company leaves")
            return {"leaves": leaves, "count": len(leaves)}
            
        except Exception as e:
            logger.error(f"❌ Failed to get all leaves: {e}")
            raise
    
    def test_get_active_leaves(self) -> Dict[str, Any]:
        """Test retrieving active company leaves"""
        logger.info("Testing get active leaves...")
        
        try:
            use_case = GetCompanyLeavesUseCase(query_repository=self.query_repo)
            leaves = use_case.get_active_company_leaves()
            
            logger.info(f"✅ Retrieved {len(leaves)} active company leaves")
            return {"leaves": leaves, "count": len(leaves)}
            
        except Exception as e:
            logger.error(f"❌ Failed to get active leaves: {e}")
            raise
    
    def test_get_applicable_leaves_for_employee(self) -> Dict[str, Any]:
        """Test retrieving applicable leaves for different employee types"""
        logger.info("Testing get applicable leaves for employees...")
        
        try:
            use_case = GetCompanyLeavesUseCase(query_repository=self.query_repo)
            
            # Test for female employee not on probation
            female_leaves = use_case.get_applicable_leaves_for_employee(
                employee_gender="female",
                is_on_probation=False
            )
            
            # Test for male employee on probation
            male_probation_leaves = use_case.get_applicable_leaves_for_employee(
                employee_gender="male",
                is_on_probation=True
            )
            
            logger.info(f"✅ Female employee applicable leaves: {len(female_leaves)}")
            logger.info(f"✅ Male probation employee applicable leaves: {len(male_probation_leaves)}")
            
            return {
                "female_leaves": female_leaves,
                "male_probation_leaves": male_probation_leaves
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get applicable leaves: {e}")
            raise
    
    def test_get_leave_statistics(self) -> Dict[str, Any]:
        """Test retrieving leave statistics"""
        logger.info("Testing get leave statistics...")
        
        try:
            use_case = GetCompanyLeavesUseCase(query_repository=self.query_repo)
            statistics = use_case.get_company_leave_statistics()
            
            logger.info(f"✅ Retrieved leave statistics")
            logger.info(f"   Total leave types: {statistics['summary']['total_leave_types']}")
            logger.info(f"   Active leave types: {statistics['summary']['active_leave_types']}")
            logger.info(f"   Total allocation: {statistics['summary']['total_annual_allocation']}")
            
            return statistics
            
        except Exception as e:
            logger.error(f"❌ Failed to get leave statistics: {e}")
            raise
    
    def test_search_leaves(self) -> Dict[str, Any]:
        """Test searching leaves with filters"""
        logger.info("Testing search leaves...")
        
        try:
            use_case = GetCompanyLeavesUseCase(query_repository=self.query_repo)
            
            # Search by category
            sick_leaves = use_case.search_company_leaves(category="sick")
            
            # Search by encashable
            encashable_leaves = use_case.search_company_leaves(is_encashable=True)
            
            # Search by term
            casual_leaves = use_case.search_company_leaves(search_term="casual")
            
            logger.info(f"✅ Sick leaves found: {len(sick_leaves)}")
            logger.info(f"✅ Encashable leaves found: {len(encashable_leaves)}")
            logger.info(f"✅ Casual leaves found: {len(casual_leaves)}")
            
            return {
                "sick_leaves": sick_leaves,
                "encashable_leaves": encashable_leaves,
                "casual_leaves": casual_leaves
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to search leaves: {e}")
            raise
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests"""
        logger.info("🚀 Starting Company Leave Test Suite...")
        
        results = {}
        
        try:
            # Test creation
            results["casual_leave"] = self.test_create_casual_leave()
            results["sick_leave"] = self.test_create_sick_leave()
            results["annual_leave"] = self.test_create_annual_leave()
            results["maternity_leave"] = self.test_create_maternity_leave()
            
            # Test retrieval
            results["all_leaves"] = self.test_get_all_leaves()
            results["active_leaves"] = self.test_get_active_leaves()
            results["applicable_leaves"] = self.test_get_applicable_leaves_for_employee()
            results["statistics"] = self.test_get_leave_statistics()
            results["search_results"] = self.test_search_leaves()
            
            logger.info("🎉 All tests completed successfully!")
            return results
            
        except Exception as e:
            logger.error(f"💥 Test suite failed: {e}")
            raise


def main():
    """Main function to run tests"""
    try:
        test_suite = CompanyLeaveTestSuite()
        results = test_suite.run_all_tests()
        
        print("\n" + "="*50)
        print("COMPANY LEAVE TEST RESULTS")
        print("="*50)
        
        print(f"✅ Created {len([r for r in results.values() if 'company_leave_id' in str(r)])} leave policies")
        print(f"✅ Total leaves in system: {results['all_leaves']['count']}")
        print(f"✅ Active leaves: {results['active_leaves']['count']}")
        print(f"✅ Statistics generated successfully")
        print(f"✅ Search functionality working")
        
        print("\n🎉 Company Leave implementation is working correctly!")
        
    except Exception as e:
        print(f"\n💥 Tests failed: {e}")
        raise


if __name__ == "__main__":
    main() 