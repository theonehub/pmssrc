"""
Attendance Event Handlers
Concrete implementations of event handlers for attendance domain events
"""

import logging
from typing import List, Optional
from datetime import datetime

from app.application.interfaces.services.event_handler import BaseEventHandler
from app.application.interfaces.services.notification_service import NotificationService
from app.domain.events.base_event import DomainEvent
from app.domain.events.attendance_events import (
    AttendanceCheckedInEvent,
    AttendanceCheckedOutEvent,
    AttendanceLateArrivalEvent,
    AttendanceOvertimeEvent,
    AttendanceAbsentEvent,
    AttendanceRegularizedEvent,
    BreakStartedEvent,
    BreakEndedEvent
)

logger = logging.getLogger(__name__)


class AttendanceNotificationHandler(BaseEventHandler):
    """
    Handler for sending notifications based on attendance events.
    
    Sends notifications for:
    - Late arrivals
    - Overtime work
    - Absences
    - Check-in/check-out confirmations
    """
    
    def __init__(self, notification_service: NotificationService, priority: int = 50):
        """
        Initialize attendance notification handler.
        
        Args:
            notification_service: Service for sending notifications
            priority: Handler priority (lower = higher priority)
        """
        super().__init__(
            supported_event_types=[
                "AttendanceCheckedIn",
                "AttendanceCheckedOut", 
                "AttendanceLateArrival",
                "AttendanceOvertime",
                "AttendanceAbsent",
                "AttendanceRegularized"
            ],
            priority=priority
        )
        self.notification_service = notification_service
    
    async def handle(self, event: DomainEvent) -> None:
        """Handle attendance event and send appropriate notifications"""
        try:
            if isinstance(event, AttendanceCheckedInEvent):
                await self._handle_check_in(event)
            elif isinstance(event, AttendanceCheckedOutEvent):
                await self._handle_check_out(event)
            elif isinstance(event, AttendanceLateArrivalEvent):
                await self._handle_late_arrival(event)
            elif isinstance(event, AttendanceOvertimeEvent):
                await self._handle_overtime(event)
            elif isinstance(event, AttendanceAbsentEvent):
                await self._handle_absence(event)
            elif isinstance(event, AttendanceRegularizedEvent):
                await self._handle_regularization(event)
            else:
                logger.warning(f"Unhandled event type: {event.get_event_type()}")
                
        except Exception as e:
            logger.error(f"Error handling attendance event {event.get_event_type()}: {e}")
            # Don't re-raise to avoid breaking other handlers
    
    async def _handle_check_in(self, event: AttendanceCheckedInEvent) -> None:
        """Handle check-in event notification"""
        try:
            message = f"Check-in recorded at {event.check_in_time.strftime('%H:%M')}"
            if event.location:
                message += f" from {event.location}"
            
            await self.notification_service.send_notification(
                recipient_id=event.employee_id,
                message=message,
                notification_type="attendance_checkin",
                metadata={
                    "attendance_id": event.attendance_id,
                    "check_in_time": event.check_in_time.isoformat(),
                    "location": event.location
                }
            )
            
            logger.info(f"Check-in notification sent for employee {event.employee_id}")
            
        except Exception as e:
            logger.error(f"Error sending check-in notification: {e}")
    
    async def _handle_check_out(self, event: AttendanceCheckedOutEvent) -> None:
        """Handle check-out event notification"""
        try:
            message = f"Check-out recorded at {event.check_out_time.strftime('%H:%M')}"
            message += f" - Total hours: {event.working_hours:.1f}"
            
            if event.overtime_hours > 0:
                message += f" (Overtime: {event.overtime_hours:.1f}h)"
            
            await self.notification_service.send_notification(
                recipient_id=event.employee_id,
                message=message,
                notification_type="attendance_checkout",
                metadata={
                    "attendance_id": event.attendance_id,
                    "check_out_time": event.check_out_time.isoformat(),
                    "working_hours": event.working_hours,
                    "overtime_hours": event.overtime_hours,
                    "location": event.location
                }
            )
            
            logger.info(f"Check-out notification sent for employee {event.employee_id}")
            
        except Exception as e:
            logger.error(f"Error sending check-out notification: {e}")
    
    async def _handle_late_arrival(self, event: AttendanceLateArrivalEvent) -> None:
        """Handle late arrival event notification"""
        try:
            message = f"Late arrival detected - {event.late_minutes} minutes late"
            message += f" (Expected: {event.expected_start_time.strftime('%H:%M')}, "
            message += f"Actual: {event.actual_start_time.strftime('%H:%M')})"
            
            # Send to employee
            await self.notification_service.send_notification(
                recipient_id=event.employee_id,
                message=message,
                notification_type="attendance_late_arrival",
                metadata={
                    "attendance_id": event.attendance_id,
                    "late_minutes": event.late_minutes,
                    "expected_time": event.expected_start_time.isoformat(),
                    "actual_time": event.actual_start_time.isoformat()
                }
            )
            
            # TODO: Send to manager/HR if configured
            
            logger.info(f"Late arrival notification sent for employee {event.employee_id}")
            
        except Exception as e:
            logger.error(f"Error sending late arrival notification: {e}")
    
    async def _handle_overtime(self, event: AttendanceOvertimeEvent) -> None:
        """Handle overtime event notification"""
        try:
            message = f"Overtime work detected - {event.overtime_hours:.1f} hours"
            message += f" (Total: {event.total_hours:.1f}h, Regular: {event.regular_hours:.1f}h)"
            
            await self.notification_service.send_notification(
                recipient_id=event.employee_id,
                message=message,
                notification_type="attendance_overtime",
                metadata={
                    "attendance_id": event.attendance_id,
                    "overtime_hours": event.overtime_hours,
                    "total_hours": event.total_hours,
                    "regular_hours": event.regular_hours,
                    "overtime_rate": event.overtime_rate
                }
            )
            
            logger.info(f"Overtime notification sent for employee {event.employee_id}")
            
        except Exception as e:
            logger.error(f"Error sending overtime notification: {e}")
    
    async def _handle_absence(self, event: AttendanceAbsentEvent) -> None:
        """Handle absence event notification"""
        try:
            message = f"Absence recorded for {event.absence_date}"
            if event.absence_reason:
                message += f" - Reason: {event.absence_reason}"
            
            await self.notification_service.send_notification(
                recipient_id=event.employee_id,
                message=message,
                notification_type="attendance_absence",
                metadata={
                    "attendance_id": event.attendance_id,
                    "absence_date": event.absence_date,
                    "absence_reason": event.absence_reason,
                    "marked_by": event.marked_by
                }
            )
            
            logger.info(f"Absence notification sent for employee {event.employee_id}")
            
        except Exception as e:
            logger.error(f"Error sending absence notification: {e}")
    
    async def _handle_regularization(self, event: AttendanceRegularizedEvent) -> None:
        """Handle regularization event notification"""
        try:
            message = f"Attendance regularized by {event.regularized_by}"
            message += f" - Status changed from {event.previous_status} to {event.new_status}"
            message += f" - Reason: {event.regularization_reason}"
            
            await self.notification_service.send_notification(
                recipient_id=event.employee_id,
                message=message,
                notification_type="attendance_regularization",
                metadata={
                    "attendance_id": event.attendance_id,
                    "regularized_by": event.regularized_by,
                    "previous_status": event.previous_status,
                    "new_status": event.new_status,
                    "reason": event.regularization_reason
                }
            )
            
            logger.info(f"Regularization notification sent for employee {event.employee_id}")
            
        except Exception as e:
            logger.error(f"Error sending regularization notification: {e}")


