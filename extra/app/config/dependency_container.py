"""
Dependency Injection Container
IoC container for managing application dependencies
"""

import logging
from typing import Dict, Any

from app.infrastructure.database.database_connector import database_connector

# Repository implementations
from app.infrastructure.repositories.mongodb_user_repository import MongoDBUserRepository
from app.infrastructure.repositories.mongodb_taxation_repository import MongoDBTaxationRepository

# Service implementations
from app.infrastructure.services.user_service_impl import UserServiceImpl
from app.domain.services.tax_calculation_service import TaxCalculationService, RegimeComparisonService
# EnhancedTaxCalculationService functionality merged into TaxCalculationService

# Command handlers
from app.application.commands.taxation_commands import (
    CreateTaxationRecordCommandHandler,
    UpdateSalaryIncomeCommandHandler,
    UpdateDeductionsCommandHandler,
    ChangeRegimeCommandHandler,
    CalculateTaxCommandHandler,
    FinalizeRecordCommandHandler,
    ReopenRecordCommandHandler,
    DeleteTaxationRecordCommandHandler,
    EnhancedTaxCalculationCommand,
    MidYearJoinerCommand,
    MidYearIncrementCommand,
    ScenarioComparisonCommand
)

# Controllers
from app.api.controllers.user_controller import UserController
from app.api.controllers.taxation_controller import UnifiedTaxationController

logger = logging.getLogger(__name__)


