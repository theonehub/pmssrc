"""
Dependency Injection Container
Manages all dependencies using SOLID principles
"""

import logging
from typing import Dict, Any

# Domain imports
from app.domain.services.formula_engine import FormulaEngine

# Application interface imports
from app.application.interfaces.repositories.salary_component_repository import SalaryComponentRepository
from app.application.interfaces.repositories.salary_component_assignment_repository import (
    SalaryComponentAssignmentRepository,
    GlobalSalaryComponentRepository
)
from app.application.interfaces.services.salary_component_service import SalaryComponentService

# Application use case imports
from app.application.use_cases.salary_component_assignment.get_global_salary_components_use_case import (
    GetGlobalSalaryComponentsUseCase
)
from app.application.use_cases.salary_component_assignment.get_organization_components_use_case import (
    GetOrganizationComponentsUseCase
)
from app.application.use_cases.salary_component_assignment.assign_components_use_case import (
    AssignComponentsUseCase
)
from app.application.use_cases.salary_component_assignment.remove_components_use_case import (
    RemoveComponentsUseCase
)
from app.application.use_cases.salary_component_assignment.get_comparison_data_use_case import (
    GetComparisonDataUseCase
)

# Infrastructure imports
from app.infrastructure.database.mongodb_connector import MongoDBConnector
from app.infrastructure.repositories.mongodb_salary_component_repository import MongoDBSalaryComponentRepository
from app.infrastructure.repositories.mongodb_salary_component_assignment_repository import (
    MongoDBSalaryComponentAssignmentRepository,
    MongoDBGlobalSalaryComponentRepository
)
from app.infrastructure.services.salary_component_service_impl import SalaryComponentServiceImpl

# API imports
from app.api.controllers.salary_component_controller import SalaryComponentController
from app.api.controllers.salary_component_assignment_controller import SalaryComponentAssignmentController

logger = logging.getLogger(__name__)