class AttendanceAnalyticsHandler(BaseEventHandler):
    """
    Handler for updating analytics and statistics based on attendance events.
    
    Updates:
    - Daily/monthly attendance statistics
    - Late arrival trends
    - Overtime patterns
    - Absence tracking
    """
    
    def __init__(self, priority: int = 75):
        """
        Initialize attendance analytics handler.
        
        Args:
            priority: Handler priority (lower = higher priority)
        """
        super().__init__(
            supported_event_types=[
                "AttendanceCheckedIn",
                "AttendanceCheckedOut",
                "AttendanceLateArrival", 
                "AttendanceOvertime",
                "AttendanceAbsent",
                "BreakStarted",
                "BreakEnded"
            ],
            priority=priority
        )
    
    async def handle(self, event: DomainEvent) -> None:
        """Handle attendance event and update analytics"""
        try:
            if isinstance(event, AttendanceCheckedInEvent):
                await self._update_checkin_analytics(event)
            elif isinstance(event, AttendanceCheckedOutEvent):
                await self._update_checkout_analytics(event)
            elif isinstance(event, AttendanceLateArrivalEvent):
                await self._update_late_arrival_analytics(event)
            elif isinstance(event, AttendanceOvertimeEvent):
                await self._update_overtime_analytics(event)
            elif isinstance(event, AttendanceAbsentEvent):
                await self._update_absence_analytics(event)
            elif isinstance(event, BreakStartedEvent):
                await self._update_break_analytics(event, "started")
            elif isinstance(event, BreakEndedEvent):
                await self._update_break_analytics(event, "ended")
            else:
                logger.warning(f"Unhandled analytics event type: {event.get_event_type()}")
                
        except Exception as e:
            logger.error(f"Error updating analytics for event {event.get_event_type()}: {e}")
    
    async def _update_checkin_analytics(self, event: AttendanceCheckedInEvent) -> None:
        """Update check-in analytics"""
        # TODO: Implement analytics update logic
        # This would typically update:
        # - Daily check-in count
        # - Average check-in time
        # - Location-based statistics
        logger.info(f"Analytics: Check-in recorded for employee {event.employee_id}")
    
    async def _update_checkout_analytics(self, event: AttendanceCheckedOutEvent) -> None:
        """Update check-out analytics"""
        # TODO: Implement analytics update logic
        # This would typically update:
        # - Daily working hours statistics
        # - Average working hours
        # - Productivity metrics
        logger.info(f"Analytics: Check-out recorded for employee {event.employee_id} - {event.working_hours}h worked")
    
    async def _update_late_arrival_analytics(self, event: AttendanceLateArrivalEvent) -> None:
        """Update late arrival analytics"""
        # TODO: Implement analytics update logic
        # This would typically update:
        # - Late arrival frequency
        # - Average lateness
        # - Trend analysis
        logger.info(f"Analytics: Late arrival recorded for employee {event.employee_id} - {event.late_minutes} minutes")
    
    async def _update_overtime_analytics(self, event: AttendanceOvertimeEvent) -> None:
        """Update overtime analytics"""
        # TODO: Implement analytics update logic
        # This would typically update:
        # - Overtime frequency
        # - Total overtime hours
        # - Cost calculations
        logger.info(f"Analytics: Overtime recorded for employee {event.employee_id} - {event.overtime_hours}h")
    
    async def _update_absence_analytics(self, event: AttendanceAbsentEvent) -> None:
        """Update absence analytics"""
        # TODO: Implement analytics update logic
        # This would typically update:
        # - Absence frequency
        # - Absence patterns
        # - Team impact analysis
        logger.info(f"Analytics: Absence recorded for employee {event.employee_id} on {event.absence_date}")
    
    async def _update_break_analytics(self, event: DomainEvent, break_type: str) -> None:
        """Update break analytics"""
        # TODO: Implement analytics update logic
        # This would typically update:
        # - Break frequency
        # - Break duration patterns
        # - Productivity correlation
        logger.info(f"Analytics: Break {break_type} for employee {event.employee_id}")