class DependencyContainer:
    """
    Dependency injection container following SOLID principles.
    
    Manages the creation and lifecycle of application dependencies
    using the Singleton pattern for shared instances.
    """
    
    def __init__(self):
        """Initialize dependency container."""
        self._repositories: Dict[str, Any] = {}
        self._services: Dict[str, Any] = {}
        self._controllers: Dict[str, Any] = {}
        self._handlers: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
    
    # Database dependencies
    def get_database_connector(self):
        """Get database connector instance."""
        return database_connector
    
    # Repository dependencies
    def get_user_repository(self) -> MongoDBUserRepository:
        """Get user repository instance."""
        if 'user' not in self._repositories:
            self._repositories['user'] = MongoDBUserRepository(
                self.get_database_connector()
            )
            logger.info("Created user repository instance")
        return self._repositories['user']
    
    def get_taxation_repository(self) -> MongoDBTaxationRepository:
        """Get taxation repository instance."""
        if 'taxation' not in self._repositories:
            self._repositories['taxation'] = MongoDBTaxationRepository(
                self.get_database_connector()
            )
            logger.info("Created taxation repository instance")
        return self._repositories['taxation']
    
    # Service dependencies
    def get_user_service(self) -> UserServiceImpl:
        """Get user service instance."""
        if 'user' not in self._services:
            self._services['user'] = UserServiceImpl(
                self.get_user_repository()
            )
            logger.info("Created user service instance")
        return self._services['user']
    
    def get_tax_calculation_service(self) -> TaxCalculationService:
        """Get tax calculation service instance."""
        if 'tax_calculation' not in self._services:
            self._services['tax_calculation'] = TaxCalculationService()
            logger.info("Created tax calculation service instance")
        return self._services['tax_calculation']
    
    def get_regime_comparison_service(self) -> RegimeComparisonService:
        """Get regime comparison service instance."""
        if 'regime_comparison' not in self._services:
            self._services['regime_comparison'] = RegimeComparisonService(
                self.get_tax_calculation_service()
            )
            logger.info("Created regime comparison service instance")
        return self._services['regime_comparison']
    
    def get_enhanced_tax_calculation_service(self) -> TaxCalculationService:
        """Get enhanced tax calculation service (now merged with TaxCalculationService)."""
        return self.get_tax_calculation_service()
    
    # Command handler dependencies
    def get_create_taxation_handler(self) -> CreateTaxationRecordCommandHandler:
        """Get create taxation record command handler."""
        if 'create_taxation' not in self._handlers:
            self._handlers['create_taxation'] = CreateTaxationRecordCommandHandler(
                self.get_taxation_repository()
            )
            logger.info("Created create taxation command handler instance")
        return self._handlers['create_taxation']
    
    def get_update_salary_handler(self) -> UpdateSalaryIncomeCommandHandler:
        """Get update salary income command handler."""
        if 'update_salary' not in self._handlers:
            self._handlers['update_salary'] = UpdateSalaryIncomeCommandHandler(
                self.get_taxation_repository()
            )
            logger.info("Created update salary command handler instance")
        return self._handlers['update_salary']
    
    def get_update_deductions_handler(self) -> UpdateDeductionsCommandHandler:
        """Get update deductions command handler."""
        if 'update_deductions' not in self._handlers:
            self._handlers['update_deductions'] = UpdateDeductionsCommandHandler(
                self.get_taxation_repository()
            )
            logger.info("Created update deductions command handler instance")
        return self._handlers['update_deductions']
    
    def get_change_regime_handler(self) -> ChangeRegimeCommandHandler:
        """Get change regime command handler."""
        if 'change_regime' not in self._handlers:
            self._handlers['change_regime'] = ChangeRegimeCommandHandler(
                self.get_taxation_repository()
            )
            logger.info("Created change regime command handler instance")
        return self._handlers['change_regime']
    
    def get_calculate_tax_handler(self) -> CalculateTaxCommandHandler:
        """Get calculate tax command handler."""
        if 'calculate_tax' not in self._handlers:
            self._handlers['calculate_tax'] = CalculateTaxCommandHandler(
                self.get_taxation_repository(),
                self.get_tax_calculation_service()
            )
            logger.info("Created calculate tax command handler instance")
        return self._handlers['calculate_tax']
    
    def get_finalize_handler(self) -> FinalizeRecordCommandHandler:
        """Get finalize record command handler."""
        if 'finalize_record' not in self._handlers:
            self._handlers['finalize_record'] = FinalizeRecordCommandHandler(
                self.get_taxation_repository()
            )
            logger.info("Created finalize record command handler instance")
        return self._handlers['finalize_record']
    
    def get_reopen_handler(self) -> ReopenRecordCommandHandler:
        """Get reopen record command handler."""
        if 'reopen_record' not in self._handlers:
            self._handlers['reopen_record'] = ReopenRecordCommandHandler(
                self.get_taxation_repository()
            )
            logger.info("Created reopen record command handler instance")
        return self._handlers['reopen_record']
    
    def get_delete_handler(self) -> DeleteTaxationRecordCommandHandler:
        """Get delete record command handler."""
        if 'delete_record' not in self._handlers:
            self._handlers['delete_record'] = DeleteTaxationRecordCommandHandler(
                self.get_taxation_repository()
            )
            logger.info("Created delete record command handler instance")
        return self._handlers['delete_record']
    
    def get_enhanced_tax_calculation_command(self) -> EnhancedTaxCalculationCommand:
        """Get enhanced tax calculation command handler."""
        if 'enhanced_tax_calculation' not in self._handlers:
            self._handlers['enhanced_tax_calculation'] = EnhancedTaxCalculationCommand(
                self.get_tax_calculation_service()
            )
            logger.info("Created enhanced tax calculation command handler instance")
        return self._handlers['enhanced_tax_calculation']
    
    def get_mid_year_joiner_command(self) -> MidYearJoinerCommand:
        """Get mid-year joiner command handler."""
        if 'mid_year_joiner' not in self._handlers:
            self._handlers['mid_year_joiner'] = MidYearJoinerCommand(
                self.get_tax_calculation_service()
            )
            logger.info("Created mid-year joiner command handler instance")
        return self._handlers['mid_year_joiner']
    
    def get_mid_year_increment_command(self) -> MidYearIncrementCommand:
        """Get mid-year increment command handler."""
        if 'mid_year_increment' not in self._handlers:
            self._handlers['mid_year_increment'] = MidYearIncrementCommand(
                self.get_tax_calculation_service()
            )
            logger.info("Created mid-year increment command handler instance")
        return self._handlers['mid_year_increment']
    
    def get_scenario_comparison_command(self) -> ScenarioComparisonCommand:
        """Get scenario comparison command handler."""
        if 'scenario_comparison' not in self._handlers:
            self._handlers['scenario_comparison'] = ScenarioComparisonCommand(
                self.get_tax_calculation_service()
            )
            logger.info("Created scenario comparison command handler instance")
        return self._handlers['scenario_comparison']
    
    # Controller dependencies
    def get_user_controller(self) -> UserController:
        """Get user controller instance."""
        if 'user' not in self._controllers:
            self._controllers['user'] = UserController(
                self.get_user_service()
            )
            logger.info("Created user controller instance")
        return self._controllers['user']
    
    def get_taxation_controller(self) -> UnifiedTaxationController:
        """Get unified taxation controller instance."""
        if 'taxation' not in self._controllers:
            from app.domain.services.payroll_tax_service import PayrollTaxService
            
            # Create payroll tax service
            payroll_tax_service = PayrollTaxService()
            
            self._controllers['taxation'] = UnifiedTaxationController(
                # Command handlers for basic operations
                create_handler=self.get_create_taxation_handler(),
                update_salary_handler=self.get_update_salary_handler(),
                update_deductions_handler=self.get_update_deductions_handler(),
                change_regime_handler=self.get_change_regime_handler(),
                calculate_tax_handler=self.get_calculate_tax_handler(),
                finalize_handler=self.get_finalize_handler(),
                reopen_handler=self.get_reopen_handler(),
                delete_handler=self.get_delete_handler(),
                
                # Services for comprehensive calculations
                enhanced_tax_service=self.get_tax_calculation_service(),
                payroll_tax_service=payroll_tax_service
            )
            logger.info("Created unified taxation controller instance")
        return self._controllers['taxation']
    
    def get_unified_taxation_controller(self) -> UnifiedTaxationController:
        """Get unified taxation controller instance (same as get_taxation_controller)."""
        return self.get_taxation_controller()
    
    def get_enhanced_taxation_controller(self) -> UnifiedTaxationController:
        """Get enhanced taxation controller (now unified controller)."""
        return self.get_taxation_controller()
    
    def get_comprehensive_taxation_controller(self) -> UnifiedTaxationController:
        """Get comprehensive taxation controller (now unified controller)."""
        return self.get_taxation_controller()
    
    # Utility methods
    def clear_cache(self) -> None:
        """Clear all cached instances (useful for testing)."""
        self._repositories.clear()
        self._services.clear()
        self._controllers.clear()
        self._handlers.clear()
        self._singletons.clear()
        logger.info("Cleared dependency container cache")
    
    def get_singleton(self, key: str, factory_func) -> Any:
        """Get or create singleton instance."""
        if key not in self._singletons:
            self._singletons[key] = factory_func()
            logger.info(f"Created singleton instance: {key}")
        return self._singletons[key]


