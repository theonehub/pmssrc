"""
Dependency Injection Configuration
Sets up all dependencies for the organization system
"""

import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from app.infrastructure.repositories.mongodb_organization_repository import MongoDBOrganizationRepository
from app.infrastructure.services.organization_service_impl import OrganizationServiceImpl
from app.application.use_cases.organization.create_organization_use_case import CreateOrganizationUseCase
from app.application.use_cases.organization.update_organization_use_case import UpdateOrganizationUseCase
from app.application.use_cases.organization.get_organization_use_case import GetOrganizationUseCase
from app.application.use_cases.organization.list_organizations_use_case import ListOrganizationsUseCase
from app.application.use_cases.organization.delete_organization_use_case import DeleteOrganizationUseCase
from api.controllers.organization_controller import OrganizationController
from database.database_connector import connect_to_database


logger = logging.getLogger(__name__)


class OrganizationDependencyContainer:
    """
    Dependency injection container for organization system.
    
    Follows SOLID principles:
    - SRP: Only handles dependency creation and management
    - OCP: Can be extended with new dependencies
    - LSP: Can be substituted with other containers
    - ISP: Focused interface for dependency injection
    - DIP: Manages abstractions and implementations
    """
    
    def __init__(self):
        self._database: Optional[AsyncIOMotorDatabase] = None
        self._repository: Optional[MongoDBOrganizationRepository] = None
        self._service: Optional[OrganizationServiceImpl] = None
        self._use_cases: dict = {}
        self._controller: Optional[OrganizationController] = None
    
    def get_database(self) -> AsyncIOMotorDatabase:
        """Get database connection"""
        if self._database is None:
            self._database = connect_to_database("global_database")
        return self._database
    
    def get_repository(self) -> MongoDBOrganizationRepository:
        """Get organization repository"""
        if self._repository is None:
            database = self.get_database()
            self._repository = MongoDBOrganizationRepository(database)
        return self._repository
    
    def get_service(self) -> OrganizationServiceImpl:
        """Get organization service"""
        if self._service is None:
            repository = self.get_repository()
            # For now, we'll use a simple event publisher
            from app.infrastructure.services.simple_event_publisher import SimpleEventPublisher
            event_publisher = SimpleEventPublisher()
            self._service = OrganizationServiceImpl(repository, event_publisher)
        return self._service
    
    def get_create_use_case(self) -> CreateOrganizationUseCase:
        """Get create organization use case"""
        if 'create' not in self._use_cases:
            repository = self.get_repository()
            service = self.get_service()
            self._use_cases['create'] = CreateOrganizationUseCase(
                command_repository=repository,
                query_repository=repository,
                validation_service=service,
                notification_service=service
            )
        return self._use_cases['create']
    
    def get_update_use_case(self) -> UpdateOrganizationUseCase:
        """Get update organization use case"""
        if 'update' not in self._use_cases:
            repository = self.get_repository()
            service = self.get_service()
            self._use_cases['update'] = UpdateOrganizationUseCase(
                command_repository=repository,
                query_repository=repository,
                validation_service=service,
                notification_service=service
            )
        return self._use_cases['update']
    
    def get_get_use_case(self) -> GetOrganizationUseCase:
        """Get get organization use case"""
        if 'get' not in self._use_cases:
            repository = self.get_repository()
            self._use_cases['get'] = GetOrganizationUseCase(
                query_repository=repository
            )
        return self._use_cases['get']
    
    def get_list_use_case(self) -> ListOrganizationsUseCase:
        """Get list organizations use case"""
        if 'list' not in self._use_cases:
            repository = self.get_repository()
            self._use_cases['list'] = ListOrganizationsUseCase(
                query_repository=repository
            )
        return self._use_cases['list']
    
    def get_delete_use_case(self) -> DeleteOrganizationUseCase:
        """Get delete organization use case"""
        if 'delete' not in self._use_cases:
            repository = self.get_repository()
            service = self.get_service()
            self._use_cases['delete'] = DeleteOrganizationUseCase(
                command_repository=repository,
                query_repository=repository,
                notification_service=service
            )
        return self._use_cases['delete']
    
    def get_controller(self) -> OrganizationController:
        """Get organization controller"""
        if self._controller is None:
            self._controller = OrganizationController(
                create_use_case=self.get_create_use_case(),
                update_use_case=self.get_update_use_case(),
                get_use_case=self.get_get_use_case(),
                list_use_case=self.get_list_use_case(),
                delete_use_case=self.get_delete_use_case()
            )
        return self._controller


# Global container instance
_container: Optional[OrganizationDependencyContainer] = None


def get_organization_container() -> OrganizationDependencyContainer:
    """Get the global organization dependency container"""
    global _container
    if _container is None:
        _container = OrganizationDependencyContainer()
    return _container


def initialize_organization_dependencies():
    """Initialize all organization dependencies"""
    try:
        container = get_organization_container()
        
        # Initialize all components
        repository = container.get_repository()
        service = container.get_service()
        controller = container.get_controller()
        
        # Set the global controller in the API module
        from api.controllers import organization_controller
        organization_controller.controller = controller
        
        logger.info("Organization dependencies initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize organization dependencies: {e}")
        return False 