class AttendanceAuditHandler(BaseEventHandler):
    """
    Handler for maintaining audit trail of attendance events.
    
    Logs all attendance events for:
    - Compliance tracking
    - Audit requirements
    - Historical analysis
    """
    
    def __init__(self, priority: int = 90):
        """
        Initialize attendance audit handler.
        
        Args:
            priority: Handler priority (lower = higher priority)
        """
        super().__init__(
            supported_event_types=[
                "AttendanceCreated",
                "AttendanceCheckedIn",
                "AttendanceCheckedOut",
                "AttendanceUpdated",
                "AttendanceDeleted",
                "AttendanceRegularized",
                "BreakStarted",
                "BreakEnded",
                "AttendanceLateArrival",
                "AttendanceEarlyDeparture",
                "AttendanceOvertime",
                "AttendanceAbsent",
                "AttendanceHalfDay",
                "AttendanceWorkFromHome",
                "AttendanceCommentAdded"
            ],
            priority=priority
        )
    
    async def handle(self, event: DomainEvent) -> None:
        """Handle attendance event and create audit log"""
        try:
            audit_entry = {
                "event_id": event.event_id,
                "event_type": event.get_event_type(),
                "aggregate_id": event.get_aggregate_id(),
                "employee_id": getattr(event, 'employee_id', None),
                "occurred_at": event.occurred_at.isoformat(),
                "event_data": event.to_dict(),
                "audit_timestamp": datetime.utcnow().isoformat()
            }
            
            # TODO: Store audit entry in audit log storage
            # This could be a separate database, file system, or audit service
            
            logger.info(f"Audit: {event.get_event_type()} event logged for attendance {event.get_aggregate_id()}")
            
        except Exception as e:
            logger.error(f"Error creating audit log for event {event.get_event_type()}: {e}")


