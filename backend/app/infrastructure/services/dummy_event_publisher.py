"""
Dummy Event Publisher Implementation
Temporary implementation for event publishing until proper event system is set up
"""

import logging
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime

from app.application.interfaces.services.event_publisher import EventPublisher
from app.domain.events.base_event import DomainEvent

logger = logging.getLogger(__name__)


class DummyEventPublisher(EventPublisher):
    """
    Dummy implementation of EventPublisher.
    
    This is a temporary implementation that logs events instead of actually publishing them.
    In a production system, this would be replaced with a proper event publishing mechanism
    like Redis, RabbitMQ, or Kafka.
    """
    
    async def publish(self, event: DomainEvent) -> None:
        """
        Log the event instead of publishing it.
        
        Args:
            event: Domain event to publish
        """
        try:
            logger.info(f"Publishing event '{event.get_event_type()}' for aggregate '{event.get_aggregate_id()}'")
        except Exception as e:
            logger.error(f"Error logging event: {e}")
    
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """
        Log multiple events instead of publishing them.
        
        Args:
            events: List of domain events to publish
        """
        try:
            logger.info(f"Publishing {len(events)} events in batch")
            for event in events:
                await self.publish(event)
        except Exception as e:
            logger.error(f"Error logging batch events: {e}")
    
    def subscribe(
        self, 
        event_type: str, 
        handler: Callable[[DomainEvent], None]
    ) -> str:
        """
        Dummy subscription that just logs.
        
        Args:
            event_type: Type of events to subscribe to
            handler: Function to handle the events
            
        Returns:
            Dummy subscription ID
        """
        logger.info(f"Dummy subscription to event type '{event_type}'")
        return f"dummy_sub_{event_type}"
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Dummy unsubscription that just logs.
        
        Args:
            subscription_id: ID of subscription to remove
            
        Returns:
            Always returns True
        """
        logger.info(f"Dummy unsubscribe from '{subscription_id}'")
        return True
    
    def get_event_history(
        self,
        aggregate_id: Optional[str] = None,
        event_type: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[DomainEvent]:
        """
        Return empty event history for dummy implementation.
        
        Returns:
            Empty list
        """
        logger.info("Dummy event history request - returning empty list")
        return [] 