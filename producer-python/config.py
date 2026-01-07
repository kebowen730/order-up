"""
Configuration for Order Producer
"""

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
SCHEMA_REGISTRY_URL = "http://localhost:8081"

# Topic Configuration
RAW_TOPIC = "orders.events.raw"

# Producer Configuration
PRODUCER_CONFIG = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'client.id': 'order-producer-python',
    # Idempotency settings
    'enable.idempotence': True,
    'acks': 'all',
    'retries': 2147483647,  # max retries
    'max.in.flight.requests.per.connection': 5,
}

# Simulation Configuration
SIMULATION_CONFIG = {
    # Number of unique orders to generate
    'num_orders': 20,
    
    # Probability of generating edge cases
    'duplicate_probability': 0.15,  # 15% chance to duplicate an event
    'out_of_order_probability': 0.20,  # 20% chance to send events out of order
    'late_arrival_probability': 0.10,  # 10% chance for late arrivals
    
    # Timing
    'event_delay_seconds': 1.0,  # Base delay between events
    'late_arrival_delay_seconds': 5.0,  # Additional delay for late arrivals
}

# Order Lifecycle Patterns
# Each pattern represents a different order journey
ORDER_PATTERNS = [
    # Happy path: created -> items added -> confirmed -> completed
    {
        'name': 'HAPPY_PATH',
        'weight': 0.5,
        'events': ['ORDER_CREATED', 'ORDER_ITEM_ADDED', 'ORDER_ITEM_ADDED', 'ORDER_CONFIRMED', 'ORDER_COMPLETED']
    },
    # Cancelled after creation
    {
        'name': 'EARLY_CANCEL',
        'weight': 0.15,
        'events': ['ORDER_CREATED', 'ORDER_ITEM_ADDED', 'ORDER_CANCELLED']
    },
    # Cancelled after confirmation
    {
        'name': 'LATE_CANCEL',
        'weight': 0.10,
        'events': ['ORDER_CREATED', 'ORDER_ITEM_ADDED', 'ORDER_CONFIRMED', 'ORDER_CANCELLED']
    },
    # Multiple item changes
    {
        'name': 'COMPLEX_ORDER',
        'weight': 0.15,
        'events': ['ORDER_CREATED', 'ORDER_ITEM_ADDED', 'ORDER_ITEM_ADDED', 'ORDER_ITEM_REMOVED', 
                   'ORDER_ITEM_ADDED', 'ORDER_CONFIRMED', 'ORDER_COMPLETED']
    },
    # Status updates
    {
        'name': 'WITH_UPDATES',
        'weight': 0.10,
        'events': ['ORDER_CREATED', 'ORDER_ITEM_ADDED', 'ORDER_UPDATED', 'ORDER_CONFIRMED', 'ORDER_COMPLETED']
    }
]