class AttendanceIntegrationHandler(BaseEventHandler):
    """
    Handler for integrating attendance events with external systems.
    
    Integrates with:
    - Payroll systems
    - HR management systems
    - Time tracking tools
    - Reporting systems
    """
    
    def __init__(self, priority: int = 100):
        """
        Initialize attendance integration handler.
        
        Args:
            priority: Handler priority (lower = higher priority)
        """
        super().__init__(
            supported_event_types=[
                "AttendanceCheckedOut",
                "AttendanceOvertime",
                "AttendanceAbsent",
                "AttendanceRegularized"
            ],
            priority=priority
        )
    
    async def handle(self, event: DomainEvent) -> None:
        """Handle attendance event and trigger integrations"""
        try:
            if isinstance(event, AttendanceCheckedOutEvent):
                await self._sync_with_payroll(event)
            elif isinstance(event, AttendanceOvertimeEvent):
                await self._sync_overtime_with_payroll(event)
            elif isinstance(event, AttendanceAbsentEvent):
                await self._sync_absence_with_hr(event)
            elif isinstance(event, AttendanceRegularizedEvent):
                await self._sync_regularization_with_systems(event)
            else:
                logger.warning(f"Unhandled integration event type: {event.get_event_type()}")
                
        except Exception as e:
            logger.error(f"Error in integration for event {event.get_event_type()}: {e}")
    
    async def _sync_with_payroll(self, event: AttendanceCheckedOutEvent) -> None:
        """Sync attendance data with payroll system"""
        # TODO: Implement payroll system integration
        logger.info(f"Integration: Syncing attendance with payroll for employee {event.employee_id}")
    
    async def _sync_overtime_with_payroll(self, event: AttendanceOvertimeEvent) -> None:
        """Sync overtime data with payroll system"""
        # TODO: Implement overtime payroll integration
        logger.info(f"Integration: Syncing overtime with payroll for employee {event.employee_id}")
    
    async def _sync_absence_with_hr(self, event: AttendanceAbsentEvent) -> None:
        """Sync absence data with HR system"""
        # TODO: Implement HR system integration
        logger.info(f"Integration: Syncing absence with HR for employee {event.employee_id}")
    
    async def _sync_regularization_with_systems(self, event: AttendanceRegularizedEvent) -> None:
        """Sync regularization with external systems"""
        # TODO: Implement regularization sync
        logger.info(f"Integration: Syncing regularization with external systems for employee {event.employee_id}") 