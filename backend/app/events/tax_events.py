"""
Tax Event System - Event-Driven Architecture Components
Handles all tax-related events and their processing
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Callable, Protocol
from enum import Enum
import uuid
import json
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class TaxEventType(Enum):
    SALARY_CHANGED = "salary_changed"
    EMPLOYEE_JOINED = "employee_joined"
    EMPLOYEE_LEFT = "employee_left"
    TAX_REGIME_CHANGED = "tax_regime_changed"
    INVESTMENT_DECLARATION_CHANGED = "investment_declaration_changed"
    PAYOUT_PROCESSED = "payout_processed"
    LWP_APPLIED = "lwp_applied"
    BONUS_PAID = "bonus_paid"
    ARREARS_PAID = "arrears_paid"
    DEDUCTION_CHANGED = "deduction_changed"
    PERQUISITE_ADDED = "perquisite_added"
    TAX_CALCULATED = "tax_calculated"
    COMPLIANCE_DEADLINE = "compliance_deadline"
    AUDIT_INITIATED = "audit_initiated"


class TaxEventPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaxEventStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


@dataclass
class TaxEvent:
    """
    Base tax event model
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: TaxEventType = TaxEventType.TAX_CALCULATED
    employee_id: str = ""
    event_date: datetime = field(default_factory=datetime.now)
    impact_on_tax: float = 0.0
    requires_recalculation: bool = True
    priority: TaxEventPriority = TaxEventPriority.MEDIUM
    status: TaxEventStatus = TaxEventStatus.PENDING
    processed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "employee_id": self.employee_id,
            "event_date": self.event_date.isoformat(),
            "impact_on_tax": self.impact_on_tax,
            "requires_recalculation": self.requires_recalculation,
            "priority": self.priority.value,
            "status": self.status.value,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "error_message": self.error_message,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaxEvent':
        """Create from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            event_type=TaxEventType(data.get("event_type", "tax_calculated")),
            employee_id=data.get("employee_id", ""),
            event_date=datetime.fromisoformat(data.get("event_date", datetime.now().isoformat())),
            impact_on_tax=data.get("impact_on_tax", 0.0),
            requires_recalculation=data.get("requires_recalculation", True),
            priority=TaxEventPriority(data.get("priority", "medium")),
            status=TaxEventStatus(data.get("status", "pending")),
            processed_at=datetime.fromisoformat(data["processed_at"]) if data.get("processed_at") else None,
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            error_message=data.get("error_message"),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )


@dataclass
class SalaryChangeEvent(TaxEvent):
    """Salary change specific event"""
    event_type: TaxEventType = TaxEventType.SALARY_CHANGED
    old_annual_salary: float = 0.0
    new_annual_salary: float = 0.0
    effective_date: date = field(default_factory=date.today)
    change_reason: str = ""
    is_retroactive: bool = False
    
    def __post_init__(self):
        self.impact_on_tax = abs(self.new_annual_salary - self.old_annual_salary) * 0.3  # Rough estimate
        self.requires_recalculation = True
        self.priority = TaxEventPriority.HIGH
        self.metadata.update({
            "old_annual_salary": self.old_annual_salary,
            "new_annual_salary": self.new_annual_salary,
            "effective_date": self.effective_date.isoformat(),
            "change_reason": self.change_reason,
            "is_retroactive": self.is_retroactive
        })


@dataclass
class EmployeeJoinedEvent(TaxEvent):
    """New employee joined event"""
    event_type: TaxEventType = TaxEventType.EMPLOYEE_JOINED
    join_date: date = field(default_factory=date.today)
    annual_salary: float = 0.0
    previous_employment_tds: float = 0.0
    
    def __post_init__(self):
        self.requires_recalculation = True
        self.priority = TaxEventPriority.MEDIUM
        self.metadata.update({
            "join_date": self.join_date.isoformat(),
            "annual_salary": self.annual_salary,
            "previous_employment_tds": self.previous_employment_tds
        })


@dataclass
class EmployeeLeftEvent(TaxEvent):
    """Employee left event"""
    event_type: TaxEventType = TaxEventType.EMPLOYEE_LEFT
    exit_date: date = field(default_factory=date.today)
    exit_type: str = "resignation"  # resignation, termination, retirement
    final_settlement_amount: float = 0.0
    
    def __post_init__(self):
        self.requires_recalculation = True
        self.priority = TaxEventPriority.HIGH
        self.metadata.update({
            "exit_date": self.exit_date.isoformat(),
            "exit_type": self.exit_type,
            "final_settlement_amount": self.final_settlement_amount
        })


@dataclass
class TaxRegimeChangeEvent(TaxEvent):
    """Tax regime change event"""
    event_type: TaxEventType = TaxEventType.TAX_REGIME_CHANGED
    old_regime: str = "old"
    new_regime: str = "new"
    
    def __post_init__(self):
        self.requires_recalculation = True
        self.priority = TaxEventPriority.CRITICAL
        self.metadata.update({
            "old_regime": self.old_regime,
            "new_regime": self.new_regime
        })


# Event Handler Protocol
class EventHandler(Protocol):
    """Protocol for event handlers"""
    
    def can_handle(self, event: TaxEvent) -> bool:
        """Check if this handler can process the event"""
        ...
    
    def handle(self, event: TaxEvent) -> bool:
        """Handle the event, return True if successful"""
        ...
    
    def get_priority(self) -> int:
        """Get handler priority (lower number = higher priority)"""
        ...


class BaseEventHandler(ABC):
    """Base class for event handlers"""
    
    def __init__(self, name: str, priority: int = 100):
        self.name = name
        self.priority = priority
        self.logger = logging.getLogger(f"EventHandler.{name}")
    
    @abstractmethod
    def can_handle(self, event: TaxEvent) -> bool:
        """Check if this handler can process the event"""
        pass
    
    @abstractmethod
    def handle(self, event: TaxEvent) -> bool:
        """Handle the event, return True if successful"""
        pass
    
    def get_priority(self) -> int:
        """Get handler priority"""
        return self.priority


class SalaryChangeEventHandler(BaseEventHandler):
    """Handler for salary change events"""
    
    def __init__(self, salary_service, tax_engine, payout_service):
        super().__init__("SalaryChangeHandler", priority=10)
        self.salary_service = salary_service
        self.tax_engine = tax_engine
        self.payout_service = payout_service
    
    def can_handle(self, event: TaxEvent) -> bool:
        return event.event_type == TaxEventType.SALARY_CHANGED
    
    def handle(self, event: TaxEvent) -> bool:
        try:
            self.logger.info(f"Processing salary change event for employee {event.employee_id}")
            
            # 1. Recalculate annual salary projection
            projection = self.salary_service.calculate_annual_projection(
                event.employee_id, 
                self._get_current_tax_year()
            )
            
            # 2. Recalculate tax liability
            new_tax = self.tax_engine.calculate_tax(event.employee_id)
            
            # 3. Calculate catch-up tax for remaining months
            catch_up_tax = self.tax_engine.calculate_catch_up_tax(
                event.employee_id, 
                event.metadata.get("effective_date")
            )
            
            # 4. Update future payouts with new TDS
            self.payout_service.update_future_payouts_tds(
                event.employee_id,
                catch_up_tax.new_monthly_tds
            )
            
            # 5. Send notifications
            self._send_salary_change_notifications(event, catch_up_tax)
            
            self.logger.info(f"Successfully processed salary change event for {event.employee_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing salary change event: {str(e)}")
            return False
    
    def _get_current_tax_year(self) -> str:
        """Get current tax year"""
        now = datetime.now()
        if now.month >= 4:
            return f"{now.year}-{now.year + 1}"
        else:
            return f"{now.year - 1}-{now.year}"
    
    def _send_salary_change_notifications(self, event: TaxEvent, catch_up_tax) -> None:
        """Send notifications about salary change"""
        # Implementation for sending notifications
        pass


class TaxRegimeChangeEventHandler(BaseEventHandler):
    """Handler for tax regime change events"""
    
    def __init__(self, tax_engine, payout_service):
        super().__init__("TaxRegimeChangeHandler", priority=5)
        self.tax_engine = tax_engine
        self.payout_service = payout_service
    
    def can_handle(self, event: TaxEvent) -> bool:
        return event.event_type == TaxEventType.TAX_REGIME_CHANGED
    
    def handle(self, event: TaxEvent) -> bool:
        try:
            self.logger.info(f"Processing tax regime change for employee {event.employee_id}")
            
            # 1. Recalculate entire tax liability from April
            new_tax = self.tax_engine.recalculate_from_april(
                event.employee_id,
                event.metadata.get("new_regime")
            )
            
            # 2. Adjust all future payouts
            self.payout_service.recalculate_all_future_payouts(event.employee_id)
            
            # 3. Generate compliance reports
            self._generate_regime_change_reports(event)
            
            self.logger.info(f"Successfully processed regime change for {event.employee_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing regime change: {str(e)}")
            return False
    
    def _generate_regime_change_reports(self, event: TaxEvent) -> None:
        """Generate reports for regime change"""
        # Implementation for generating reports
        pass


class NewJoinerEventHandler(BaseEventHandler):
    """Handler for new joiner events"""
    
    def __init__(self, employee_lifecycle_service, tax_engine):
        super().__init__("NewJoinerHandler", priority=20)
        self.employee_lifecycle_service = employee_lifecycle_service
        self.tax_engine = tax_engine
    
    def can_handle(self, event: TaxEvent) -> bool:
        return event.event_type == TaxEventType.EMPLOYEE_JOINED
    
    def handle(self, event: TaxEvent) -> bool:
        try:
            self.logger.info(f"Processing new joiner event for employee {event.employee_id}")
            
            # Process new joiner with previous employment consideration
            result = self.employee_lifecycle_service.handle_new_joiner(
                event.employee_id,
                event.metadata.get("join_date"),
                event.metadata.get("previous_employment")
            )
            
            self.logger.info(f"Successfully processed new joiner {event.employee_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing new joiner: {str(e)}")
            return False


class EventStore:
    """Event store for persisting events"""
    
    def __init__(self, database_connection):
        self.db = database_connection
        self.logger = logging.getLogger("EventStore")
    
    def save(self, event: TaxEvent) -> bool:
        """Save event to database"""
        try:
            # Implementation depends on your database
            # This is a placeholder
            self.logger.info(f"Saving event {event.id} of type {event.event_type.value}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving event: {str(e)}")
            return False
    
    def get_events_by_employee(self, employee_id: str, 
                              event_types: Optional[List[TaxEventType]] = None) -> List[TaxEvent]:
        """Get events for an employee"""
        # Implementation placeholder
        return []
    
    def get_pending_events(self) -> List[TaxEvent]:
        """Get all pending events"""
        # Implementation placeholder
        return []
    
    def update_event_status(self, event_id: str, status: TaxEventStatus, 
                           error_message: Optional[str] = None) -> bool:
        """Update event status"""
        try:
            # Implementation placeholder
            self.logger.info(f"Updating event {event_id} status to {status.value}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating event status: {str(e)}")
            return False


class TaxEventPublisher:
    """Event publisher for tax events"""
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self.handlers: Dict[TaxEventType, List[EventHandler]] = {}
        self.logger = logging.getLogger("TaxEventPublisher")
    
    def publish(self, event: TaxEvent) -> bool:
        """Publish an event"""
        try:
            # 1. Save event to store
            if not self.event_store.save(event):
                self.logger.error(f"Failed to save event {event.id}")
                return False
            
            # 2. Process event with handlers
            return self._process_event(event)
            
        except Exception as e:
            self.logger.error(f"Error publishing event: {str(e)}")
            return False
    
    def subscribe(self, event_type: TaxEventType, handler: EventHandler) -> None:
        """Subscribe a handler to an event type"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        
        self.handlers[event_type].append(handler)
        # Sort by priority
        self.handlers[event_type].sort(key=lambda h: h.get_priority())
        
        self.logger.info(f"Subscribed {handler.__class__.__name__} to {event_type.value}")
    
    def _process_event(self, event: TaxEvent) -> bool:
        """Process event with registered handlers"""
        handlers = self.handlers.get(event.event_type, [])
        
        if not handlers:
            self.logger.warning(f"No handlers registered for event type {event.event_type.value}")
            return True
        
        success = True
        for handler in handlers:
            try:
                if handler.can_handle(event):
                    self.logger.info(f"Processing event {event.id} with {handler.__class__.__name__}")
                    
                    # Update event status
                    event.status = TaxEventStatus.PROCESSING
                    self.event_store.update_event_status(event.id, TaxEventStatus.PROCESSING)
                    
                    # Handle event
                    if handler.handle(event):
                        self.logger.info(f"Successfully processed event {event.id}")
                    else:
                        self.logger.error(f"Handler failed to process event {event.id}")
                        success = False
                        
            except Exception as e:
                self.logger.error(f"Error in handler {handler.__class__.__name__}: {str(e)}")
                success = False
        
        # Update final status
        final_status = TaxEventStatus.COMPLETED if success else TaxEventStatus.FAILED
        event.status = final_status
        event.processed_at = datetime.now()
        self.event_store.update_event_status(event.id, final_status)
        
        return success
    
    def process_pending_events(self) -> Dict[str, int]:
        """Process all pending events"""
        pending_events = self.event_store.get_pending_events()
        
        results = {
            "total": len(pending_events),
            "successful": 0,
            "failed": 0
        }
        
        for event in pending_events:
            if self._process_event(event):
                results["successful"] += 1
            else:
                results["failed"] += 1
        
        return results


