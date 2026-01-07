# Producer (Python)

## Purpose

Generates order events and publishes them to Kafka topic `orders.events.raw`.

## Responsibilities

- Generate realistic order events (ORDER_CREATED, ORDER_UPDATED, ORDER_CANCELLED, etc.)
- Serialize events using Avro schema from Schema Registry
- Publish to `orders.events.raw` with proper partitioning (by order_id)
- Include event metadata (event_id, event_ts, schema_version)

## Output Contract

**Topic**: `orders.events.raw`

**Key**: `order_id` (string)

**Value**: Avro envelope with:
- `event_id`: UUID
- `event_type`: enum
- `event_ts`: timestamp (event time)
- `order_id`: string
- `payload`: union (varies by event type)
- `schema_version`: int

## Dependencies

- `confluent-kafka[avro]` - Kafka producer with Avro support
- `faker` - Generate realistic test data
- Schema Registry client

## Coming Soon

- Event generator with configurable rate
- Multiple event types (CREATE, UPDATE, CANCEL, COMPLETE)
- Realistic order lifecycle simulation

