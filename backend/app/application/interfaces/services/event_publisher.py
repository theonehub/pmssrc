"""
Event Publisher Interface
Abstract interface for publishing domain events
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime

from domain.events.base_event import DomainEvent


class EventPublisher(ABC):
    """
    Abstract interface for publishing domain events.
    
    Follows SOLID principles:
    - SRP: Only handles event publishing
    - OCP: Can be extended with new implementations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for event publishing
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """
        Publish a single domain event.
        
        Args:
            event: Domain event to publish
        """
        pass
    
    @abstractmethod
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """
        Publish multiple domain events.
        
        Args:
            events: List of domain events to publish
        """
        pass
    
    @abstractmethod
    def subscribe(
        self, 
        event_type: str, 
        handler: Callable[[DomainEvent], None]
    ) -> str:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: Type of events to subscribe to
            handler: Function to handle the events
            
        Returns:
            Subscription ID for managing the subscription
        """
        pass
    
    @abstractmethod
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events.
        
        Args:
            subscription_id: ID of subscription to remove
            
        Returns:
            True if unsubscribed successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def get_event_history(
        self,
        aggregate_id: Optional[str] = None,
        event_type: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[DomainEvent]:
        """
        Get event history with optional filtering.
        
        Args:
            aggregate_id: Filter by aggregate ID
            event_type: Filter by event type
            from_date: Filter events from this date
            to_date: Filter events until this date
            limit: Maximum number of events to return
            
        Returns:
            List of domain events matching the criteria
        """
        pass


class InMemoryEventPublisher(EventPublisher):
    """
    In-memory event publisher implementation for testing and development.
    
    This implementation stores events in memory and provides synchronous
    event handling. Suitable for testing and single-instance deployments.
    """
    
    def __init__(self):
        self._event_store: List[DomainEvent] = []
        self._subscribers: Dict[str, List[Callable]] = {}
        self._subscription_counter = 0
        self._subscriptions: Dict[str, tuple] = {}  # subscription_id -> (event_type, handler)
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish event and notify subscribers"""
        try:
            # Store event
            self._event_store.append(event)
            
            # Notify subscribers
            event_type = event.get_event_type()
            if event_type in self._subscribers:
                for handler in self._subscribers[event_type]:
                    try:
                        await handler(event)
                    except Exception as e:
                        # Log error but don't fail the publish operation
                        print(f"Error in event handler: {e}")
        except Exception:
            pass
    
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """Publish multiple events"""
        for event in events:
            await self.publish(event)
    
    def subscribe(
        self, 
        event_type: str, 
        handler: Callable[[DomainEvent], None]
    ) -> str:
        """Subscribe to events of specific type"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(handler)
        
        # Generate subscription ID
        self._subscription_counter += 1
        subscription_id = f"sub_{self._subscription_counter}"
        self._subscriptions[subscription_id] = (event_type, handler)
        
        return subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events"""
        if subscription_id not in self._subscriptions:
            return False
        
        event_type, handler = self._subscriptions[subscription_id]
        
        if event_type in self._subscribers and handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)
            del self._subscriptions[subscription_id]
            return True
        
        return False
    
    def get_event_history(
        self,
        aggregate_id: Optional[str] = None,
        event_type: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[DomainEvent]:
        """Get filtered event history"""
        
        filtered_events = self._event_store
        
        # Apply filters
        if aggregate_id:
            filtered_events = [e for e in filtered_events if e.get_aggregate_id() == aggregate_id]
        
        if event_type:
            filtered_events = [e for e in filtered_events if e.get_event_type() == event_type]
        
        if from_date:
            filtered_events = [e for e in filtered_events if e.occurred_at >= from_date]
        
        if to_date:
            filtered_events = [e for e in filtered_events if e.occurred_at <= to_date]
        
        # Sort by occurrence time (newest first) and apply limit
        filtered_events.sort(key=lambda e: e.occurred_at, reverse=True)
        
        return filtered_events[:limit]
    
    def clear_events(self):
        """Clear all stored events (useful for testing)"""
        self._event_store.clear()
    
    def get_subscriber_count(self, event_type: str) -> int:
        """Get number of subscribers for event type"""
        return len(self._subscribers.get(event_type, []))


class EventPublisherError(Exception):
    """Base exception for event publisher operations"""
    pass


class EventPublishError(EventPublisherError):
    """Exception raised when event publishing fails"""
    
    def __init__(self, event: DomainEvent, reason: str):
        self.event = event
        self.reason = reason
        super().__init__(f"Failed to publish event {event.get_event_type()}: {reason}")


class EventSubscriptionError(EventPublisherError):
    """Exception raised when event subscription fails"""
    
    def __init__(self, event_type: str, reason: str):
        self.event_type = event_type
        self.reason = reason
        super().__init__(f"Failed to subscribe to event type '{event_type}': {reason}")


class EventHandlerError(EventPublisherError):
    """Exception raised when event handler execution fails"""
    
    def __init__(self, event: DomainEvent, handler_name: str, reason: str):
        self.event = event
        self.handler_name = handler_name
        self.reason = reason
        super().__init__(f"Event handler '{handler_name}' failed for event {event.get_event_type()}: {reason}") 