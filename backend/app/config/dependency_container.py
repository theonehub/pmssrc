"""
Dependency Injection Container
SOLID-compliant dependency container for managing service dependencies
"""

from typing import Optional

# Repository implementations - will be imported lazily to avoid circular imports

# Service implementations
from app.infrastructure.services.user_service_impl import UserServiceImpl
from app.infrastructure.services.organisation_service_impl import OrganisationServiceImpl
from app.infrastructure.services.company_leave_service_impl import CompanyLeaveServiceImpl
from app.infrastructure.services.public_holiday_service_impl import PublicHolidayServiceImpl
from app.infrastructure.services.tax_calculation_service_impl import TaxCalculationServiceImpl
from app.infrastructure.services.reimbursement_service_impl import ReimbursementServiceImpl
from app.infrastructure.services.project_attributes_service_impl import ProjectAttributesServiceImpl
from app.infrastructure.services.employee_leave_service_impl import EmployeeLeaveServiceImpl
from app.infrastructure.services.reporting_service_impl import ReportingServiceImpl
from app.infrastructure.services.lwp_calculation_service import LWPCalculationService
from app.infrastructure.services.file_generation_service_impl import FileGenerationServiceImpl

# Infrastructure services
from app.infrastructure.services.password_service import PasswordService
from app.infrastructure.services.notification_service import EmailNotificationService, CompositeNotificationService
from app.infrastructure.services.file_upload_service import LocalFileUploadService, FileUploadServiceFactory
from app.infrastructure.database.database_connector import DatabaseConnector
from app.infrastructure.database.mongodb_connector import MongoDBConnector

# Centralized configuration
from app.config.mongodb_config import (
    get_database_config as get_mongodb_config
)
from app.utils.logger import get_logger
from app.infrastructure.services.event_publisher_impl import EventPublisherImpl
from app.infrastructure.services.attendance_service_impl import AttendanceServiceImpl

