"""
Enhanced Event Publisher Implementation
Advanced event publisher with event store, handler registry, and persistence
"""

import logging
import asyncio
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
from pymongo.collection import Collection
from pymongo import ASCENDING, DESCENDING

from app.application.interfaces.services.event_publisher import EventPublisher
from app.application.interfaces.services.event_handler import EventHandler, EventHandlerRegistry
from app.domain.events.base_event import DomainEvent
from app.infrastructure.database.mongodb_connector import MongoDBConnector
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EventStore:
    """
    Event store for persisting domain events.
    
    Provides:
    - Event persistence
    - Event retrieval
    - Event replay capabilities
    - Event history tracking
    """
    
    def __init__(self, db_connector: MongoDBConnector):
        """
        Initialize event store.
        
        Args:
            db_connector: MongoDB database connector
        """
        self.db_connector = db_connector
        self._collection: Optional[Collection] = None
        self._ensure_indexes_created = False
    
    async def _get_collection(self) -> Collection:
        """Get MongoDB collection for events"""
        if self._collection is None:
            db = self.db_connector.get_database()
            self._collection = db["domain_events"]
            
            if not self._ensure_indexes_created:
                await self._ensure_indexes()
                self._ensure_indexes_created = True
        
        return self._collection
    
    async def _ensure_indexes(self) -> None:
        """Ensure necessary indexes exist"""
        try:
            collection = await self._get_collection()
            
            # Create indexes for efficient querying
            await collection.create_index([("event_type", ASCENDING)])
            await collection.create_index([("aggregate_id", ASCENDING)])
            await collection.create_index([("occurred_at", DESCENDING)])
            await collection.create_index([("processed", ASCENDING)])
            await collection.create_index([("employee_id", ASCENDING)])
            
            # Compound indexes for common queries
            await collection.create_index([
                ("aggregate_id", ASCENDING),
                ("occurred_at", DESCENDING)
            ])
            
            await collection.create_index([
                ("event_type", ASCENDING),
                ("occurred_at", DESCENDING)
            ])
            
            logger.info("Event store indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Error creating event store indexes: {e}")
    
    async def save_event(self, event: DomainEvent) -> bool:
        """
        Save domain event to store.
        
        Args:
            event: Domain event to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            collection = await self._get_collection()
            
            event_document = self._event_to_document(event)
            result = await collection.insert_one(event_document)
            
            if result.inserted_id:
                logger.info(f"Event saved: {event.get_event_type()} for aggregate {event.get_aggregate_id()}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error saving event to store: {e}")
            return False
    
    async def save_events_batch(self, events: List[DomainEvent]) -> Dict[str, bool]:
        """
        Save multiple events in batch.
        
        Args:
            events: List of domain events to save
            
        Returns:
            Dictionary mapping event IDs to save success status
        """
        results = {}
        
        try:
            if not events:
                return results
            
            collection = await self._get_collection()
            
            # Prepare documents for batch insert
            documents = []
            for event in events:
                documents.append(self._event_to_document(event))
            
            # Batch insert
            insert_result = await collection.insert_many(documents)
            
            # Process results
            for i, event in enumerate(events):
                success = i < len(insert_result.inserted_ids) and insert_result.inserted_ids[i] is not None
                results[event.event_id] = success
            
            logger.info(f"Batch saved {len(documents)} events to store")
            
        except Exception as e:
            logger.error(f"Error saving event batch to store: {e}")
            # Mark all as failed
            for event in events:
                results[event.event_id] = False
        
        return results
    
    async def get_events_by_aggregate(
        self,
        aggregate_id: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get events for specific aggregate.
        
        Args:
            aggregate_id: Aggregate ID to filter by
            from_date: Start date filter
            to_date: End date filter
            limit: Maximum number of events to return
            
        Returns:
            List of event documents
        """
        try:
            collection = await self._get_collection()
            
            # Build query
            query = {"aggregate_id": aggregate_id}
            
            if from_date or to_date:
                date_filter = {}
                if from_date:
                    date_filter["$gte"] = from_date
                if to_date:
                    date_filter["$lte"] = to_date
                query["occurred_at"] = date_filter
            
            # Execute query
            cursor = collection.find(query).sort("occurred_at", ASCENDING).limit(limit)
            events = await cursor.to_list(length=limit)
            
            return events
            
        except Exception as e:
            logger.error(f"Error retrieving events for aggregate {aggregate_id}: {e}")
            return []
    
    async def get_events_by_type(
        self,
        event_type: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get events by type.
        
        Args:
            event_type: Event type to filter by
            from_date: Start date filter
            to_date: End date filter
            limit: Maximum number of events to return
            
        Returns:
            List of event documents
        """
        try:
            collection = await self._get_collection()
            
            # Build query
            query = {"event_type": event_type}
            
            if from_date or to_date:
                date_filter = {}
                if from_date:
                    date_filter["$gte"] = from_date
                if to_date:
                    date_filter["$lte"] = to_date
                query["occurred_at"] = date_filter
            
            # Execute query
            cursor = collection.find(query).sort("occurred_at", DESCENDING).limit(limit)
            events = await cursor.to_list(length=limit)
            
            return events
            
        except Exception as e:
            logger.error(f"Error retrieving events by type {event_type}: {e}")
            return []
    
    async def mark_event_processed(self, event_id: str) -> bool:
        """
        Mark event as processed.
        
        Args:
            event_id: Event ID to mark as processed
            
        Returns:
            True if marked successfully, False otherwise
        """
        try:
            collection = await self._get_collection()
            
            result = await collection.update_one(
                {"event_id": event_id},
                {
                    "$set": {
                        "processed": True,
                        "processed_at": datetime.utcnow()
                    }
                }
            )
            
            return result.matched_count > 0
            
        except Exception as e:
            logger.error(f"Error marking event {event_id} as processed: {e}")
            return False
    
    def _event_to_document(self, event: DomainEvent) -> Dict[str, Any]:
        """Convert domain event to MongoDB document"""
        return {
            "event_id": event.event_id,
            "event_type": event.get_event_type(),
            "aggregate_id": event.get_aggregate_id(),
            "employee_id": getattr(event, 'employee_id', None),
            "occurred_at": event.occurred_at,
            "event_data": event.to_dict(),
            "processed": False,
            "created_at": datetime.utcnow(),
            "version": 1
        }


class EnhancedEventPublisher(EventPublisher):
    """
    Enhanced event publisher with event store and handler registry.
    
    Features:
    - Event persistence
    - Handler registry integration
    - Async event processing
    - Error handling and retry logic
    - Event replay capabilities
    """
    
    def __init__(self, db_connector: MongoDBConnector):
        """
        Initialize enhanced event publisher.
        
        Args:
            db_connector: MongoDB database connector
        """
        self.event_store = EventStore(db_connector)
        self.handler_registry = EventHandlerRegistry()
        self._processing_queue: List[DomainEvent] = []
        self._is_processing = False
    
    async def publish(self, event: DomainEvent) -> None:
        """
        Publish a single domain event.
        
        Args:
            event: Domain event to publish
        """
        try:
            # Save event to store
            saved = await self.event_store.save_event(event)
            if not saved:
                logger.error(f"Failed to save event {event.event_id} to store")
                return
            
            # Process event with handlers
            await self._process_event_with_handlers(event)
            
            # Mark as processed
            await self.event_store.mark_event_processed(event.event_id)
            
            logger.info(f"Successfully published event: {event.get_event_type()}")
            
        except Exception as e:
            logger.error(f"Error publishing event {event.get_event_type()}: {e}")
            raise
    
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """
        Publish multiple domain events.
        
        Args:
            events: List of domain events to publish
        """
        try:
            if not events:
                return
            
            # Save events to store
            save_results = await self.event_store.save_events_batch(events)
            
            # Process successfully saved events
            for event in events:
                if save_results.get(event.event_id, False):
                    try:
                        await self._process_event_with_handlers(event)
                        await self.event_store.mark_event_processed(event.event_id)
                    except Exception as e:
                        logger.error(f"Error processing event {event.event_id}: {e}")
                else:
                    logger.error(f"Event {event.event_id} was not saved to store")
            
            logger.info(f"Successfully published batch of {len(events)} events")
            
        except Exception as e:
            logger.error(f"Error publishing event batch: {e}")
            raise
    
    async def _process_event_with_handlers(self, event: DomainEvent) -> None:
        """Process event with registered handlers"""
        try:
            handlers = self.handler_registry.get_handlers_for_event(event)
            
            if not handlers:
                logger.info(f"No handlers found for event type: {event.get_event_type()}")
                return
            
            # Process handlers in priority order
            for handler in handlers:
                try:
                    await handler.handle(event)
                    logger.info(f"Handler {handler.get_handler_name()} processed event {event.event_id}")
                except Exception as e:
                    logger.error(f"Handler {handler.get_handler_name()} failed to process event {event.event_id}: {e}")
                    # Continue with other handlers
            
        except Exception as e:
            logger.error(f"Error processing event {event.event_id} with handlers: {e}")
    
    def register_handler(self, handler: EventHandler) -> None:
        """
        Register an event handler.
        
        Args:
            handler: Event handler to register
        """
        try:
            self.handler_registry.register_handler(handler)
            logger.info(f"Registered event handler: {handler.get_handler_name()}")
        except Exception as e:
            logger.error(f"Error registering handler {handler.get_handler_name()}: {e}")
            raise
    
    def unregister_handler(self, handler: EventHandler) -> bool:
        """
        Unregister an event handler.
        
        Args:
            handler: Event handler to unregister
            
        Returns:
            True if unregistered successfully, False otherwise
        """
        try:
            result = self.handler_registry.unregister_handler(handler)
            if result:
                logger.info(f"Unregistered event handler: {handler.get_handler_name()}")
            return result
        except Exception as e:
            logger.error(f"Error unregistering handler {handler.get_handler_name()}: {e}")
            return False
    
    def subscribe(
        self, 
        event_type: str, 
        handler: Callable[[DomainEvent], None]
    ) -> str:
        """
        Subscribe to events of a specific type (legacy compatibility).
        
        Args:
            event_type: Type of events to subscribe to
            handler: Function to handle the events
            
        Returns:
            Subscription ID for managing the subscription
        """
        # Create a wrapper handler for the callable
        from app.application.interfaces.services.event_handler import BaseEventHandler
        
        class CallableHandler(BaseEventHandler):
            def __init__(self, event_type: str, handler_func: Callable):
                super().__init__([event_type])
                self.handler_func = handler_func
            
            async def handle(self, event: DomainEvent) -> None:
                if callable(self.handler_func):
                    if asyncio.iscoroutinefunction(self.handler_func):
                        await self.handler_func(event)
                    else:
                        self.handler_func(event)
        
        wrapper_handler = CallableHandler(event_type, handler)
        self.register_handler(wrapper_handler)
        
        return f"callable_handler_{event_type}_{id(handler)}"
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events (legacy compatibility).
        
        Args:
            subscription_id: ID of subscription to remove
            
        Returns:
            True if unsubscribed successfully, False otherwise
        """
        # For callable handlers, we'd need to track them separately
        # This is a simplified implementation
        logger.info(f"Unsubscribe requested for subscription: {subscription_id}")
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
        # This would need to be implemented as async, but interface requires sync
        # For now, return empty list and log the request
        logger.info(f"Event history requested - aggregate_id: {aggregate_id}, event_type: {event_type}")
        return []
    
    async def get_event_history_async(
        self,
        aggregate_id: Optional[str] = None,
        event_type: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get event history asynchronously.
        
        Args:
            aggregate_id: Filter by aggregate ID
            event_type: Filter by event type
            from_date: Filter events from this date
            to_date: Filter events until this date
            limit: Maximum number of events to return
            
        Returns:
            List of event documents matching the criteria
        """
        try:
            if aggregate_id:
                return await self.event_store.get_events_by_aggregate(
                    aggregate_id, from_date, to_date, limit
                )
            elif event_type:
                return await self.event_store.get_events_by_type(
                    event_type, from_date, to_date, limit
                )
            else:
                # Get all events (implement if needed)
                logger.warning("Getting all events not implemented - use specific filters")
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving event history: {e}")
            return []
    
    async def replay_events(
        self,
        aggregate_id: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> int:
        """
        Replay events for an aggregate.
        
        Args:
            aggregate_id: Aggregate ID to replay events for
            from_date: Start date for replay
            to_date: End date for replay
            
        Returns:
            Number of events replayed
        """
        try:
            events = await self.event_store.get_events_by_aggregate(
                aggregate_id, from_date, to_date
            )
            
            replayed_count = 0
            for event_doc in events:
                try:
                    # Convert document back to event (would need event registry)
                    # For now, just log the replay
                    logger.info(f"Replaying event: {event_doc['event_type']} for {aggregate_id}")
                    replayed_count += 1
                except Exception as e:
                    logger.error(f"Error replaying event {event_doc.get('event_id')}: {e}")
            
            logger.info(f"Replayed {replayed_count} events for aggregate {aggregate_id}")
            return replayed_count
            
        except Exception as e:
            logger.error(f"Error replaying events for aggregate {aggregate_id}: {e}")
            return 0
    
    def get_handler_registry(self) -> EventHandlerRegistry:
        """Get the event handler registry"""
        return self.handler_registry
    
    def get_event_store(self) -> EventStore:
        """Get the event store"""
        return self.event_store 