class EventFactory:
    """Factory for creating tax events"""
    
    @staticmethod
    def create_salary_change_event(employee_id: str, old_salary: float, 
                                 new_salary: float, effective_date: date,
                                 change_reason: str = "", is_retroactive: bool = False) -> SalaryChangeEvent:
        """Create salary change event"""
        return SalaryChangeEvent(
            employee_id=employee_id,
            old_annual_salary=old_salary,
            new_annual_salary=new_salary,
            effective_date=effective_date,
            change_reason=change_reason,
            is_retroactive=is_retroactive
        )
    
    @staticmethod
    def create_employee_joined_event(employee_id: str, join_date: date,
                                   annual_salary: float, previous_tds: float = 0.0) -> EmployeeJoinedEvent:
        """Create employee joined event"""
        return EmployeeJoinedEvent(
            employee_id=employee_id,
            join_date=join_date,
            annual_salary=annual_salary,
            previous_employment_tds=previous_tds
        )
    
    @staticmethod
    def create_employee_left_event(employee_id: str, exit_date: date,
                                 exit_type: str, final_settlement: float = 0.0) -> EmployeeLeftEvent:
        """Create employee left event"""
        return EmployeeLeftEvent(
            employee_id=employee_id,
            exit_date=exit_date,
            exit_type=exit_type,
            final_settlement_amount=final_settlement
        )
    
    @staticmethod
    def create_regime_change_event(employee_id: str, old_regime: str, 
                                 new_regime: str) -> TaxRegimeChangeEvent:
        """Create tax regime change event"""
        return TaxRegimeChangeEvent(
            employee_id=employee_id,
            old_regime=old_regime,
            new_regime=new_regime
        )