logger = get_logger(__name__)


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
        
        self._db_config = get_database_config()
    
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
        # Database connector with centralized MongoDB configuration
        self._database_connector = MongoDBConnector()
        
        # Get configuration from centralized config
        self._mongodb_connection_string = self._db_config["connection_string"]
        self._mongodb_client_options = self._db_config["client_options"]
        
        # NOTE: Do NOT establish connection here! Let FastAPI's event loop handle it
        logger.info(f"MongoDB connector configured with database: {self._db_config['database_name']}")
        logger.info("MongoDB connection will be established lazily when first needed")
        
        # Password service
        self._password_service = PasswordService()
        
        # File upload service - using environment variable or default
        import os
        file_storage_config = {
            "type": os.getenv("FILE_STORAGE_TYPE", "local"),
            "base_path": os.getenv("FILE_STORAGE_BASE_PATH", "uploads")
        }
        
        self._file_upload_service = FileUploadServiceFactory.create_service(
            storage_type=file_storage_config["type"],
            base_upload_path=file_storage_config["base_path"]
        )
        
        # Notification services - using environment variables
        notification_services = []
        
        email_enabled = os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "true").lower() == "true"
        sms_enabled = os.getenv("SMS_NOTIFICATIONS_ENABLED", "false").lower() == "true"
        
        if email_enabled:
            email_service = EmailNotificationService()
            notification_services.append(email_service)
        
        if sms_enabled:
            # Would add SMS service here when implemented
            pass
        
        if len(notification_services) == 1:
            self._notification_service = notification_services[0]
        else:
            self._notification_service = CompositeNotificationService(notification_services)
    
    def _setup_repositories(self):
        """Setup repository implementations."""
        try:
            # Lazy import all repositories to avoid circular imports
            from app.infrastructure.repositories.mongodb_user_repository import MongoDBUserRepository
            from app.infrastructure.repositories.mongodb_organisation_repository import MongoDBOrganisationRepository
            from app.infrastructure.repositories.mongodb_public_holiday_repository import MongoDBPublicHolidayRepository
            from app.infrastructure.repositories.mongodb_company_leave_repository import MongoDBCompanyLeaveRepository
            from app.infrastructure.repositories.mongodb_salary_package_repository import MongoDBSalaryPackageRepository
            from app.infrastructure.repositories.mongodb_attendance_repository import MongoDBAttendanceRepository
            from app.infrastructure.repositories.mongodb_monthly_salary_repository import MongoDBMonthlySalaryRepository
            from app.infrastructure.repositories.mongodb_reimbursement_repository import MongoDBReimbursementRepository
            from app.infrastructure.repositories.project_attributes_repository_impl import ProjectAttributesRepositoryImpl
            from app.infrastructure.repositories.employee_leave_repository_impl import EmployeeLeaveRepositoryImpl
            from app.infrastructure.repositories.mongodb_reporting_repository import MongoDBReportingRepository
            
            # Create all repositories with database connector
            user_repository = MongoDBUserRepository(self._database_connector)
            organisation_repository = MongoDBOrganisationRepository(self._database_connector)
            public_holiday_repository = MongoDBPublicHolidayRepository(self._database_connector)
            company_leave_repository = MongoDBCompanyLeaveRepository(self._database_connector)
            salary_package_repository = MongoDBSalaryPackageRepository(self._database_connector)
            attendance_repository = MongoDBAttendanceRepository(self._database_connector)
            monthly_salary_repository = MongoDBMonthlySalaryRepository(self._database_connector)
            reimbursement_repository = MongoDBReimbursementRepository(self._database_connector)
            project_attributes_repository = ProjectAttributesRepositoryImpl(self._database_connector)
            employee_leave_repository = EmployeeLeaveRepositoryImpl(self._database_connector)
            reporting_repository = MongoDBReportingRepository(self._database_connector)
            
            # Configure connection for all repositories using centralized config
            repositories = [
                user_repository,
                organisation_repository,
                public_holiday_repository,
                company_leave_repository,
                salary_package_repository,
                monthly_salary_repository,
                attendance_repository,
                reimbursement_repository,
                project_attributes_repository,
                employee_leave_repository,
                reporting_repository
            ]
            
            for repo in repositories:
                if hasattr(repo, 'set_connection_config'):
                    repo.set_connection_config(
                        self._mongodb_connection_string,
                        self._mongodb_client_options
                    )
            
            # Store repositories
            self._repositories['user'] = user_repository
            self._repositories['organisation'] = organisation_repository
            self._repositories['public_holiday'] = public_holiday_repository
            self._repositories['company_leave'] = company_leave_repository
            self._repositories['salary_package'] = salary_package_repository
            self._repositories['monthly_salary'] = monthly_salary_repository
            self._repositories['attendance'] = attendance_repository
            self._repositories['reimbursement'] = reimbursement_repository
            self._repositories['project_attributes'] = project_attributes_repository
            self._repositories['employee_leave'] = employee_leave_repository
            self._repositories['reporting'] = reporting_repository
            
            # File generation service
            self._file_generation_service = FileGenerationServiceImpl(
                organisation_repository=organisation_repository,
                user_repository=user_repository
            )
            
            logger.info("Repositories initialized with centralized MongoDB configuration")
            
        except Exception as e:
            logger.error(f"Error setting up repositories: {e}")
            raise
    
    def _setup_services(self):
        """Setup service implementations."""
        try:
            # User service
            self._services['user'] = UserServiceImpl(
                user_repository=self._repositories['user'],
                company_leave_query_repository=self._repositories['company_leave'],
                organisation_query_repository=self._repositories['organisation'],
                organisation_command_repository=self._repositories['organisation'],
                password_service=self._password_service,
                notification_service=self._notification_service,
                file_upload_service=self._file_upload_service
            )
            
            # Organisation service
            self._services['organisation'] = OrganisationServiceImpl(
                repository=self._repositories['organisation'],
                notification_service=self._notification_service,
                event_publisher=self._get_event_publisher()
            )
            
            # Public holiday service
            self._services['public_holiday'] = PublicHolidayServiceImpl(
                public_holiday_repository=self._repositories['public_holiday'],
                notification_service=self._notification_service
            )
            
            # Company leave service
            self._services['company_leave'] = CompanyLeaveServiceImpl(
                repository=self._repositories['company_leave'],
                notification_service=self._notification_service
            )
            
            # Tax calculation service
            self._services['tax_calculation'] = TaxCalculationServiceImpl(
                salary_package_repository=self._repositories['salary_package'],
                user_repository=self._repositories['user']
            )
            
            # Attendance service with use cases
            attendance_use_cases = self._create_attendance_use_cases()
            self._services['attendance'] = AttendanceServiceImpl(
                repository=self._repositories['attendance'],
                notification_service=self._notification_service,
                checkin_use_case=attendance_use_cases['checkin'],
                checkout_use_case=attendance_use_cases['checkout'],
                query_use_case=attendance_use_cases['query'],
                analytics_use_case=attendance_use_cases['analytics']
            )
            
            # Reimbursement service  
            self._services['reimbursement'] = ReimbursementServiceImpl(
                repository=self._repositories['reimbursement'],
                notification_service=self._notification_service,
                employee_repository=self._repositories['user']  # Use user repository as employee repository
            )
            
            # Project attributes service
            self._services['project_attributes'] = ProjectAttributesServiceImpl(
                repository=self._repositories['project_attributes']
            )
            
            # Employee leave service
            self._services['employee_leave'] = EmployeeLeaveServiceImpl(
                repository=self._repositories['employee_leave']
            )
            
            # LWP calculation service
            self._services['lwp_calculation'] = LWPCalculationService(
                attendance_service=self._services['attendance'],
                employee_leave_repository=self._repositories['employee_leave'],
                public_holiday_repository=self._repositories['public_holiday']
            )
            
            # Reporting service
            self._services['reporting'] = ReportingServiceImpl(
                reporting_repository=self._repositories['reporting'],
                user_repository=self._repositories['user'],
                reimbursement_repository=self._repositories['reimbursement'],
                attendance_repository=self._repositories['attendance']
            )
            
            logger.info("Services initialized")
            
        except Exception as e:
            logger.error(f"Error setting up services: {e}")
            raise
    
    def _create_attendance_use_cases(self):
        """Create and configure attendance use cases"""
        try:
            # Import use cases here to avoid circular imports
            from app.application.use_cases.attendance.check_in_use_case import CheckInUseCase
            from app.application.use_cases.attendance.check_out_use_case import CheckOutUseCase
            from app.application.use_cases.attendance.attendance_query_use_case import AttendanceQueryUseCase
            from app.application.use_cases.attendance.attendance_analytics_use_case import AttendanceAnalyticsUseCase
            
            # Get required dependencies
            attendance_repository = self._repositories['attendance']
            event_publisher = self._get_event_publisher()
            
            # Use user repository as employee repository (users are employees)
            employee_repository = self._repositories['user']
            
            # Create use cases
            checkin_use_case = CheckInUseCase(
                attendance_command_repository=attendance_repository,
                attendance_query_repository=attendance_repository,
                employee_repository=employee_repository,
                event_publisher=event_publisher,
                notification_service=self._notification_service
            )
            
            checkout_use_case = CheckOutUseCase(
                attendance_command_repository=attendance_repository,
                attendance_query_repository=attendance_repository,
                employee_repository=employee_repository,
                event_publisher=event_publisher,
                notification_service=self._notification_service
            )
            
            query_use_case = AttendanceQueryUseCase(
                attendance_query_repository=attendance_repository,
                employee_repository=employee_repository
            )
            
            analytics_use_case = AttendanceAnalyticsUseCase(
                attendance_query_repository=attendance_repository,
                employee_repository=employee_repository
            )
            
            logger.info("Attendance use cases created successfully")
            
            return {
                'checkin': checkin_use_case,
                'checkout': checkout_use_case,
                'query': query_use_case,
                'analytics': analytics_use_case
            }
            
        except Exception as e:
            logger.error(f"Error creating attendance use cases: {e}")
            # Return None use cases to allow fallback behavior
            return {
                'checkin': None,
                'checkout': None,
                'query': None,
                'analytics': None
            }
    
    def _setup_controllers(self):
        """Setup controller implementations."""
        # Controllers will be created on-demand to avoid circular imports
        logger.info("Controllers setup deferred")
    
    # ==================== REPOSITORY GETTERS ====================
    
    def get_user_repository(self):
        """Get user repository instance."""
        self.initialize()
        return self._repositories['user']
    
    def get_organisation_repository(self):
        """Get organisation repository instance."""
        self.initialize()
        return self._repositories['organisation']
    
    def get_public_holiday_repository(self):
        """Get public holiday repository instance."""
        self.initialize()
        return self._repositories['public_holiday']
    
    def get_company_leave_repository(self):
        """Get company leave repository instance."""
        self.initialize()
        return self._repositories['company_leave']
    
    def get_attendance_repository(self):
        """Get attendance repository instance."""
        self.initialize()
        return self._repositories['attendance']
    
    def get_reimbursement_repository(self):
        """Get reimbursement repository instance."""
        self.initialize()
        return self._repositories['reimbursement']
    
    def get_project_attributes_repository(self):
        """Get project attributes repository instance."""
        self.initialize()
        return self._repositories['project_attributes']
    
    def get_employee_leave_repository(self):
        """Get employee leave repository instance."""
        self.initialize()
        return self._repositories['employee_leave']
    
    def get_reporting_repository(self):
        """Get reporting repository instance."""
        self.initialize()
        return self._repositories['reporting']
    
    def get_salary_package_repository(self):
        """Get salary package repository instance."""
        self.initialize()
        return self._repositories['salary_package']
    
    def get_monthly_salary_repository(self):
        """Get monthly salary repository instance."""
        self.initialize()
        return self._repositories['monthly_salary']
    
    # ==================== SERVICE GETTERS ====================
    
    def get_user_service(self) -> UserServiceImpl:
        """Get user service instance."""
        self.initialize()
        return self._services['user']
    
    def get_organisation_service(self) -> OrganisationServiceImpl:
        """Get organisation service instance."""
        self.initialize()
        return self._services['organisation']
    
    def get_public_holiday_service(self) -> PublicHolidayServiceImpl:
        """Get public holiday service instance."""
        self.initialize()
        return self._services['public_holiday']
    
    def get_company_leave_service(self) -> CompanyLeaveServiceImpl:
        """Get company leave service instance."""
        self.initialize()
        return self._services['company_leave']
    
    def get_attendance_service(self):
        """Get attendance service instance."""
        self.initialize()
        return self._services['attendance']
    
    def get_reimbursement_service(self) -> ReimbursementServiceImpl:
        """Get reimbursement service instance."""
        self.initialize()
        return self._services['reimbursement']
    
    def get_project_attributes_service(self) -> ProjectAttributesServiceImpl:
        """Get project attributes service instance."""
        self.initialize()
        return self._services['project_attributes']
    
    def get_employee_leave_service(self) -> EmployeeLeaveServiceImpl:
        """Get employee leave service instance."""
        self.initialize()
        return self._services['employee_leave']
    
    def get_reporting_service(self) -> ReportingServiceImpl:
        """Get reporting service instance."""
        self.initialize()
        return self._services['reporting']
    
    def get_lwp_calculation_service(self) -> LWPCalculationService:
        """Get LWP calculation service instance."""
        self.initialize()
        return self._services['lwp_calculation']
    
    def get_tax_calculation_service(self) -> TaxCalculationServiceImpl:
        """Get tax calculation service instance."""
        self.initialize()
        return self._services['tax_calculation']
    
    def get_file_generation_service(self) -> FileGenerationServiceImpl:
        """Get file generation service instance."""
        self.initialize()
        return self._file_generation_service
    
    
    # ==================== INFRASTRUCTURE SERVICE GETTERS ====================
    
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
    
    def get_database_connector(self) -> DatabaseConnector:
        """Get database connector instance."""
        self.initialize()
        return self._database_connector
    
    def get_database_config(self) -> dict:
        """Get complete database configuration."""
        return self._db_config
    
    def _get_event_publisher(self):
        """Get event publisher instance."""
        # Use enhanced event publisher with event store and handlers
        from app.infrastructure.services.enhanced_event_publisher import EnhancedEventPublisher
        from app.application.event_handlers.attendance_event_handlers import (
            AttendanceNotificationHandler,
            AttendanceAnalyticsHandler,
            AttendanceAuditHandler,
            AttendanceIntegrationHandler
        )
        
        try:
            # Create enhanced event publisher
            enhanced_publisher = EnhancedEventPublisher(self._database_connector)
            
            # Register attendance event handlers
            enhanced_publisher.register_handler(
                AttendanceNotificationHandler(self._notification_service, priority=50)
            )
            enhanced_publisher.register_handler(
                AttendanceAnalyticsHandler(priority=75)
            )
            enhanced_publisher.register_handler(
                AttendanceAuditHandler(priority=90)
            )
            enhanced_publisher.register_handler(
                AttendanceIntegrationHandler(priority=100)
            )
            
            logger.info("Enhanced event publisher configured with attendance handlers")
            return enhanced_publisher
            
        except Exception as e:
            logger.warning(f"Failed to create enhanced event publisher: {e}")
            # Fallback to simple implementation
            return EventPublisherImpl()
    
    # ==================== CONTROLLER GETTERS ====================
    
    def get_user_controller(self):
        """Get user controller instance."""
        self.initialize()
        
        # Import here to avoid circular imports
        from app.api.controllers.user_controller import UserController
        
        if 'user' not in self._controllers:
            self._controllers['user'] = UserController(
                user_service=self._services['user'],
                file_upload_service=self._file_upload_service
            )
        
        return self._controllers['user']
    
    def get_organisation_controller(self):
        """Get organisation controller instance."""
        self.initialize()
        
        # Import here to avoid circular imports
        from app.api.controllers.organisation_controller import OrganisationController
        from app.application.use_cases.organisation.create_organisation_use_case import CreateOrganisationUseCase
        from app.application.use_cases.organisation.update_organisation_use_case import UpdateOrganisationUseCase
        from app.application.use_cases.organisation.get_organisation_use_case import GetOrganisationUseCase
        from app.application.use_cases.organisation.list_organisations_use_case import ListOrganisationsUseCase
        from app.application.use_cases.organisation.delete_organisation_use_case import DeleteOrganisationUseCase
        
        if 'organisation' not in self._controllers:
            # Get repositories
            organisation_repository = self._repositories['organisation']
            
            # Get services (the OrganisationServiceImpl implements all service interfaces)
            organisation_service = self._services['organisation']
            
            # Create use cases with proper dependencies
            create_use_case = CreateOrganisationUseCase(
                command_repository=organisation_repository,
                query_repository=organisation_repository,
                validation_service=organisation_service,
                notification_service=organisation_service
            )
            
            update_use_case = UpdateOrganisationUseCase(
                command_repository=organisation_repository,
                query_repository=organisation_repository,
                validation_service=organisation_service,
                notification_service=organisation_service
            )
            
            get_use_case = GetOrganisationUseCase(
                query_repository=organisation_repository
            )
            
            list_use_case = ListOrganisationsUseCase(
                query_repository=organisation_repository
            )
            
            delete_use_case = DeleteOrganisationUseCase(
                command_repository=organisation_repository,
                query_repository=organisation_repository,
                notification_service=organisation_service
            )
            
            # Create controller with use cases
            self._controllers['organisation'] = OrganisationController(
                create_use_case=create_use_case,
                update_use_case=update_use_case,
                get_use_case=get_use_case,
                list_use_case=list_use_case,
                delete_use_case=delete_use_case
            )
        
        return self._controllers['organisation']
    
    def get_public_holiday_controller(self):
        """Get public holiday controller instance."""
        self.initialize()
        
        # Import here to avoid circular imports
        from app.api.controllers.public_holiday_controller import PublicHolidayController
        
        if 'public_holiday' not in self._controllers:
            self._controllers['public_holiday'] = PublicHolidayController(
                public_holiday_service=self.get_public_holiday_service()
            )
        
        return self._controllers['public_holiday']
    
    def get_company_leave_controller(self):
        """Get company leave controller instance."""
        self.initialize()
        
        # Import here to avoid circular imports
        from app.api.controllers.company_leave_controller import CompanyLeaveController
        
        if 'company_leave' not in self._controllers:
            self._controllers['company_leave'] = CompanyLeaveController(
                company_leave_service=self._services['company_leave']
            )
        
        return self._controllers['company_leave']
    
    def get_attendance_controller(self):
        """Get attendance controller instance."""
        self.initialize()
        
        # Import here to avoid circular imports
        from app.api.controllers.attendance_controller import AttendanceController
        
        if 'attendance' not in self._controllers:
            self._controllers['attendance'] = AttendanceController(
                attendance_service=self._services['attendance']
            )
        
        return self._controllers['attendance']
    
    def get_reimbursement_controller(self):
        """Get reimbursement controller instance."""
        self.initialize()
        
        # Import here to avoid circular imports
        from app.api.controllers.reimbursement_controller import ReimbursementController
        
        if 'reimbursement' not in self._controllers:
            self._controllers['reimbursement'] = ReimbursementController(
                reimbursement_service=self._services['reimbursement'],
                file_upload_service=self._file_upload_service
            )
        
        return self._controllers['reimbursement']
    
    def get_project_attributes_controller(self):
        """Get project attributes controller instance."""
        self.initialize()
        
        # Import here to avoid circular imports
        from app.api.controllers.project_attributes_controller import ProjectAttributesController
        
        if 'project_attributes' not in self._controllers:
            self._controllers['project_attributes'] = ProjectAttributesController(
                project_attributes_service=self._services['project_attributes']
            )
        
        return self._controllers['project_attributes']
    
    def get_employee_leave_controller(self):
        """Get employee leave controller instance."""
        self.initialize()
        
        # Import here to avoid circular imports
        from app.api.controllers.employee_leave_controller import EmployeeLeaveController
        from app.application.use_cases.employee_leave.get_employee_leaves_use_case import GetEmployeeLeavesUseCase
        from app.application.use_cases.employee_leave.apply_employee_leave_use_case import ApplyEmployeeLeaveUseCase
        from app.application.use_cases.employee_leave.approve_employee_leave_use_case import ApproveEmployeeLeaveUseCase
        
        if 'employee_leave' not in self._controllers:
            # Create query use case
            query_use_case = GetEmployeeLeavesUseCase(
                query_repository=self._repositories['employee_leave'],
                user_query_repository=self._repositories['user'],
                analytics_repository=self._repositories['employee_leave']  # Pass the same repository as it implements analytics interface
            )
            
            # Create apply use case
            apply_use_case = ApplyEmployeeLeaveUseCase(
                leave_command_repository=self._repositories['employee_leave'],
                leave_query_repository=self._repositories['employee_leave'],
                company_leave_repository=self._repositories['company_leave'],
                user_query_repository=self._repositories['user'],
                notification_service=self._notification_service
            )
            
            # Create approve use case
            approve_use_case = ApproveEmployeeLeaveUseCase(
                command_repository=self._repositories['employee_leave'],
                query_repository=self._repositories['employee_leave'],
                event_publisher=self._get_event_publisher(),
                email_service=None  # Email service not implemented yet
            )
            
            # Create controller with all use cases
            self._controllers['employee_leave'] = EmployeeLeaveController(
                apply_use_case=apply_use_case,
                approve_use_case=approve_use_case,
                query_use_case=query_use_case
            )
        
        return self._controllers['employee_leave']
    
    def get_reporting_controller(self):
        """Get reporting controller instance."""
        self.initialize()
        
        # Import here to avoid circular imports
        from app.api.controllers.reporting_controller import ReportingController
        
        if 'reporting' not in self._controllers:
            self._controllers['reporting'] = ReportingController(
                reporting_service=self._services['reporting']
            )
        
        return self._controllers['reporting']
    
    def get_taxation_controller(self):
        """Get taxation controller instance."""
        self.initialize()
        
        from app.api.controllers.taxation_controller import UnifiedTaxationController

        # Create controller with all handlers and services
        self._controllers['taxation'] = UnifiedTaxationController(
            user_repository=self._repositories['user'],
            salary_package_repository=self._repositories['salary_package'],
            monthly_salary_repository=self._repositories['monthly_salary']
        )
        
        return self._controllers['taxation']
    
    def get_export_controller(self):
        """Get export controller instance."""
        self.initialize()
        
        # Import here to avoid circular imports
        from app.api.controllers.export_controller import ExportController
        
        if 'export' not in self._controllers:
            self._controllers['export'] = ExportController(
                file_generation_service=self._file_generation_service,
                monthly_salary_repository=self._repositories['monthly_salary'],
                taxation_controller=self.get_taxation_controller()
            )
        
        return self._controllers['export']
    

    # ==================== UTILITY METHODS ====================
    
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
            "components": {},
            "database_config": {
                "database_name": self._db_config["database_name"],
                "connection_configured": bool(self._db_config["connection_string"])
            }
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


