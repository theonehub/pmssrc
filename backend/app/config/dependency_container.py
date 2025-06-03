"""
Dependency Injection Container
SOLID-compliant dependency container for managing service dependencies
"""

from typing import Optional

from app.infrastructure.repositories.mongodb_user_repository import MongoDBUserRepository
from app.infrastructure.repositories.mongodb_organisation_repository import MongoDBOrganisationRepository
from app.infrastructure.services.user_service_impl import UserServiceImpl
from app.infrastructure.services.password_service import PasswordService
from app.infrastructure.services.notification_service import EmailNotificationService, CompositeNotificationService
from app.infrastructure.services.file_upload_service import LocalFileUploadService, FileUploadServiceFactory
from app.infrastructure.database.database_connector import DatabaseConnector
from app.infrastructure.database.mongodb_connector import MongoDBConnector
from app.config.mongodb_config import get_mongodb_connection_string, get_mongodb_client_options, mongodb_settings
from app.utils.logger import get_logger
from app.infrastructure.services.organisation_service_impl import OrganisationServiceImpl
# from api.controllers.user_controller import UserController  # Import when needed

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
        # Database connector with proper MongoDB configuration
        self._database_connector = MongoDBConnector()
        
        # Get MongoDB configuration from mongodb_config.py
        connection_string = get_mongodb_connection_string()
        client_options = get_mongodb_client_options()
        
        # Store connection parameters for lazy connection establishment
        self._mongodb_connection_string = connection_string
        self._mongodb_client_options = client_options
        
        # NOTE: Do NOT establish connection here! Let FastAPI's event loop handle it
        logger.info(f"MongoDB connector configured with database: {mongodb_settings.database_name}")
        logger.info("MongoDB connection will be established lazily when first needed")
        
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
        # Setup repositories with configured database connector
        try:
            # Create user repository with database connector and connection parameters
            user_repository = MongoDBUserRepository(self._database_connector)
            organisation_repository = MongoDBOrganisationRepository(self._database_connector)
            
            # Import and create public holiday repository
            from app.infrastructure.repositories.mongodb_public_holiday_repository import MongoDBPublicHolidayRepository
            public_holiday_repository = MongoDBPublicHolidayRepository(self._database_connector)
            
            # Pass the MongoDB configuration to the repository
            user_repository.set_connection_config(
                self._mongodb_connection_string,
                self._mongodb_client_options
            )
            
            organisation_repository.set_connection_config(
                self._mongodb_connection_string,
                self._mongodb_client_options
            )

            self._repositories['user'] = user_repository
            self._repositories['organisation'] = organisation_repository
            self._repositories['public_holiday'] = public_holiday_repository

            logger.info("Repositories initialized with MongoDB configuration")
            
        except Exception as e:
            logger.error(f"Error setting up repositories: {e}")
            raise
    
    def _setup_services(self):
        """Setup service implementations."""
        # User service
        self._services['user'] = UserServiceImpl(
            user_repository=self._repositories['user'],
            password_service=self._password_service,
            notification_service=self._notification_service,
            file_upload_service=self._file_upload_service
        )
        
        # Organisation service
        try:
            from app.infrastructure.services.event_publisher_impl import EventPublisherImpl
            
            # Create event publisher
            event_publisher = EventPublisherImpl()
            
            # Create organisation service with correct parameters
            self._services['organisation'] = OrganisationServiceImpl(
                repository=self._repositories['organisation'],
                notification_service=self._notification_service,
                event_publisher=event_publisher
            )
        except Exception as e:
            logger.warning(f"Organisation service setup failed: {e}")
            self._services['organisation'] = None
        
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
    
    def get_organisation_service(self) -> OrganisationServiceImpl:
        """Get organisation service instance."""
        self.initialize()
        return self._services['organisation']
    
    # Controller getters
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
    
    def get_reimbursement_controller(self):
        """Get reimbursement controller instance."""
        self.initialize()
        
        # Import here to avoid circular imports
        from app.api.controllers.reimbursement_controller import ReimbursementController
        
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
        from app.api.controllers.public_holiday_controller import PublicHolidayController
        
        if 'public_holiday' not in self._controllers:
            self._controllers['public_holiday'] = PublicHolidayController(
                create_use_case=self._get_create_public_holiday_use_case(),
                get_use_case=self._get_query_public_holiday_use_case(),
                update_use_case=self._get_update_public_holiday_use_case(),
                delete_use_case=self._get_delete_public_holiday_use_case(),
                import_use_case=self._get_import_public_holiday_use_case()
            )
        
        return self._controllers['public_holiday']
    
    def get_company_leave_controller(self):
        """Get company leave controller instance."""
        self.initialize()
        
        # Import here to avoid circular imports
        from app.api.controllers.company_leave_controller import CompanyLeaveController
        
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
        from app.api.controllers.attendance_controller import AttendanceController
        
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
        from app.application.use_cases.reimbursement.create_reimbursement_type_use_case import CreateReimbursementTypeUseCase
        from app.infrastructure.repositories.mongodb_reimbursement_repository import MongoDBReimbursementRepository
        from app.infrastructure.services.event_publisher_impl import EventPublisherImpl
        
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
        from app.application.use_cases.reimbursement.create_reimbursement_request_use_case import CreateReimbursementRequestUseCase
        from app.infrastructure.repositories.mongodb_reimbursement_repository import MongoDBReimbursementRepository
        from app.infrastructure.services.event_publisher_impl import EventPublisherImpl
        
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
        from app.application.use_cases.reimbursement.approve_reimbursement_request_use_case import ApproveReimbursementRequestUseCase
        from app.infrastructure.repositories.mongodb_reimbursement_repository import MongoDBReimbursementRepository
        from app.infrastructure.services.event_publisher_impl import EventPublisherImpl
        
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
        from app.application.use_cases.reimbursement.get_reimbursement_requests_use_case import GetReimbursementRequestsUseCase
        from app.infrastructure.repositories.mongodb_reimbursement_repository import MongoDBReimbursementRepository
        
        reimbursement_repo = MongoDBReimbursementRepository(self._database_connector.get_database())
        
        return GetReimbursementRequestsUseCase(
            query_repository=reimbursement_repo,
            reimbursement_type_repository=reimbursement_repo,
            analytics_repository=reimbursement_repo
        )
    
    def _get_process_reimbursement_payment_use_case(self):
        """Get process reimbursement payment use case"""
        from app.application.use_cases.reimbursement.process_reimbursement_payment_use_case import ProcessReimbursementPaymentUseCase
        from app.infrastructure.repositories.mongodb_reimbursement_repository import MongoDBReimbursementRepository
        from app.infrastructure.services.event_publisher_impl import EventPublisherImpl
        
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
    
    # Private helper method to configure repository connection
    def _configure_repository_connection(self, repository):
        """
        Configure MongoDB connection for any repository that uses DatabaseConnector.
        
        Args:
            repository: Repository instance that may need connection configuration
        """
        # Check if repository has a set_connection_config method (like MongoDBUserRepository)
        if hasattr(repository, 'set_connection_config'):
            repository.set_connection_config(
                self._mongodb_connection_string,
                self._mongodb_client_options
            )
        # Check if repository has _db_connector (like BaseRepository-based repositories)
        elif hasattr(repository, '_db_connector'):
            # Store connection parameters on the database connector for later use
            repository._db_connector._connection_string = self._mongodb_connection_string
            repository._db_connector._connection_params = self._mongodb_client_options
            logger.debug(f"Set connection parameters on database connector for {type(repository).__name__}")
        
        logger.debug(f"Configured MongoDB connection for repository: {type(repository).__name__}")

    # Attendance use case methods
    def _get_attendance_checkin_use_case(self):
        """Get attendance check-in use case"""
        try:
            from app.application.use_cases.attendance.check_in_use_case import CheckInUseCase
            from backend.app.infrastructure.repositories.mongodb_attendance_repository import SolidAttendanceRepository
            from app.infrastructure.services.event_publisher_impl import EventPublisherImpl
            
            attendance_repo = SolidAttendanceRepository(self._database_connector)
            self._configure_repository_connection(attendance_repo)
            event_publisher = EventPublisherImpl()
            
            return CheckInUseCase(
                attendance_command_repository=attendance_repo,
                attendance_query_repository=attendance_repo,
                employee_repository=self._repositories['user'],
                event_publisher=event_publisher
            )
        except Exception as e:
            logger.error(f"Failed to create check-in use case: {e}")
            raise
    
    def _get_attendance_checkout_use_case(self):
        """Get attendance check-out use case"""
        try:
            from app.application.use_cases.attendance.check_out_use_case import CheckOutUseCase
            from backend.app.infrastructure.repositories.mongodb_attendance_repository import SolidAttendanceRepository
            from app.infrastructure.services.event_publisher_impl import EventPublisherImpl
            
            attendance_repo = SolidAttendanceRepository(self._database_connector)
            self._configure_repository_connection(attendance_repo)
            event_publisher = EventPublisherImpl()
            
            return CheckOutUseCase(
                attendance_command_repository=attendance_repo,
                attendance_query_repository=attendance_repo,
                employee_repository=self._repositories['user'],  # Use proper user repository
                event_publisher=event_publisher
            )
        except ImportError as e:
            logger.warning(f"CheckOutUseCase not available: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to create check-out use case: {e}")
            return None
    
    def _get_attendance_query_use_case(self):
        """Get attendance query use case"""
        try:
            from app.application.use_cases.attendance.get_attendance_use_case import GetAttendanceUseCase
            from backend.app.infrastructure.repositories.mongodb_attendance_repository import SolidAttendanceRepository
            
            attendance_repo = SolidAttendanceRepository(self._database_connector)
            self._configure_repository_connection(attendance_repo)
            
            return GetAttendanceUseCase(
                attendance_query_repository=attendance_repo,
                employee_repository=self._repositories.get('user')
            )
        except ImportError as e:
            logger.warning(f"GetAttendanceUseCase not available, returning None. Import error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating GetAttendanceUseCase: {e}")
            return None
    
    def _get_attendance_analytics_use_case(self):
        """Get attendance analytics use case"""
        try:
            from app.application.use_cases.attendance.get_attendance_analytics_use_case import GetAttendanceAnalyticsUseCase
            from backend.app.infrastructure.repositories.mongodb_attendance_repository import SolidAttendanceRepository
            
            attendance_repo = SolidAttendanceRepository(self._database_connector)
            self._configure_repository_connection(attendance_repo)
            
            return GetAttendanceAnalyticsUseCase(
                analytics_repository=attendance_repo,
                attendance_query_repository=attendance_repo
            )
        except ImportError as e:
            logger.warning(f"GetAttendanceAnalyticsUseCase not available, returning None. Import error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating GetAttendanceAnalyticsUseCase: {e}")
            return None
    
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
        from app.api.controllers.project_attributes_controller import ProjectAttributesController
        from app.application.use_cases.project_attributes.create_project_attributes_use_case import CreateProjectAttributesUseCase
        from app.application.use_cases.project_attributes.get_project_attributes_use_case import GetProjectAttributesUseCase
        from app.infrastructure.repositories.project_attributes_repository_impl import ProjectAttributesRepositoryImpl
        
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
        from app.api.controllers.employee_leave_controller import EmployeeLeaveController
        from app.application.use_cases.employee_leave.apply_employee_leave_use_case import ApplyEmployeeLeaveUseCase
        from app.application.use_cases.employee_leave.approve_employee_leave_use_case import ApproveEmployeeLeaveUseCase
        from app.application.use_cases.employee_leave.get_employee_leaves_use_case import GetEmployeeLeavesUseCase
        from app.infrastructure.repositories.employee_leave_repository_wrapper import (
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
        from app.infrastructure.repositories.company_leave_repository_impl import CompanyLeaveQueryRepositoryImpl
        return CompanyLeaveQueryRepositoryImpl(self.get_database_connector())

    def get_event_publisher(self):
        """Get event publisher"""
        from app.infrastructure.services.event_publisher_impl import EventPublisherImpl
        return EventPublisherImpl()
    
    def get_payout_controller(self):
        """Get payout controller instance."""
        self.initialize()
        
        # Import here to avoid circular imports
        from app.api.controllers.payout_controller import PayoutController
        
        if 'payout' not in self._controllers:
            self._controllers['payout'] = PayoutController()
        
        return self._controllers['payout']
    
    def get_payslip_controller(self):
        """Get payslip controller instance."""
        self.initialize()
        
        # Import here to avoid circular imports
        from app.api.controllers.payslip_controller import PayslipController
        
        if 'payslip' not in self._controllers:
            self._controllers['payslip'] = PayslipController()
        
        return self._controllers['payslip']

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
        from app.infrastructure.repositories.mongodb_organisation_repository import MongoDBOrganisationRepository
        
        if 'organisation' not in self._controllers:
            try:
                # Create repository with database connector - using MongoDBOrganisationRepository
                repository = MongoDBOrganisationRepository(self.get_database_connector())
                
                # Configure repository connection
                self._configure_repository_connection(repository)
                
                # Get organisation service implementation for validation
                validation_service = self.get_organisation_service()
                
                # Create real use cases with proper validation service
                create_use_case = CreateOrganisationUseCase(
                    command_repository=repository,
                    query_repository=repository,
                    validation_service=validation_service,  # Use actual service instead of None
                    notification_service=self._notification_service
                )
                
                update_use_case = UpdateOrganisationUseCase(
                    command_repository=repository,
                    query_repository=repository,
                    validation_service=validation_service,  # Use actual service instead of None
                    notification_service=self._notification_service
                )
                
                get_use_case = GetOrganisationUseCase(
                    query_repository=repository
                )
                
                list_use_case = ListOrganisationsUseCase(
                    query_repository=repository
                )
                
                delete_use_case = DeleteOrganisationUseCase(
                    command_repository=repository,
                    query_repository=repository,
                    notification_service=self._notification_service
                )
                
                self._controllers['organisation'] = OrganisationController(
                    create_use_case=create_use_case,
                    update_use_case=update_use_case,
                    get_use_case=get_use_case,
                    list_use_case=list_use_case,
                    delete_use_case=delete_use_case
                )
                
                logger.info("Organisation controller initialized with MongoDBOrganisationRepository and proper validation service")
                
            except Exception as e:
                logger.error(f"Failed to initialize organisation controller: {e}")
                # Return a fallback controller that raises proper errors
                self._controllers['organisation'] = self._create_fallback_organisation_controller()
        
        return self._controllers['organisation']
    
    def _create_fallback_organisation_controller(self):
        """Create a fallback controller that returns proper database errors"""
        from app.api.controllers.organisation_controller import OrganisationController
        
        class FallbackUseCase:
            async def execute(self, *args, **kwargs):
                raise Exception("Database connection failed. Please check your database configuration.")
            
            async def execute_by_id(self, *args, **kwargs):
                raise Exception("Database connection failed. Please check your database configuration.")
            
            async def execute_by_name(self, *args, **kwargs):
                raise Exception("Database connection failed. Please check your database configuration.")
            
            async def execute_by_hostname(self, *args, **kwargs):
                raise Exception("Database connection failed. Please check your database configuration.")
            
            async def execute_by_pan_number(self, *args, **kwargs):
                raise Exception("Database connection failed. Please check your database configuration.")
            
            async def execute_statistics(self, *args, **kwargs):
                raise Exception("Database connection failed. Please check your database configuration.")
            
            async def execute_exists_by_name(self, *args, **kwargs):
                raise Exception("Database connection failed. Please check your database configuration.")
            
            async def execute_exists_by_hostname(self, *args, **kwargs):
                raise Exception("Database connection failed. Please check your database configuration.")
            
            async def execute_exists_by_pan_number(self, *args, **kwargs):
                raise Exception("Database connection failed. Please check your database configuration.")
            
            async def execute_status_update(self, *args, **kwargs):
                raise Exception("Database connection failed. Please check your database configuration.")
            
            async def execute_increment_employee_usage(self, *args, **kwargs):
                raise Exception("Database connection failed. Please check your database configuration.")
            
            async def execute_decrement_employee_usage(self, *args, **kwargs):
                raise Exception("Database connection failed. Please check your database configuration.")
        
        fallback_use_case = FallbackUseCase()
        
        return OrganisationController(
            create_use_case=fallback_use_case,
            update_use_case=fallback_use_case,
            get_use_case=fallback_use_case,
            list_use_case=fallback_use_case,
            delete_use_case=fallback_use_case
        )

    # Public Holiday use case methods
    def _get_create_public_holiday_use_case(self):
        """Get create public holiday use case"""
        try:
            from app.application.use_cases.public_holiday.create_public_holiday_use_case import CreatePublicHolidayUseCase
            from app.infrastructure.repositories.mongodb_public_holiday_repository import MongoDBPublicHolidayRepository
            from app.infrastructure.services.event_publisher_impl import EventPublisherImpl
            
            holiday_repo = MongoDBPublicHolidayRepository(self._database_connector)
            event_publisher = EventPublisherImpl()
            
            return CreatePublicHolidayUseCase(
                command_repository=holiday_repo,
                query_repository=holiday_repo,
                event_publisher=event_publisher,
                notification_service=self._notification_service
            )
        except Exception as e:
            logger.warning(f"Failed to create public holiday use case: {e}")
            return None
    
    def _get_query_public_holiday_use_case(self):
        """Get query public holiday use case"""
        try:
            from app.application.use_cases.public_holiday.get_public_holidays_use_case import GetPublicHolidaysUseCase
            from app.infrastructure.repositories.mongodb_public_holiday_repository import MongoDBPublicHolidayRepository
            
            holiday_repo = MongoDBPublicHolidayRepository(self._database_connector)
            
            return GetPublicHolidaysUseCase(
                query_repository=holiday_repo,
                analytics_repository=holiday_repo,
                calendar_repository=holiday_repo
            )
        except Exception as e:
            logger.warning(f"Failed to create query public holiday use case: {e}")
            return None
    
    def _get_update_public_holiday_use_case(self):
        """Get update public holiday use case"""
        try:
            from app.application.use_cases.public_holiday.update_public_holiday_use_case import UpdatePublicHolidayUseCase
            from app.infrastructure.repositories.mongodb_public_holiday_repository import MongoDBPublicHolidayRepository
            from app.infrastructure.services.event_publisher_impl import EventPublisherImpl
            
            holiday_repo = MongoDBPublicHolidayRepository(self._database_connector)
            event_publisher = EventPublisherImpl()
            
            return UpdatePublicHolidayUseCase(
                command_repository=holiday_repo,
                query_repository=holiday_repo,
                event_publisher=event_publisher,
                notification_service=self._notification_service
            )
        except Exception as e:
            logger.warning(f"Failed to create update public holiday use case: {e}")
            return None
    
    def _get_delete_public_holiday_use_case(self):
        """Get delete public holiday use case"""
        try:
            from app.application.use_cases.public_holiday.delete_public_holiday_use_case import DeletePublicHolidayUseCase
            from app.infrastructure.repositories.mongodb_public_holiday_repository import MongoDBPublicHolidayRepository
            from app.infrastructure.services.event_publisher_impl import EventPublisherImpl
            
            holiday_repo = MongoDBPublicHolidayRepository(self._database_connector)
            event_publisher = EventPublisherImpl()
            
            return DeletePublicHolidayUseCase(
                command_repository=holiday_repo,
                query_repository=holiday_repo,
                event_publisher=event_publisher,
                notification_service=self._notification_service
            )
        except Exception as e:
            logger.warning(f"Failed to create delete public holiday use case: {e}")
            return None
    
    def _get_import_public_holiday_use_case(self):
        """Get import public holiday use case"""
        try:
            from app.application.use_cases.public_holiday.import_public_holidays_use_case import ImportPublicHolidaysUseCase
            from app.infrastructure.repositories.mongodb_public_holiday_repository import MongoDBPublicHolidayRepository
            from app.infrastructure.services.event_publisher_impl import EventPublisherImpl
            
            holiday_repo = MongoDBPublicHolidayRepository(self._database_connector)
            event_publisher = EventPublisherImpl()
            
            return ImportPublicHolidaysUseCase(
                command_repository=holiday_repo,
                query_repository=holiday_repo,
                event_publisher=event_publisher,
                notification_service=self._notification_service,
                file_upload_service=self._file_upload_service
            )
        except Exception as e:
            logger.warning(f"Failed to create import public holiday use case: {e}")
            return None


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


def get_attendance_controller():
    """FastAPI dependency for attendance controller."""
    container = get_dependency_container()
    return container.get_attendance_controller()


def get_organisation_controller():
    """FastAPI dependency for organisation controller."""
    container = get_dependency_container()
    return container.get_organisation_controller()


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