class DependencyContainer:
    """
    Dependency Injection Container following SOLID principles
    
    Manages the lifecycle and dependencies of all components in the system.
    Uses the Dependency Inversion Principle to depend on abstractions.
    """
    
    def __init__(self):
        """Initialize container"""
        self._instances: Dict[str, Any] = {}
        self._initialized = False
        
        logger.info("Initializing Dependency Container")
    
    async def initialize(self):
        """Initialize all dependencies"""
        if self._initialized:
            return
        
        try:
            logger.info("Setting up dependency container...")
            
            # 1. Initialize Database Infrastructure
            await self._setup_database()
            
            # 2. Initialize Domain Services
            self._setup_domain_services()
            
            # 3. Initialize Repository Implementations
            self._setup_repositories()
            
            # 4. Initialize Application Services
            self._setup_application_services()
            
            # 5. Initialize Use Cases
            self._setup_use_cases()
            
            # 6. Initialize API Controllers
            self._setup_controllers()
            
            self._initialized = True
            logger.info("Dependency container initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize dependency container: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if "mongodb_connector" in self._instances:
                await self._instances["mongodb_connector"].cleanup()
            
            self._instances.clear()
            self._initialized = False
            logger.info("Dependency container cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def _setup_database(self):
        """Setup database connections"""
        logger.info("Setting up database connections...")
        
        # MongoDB Connector
        mongodb_connector = MongoDBConnector()
        await mongodb_connector.initialize()
        self._instances["mongodb_connector"] = mongodb_connector
        
        logger.info("Database connections established")
    
    def _setup_domain_services(self):
        """Setup domain services"""
        logger.info("Setting up domain services...")
        
        # Formula Engine
        formula_engine = FormulaEngine()
        self._instances["formula_engine"] = formula_engine
        
        logger.info("Domain services initialized")
    
    def _setup_repositories(self):
        """Setup repository implementations"""
        logger.info("Setting up repositories...")
        
        # Salary Component Repository (for organization-specific components)
        salary_component_repository = MongoDBSalaryComponentRepository(
            database_connector=self._instances["mongodb_connector"]
        )
        self._instances["salary_component_repository"] = salary_component_repository
        
        # Salary Component Assignment Repository
        salary_component_assignment_repository = MongoDBSalaryComponentAssignmentRepository(
            db_connector=self._instances["mongodb_connector"]
        )
        self._instances["salary_component_assignment_repository"] = salary_component_assignment_repository
        
        # Global Salary Component Repository
        global_salary_component_repository = MongoDBGlobalSalaryComponentRepository(
            db_connector=self._instances["mongodb_connector"]
        )
        self._instances["global_salary_component_repository"] = global_salary_component_repository
        
        logger.info("Repositories initialized")
    
    def _setup_application_services(self):
        """Setup application services"""
        logger.info("Setting up application services...")
        
        # Salary Component Service
        salary_component_service = SalaryComponentServiceImpl(
            repository=self._instances["salary_component_repository"],
            formula_engine=self._instances["formula_engine"]
        )
        self._instances["salary_component_service"] = salary_component_service
        
        logger.info("Application services initialized")
    
    def _setup_use_cases(self):
        """Setup use cases"""
        logger.info("Setting up use cases...")
        
        # Get Global Salary Components Use Case
        get_global_components_use_case = GetGlobalSalaryComponentsUseCase(
            global_component_repository=self._instances["global_salary_component_repository"]
        )
        self._instances["get_global_components_use_case"] = get_global_components_use_case
        
        # Get Organization Components Use Case
        get_organization_components_use_case = GetOrganizationComponentsUseCase(
            assignment_repository=self._instances["salary_component_assignment_repository"],
            global_component_repository=self._instances["global_salary_component_repository"]
        )
        self._instances["get_organization_components_use_case"] = get_organization_components_use_case
        
        # Assign Components Use Case
        assign_components_use_case = AssignComponentsUseCase(
            assignment_repository=self._instances["salary_component_assignment_repository"],
            global_component_repository=self._instances["global_salary_component_repository"],
            organization_component_repository=self._instances["salary_component_repository"]
        )
        self._instances["assign_components_use_case"] = assign_components_use_case
        
        # Remove Components Use Case
        remove_components_use_case = RemoveComponentsUseCase(
            assignment_repository=self._instances["salary_component_assignment_repository"],
            organization_component_repository=self._instances["salary_component_repository"]
        )
        self._instances["remove_components_use_case"] = remove_components_use_case
        
        # Get Comparison Data Use Case
        get_comparison_data_use_case = GetComparisonDataUseCase(
            assignment_repository=self._instances["salary_component_assignment_repository"],
            global_component_repository=self._instances["global_salary_component_repository"]
        )
        self._instances["get_comparison_data_use_case"] = get_comparison_data_use_case
        
        logger.info("Use cases initialized")
    
    def _setup_controllers(self):
        """Setup API controllers"""
        logger.info("Setting up controllers...")
        
        # Salary Component Controller
        salary_component_controller = SalaryComponentController(
            service=self._instances["salary_component_service"]
        )
        self._instances["salary_component_controller"] = salary_component_controller
        
        # Salary Component Assignment Controller
        salary_component_assignment_controller = SalaryComponentAssignmentController(
            get_global_components_use_case=self._instances["get_global_components_use_case"],
            get_organization_components_use_case=self._instances["get_organization_components_use_case"],
            assign_components_use_case=self._instances["assign_components_use_case"],
            remove_components_use_case=self._instances["remove_components_use_case"],
            get_comparison_data_use_case=self._instances["get_comparison_data_use_case"]
        )
        self._instances["salary_component_assignment_controller"] = salary_component_assignment_controller
        
        logger.info("Controllers initialized")
    
    # Dependency Accessors
    def get_mongodb_connector(self) -> MongoDBConnector:
        """Get MongoDB connector"""
        return self._instances["mongodb_connector"]
    
    def get_formula_engine(self) -> FormulaEngine:
        """Get formula engine"""
        return self._instances["formula_engine"]
    
    def get_salary_component_repository(self) -> SalaryComponentRepository:
        """Get salary component repository"""
        return self._instances["salary_component_repository"]
    
    def get_salary_component_service(self) -> SalaryComponentService:
        """Get salary component service"""
        return self._instances["salary_component_service"]
    
    def get_salary_component_controller(self) -> SalaryComponentController:
        """Get salary component controller"""
        return self._instances["salary_component_controller"]
    
    def get_salary_component_assignment_repository(self) -> SalaryComponentAssignmentRepository:
        """Get salary component assignment repository"""
        return self._instances["salary_component_assignment_repository"]
    
    def get_global_salary_component_repository(self) -> GlobalSalaryComponentRepository:
        """Get global salary component repository"""
        return self._instances["global_salary_component_repository"]
    
    def get_salary_component_assignment_controller(self) -> SalaryComponentAssignmentController:
        """Get salary component assignment controller"""
        return self._instances["salary_component_assignment_controller"]
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all components"""
        status = {
            "container_initialized": self._initialized,
            "total_components": len(self._instances)
        }
        
        # Add database health if available
        if "mongodb_connector" in self._instances:
            try:
                status["database"] = await self._instances["mongodb_connector"].get_health_status()
            except Exception as e:
                logger.warning(f"Error getting database health status: {e}")
                status["database"] = {"error": str(e)}
        
        return status


# Global container instance
container = DependencyContainer() 