# ==================== GLOBAL CONTAINER INSTANCE ====================

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


# ==================== FASTAPI DEPENDENCY FUNCTIONS ====================

def get_user_controller():
    """FastAPI dependency for user controller."""
    container = get_dependency_container()
    return container.get_user_controller()


def get_user_service() -> UserServiceImpl:
    """FastAPI dependency for user service."""
    container = get_dependency_container()
    return container.get_user_service()


def get_user_repository():
    """FastAPI dependency for user repository."""
    container = get_dependency_container()
    return container.get_user_repository()


def get_organisation_controller():
    """FastAPI dependency for organisation controller."""
    container = get_dependency_container()
    return container.get_organisation_controller()


def get_organisation_service():
    """FastAPI dependency for organisation service."""
    container = get_dependency_container()
    return container.get_organisation_service()


def get_organisation_repository():
    """FastAPI dependency for organisation repository."""
    container = get_dependency_container()
    return container.get_organisation_repository()


def get_public_holiday_controller():
    """FastAPI dependency for public holiday controller."""
    container = get_dependency_container()
    return container.get_public_holiday_controller()


def get_public_holiday_service():
    """FastAPI dependency for public holiday service."""
    container = get_dependency_container()
    return container.get_public_holiday_service()


def get_public_holiday_repository():
    """FastAPI dependency for public holiday repository."""
    container = get_dependency_container()
    return container.get_public_holiday_repository()


