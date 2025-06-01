"""
Public Holiday Domain Events
Events for public holiday lifecycle and business operations
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass

from app.domain.events.employee_events import DomainEvent
from app.domain.value_objects.holiday_type import HolidayType
from app.domain.value_objects.holiday_date_range import HolidayDateRange


@dataclass
class PublicHolidayCreated(DomainEvent):
    """Event raised when a public holiday is created"""
    
    holiday_id: str
    holiday_type: HolidayType
    date_range: HolidayDateRange
    created_by: str
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "PublicHolidayCreated"
    
    def get_aggregate_id(self) -> str:
        return self.holiday_id
    
    def get_event_description(self) -> str:
        return f"Public holiday '{self.holiday_type.name}' created for {self.date_range.get_formatted_date_range()}"


@dataclass
class PublicHolidayUpdated(DomainEvent):
    """Event raised when a public holiday is updated"""
    
    holiday_id: str
    old_holiday_type: HolidayType
    new_holiday_type: HolidayType
    updated_by: Optional[str]
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "PublicHolidayUpdated"
    
    def get_aggregate_id(self) -> str:
        return self.holiday_id
    
    def get_event_description(self) -> str:
        return f"Public holiday updated from '{self.old_holiday_type.name}' to '{self.new_holiday_type.name}'"


@dataclass
class PublicHolidayDateChanged(DomainEvent):
    """Event raised when a public holiday date is changed"""
    
    holiday_id: str
    old_date_range: HolidayDateRange
    new_date_range: HolidayDateRange
    reason: Optional[str]
    updated_by: Optional[str]
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "PublicHolidayDateChanged"
    
    def get_aggregate_id(self) -> str:
        return self.holiday_id
    
    def get_event_description(self) -> str:
        reason_text = f" (Reason: {self.reason})" if self.reason else ""
        return f"Holiday date changed from {self.old_date_range.get_formatted_date_range()} to {self.new_date_range.get_formatted_date_range()}{reason_text}"


@dataclass
class PublicHolidayActivated(DomainEvent):
    """Event raised when a public holiday is activated"""
    
    holiday_id: str
    holiday_type: HolidayType
    date_range: HolidayDateRange
    activated_by: Optional[str]
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "PublicHolidayActivated"
    
    def get_aggregate_id(self) -> str:
        return self.holiday_id
    
    def get_event_description(self) -> str:
        return f"Public holiday '{self.holiday_type.name}' activated for {self.date_range.get_formatted_date_range()}"


@dataclass
class PublicHolidayDeactivated(DomainEvent):
    """Event raised when a public holiday is deactivated"""
    
    holiday_id: str
    holiday_type: HolidayType
    date_range: HolidayDateRange
    reason: Optional[str]
    deactivated_by: Optional[str]
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "PublicHolidayDeactivated"
    
    def get_aggregate_id(self) -> str:
        return self.holiday_id
    
    def get_event_description(self) -> str:
        reason_text = f" (Reason: {self.reason})" if self.reason else ""
        return f"Public holiday '{self.holiday_type.name}' deactivated{reason_text}"


@dataclass
class PublicHolidayConflictDetected(DomainEvent):
    """Event raised when a holiday conflict is detected"""
    
    holiday_id: str
    conflicting_holiday_id: str
    holiday_type: HolidayType
    conflicting_holiday_type: HolidayType
    date_range: HolidayDateRange
    detected_by: Optional[str]
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "PublicHolidayConflictDetected"
    
    def get_aggregate_id(self) -> str:
        return self.holiday_id
    
    def get_event_description(self) -> str:
        return f"Holiday conflict detected between '{self.holiday_type.name}' and '{self.conflicting_holiday_type.name}' on {self.date_range.get_formatted_date_range()}"


@dataclass
class PublicHolidayImported(DomainEvent):
    """Event raised when holidays are imported in bulk"""
    
    import_batch_id: str
    holidays_count: int
    successful_imports: int
    failed_imports: int
    imported_by: str
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "PublicHolidayImported"
    
    def get_aggregate_id(self) -> str:
        return self.import_batch_id
    
    def get_event_description(self) -> str:
        return f"Bulk import completed: {self.successful_imports}/{self.holidays_count} holidays imported successfully"


@dataclass
class PublicHolidayCalendarGenerated(DomainEvent):
    """Event raised when a holiday calendar is generated"""
    
    calendar_id: str
    year: int
    month: Optional[int]
    holidays_count: int
    generated_by: Optional[str]
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "PublicHolidayCalendarGenerated"
    
    def get_aggregate_id(self) -> str:
        return self.calendar_id
    
    def get_event_description(self) -> str:
        period = f"{self.year}" if not self.month else f"{self.month}/{self.year}"
        return f"Holiday calendar generated for {period} with {self.holidays_count} holidays"


@dataclass
class PublicHolidayNotificationSent(DomainEvent):
    """Event raised when holiday notifications are sent"""
    
    notification_id: str
    holiday_id: str
    holiday_type: HolidayType
    date_range: HolidayDateRange
    notification_type: str  # "upcoming", "reminder", "change"
    recipients_count: int
    sent_by: Optional[str]
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "PublicHolidayNotificationSent"
    
    def get_aggregate_id(self) -> str:
        return self.holiday_id
    
    def get_event_description(self) -> str:
        return f"{self.notification_type.title()} notification sent for '{self.holiday_type.name}' to {self.recipients_count} recipients"


@dataclass
class PublicHolidayComplianceAlert(DomainEvent):
    """Event raised for holiday compliance issues"""
    
    alert_id: str
    holiday_id: str
    holiday_type: HolidayType
    compliance_issue: str
    severity: str  # "low", "medium", "high", "critical"
    detected_by: Optional[str]
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "PublicHolidayComplianceAlert"
    
    def get_aggregate_id(self) -> str:
        return self.holiday_id
    
    def get_event_description(self) -> str:
        return f"{self.severity.upper()} compliance alert for '{self.holiday_type.name}': {self.compliance_issue}"


# Event registry for type lookup
HOLIDAY_EVENT_TYPES = {
    "PublicHolidayCreated": PublicHolidayCreated,
    "PublicHolidayUpdated": PublicHolidayUpdated,
    "PublicHolidayDateChanged": PublicHolidayDateChanged,
    "PublicHolidayActivated": PublicHolidayActivated,
    "PublicHolidayDeactivated": PublicHolidayDeactivated,
    "PublicHolidayConflictDetected": PublicHolidayConflictDetected,
    "PublicHolidayImported": PublicHolidayImported,
    "PublicHolidayCalendarGenerated": PublicHolidayCalendarGenerated,
    "PublicHolidayNotificationSent": PublicHolidayNotificationSent,
    "PublicHolidayComplianceAlert": PublicHolidayComplianceAlert
}


def get_holiday_event_class(event_type: str):
    """Get event class by type name"""
    return HOLIDAY_EVENT_TYPES.get(event_type)


def get_all_holiday_event_types() -> list:
    """Get all holiday event type names"""
    return list(HOLIDAY_EVENT_TYPES.keys()) 