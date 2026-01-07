# Avro Schemas — Contracts & Compatibility

**Single source of truth** for all data contracts in the pipeline.

---

## Schema Files

### `order-event-raw.avsc`

Raw events on topic `orders.events.raw` (immutable, append-only).

**Key fields**:
- `event_id`: UUID for deduplication
- `event_type`: Enum (ORDER_CREATED, ORDER_UPDATED, ORDER_ITEM_ADDED, etc.)
- `event_ts`: Event timestamp (event time)
- `order_id`: Business key (Kafka message key)
- `payload`: Union of event-specific payloads
- `schema_version`: Schema evolution tracking

### `order-curated.avsc`

Curated orders on topic `orders.orders.curated`.

**🎯 This is the ENGINE CONTRACT** - both Kafka Streams and Flink must produce this exact shape.

**Key fields**:
- `order_id`: Primary key
- `customer_id`, `restaurant_id`: Dimension keys
- `order_status`: Current state (PENDING, CONFIRMED, CANCELLED, COMPLETED)
- `items`: Array of order items
- `total_amount`: Computed aggregate
- `created_at`, `updated_at`: Event time tracking
- `event_count`, `last_event_id`: Audit trail
- `processing_ts`: When engine emitted this

**Design**: Materialized view, Snowflake-ready, idempotent via `updated_at` + `order_id`.

---

## Why Schemas Are Engine-Agnostic

> **Avro schemas define behavior, not implementation.**

Both Kafka Streams and Flink can read/write Avro via Schema Registry. The engine is an implementation detail.

### What Changes When Swapping Engines?

| Component | Streams | Flink | Changes? |
|-----------|---------|-------|----------|
| Input topic | `orders.events.raw` | `orders.events.raw` | **Same** |
| Input schema | `order-event-raw.avsc` | `order-event-raw.avsc` | **Same** |
| Output topic | `orders.orders.curated` | `orders.orders.curated` | **Same** |
| Output schema | `order-curated.avsc` | `order-curated.avsc` | **Same** |
| Processing logic | KTable aggregation | KeyedStream state | Different |
| Producer/Sink | N/A | N/A | **No changes** |

**Both engines fulfill the same contract.**

---

## Schema Evolution & Compatibility

Using **FULL compatibility mode** (BACKWARD + FORWARD):
- ✅ Can add fields with defaults
- ✅ Can remove optional fields
- ❌ Cannot remove required fields
- ❌ Cannot change field types
- ❌ Cannot rename fields

### Evolution Example

**Safe**:
```json
{"name": "order_status", "type": "enum", "symbols": ["PENDING", "CONFIRMED", "IN_PROGRESS", "CANCELLED"]}
```
Adding enum values at the end = backward compatible.

**Unsafe**:
```json
{"name": "order_status", "type": "string"}
```
Changing type = breaking change.

---

## Best Practices

1. **Always add fields with defaults** - Makes schema backward compatible
2. **Use unions for optional fields** - `{"type": ["null", "long"], "default": null}`
3. **Document field semantics** - Event time vs processing time?
4. **Test compatibility before deploying** - Use Schema Registry check
5. **Never break the engine contract** - `order-curated.avsc` is sacred

---

## Testing Compatibility

```bash
# Test new schema
curl -X POST http://localhost:8081/compatibility/subjects/orders.orders.curated-value/versions/latest \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"schema": "..."}'

# Response:
# {"is_compatible": true}  ✅ Safe
# {"is_compatible": false} ❌ Breaking
```

---

**The foundation is set. Now we build on stable contracts.**