def get_company_leave_controller():
    """FastAPI dependency for company leave controller."""
    container = get_dependency_container()
    return container.get_company_leave_controller()


def get_company_leave_service():
    """FastAPI dependency for company leave service."""
    container = get_dependency_container()
    return container.get_company_leave_service()


def get_company_leave_repository():
    """Get company leave repository instance."""
    container = get_dependency_container()
    return container.get_company_leave_repository()


def get_attendance_controller():
    """Get attendance controller instance."""
    container = get_dependency_container()
    return container.get_attendance_controller()


def get_attendance_service():
    """FastAPI dependency for attendance service."""
    # container = get_dependency_container()
    # return container.get_attendance_service()
    raise NotImplementedError("Attendance service temporarily disabled due to circular import")


def get_reimbursement_controller():
    """FastAPI dependency for reimbursement controller."""
    container = get_dependency_container()
    return container.get_reimbursement_controller()


def get_reimbursement_service():
    """FastAPI dependency for reimbursement service."""
    container = get_dependency_container()
    return container.get_reimbursement_service()


def get_reimbursement_repository():
    """FastAPI dependency for reimbursement repository."""
    container = get_dependency_container()
    return container.get_reimbursement_repository()


def get_project_attributes_controller():
    """FastAPI dependency for project attributes controller."""
    container = get_dependency_container()
    return container.get_project_attributes_controller()


