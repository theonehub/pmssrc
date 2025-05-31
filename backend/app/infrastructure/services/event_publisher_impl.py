"""
Event Publisher Implementation
Simple implementation of event publishing for domain events
"""

import logging
from typing import Any, List, Optional, Dict, Callable
from datetime import datetime

# Use a flexible import to handle different base event classes
try:
    from app.application.interfaces.services.event_publisher import EventPublisher
except ImportError:
    # Fallback interface
    from abc import ABC, abstractmethod
    
    class EventPublisher(ABC):
        @abstractmethod
        async def publish(self, event: Any) -> None:
            pass
        
        def subscribe(self, event_type: str, handler: Callable) -> str:
            pass
        
        def unsubscribe(self, subscription_id: str) -> bool:
            pass

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
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.subscription_counter = 0
        self.subscriptions: Dict[str, tuple] = {}  # subscription_id -> (event_type, handler)
    
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
            
            # Notify any subscribers (legacy style)
            for subscriber in self.subscribers:
                try:
                    if hasattr(subscriber, 'handle'):
                        await subscriber.handle(event)
                    else:
                        # Assume it's a callable
                        await subscriber(event)
                except Exception as e:
                    logger.error(f"Error in event subscriber: {e}")
                    # Don't fail the entire operation for subscriber errors
            
            # Notify typed event handlers
            event_type = event.__class__.__name__
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    try:
                        if callable(handler):
                            # Handle both sync and async handlers
                            if hasattr(handler, '__await__'):
                                await handler(event)
                            else:
                                handler(event)
                    except Exception as e:
                        logger.error(f"Error in event handler for {event_type}: {e}")
            
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            # Don't fail the operation for event publishing errors
    
    async def publish_batch(self, events: List[Any]) -> None:
        """
        Publish multiple domain events.
        
        Args:
            events: List of domain events to publish
        """
        for event in events:
            await self.publish(event)
    
    def subscribe(self, event_type: str, handler: Callable) -> str:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: Type of events to subscribe to
            handler: Function to handle the events
            
        Returns:
            Subscription ID for managing the subscription
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        
        # Generate subscription ID
        self.subscription_counter += 1
        subscription_id = f"sub_{self.subscription_counter}"
        self.subscriptions[subscription_id] = (event_type, handler)
        
        logger.info(f"Subscribed to {event_type} events")
        return subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events.
        
        Args:
            subscription_id: ID of subscription to remove
            
        Returns:
            True if unsubscribed successfully, False otherwise
        """
        if subscription_id not in self.subscriptions:
            return False
        
        event_type, handler = self.subscriptions[subscription_id]
        
        if event_type in self.event_handlers and handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
            del self.subscriptions[subscription_id]
            logger.info(f"Unsubscribed from {event_type} events")
            return True
        
        return False
    
    def get_event_history(
        self,
        aggregate_id: Optional[str] = None,
        event_type: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Any]:
        """
        Get event history with optional filtering.
        
        This is a simple implementation that returns empty list.
        In a real implementation, this would query an event store.
        
        Args:
            aggregate_id: Filter by aggregate ID
            event_type: Filter by event type
            from_date: Filter events from this date
            to_date: Filter events until this date
            limit: Maximum number of events to return
            
        Returns:
            List of domain events matching the criteria
        """
        # Simple implementation - return empty list
        # In a real implementation, this would query an event store
        logger.debug(f"Event history requested for aggregate_id={aggregate_id}, event_type={event_type}")
        return []
    
    # Legacy methods for backward compatibility
    def add_subscriber(self, subscriber) -> None:
        """
        Add a legacy subscriber.
        
        Args:
            subscriber: Event subscriber with handle method
        """
        self.subscribers.append(subscriber)
        logger.info("Added legacy subscriber")
    
    def remove_subscriber(self, subscriber) -> None:
        """
        Remove a legacy subscriber.
        
        Args:
            subscriber: Event subscriber to remove
        """
        if subscriber in self.subscribers:
            self.subscribers.remove(subscriber)
            logger.info("Removed legacy subscriber")
    
    def get_subscriber_count(self, event_type: Optional[str] = None) -> int:
        """Get number of subscribers for event type or total"""
        if event_type:
            return len(self.event_handlers.get(event_type, []))
        else:
            return len(self.subscribers) + sum(len(handlers) for handlers in self.event_handlers.values()) 