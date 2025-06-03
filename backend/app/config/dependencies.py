"""
Dependency Injection Configuration
Sets up all dependencies for the organisation system
"""

import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from app.infrastructure.repositories.mongodb_organisation_repository import MongoDBOrganisationRepository
from app.infrastructure.services.organisation_service_impl import OrganisationServiceImpl
from app.application.use_cases.organisation.create_organisation_use_case import CreateOrganisationUseCase
from app.application.use_cases.organisation.update_organisation_use_case import UpdateOrganisationUseCase
from app.application.use_cases.organisation.get_organisation_use_case import GetOrganisationUseCase
from app.application.use_cases.organisation.list_organisations_use_case import ListOrganisationsUseCase
from app.application.use_cases.organisation.delete_organisation_use_case import DeleteOrganisationUseCase
from app.api.controllers.organisation_controller import OrganisationController
from app.database.database_connector import connect_to_database


logger = logging.getLogger(__name__)


class OrganisationDependencyContainer:
    """
    Dependency injection container for organisation system.
    
    Follows SOLID principles:
    - SRP: Only handles dependency creation and management
    - OCP: Can be extended with new dependencies
    - LSP: Can be substituted with other containers
    - ISP: Focused interface for dependency injection
    - DIP: Manages abstractions and implementations
    """
    
    def __init__(self):
        self._database: Optional[AsyncIOMotorDatabase] = None
        self._repository: Optional[MongoDBOrganisationRepository] = None
        self._service: Optional[OrganisationServiceImpl] = None
        self._use_cases: dict = {}
        self._controller: Optional[OrganisationController] = None
    
    def get_database(self) -> AsyncIOMotorDatabase:
        """Get database connection"""
        if self._database is None:
            self._database = connect_to_database("pms_global_database")
        return self._database
    
    def get_repository(self) -> MongoDBOrganisationRepository:
        """Get organisation repository"""
        if self._repository is None:
            database = self.get_database()
            self._repository = MongoDBOrganisationRepository(database)
        return self._repository
    
    def get_service(self) -> OrganisationServiceImpl:
        """Get organisation service"""
        if self._service is None:
            repository = self.get_repository()
            # For now, we'll use a simple event publisher
            from app.infrastructure.services.simple_event_publisher import SimpleEventPublisher
            event_publisher = SimpleEventPublisher()
            self._service = OrganisationServiceImpl(repository, event_publisher)
        return self._service
    
    def get_create_use_case(self) -> CreateOrganisationUseCase:
        """Get create organisation use case"""
        if 'create' not in self._use_cases:
            repository = self.get_repository()
            service = self.get_service()
            self._use_cases['create'] = CreateOrganisationUseCase(
                command_repository=repository,
                query_repository=repository,
                validation_service=service,
                notification_service=service
            )
        return self._use_cases['create']
    
    def get_update_use_case(self) -> UpdateOrganisationUseCase:
        """Get update organisation use case"""
        if 'update' not in self._use_cases:
            repository = self.get_repository()
            service = self.get_service()
            self._use_cases['update'] = UpdateOrganisationUseCase(
                command_repository=repository,
                query_repository=repository,
                validation_service=service,
                notification_service=service
            )
        return self._use_cases['update']
    
    def get_get_use_case(self) -> GetOrganisationUseCase:
        """Get get organisation use case"""
        if 'get' not in self._use_cases:
            repository = self.get_repository()
            self._use_cases['get'] = GetOrganisationUseCase(
                query_repository=repository
            )
        return self._use_cases['get']
    
    def get_list_use_case(self) -> ListOrganisationsUseCase:
        """Get list organisations use case"""
        if 'list' not in self._use_cases:
            repository = self.get_repository()
            self._use_cases['list'] = ListOrganisationsUseCase(
                query_repository=repository
            )
        return self._use_cases['list']
    
    def get_delete_use_case(self) -> DeleteOrganisationUseCase:
        """Get delete organisation use case"""
        if 'delete' not in self._use_cases:
            repository = self.get_repository()
            service = self.get_service()
            self._use_cases['delete'] = DeleteOrganisationUseCase(
                command_repository=repository,
                query_repository=repository,
                notification_service=service
            )
        return self._use_cases['delete']
    
    def get_controller(self) -> OrganisationController:
        """Get organisation controller"""
        if self._controller is None:
            self._controller = OrganisationController(
                create_use_case=self.get_create_use_case(),
                update_use_case=self.get_update_use_case(),
                get_use_case=self.get_get_use_case(),
                list_use_case=self.get_list_use_case(),
                delete_use_case=self.get_delete_use_case()
            )
        return self._controller


# Global container instance
_container: Optional[OrganisationDependencyContainer] = None


def get_organisation_container() -> OrganisationDependencyContainer:
    """Get the global organisation dependency container"""
    global _container
    if _container is None:
        _container = OrganisationDependencyContainer()
    return _container


def initialize_organisation_dependencies():
    """Initialize all organisation dependencies"""
    try:
        container = get_organisation_container()
        
        # Initialize all components
        repository = container.get_repository()
        service = container.get_service()
        controller = container.get_controller()
        
        # Initialize the global controller in the controller module
        from app.api.controllers import organisation_controller
        organisation_controller.initialize_organisation_controller(
            create_use_case=container.get_create_use_case(),
            update_use_case=container.get_update_use_case(),
            get_use_case=container.get_get_use_case(),
            list_use_case=container.get_list_use_case(),
            delete_use_case=container.get_delete_use_case()
        )
        
        logger.info("Organisation dependencies initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize organisation dependencies: {e}")
        return False 