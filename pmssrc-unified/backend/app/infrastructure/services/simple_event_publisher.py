"""
Simple Event Publisher Implementation
Basic implementation of event publishing for the organisation system
"""

import logging
from typing import Any, List, Dict
from datetime import datetime

from app.application.interfaces.services.event_publisher import EventPublisher
from app.domain.events.base_event import DomainEvent


logger = logging.getLogger(__name__)


class SimpleEventPublisher(EventPublisher):
    """
    Simple implementation of event publisher.
    
    This is a basic implementation that logs events and can be extended
    to integrate with message queues, event stores, or other systems.
    
    Follows SOLID principles:
    - SRP: Only handles event publishing
    - OCP: Can be extended with new event handlers
    - LSP: Can be substituted with other publishers
    - ISP: Implements focused interface
    - DIP: Depends on abstractions
    """
    
    def __init__(self):
        self.event_handlers: Dict[str, List[callable]] = {}
        self.published_events: List[Dict[str, Any]] = []
    
    async def publish(self, event: DomainEvent) -> None:
        """
        Publish a domain event.
        
        Args:
            event: Domain event to publish
        """
        try:
            event_data = {
                "event_type": event.__class__.__name__,
                "event_id": getattr(event, 'event_id', None),
                "aggregate_id": getattr(event, 'aggregate_id', None),
                "occurred_at": getattr(event, 'occurred_at', datetime.utcnow()),
                "event_data": event.to_dict() if hasattr(event, 'to_dict') else str(event)
            }
            
            # Store event for tracking
            self.published_events.append(event_data)
            
            # Log the event
            logger.info(f"Published event: {event_data['event_type']} for aggregate {event_data['aggregate_id']}")
            
            # Call registered handlers
            event_type = event.__class__.__name__
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    try:
                        await handler(event)
                    except Exception as e:
                        logger.error(f"Error in event handler for {event_type}: {e}")
            
        except Exception as e:
            logger.error(f"Error publishing event {event.__class__.__name__}: {e}")
            raise
    
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """
        Publish multiple domain events.
        
        Args:
            events: List of domain events to publish
        """
        for event in events:
            await self.publish(event)
    
    def register_handler(self, event_type: str, handler: callable) -> None:
        """
        Register an event handler.
        
        Args:
            event_type: Type of event to handle
            handler: Handler function
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def get_published_events(self) -> List[Dict[str, Any]]:
        """Get list of published events for testing/debugging"""
        return self.published_events.copy()
    
    def clear_published_events(self) -> None:
        """Clear published events list"""
        self.published_events.clear() 