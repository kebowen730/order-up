# Producer Output Examples

## Sample Order Lifecycle

### Happy Path Order

```
Order: order_0001

Timeline:
├─ ORDER_CREATED       [t=0]
│  payload: {customer_id, restaurant_id, initial_status: PENDING}
├─ ORDER_ITEM_ADDED    [t=12]
│  payload: {item_id, item_name: "Classic Burger", quantity: 2, price: 12.99}
├─ ORDER_ITEM_ADDED    [t=25]
│  payload: {item_id, item_name: "Caesar Salad", quantity: 1, price: 8.99}
├─ ORDER_CONFIRMED     [t=41]
│  payload: {confirmed_by, estimated_delivery_ts}
└─ ORDER_COMPLETED     [t=67]
   payload: {completed_ts, total_amount: 34.97}
```

### Message Structure (Avro)

```json
{
  "event_id": "a1b2c3d4-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
  "event_type": "ORDER_CREATED",
  "event_ts": 1641234567890,
  "order_id": "order_0001",
  "payload": {
    "com.orderup.events.OrderCreatedPayload": {
      "customer_id": "cust_abc123",
      "restaurant_id": "rest_xyz789",
      "initial_status": "PENDING"
    }
  },
  "schema_version": 1
}
```

## Edge Case Examples

### 1. Duplicate Event

```
Order: order_0003
  💥 DUPLICATE: event_id=e5f6g7h8...

Sent to Kafka:
Message 1: event_id=e5f6g7h8..., event_type=ORDER_ITEM_ADDED
Message 2: event_id=e5f6g7h8..., event_type=ORDER_ITEM_ADDED  ← Same!

Engine must: Deduplicate using event_id state store
```

### 2. Out-of-Order Events

```
Original Timeline:
1. ORDER_CREATED       [event_ts: 100]
2. ORDER_ITEM_ADDED    [event_ts: 115]
3. ORDER_CONFIRMED     [event_ts: 140]

Actual Kafka Order:
1. ORDER_CREATED       [event_ts: 100]  ← Correct
2. ORDER_CONFIRMED     [event_ts: 140]  ← Out of order!
3. ORDER_ITEM_ADDED    [event_ts: 115]  ← Late

Engine must: Use event_ts (not processing time) for ordering
```

### 3. Late Arrival

```
Order: order_0012
  ⏰ LATE ARRIVAL: event_id=q7r8s9t0...

Timeline:
t=0:    ORDER_CREATED sent
t=1:    ORDER_ITEM_ADDED sent
t=2:    ORDER_CONFIRMED sent
t=3:    ORDER_COMPLETED sent
t=8:    ORDER_UPDATED sent (5 seconds late!)

Engine must: Handle via watermarks and grace periods
```

## Order Patterns

1. **HAPPY_PATH** (50%): CREATE → ITEMS → CONFIRMED → COMPLETED
2. **EARLY_CANCEL** (15%): CREATE → ITEMS → CANCELLED
3. **LATE_CANCEL** (10%): CREATE → CONFIRMED → CANCELLED
4. **COMPLEX_ORDER** (15%): Multiple item adds/removes
5. **WITH_UPDATES** (10%): Status updates throughout

## Statistics (20 Orders)

```
Total Events:        ~100-120
Unique Events:       ~85-95
Duplicates:          ~15-20 (15%)
Out-of-Order:        4 orders (20%)
Late Arrivals:       ~10-12 (10%)

Event Types:
- ORDER_CREATED:      20
- ORDER_ITEM_ADDED:   40-50
- ORDER_CONFIRMED:    15-17
- ORDER_COMPLETED:    10-12
- ORDER_CANCELLED:    5-7
- ORDER_UPDATED:      2-3
- ORDER_ITEM_REMOVED: 2-5
```

## Kafka Topic Details

**Topic**: `orders.events.raw`  
**Partitioning**: By `order_id` (all events for same order → same partition)  
**Serialization**: Avro with Schema Registry  
**Retention**: Infinite (append-only log for audit trail)