# Event Processing Service
class TaxEventProcessor:
    """Service for processing tax events"""
    
    def __init__(self, event_publisher: TaxEventPublisher, 
                 salary_service, tax_engine, payout_service, employee_lifecycle_service):
        self.event_publisher = event_publisher
        self.logger = logging.getLogger("TaxEventProcessor")
        
        # Register handlers
        self._register_handlers(salary_service, tax_engine, payout_service, employee_lifecycle_service)
    
    def _register_handlers(self, salary_service, tax_engine, payout_service, employee_lifecycle_service):
        """Register all event handlers"""
        
        # Salary change handler
        salary_handler = SalaryChangeEventHandler(salary_service, tax_engine, payout_service)
        self.event_publisher.subscribe(TaxEventType.SALARY_CHANGED, salary_handler)
        
        # Tax regime change handler
        regime_handler = TaxRegimeChangeEventHandler(tax_engine, payout_service)
        self.event_publisher.subscribe(TaxEventType.TAX_REGIME_CHANGED, regime_handler)
        
        # New joiner handler
        joiner_handler = NewJoinerEventHandler(employee_lifecycle_service, tax_engine)
        self.event_publisher.subscribe(TaxEventType.EMPLOYEE_JOINED, joiner_handler)
        
        self.logger.info("All event handlers registered successfully")
    
    def process_salary_change(self, employee_id: str, old_salary: float, 
                            new_salary: float, effective_date: date, 
                            change_reason: str = "") -> bool:
        """Process salary change event"""
        event = EventFactory.create_salary_change_event(
            employee_id, old_salary, new_salary, effective_date, change_reason
        )
        return self.event_publisher.publish(event)
    
    def process_new_joiner(self, employee_id: str, join_date: date,
                         annual_salary: float, previous_tds: float = 0.0) -> bool:
        """Process new joiner event"""
        event = EventFactory.create_employee_joined_event(
            employee_id, join_date, annual_salary, previous_tds
        )
        return self.event_publisher.publish(event)
    
    def process_regime_change(self, employee_id: str, old_regime: str, new_regime: str) -> bool:
        """Process tax regime change event"""
        event = EventFactory.create_regime_change_event(employee_id, old_regime, new_regime)
        return self.event_publisher.publish(event) 