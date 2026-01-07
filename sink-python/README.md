# Sink (Python)

## Purpose

Consumes curated orders from `orders.orders.curated` and writes them to Snowflake.

## Responsibilities

- Consume from `orders.orders.curated`
- Deserialize Avro records
- Transform to Snowflake-compatible format
- Idempotent writes (MERGE/upsert) to fact table
- Optional: Archive raw events to S3/Iceberg

## Input Contract

**Topic**: `orders.orders.curated` (Avro)

**This is the engine contract** - expects same schema from any engine.

## Output Destinations

### Primary: Snowflake
- Table: `ORDERS.FACT_ORDERS`
- Write mode: MERGE (idempotent upsert)
- Keyed by: `order_id`

### Optional: S3/Iceberg
- Long-term archive of raw events
- Partitioned by date
- Queryable via Athena/Trino

## Idempotency

Critical for reliable pipeline:
- Use MERGE statement with `order_id` as key
- Include `updated_at` timestamp for conflict resolution
- Handle duplicates gracefully

## Dependencies

- `confluent-kafka[avro]` - Kafka consumer with Avro
- `snowflake-connector-python` - Snowflake writes
- `boto3` (optional) - S3 archive

## Configuration

- Consumer group: `snowflake-sink`
- Commit strategy: After successful write
- Batch size: Configurable (default 100 records)

## Coming Soon

- Snowflake connector implementation
- Idempotent MERGE logic
- Error handling and dead-letter queue
- Metrics and monitoring

