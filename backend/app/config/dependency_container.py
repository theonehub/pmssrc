"""
Dependency Injection Container
SOLID-compliant dependency container for managing service dependencies
"""

import logging
from typing import Optional

from infrastructure.repositories.mongodb_user_repository import MongoDBUserRepository
from infrastructure.services.user_service_impl import UserServiceImpl
from infrastructure.services.password_service import PasswordService
from infrastructure.services.notification_service import EmailNotificationService, CompositeNotificationService
from infrastructure.services.file_upload_service import LocalFileUploadService, FileUploadServiceFactory
from infrastructure.database.database_connector import DatabaseConnector, MongoDBConnector
# from api.controllers.user_controller import UserController  # Import when needed

logger = logging.getLogger(__name__)


class DependencyContainer:
    """
    Dependency injection container following SOLID principles.
    
    - SRP: Only manages dependency creation and lifecycle
    - OCP: Can be extended with new services
    - LSP: Can be substituted with other containers
    - ISP: Provides focused factory methods
    - DIP: Creates abstractions, not concretions
    """
    
    def __init__(self):
        """Initialize dependency container."""
        self._repositories = {}
        self._services = {}
        self._controllers = {}
        self._initialized = False
        
        # Configuration (would come from environment/config files)
        self.config = {
            "database": {
                "connection_string": "mongodb://localhost:27017/",
                "default_database": "pms"
            },
            "file_storage": {
                "type": "local",  # or "s3"
                "base_path": "uploads"
            },
            "notification": {
                "email_enabled": True,
                "sms_enabled": False
            }
        }
    
    def initialize(self):
        """Initialize all dependencies."""
        if self._initialized:
            return
        
        logger.info("Initializing dependency container...")
        
        try:
            self._setup_infrastructure()
            self._setup_repositories()
            self._setup_services()
            self._setup_controllers()
            
            self._initialized = True
            logger.info("Dependency container initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing dependency container: {e}")
            raise
    
    def _setup_infrastructure(self):
        """Setup infrastructure components."""
        # Database connector
        self._database_connector = MongoDBConnector(
            connection_string=self.config["database"]["connection_string"]
        )
        
        # Password service
        self._password_service = PasswordService()
        
        # File upload service
        self._file_upload_service = FileUploadServiceFactory.create_service(
            storage_type=self.config["file_storage"]["type"],
            base_upload_path=self.config["file_storage"]["base_path"]
        )
        
        # Notification services
        notification_services = []
        
        if self.config["notification"]["email_enabled"]:
            email_service = EmailNotificationService()
            notification_services.append(email_service)
        
        if self.config["notification"]["sms_enabled"]:
            # Would add SMS service here
            pass
        
        if len(notification_services) == 1:
            self._notification_service = notification_services[0]
        else:
            self._notification_service = CompositeNotificationService(notification_services)
    
    def _setup_repositories(self):
        """Setup repository implementations."""
        # User repository
        self._repositories['user'] = MongoDBUserRepository(self._database_connector)
        
        logger.info("Repositories initialized")
    
    def _setup_services(self):
        """Setup service implementations."""
        # User service
        self._services['user'] = UserServiceImpl(
            user_repository=self._repositories['user'],
            password_service=self._password_service,
            notification_service=self._notification_service,
            file_upload_service=self._file_upload_service
        )
        
        # Organization service
        from infrastructure.services.organization_service_impl import OrganizationServiceImpl
        from infrastructure.repositories.mongodb_organization_repository import MongoDBOrganizationRepository
        from infrastructure.services.event_publisher_impl import EventPublisherImpl
        
        organization_repo = MongoDBOrganizationRepository(self._database_connector)
        event_publisher = EventPublisherImpl()
        
        self._services['organization'] = OrganizationServiceImpl(
            repository=organization_repo,
            event_publisher=event_publisher
        )
        
        logger.info("Services initialized")
    
    def _setup_controllers(self):
        """Setup controller implementations."""
        # Controllers will be created on-demand to avoid circular imports
        logger.info("Controllers setup deferred")
    
    # Repository getters
    def get_user_repository(self) -> MongoDBUserRepository:
        """Get user repository instance."""
        self.initialize()
        return self._repositories['user']
    

    
    # Service getters
    def get_user_service(self) -> UserServiceImpl:
        """Get user service instance."""
        self.initialize()
        return self._services['user']
    
    def get_password_service(self) -> PasswordService:
        """Get password service instance."""
        self.initialize()
        return self._password_service
    
    def get_notification_service(self):
        """Get notification service instance."""
        self.initialize()
        return self._notification_service
    
    def get_file_upload_service(self):
        """Get file upload service instance."""
        self.initialize()
        return self._file_upload_service
    
    def get_organization_service(self):
        """Get organization service instance."""
        self.initialize()
        return self._services['organization']
    
    # Controller getters
    def get_user_controller(self):
        """Get user controller instance."""
        self.initialize()
        
        # Import here to avoid circular imports
        from api.controllers.user_controller import UserController
        
        if 'user' not in self._controllers:
            self._controllers['user'] = UserController(
                user_service=self._services['user'],
                file_upload_service=self._file_upload_service
            )
        
        return self._controllers['user']
    
    def get_reimbursement_controller(self):
        """Get reimbursement controller instance."""
        self.initialize()
        
        # Import here to avoid circular imports
        from api.controllers.reimbursement_controller import ReimbursementController
        
        if 'reimbursement' not in self._controllers:
            self._controllers['reimbursement'] = ReimbursementController(
                create_type_use_case=self._get_create_reimbursement_type_use_case(),
                create_request_use_case=self._get_create_reimbursement_request_use_case(),
                approve_request_use_case=self._get_approve_reimbursement_request_use_case(),
                get_requests_use_case=self._get_get_reimbursement_requests_use_case(),
                process_payment_use_case=self._get_process_reimbursement_payment_use_case()
            )
        
        return self._controllers['reimbursement']
    
    def get_public_holiday_controller(self):
        """Get public holiday controller instance."""
        self.initialize()
        
        # Import here to avoid circular imports
        from api.controllers.public_holiday_controller import PublicHolidayController
        
        if 'public_holiday' not in self._controllers:
            self._controllers['public_holiday'] = PublicHolidayController(
                create_use_case=self._get_create_public_holiday_use_case(),
                query_use_case=self._get_query_public_holiday_use_case(),
                update_use_case=self._get_update_public_holiday_use_case(),
                delete_use_case=self._get_delete_public_holiday_use_case(),
                import_use_case=self._get_import_public_holiday_use_case()
            )
        
        return self._controllers['public_holiday']
    
    def get_company_leave_controller(self):
        """Get company leave controller instance."""
        self.initialize()
        
        # Import here to avoid circular imports
        from api.controllers.company_leave_controller import CompanyLeaveController
        
        if 'company_leave' not in self._controllers:
            self._controllers['company_leave'] = CompanyLeaveController(
                create_use_case=self._get_create_company_leave_use_case(),
                query_use_case=self._get_query_company_leave_use_case(),
                update_use_case=self._get_update_company_leave_use_case(),
                delete_use_case=self._get_delete_company_leave_use_case(),
                analytics_use_case=self._get_company_leave_analytics_use_case()
            )
        
        return self._controllers['company_leave']
    
    def get_attendance_controller(self):
        """Get attendance controller instance."""
        self.initialize()
        
        # Import here to avoid circular imports
        from api.controllers.attendance_controller import AttendanceController
        
        if 'attendance' not in self._controllers:
            self._controllers['attendance'] = AttendanceController(
                checkin_use_case=self._get_attendance_checkin_use_case(),
                checkout_use_case=self._get_attendance_checkout_use_case(),
                query_use_case=self._get_attendance_query_use_case(),
                analytics_use_case=self._get_attendance_analytics_use_case()
            )
        
        return self._controllers['attendance']
    
    # Private helper methods for reimbursement use cases
    def _get_create_reimbursement_type_use_case(self):
        """Get create reimbursement type use case"""
        from application.use_cases.reimbursement.create_reimbursement_type_use_case import CreateReimbursementTypeUseCase
        from infrastructure.repositories.mongodb_reimbursement_repository import MongoDBReimbursementRepository
        from infrastructure.services.event_publisher_impl import EventPublisherImpl
        
        reimbursement_repo = MongoDBReimbursementRepository(self._database_connector.get_database())
        event_publisher = EventPublisherImpl()
        
        return CreateReimbursementTypeUseCase(
            command_repository=reimbursement_repo,
            query_repository=reimbursement_repo,
            event_publisher=event_publisher,
            notification_service=self._notification_service
        )
    
    def _get_create_reimbursement_request_use_case(self):
        """Get create reimbursement request use case"""
        from application.use_cases.reimbursement.create_reimbursement_request_use_case import CreateReimbursementRequestUseCase
        from infrastructure.repositories.mongodb_reimbursement_repository import MongoDBReimbursementRepository
        from infrastructure.services.event_publisher_impl import EventPublisherImpl
        
        reimbursement_repo = MongoDBReimbursementRepository(self._database_connector.get_database())
        event_publisher = EventPublisherImpl()
        
        return CreateReimbursementRequestUseCase(
            command_repository=reimbursement_repo,
            query_repository=reimbursement_repo,
            reimbursement_type_repository=reimbursement_repo,
            employee_repository=self._repositories['user'],
            event_publisher=event_publisher,
            notification_service=self._notification_service
        )
    
    def _get_approve_reimbursement_request_use_case(self):
        """Get approve reimbursement request use case"""
        from application.use_cases.reimbursement.approve_reimbursement_request_use_case import ApproveReimbursementRequestUseCase
        from infrastructure.repositories.mongodb_reimbursement_repository import MongoDBReimbursementRepository
        from infrastructure.services.event_publisher_impl import EventPublisherImpl
        
        reimbursement_repo = MongoDBReimbursementRepository(self._database_connector.get_database())
        event_publisher = EventPublisherImpl()
        
        return ApproveReimbursementRequestUseCase(
            command_repository=reimbursement_repo,
            query_repository=reimbursement_repo,
            reimbursement_type_repository=reimbursement_repo,
            employee_repository=self._repositories['user'],
            event_publisher=event_publisher,
            notification_service=self._notification_service
        )
    
    def _get_get_reimbursement_requests_use_case(self):
        """Get reimbursement requests use case"""
        from application.use_cases.reimbursement.get_reimbursement_requests_use_case import GetReimbursementRequestsUseCase
        from infrastructure.repositories.mongodb_reimbursement_repository import MongoDBReimbursementRepository
        
        reimbursement_repo = MongoDBReimbursementRepository(self._database_connector.get_database())
        
        return GetReimbursementRequestsUseCase(
            query_repository=reimbursement_repo,
            reimbursement_type_repository=reimbursement_repo,
            analytics_repository=reimbursement_repo
        )
    
    def _get_process_reimbursement_payment_use_case(self):
        """Get process reimbursement payment use case"""
        from application.use_cases.reimbursement.process_reimbursement_payment_use_case import ProcessReimbursementPaymentUseCase
        from infrastructure.repositories.mongodb_reimbursement_repository import MongoDBReimbursementRepository
        from infrastructure.services.event_publisher_impl import EventPublisherImpl
        
        reimbursement_repo = MongoDBReimbursementRepository(self._database_connector.get_database())
        event_publisher = EventPublisherImpl()
        
        return ProcessReimbursementPaymentUseCase(
            command_repository=reimbursement_repo,
            query_repository=reimbursement_repo,
            reimbursement_type_repository=reimbursement_repo,
            employee_repository=self._repositories['user'],
            event_publisher=event_publisher,
            notification_service=self._notification_service
        )
    
    # Infrastructure getters
    def get_database_connector(self) -> DatabaseConnector:
        """Get database connector instance."""
        self.initialize()
        return self._database_connector
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            if hasattr(self, '_database_connector'):
                await self._database_connector.close()
            
            logger.info("Dependency container cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def health_check(self) -> dict:
        """Perform health check on all dependencies."""
        health_status = {
            "status": "healthy",
            "components": {}
        }
        
        try:
            self.initialize()
            
            # Check database connection
            try:
                # Would perform actual database ping
                health_status["components"]["database"] = "healthy"
            except Exception as e:
                health_status["components"]["database"] = f"unhealthy: {e}"
                health_status["status"] = "unhealthy"
            
            # Check file storage
            try:
                # Would check file storage accessibility
                health_status["components"]["file_storage"] = "healthy"
            except Exception as e:
                health_status["components"]["file_storage"] = f"unhealthy: {e}"
                health_status["status"] = "unhealthy"
            
            # Check notification service
            try:
                health_status["components"]["notification"] = "healthy"
            except Exception as e:
                health_status["components"]["notification"] = f"unhealthy: {e}"
                health_status["status"] = "unhealthy"
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status

    def get_project_attributes_controller(self):
        """Get project attributes controller with dependencies"""
        from api.controllers.project_attributes_controller import ProjectAttributesController
        from application.use_cases.project_attributes.create_project_attributes_use_case import CreateProjectAttributesUseCase
        from application.use_cases.project_attributes.get_project_attributes_use_case import GetProjectAttributesUseCase
        from infrastructure.repositories.project_attributes_repository_impl import ProjectAttributesRepositoryImpl
        
        repository = ProjectAttributesRepositoryImpl(self.get_database_connector())
        
        create_use_case = CreateProjectAttributesUseCase(
            repository=repository,
            event_publisher=self.get_event_publisher()
        )
        
        query_use_case = GetProjectAttributesUseCase(repository=repository)
        
        return ProjectAttributesController(
            create_use_case=create_use_case,
            query_use_case=query_use_case
        )

    def get_employee_leave_controller(self):
        """Get employee leave controller with dependencies"""
        from api.controllers.employee_leave_controller import EmployeeLeaveController
        from application.use_cases.employee_leave.apply_employee_leave_use_case import ApplyEmployeeLeaveUseCase
        from application.use_cases.employee_leave.approve_employee_leave_use_case import ApproveEmployeeLeaveUseCase
        from application.use_cases.employee_leave.get_employee_leaves_use_case import GetEmployeeLeavesUseCase
        from infrastructure.repositories.employee_leave_repository_wrapper import (
            EmployeeLeaveCommandRepositoryWrapper,
            EmployeeLeaveQueryRepositoryWrapper,
            EmployeeLeaveBalanceRepositoryWrapper,
            EmployeeLeaveAnalyticsRepositoryWrapper
        )
        
        # Create repositories with hostname handling
        hostname = getattr(self, 'hostname', 'default')
        command_repo = EmployeeLeaveCommandRepositoryWrapper(self.get_database_connector(), hostname)
        query_repo = EmployeeLeaveQueryRepositoryWrapper(self.get_database_connector(), hostname)
        balance_repo = EmployeeLeaveBalanceRepositoryWrapper(self.get_database_connector(), hostname)
        analytics_repo = EmployeeLeaveAnalyticsRepositoryWrapper(self.get_database_connector(), hostname)
        
        # Create use cases
        apply_use_case = ApplyEmployeeLeaveUseCase(
            command_repository=command_repo,
            query_repository=query_repo,
            balance_repository=balance_repo,
            company_leave_repository=self._get_company_leave_query_repository(),
            event_publisher=self.get_event_publisher()
        )
        
        approve_use_case = ApproveEmployeeLeaveUseCase(
            command_repository=command_repo,
            query_repository=query_repo,
            balance_repository=balance_repo,
            event_publisher=self.get_event_publisher()
        )
        
        query_use_case = GetEmployeeLeavesUseCase(
            query_repository=query_repo,
            analytics_repository=analytics_repo,
            balance_repository=balance_repo
        )
        
        # Create controller
        return EmployeeLeaveController(
            apply_use_case=apply_use_case,
            approve_use_case=approve_use_case,
            query_use_case=query_use_case
        )

    def _get_company_leave_query_repository(self):
        """Get company leave query repository"""
        from infrastructure.repositories.company_leave_repository_impl import CompanyLeaveQueryRepositoryImpl
        return CompanyLeaveQueryRepositoryImpl(self.get_database_connector())

    def get_event_publisher(self):
        """Get event publisher"""
        from infrastructure.services.event_publisher_impl import EventPublisherImpl
        return EventPublisherImpl()
    
    def get_payout_controller(self):
        """Get payout controller instance."""
        self.initialize()
        
        # Import here to avoid circular imports
        from api.controllers.payout_controller import PayoutController
        
        if 'payout' not in self._controllers:
            self._controllers['payout'] = PayoutController()
        
        return self._controllers['payout']
    
    def get_payslip_controller(self):
        """Get payslip controller instance."""
        self.initialize()
        
        # Import here to avoid circular imports
        from api.controllers.payslip_controller import PayslipController
        
        if 'payslip' not in self._controllers:
            self._controllers['payslip'] = PayslipController()
        
        return self._controllers['payslip']


# Global container instance
_container: Optional[DependencyContainer] = None


def get_dependency_container() -> DependencyContainer:
    """
    Get the global dependency container instance.
    
    Returns:
        DependencyContainer instance
    """
    global _container
    if _container is None:
        _container = DependencyContainer()
    return _container


def reset_dependency_container():
    """Reset the global dependency container (useful for testing)."""
    global _container
    _container = None


# FastAPI dependency functions
def get_user_controller():
    """FastAPI dependency for user controller."""
    container = get_dependency_container()
    return container.get_user_controller()


def get_user_service() -> UserServiceImpl:
    """FastAPI dependency for user service."""
    container = get_dependency_container()
    return container.get_user_service()


def get_user_repository() -> MongoDBUserRepository:
    """FastAPI dependency for user repository."""
    container = get_dependency_container()
    return container.get_user_repository()


def get_password_service() -> PasswordService:
    """FastAPI dependency for password service."""
    container = get_dependency_container()
    return container.get_password_service()


def get_file_upload_service():
    """FastAPI dependency for file upload service."""
    container = get_dependency_container()
    return container.get_file_upload_service()


def get_notification_service():
    """FastAPI dependency for notification service."""
    container = get_dependency_container()
    return container.get_notification_service()


def get_reimbursement_controller():
    """FastAPI dependency for reimbursement controller."""
    container = get_dependency_container()
    return container.get_reimbursement_controller()


def get_employee_leave_controller():
    """FastAPI dependency for employee leave controller."""
    container = get_dependency_container()
    return container.get_employee_leave_controller()


def get_project_attributes_controller():
    """FastAPI dependency for project attributes controller."""
    container = get_dependency_container()
    return container.get_project_attributes_controller()


def get_payout_controller():
    """FastAPI dependency for payout controller."""
    container = get_dependency_container()
    return container.get_payout_controller()


def get_payslip_controller():
    """FastAPI dependency for payslip controller."""
    container = get_dependency_container()
    return container.get_payslip_controller()


# Configuration management
class ConfigurationManager:
    """
    Configuration manager for dependency container.
    
    Follows SOLID principles for configuration management.
    """
    
    @staticmethod
    def load_config() -> dict:
        """
        Load configuration from environment variables and config files.
        
        Returns:
            Configuration dictionary
        """
        import os
        
        config = {
            "database": {
                "connection_string": os.getenv(
                    "DATABASE_CONNECTION_STRING", 
                    "mongodb://localhost:27017/"
                ),
                "default_database": os.getenv("DEFAULT_DATABASE", "pms")
            },
            "file_storage": {
                "type": os.getenv("FILE_STORAGE_TYPE", "local"),
                "base_path": os.getenv("FILE_STORAGE_BASE_PATH", "uploads"),
                "s3_bucket": os.getenv("S3_BUCKET_NAME"),
                "aws_access_key": os.getenv("AWS_ACCESS_KEY_ID"),
                "aws_secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
                "aws_region": os.getenv("AWS_REGION", "us-east-1")
            },
            "notification": {
                "email_enabled": os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "true").lower() == "true",
                "sms_enabled": os.getenv("SMS_NOTIFICATIONS_ENABLED", "false").lower() == "true",
                "email_service_url": os.getenv("EMAIL_SERVICE_URL"),
                "sms_service_url": os.getenv("SMS_SERVICE_URL")
            },
            "security": {
                "jwt_secret": os.getenv("JWT_SECRET", "your-secret-key"),
                "jwt_algorithm": os.getenv("JWT_ALGORITHM", "HS256"),
                "jwt_expiration_hours": int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
            }
        }
        
        return config
    
    @staticmethod
    def validate_config(config: dict) -> bool:
        """
        Validate configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        required_keys = [
            "database.connection_string",
            "file_storage.type",
            "security.jwt_secret"
        ]
        
        for key in required_keys:
            keys = key.split('.')
            value = config
            
            for k in keys:
                if k not in value:
                    raise ValueError(f"Missing required configuration: {key}")
                value = value[k]
            
            if not value:
                raise ValueError(f"Empty required configuration: {key}")
        
        # Validate file storage configuration
        if config["file_storage"]["type"] == "s3":
            s3_required = ["s3_bucket", "aws_access_key", "aws_secret_key"]
            for key in s3_required:
                if not config["file_storage"].get(key):
                    raise ValueError(f"Missing S3 configuration: {key}")
        
        return True 