# Global dependency container instance
_container = DependencyContainer()


def get_dependency_container() -> DependencyContainer:
    """Get the global dependency container instance."""
    return _container


# FastAPI dependency functions
def get_user_repository() -> MongoDBUserRepository:
    """FastAPI dependency for user repository."""
    return _container.get_user_repository()


def get_user_service() -> UserServiceImpl:
    """FastAPI dependency for user service."""
    return _container.get_user_service()


def get_user_controller() -> UserController:
    """FastAPI dependency for user controller."""
    return _container.get_user_controller()


def get_taxation_controller() -> UnifiedTaxationController:
    """FastAPI dependency for unified taxation controller."""
    return _container.get_taxation_controller()


def get_taxation_repository() -> MongoDBTaxationRepository:
    """FastAPI dependency for taxation repository."""
    return _container.get_taxation_repository()


def get_tax_calculation_service() -> TaxCalculationService:
    """FastAPI dependency for tax calculation service."""
    return _container.get_tax_calculation_service()


def get_unified_taxation_controller() -> UnifiedTaxationController:
    """FastAPI dependency for unified taxation controller."""
    return _container.get_unified_taxation_controller()


def get_enhanced_taxation_controller() -> UnifiedTaxationController:
    """FastAPI dependency for enhanced taxation controller (now unified)."""
    return _container.get_enhanced_taxation_controller()


def get_comprehensive_taxation_controller() -> UnifiedTaxationController:
    """FastAPI dependency for comprehensive taxation controller (now unified)."""
    return _container.get_comprehensive_taxation_controller()


# Health check function
async def health_check_dependencies() -> Dict[str, str]:
    """Check health of all dependencies."""
    health_status = {}
    
    try:
        # Check database connection
        db_connector = _container.get_database_connector()
        db_healthy = await db_connector.health_check()
        health_status['database'] = 'healthy' if db_healthy else 'unhealthy'
        
        # Check repository initialization
        try:
            _container.get_user_repository()
            health_status['user_repository'] = 'healthy'
        except Exception as e:
            health_status['user_repository'] = f'unhealthy: {str(e)}'
        
        try:
            _container.get_taxation_repository()
            health_status['taxation_repository'] = 'healthy'
        except Exception as e:
            health_status['taxation_repository'] = f'unhealthy: {str(e)}'
        
        # Check service initialization
        try:
            _container.get_user_service()
            health_status['user_service'] = 'healthy'
        except Exception as e:
            health_status['user_service'] = f'unhealthy: {str(e)}'
        
        try:
            _container.get_tax_calculation_service()
            health_status['tax_calculation_service'] = 'healthy'
        except Exception as e:
            health_status['tax_calculation_service'] = f'unhealthy: {str(e)}'
        
        # Check controller initialization
        try:
            _container.get_user_controller()
            health_status['user_controller'] = 'healthy'
        except Exception as e:
            health_status['user_controller'] = f'unhealthy: {str(e)}'
        
        try:
            _container.get_taxation_controller()
            health_status['taxation_controller'] = 'healthy'
        except Exception as e:
            health_status['taxation_controller'] = f'unhealthy: {str(e)}'
            
    except Exception as e:
        logger.error(f"Error during health check: {e}")
        health_status['error'] = str(e)
    
    return health_status 