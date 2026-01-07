"""
Event Generator: Creates realistic order events with proper payloads
"""
import uuid
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from faker import Faker

from config import ORDER_PATTERNS


class EventGenerator:
    """Generates realistic order events with proper Avro payloads"""
    
    def __init__(self, seed: int = 42):
        self.faker = Faker()
        Faker.seed(seed)
        random.seed(seed)
        
        # Track items for each order
        self.order_items: Dict[str, List[Dict[str, Any]]] = {}
        
    def generate_order_lifecycle(self, order_id: str, base_timestamp: datetime) -> List[Dict[str, Any]]:
        """
        Generate a complete lifecycle for an order
        Returns list of event dictionaries ready for Avro serialization
        """
        # Choose a pattern based on weights
        pattern = random.choices(
            ORDER_PATTERNS,
            weights=[p['weight'] for p in ORDER_PATTERNS],
            k=1
        )[0]
        
        events = []
        current_ts = base_timestamp
        self.order_items[order_id] = []
        
        # Generate customer and restaurant for this order
        customer_id = f"cust_{self.faker.uuid4()[:8]}"
        restaurant_id = f"rest_{self.faker.uuid4()[:8]}"
        current_status = "PENDING"
        
        for event_type in pattern['events']:
            # Increment timestamp for each event (simulate real timeline)
            current_ts += timedelta(seconds=random.uniform(1, 30))
            
            event = self._create_event(
                order_id=order_id,
                event_type=event_type,
                event_ts=current_ts,
                customer_id=customer_id,
                restaurant_id=restaurant_id,
                current_status=current_status
            )
            
            # Update status for next event
            if event_type == 'ORDER_CONFIRMED':
                current_status = 'CONFIRMED'
            elif event_type == 'ORDER_CANCELLED':
                current_status = 'CANCELLED'
            elif event_type == 'ORDER_COMPLETED':
                current_status = 'COMPLETED'
            
            events.append(event)
        
        return events
    
    def _create_event(
        self,
        order_id: str,
        event_type: str,
        event_ts: datetime,
        customer_id: str,
        restaurant_id: str,
        current_status: str
    ) -> Dict[str, Any]:
        """Create a single event with proper Avro payload"""
        event_id = str(uuid.uuid4())
        event_ts_millis = int(event_ts.timestamp() * 1000)
        
        # Create the appropriate payload based on event type
        payload = self._create_payload(
            event_type=event_type,
            order_id=order_id,
            customer_id=customer_id,
            restaurant_id=restaurant_id,
            current_status=current_status,
            event_ts=event_ts
        )
        
        return {
            'event_id': event_id,
            'event_type': event_type,
            'event_ts': event_ts_millis,
            'order_id': order_id,
            'payload': payload,
            'schema_version': 1
        }
    
    def _create_payload(
        self,
        event_type: str,
        order_id: str,
        customer_id: str,
        restaurant_id: str,
        current_status: str,
        event_ts: datetime
    ) -> Dict[str, Any]:
        """Create event-specific payload (union type in Avro)"""
        
        if event_type == 'ORDER_CREATED':
            return {
                'com.orderup.events.OrderCreatedPayload': {
                    'customer_id': customer_id,
                    'restaurant_id': restaurant_id,
                    'initial_status': 'PENDING'
                }
            }
        
        elif event_type == 'ORDER_UPDATED':
            new_status = random.choice(['PENDING', 'CONFIRMED'])
            return {
                'com.orderup.events.OrderUpdatedPayload': {
                    'old_status': current_status,
                    'new_status': new_status
                }
            }
        
        elif event_type == 'ORDER_ITEM_ADDED':
            item = {
                'item_id': f"item_{self.faker.uuid4()[:8]}",
                'item_name': self.faker.word().title() + " " + random.choice(['Burger', 'Pizza', 'Salad', 'Pasta', 'Taco']),
                'quantity': random.randint(1, 5),
                'price': round(random.uniform(5.99, 29.99), 2)
            }
            # Track this item for potential removal
            self.order_items[order_id].append(item)
            
            return {
                'com.orderup.events.OrderItemAddedPayload': item
            }
        
        elif event_type == 'ORDER_ITEM_REMOVED':
            # Remove a random item if any exist
            if self.order_items.get(order_id):
                removed_item = random.choice(self.order_items[order_id])
                self.order_items[order_id].remove(removed_item)
                return {
                    'com.orderup.events.OrderItemRemovedPayload': {
                        'item_id': removed_item['item_id']
                    }
                }
            else:
                # Fallback: create a dummy item to remove
                return {
                    'com.orderup.events.OrderItemRemovedPayload': {
                        'item_id': f"item_{self.faker.uuid4()[:8]}"
                    }
                }
        
        elif event_type == 'ORDER_CONFIRMED':
            return {
                'com.orderup.events.OrderConfirmedPayload': {
                    'confirmed_by': f"user_{self.faker.uuid4()[:8]}",
                    'estimated_delivery_ts': int((event_ts + timedelta(minutes=random.randint(30, 90))).timestamp() * 1000)
                }
            }
        
        elif event_type == 'ORDER_CANCELLED':
            reasons = [
                'Customer requested cancellation',
                'Restaurant unavailable',
                'Payment failed',
                'Item out of stock',
                None  # Sometimes no reason
            ]
            return {
                'com.orderup.events.OrderCancelledPayload': {
                    'cancelled_by': f"user_{self.faker.uuid4()[:8]}",
                    'reason': random.choice(reasons)
                }
            }
        
        elif event_type == 'ORDER_COMPLETED':
            # Calculate total from items
            total = sum(item['price'] * item['quantity'] for item in self.order_items.get(order_id, []))
            if total == 0:
                total = round(random.uniform(15.99, 99.99), 2)  # Fallback
            
            return {
                'com.orderup.events.OrderCompletedPayload': {
                    'completed_ts': int(event_ts.timestamp() * 1000),
                    'total_amount': total
                }
            }
        
        else:
            raise ValueError(f"Unknown event type: {event_type}")