def get_project_attributes_service():
    """FastAPI dependency for project attributes service."""
    container = get_dependency_container()
    return container.get_project_attributes_service()


def get_project_attributes_repository():
    """FastAPI dependency for project attributes repository."""
    container = get_dependency_container()
    return container.get_project_attributes_repository()


def get_employee_leave_controller():
    """Get employee leave controller instance."""
    container = get_dependency_container()
    return container.get_employee_leave_controller()


def get_employee_leave_service():
    """FastAPI dependency for employee leave service."""
    container = get_dependency_container()
    return container.get_employee_leave_service()


def get_employee_leave_repository():
    """FastAPI dependency for employee leave repository."""
    container = get_dependency_container()
    return container.get_employee_leave_repository()


def get_payout_controller():
    """FastAPI dependency for payout controller."""
    container = get_dependency_container()
    return container.get_payout_controller()


def get_payslip_controller():
    """FastAPI dependency for payslip controller."""
    container = get_dependency_container()
    return container.get_payslip_controller()


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


def get_database_config() -> dict:
    """FastAPI dependency for database configuration."""
    return get_mongodb_config()


def get_attendance_repository():
    """FastAPI dependency for attendance repository."""
    container = get_dependency_container()
    return container.get_attendance_repository()


def get_reporting_controller():
    """FastAPI dependency for reporting controller."""
    container = get_dependency_container()
    return container.get_reporting_controller()


def get_reporting_service():
    """FastAPI dependency for reporting service."""
    container = get_dependency_container()
    return container.get_reporting_service()


def get_reporting_repository():
    """FastAPI dependency for reporting repository."""
    container = get_dependency_container()
    return container.get_reporting_repository()


def get_tax_calculation_service():
    """FastAPI dependency for tax calculation service."""
    container = get_dependency_container()
    return container.get_tax_calculation_service()

def get_taxation_controller():
    """FastAPI dependency for taxation controller."""
    container = get_dependency_container()
    return container.get_taxation_controller()


def get_export_controller():
    """FastAPI dependency for export controller."""
    container = get_dependency_container()
    return container.get_export_controller()
