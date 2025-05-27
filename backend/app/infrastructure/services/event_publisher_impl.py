"""
Event Publisher Implementation
Simple implementation of event publishing for domain events
"""

import logging
from typing import Any
from application.interfaces.services.event_publisher import EventPublisher

logger = logging.getLogger(__name__)


class EventPublisherImpl(EventPublisher):
    """
    Simple event publisher implementation.
    
    Follows SOLID principles:
    - SRP: Only handles event publishing
    - OCP: Can be extended with different publishing strategies
    - LSP: Can be substituted with other implementations
    - ISP: Implements focused event publishing interface
    - DIP: Depends on abstractions
    """
    
    def __init__(self):
        """Initialize event publisher"""
        self.subscribers = []
    
    async def publish(self, event: Any) -> None:
        """
        Publish a domain event.
        
        Args:
            event: Domain event to publish
        """
        try:
            # For now, just log the event
            # In a real implementation, this would publish to a message queue
            logger.info(f"Publishing event: {event.__class__.__name__}")
            logger.debug(f"Event details: {event}")
            
            # Notify any subscribers
            for subscriber in self.subscribers:
                try:
                    await subscriber.handle(event)
                except Exception as e:
                    logger.error(f"Error in event subscriber: {e}")
                    # Don't fail the entire operation for subscriber errors
            
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            # Don't fail the operation for event publishing errors
    
    def subscribe(self, subscriber) -> None:
        """
        Subscribe to events.
        
        Args:
            subscriber: Event subscriber with handle method
        """
        self.subscribers.append(subscriber)
    
    def unsubscribe(self, subscriber) -> None:
        """
        Unsubscribe from events.
        
        Args:
            subscriber: Event subscriber to remove
        """
        if subscriber in self.subscribers:
            self.subscribers.remove(subscriber) 