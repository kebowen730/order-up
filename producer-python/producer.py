#!/usr/bin/env python3
"""
Order Event Producer

Features:
- Idempotent producer
- Keyed by order_id
- Generates realistic order lifecycles
- Injects edge cases: duplicates, out-of-order, late arrivals
"""
import sys
import time
import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any

from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

from config import (
    KAFKA_BOOTSTRAP_SERVERS,
    SCHEMA_REGISTRY_URL,
    RAW_TOPIC,
    PRODUCER_CONFIG,
    SIMULATION_CONFIG
)
from event_generator import EventGenerator
from edge_case_injector import EdgeCaseInjector


class OrderProducer:
    """Produces order events to Kafka with Avro serialization"""
    
    def __init__(self):
        # Schema Registry setup
        self.schema_registry_client = SchemaRegistryClient({'url': SCHEMA_REGISTRY_URL})
        
        # Load Avro schema
        self.schema_str = self._load_schema()
        
        # Create Avro serializer
        self.avro_serializer = AvroSerializer(
            self.schema_registry_client,
            self.schema_str,
            to_dict=lambda obj, ctx: obj  # Events are already dicts
        )
        
        # Create Kafka producer (with idempotency enabled!)
        self.producer = Producer(PRODUCER_CONFIG)
        
        # Event generator and edge case injector
        self.event_generator = EventGenerator()
        self.edge_case_injector = EdgeCaseInjector(
            duplicate_probability=SIMULATION_CONFIG['duplicate_probability'],
            out_of_order_probability=SIMULATION_CONFIG['out_of_order_probability'],
            late_arrival_probability=SIMULATION_CONFIG['late_arrival_probability']
        )
        
        # Delivery stats
        self.delivered_count = 0
        self.failed_count = 0
        
    def _load_schema(self) -> str:
        """Load Avro schema from file"""
        schema_path = '../schemas/order-event-raw.avsc'
        try:
            with open(schema_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            print(f"❌ Schema file not found: {schema_path}")
            print("   Make sure you're running from the producer-python directory")
            sys.exit(1)
    
    def delivery_callback(self, err, msg):
        """Callback for message delivery reports"""
        if err:
            self.failed_count += 1
            print(f'❌ Message delivery failed: {err}')
        else:
            self.delivered_count += 1
            # Only print occasional confirmations to avoid spam
            if self.delivered_count % 10 == 0:
                print(f'✅ Delivered {self.delivered_count} messages (partition={msg.partition()}, offset={msg.offset()})')
    
    def send_event(self, event: Dict[str, Any], delay_seconds: float = 0):
        """Send a single event to Kafka"""
        if delay_seconds > 0:
            time.sleep(delay_seconds)
        
        try:
            # Serialize value (the entire event envelope)
            serialization_context = SerializationContext(RAW_TOPIC, MessageField.VALUE)
            serialized_value = self.avro_serializer(event, serialization_context)
            
            # Key is order_id (as bytes)
            key = event['order_id'].encode('utf-8')
            
            # Produce to Kafka
            self.producer.produce(
                topic=RAW_TOPIC,
                key=key,
                value=serialized_value,
                on_delivery=self.delivery_callback
            )
            
            # Trigger callbacks (non-blocking)
            self.producer.poll(0)
            
        except Exception as e:
            print(f"❌ Error sending event: {e}")
            raise
    
    def run_simulation(self):
        """Run the full order simulation with edge cases"""
        print("=" * 80)
        print("🚀 Order Event Producer")
        print("=" * 80)
        print(f"Kafka: {KAFKA_BOOTSTRAP_SERVERS}")
        print(f"Schema Registry: {SCHEMA_REGISTRY_URL}")
        print(f"Topic: {RAW_TOPIC}")
        print(f"Orders: {SIMULATION_CONFIG['num_orders']}")
        print(f"Idempotent: {PRODUCER_CONFIG['enable.idempotence']}")
        print()
        print("Edge Case Probabilities:")
        print(f"  - Duplicates: {SIMULATION_CONFIG['duplicate_probability']*100}%")
        print(f"  - Out-of-order: {SIMULATION_CONFIG['out_of_order_probability']*100}%")
        print(f"  - Late arrivals: {SIMULATION_CONFIG['late_arrival_probability']*100}%")
        print("=" * 80)
        print()
        
        # Track all late arrival events
        all_late_arrivals = []
        
        # Generate events for each order
        num_orders = SIMULATION_CONFIG['num_orders']
        base_timestamp = datetime.now() - timedelta(hours=2)  # Start 2 hours ago
        
        for order_num in range(num_orders):
            order_id = f"order_{order_num:04d}"
            
            # Generate lifecycle events for this order
            events = self.event_generator.generate_order_lifecycle(
                order_id=order_id,
                base_timestamp=base_timestamp + timedelta(minutes=order_num * 5)
            )
            
            print(f"📦 Order {order_num + 1}/{num_orders}: {order_id}")
            print(f"   Events: {len(events)} ({', '.join(e['event_type'] for e in events)})")
            
            # Inject edge cases
            main_events, late_arrivals = self.edge_case_injector.inject_edge_cases(events)
            all_late_arrivals.extend(late_arrivals)
            
            # Send main events
            for event in main_events:
                self.send_event(event, delay_seconds=SIMULATION_CONFIG['event_delay_seconds'])
            
            print()
        
        # Flush to ensure all messages are sent
        print("⏳ Flushing producer...")
        remaining = self.producer.flush(timeout=10)
        if remaining > 0:
            print(f"⚠️  Warning: {remaining} messages still in queue")
        
        # Send late arrivals after a delay
        if all_late_arrivals:
            print()
            print(f"⏰ Waiting {SIMULATION_CONFIG['late_arrival_delay_seconds']}s before sending {len(all_late_arrivals)} late arrivals...")
            time.sleep(SIMULATION_CONFIG['late_arrival_delay_seconds'])
            
            print(f"📨 Sending late arrivals...")
            for event in all_late_arrivals:
                self.send_event(event, delay_seconds=0.5)
            
            print("⏳ Flushing late arrivals...")
            self.producer.flush(timeout=10)
        
        print()
        print("=" * 80)
        print("✅ Simulation Complete!")
        print(f"   Delivered: {self.delivered_count}")
        print(f"   Failed: {self.failed_count}")
        print("=" * 80)


def main():
    """Main entry point"""
    try:
        producer = OrderProducer()
        producer.run_simulation()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

