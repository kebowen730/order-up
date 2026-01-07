# Avro Schemas — Contracts & Compatibility

## Purpose

**Single source of truth** for all data contracts in the pipeline.

These schemas define the interface between components and enable the engine swap strategy.

---

## Schema Files

### `order-event-raw.avsc`

Envelope schema for raw events on topic `orders.events.raw`.

**Type**: Immutable event log (append-only)

**Key fields**:
- `event_id`: UUID for deduplication
- `event_type`: Enum (ORDER_CREATED, ORDER_UPDATED, ORDER_ITEM_ADDED, etc.)
- `event_ts`: Event timestamp (event time, not ingestion time)
- `order_id`: Business key (used as Kafka message key)
- `payload`: Union of event-specific payloads
- `schema_version`: Schema evolution tracking

**Design choices**:
- **Union type payload**: Each event type has its own record shape
- **Event time first**: `event_ts` is the source of truth for time
- **Event ID for dedup**: Allows idempotent processing
- **Append-only**: Events are never updated or deleted

### `order-curated.avsc`

Output schema for curated orders on topic `orders.orders.curated`.

**🎯 This is the ENGINE CONTRACT** - both Kafka Streams and Flink must produce this exact shape.

**Key fields**:
- `order_id`: Primary key
- `customer_id`, `restaurant_id`: Dimension foreign keys
- `order_status`: Current state (PENDING, CONFIRMED, CANCELLED, COMPLETED)
- `items`: Array of order items
- `total_amount`: Computed aggregate
- `created_at`, `updated_at`: Event time tracking
- `event_count`: Number of events processed
- `last_event_id`: Most recent event (for dedup tracking)
- `processing_ts`: When the engine emitted this record

**Design choices**:
- **Materialized view**: Aggregated state from multiple events
- **Snowflake-ready**: Designed for direct consumption by warehouse
- **Idempotency support**: `updated_at` and `order_id` enable MERGE logic
- **Audit trail**: Includes event count and last event ID

---

## Why Schemas Are Engine-Agnostic

### The Key Insight

> **Avro schemas define behavior, not implementation.**

Both Kafka Streams and Flink can:
- Read Avro from Kafka ✅
- Deserialize using Schema Registry ✅
- Apply transformations ✅
- Serialize back to Avro ✅
- Write to Kafka ✅

**The engine is an implementation detail.**

### What Changes When Swapping Engines?

| Component | Streams | Flink | Notes |
|-----------|---------|-------|-------|
| Input topic | `orders.events.raw` | `orders.events.raw` | **Same** |
| Input schema | `order-event-raw.avsc` | `order-event-raw.avsc` | **Same** |
| Output topic | `orders.orders.curated` | `orders.orders.curated` | **Same** |
| Output schema | `order-curated.avsc` | `order-curated.avsc` | **Same** |
| Processing logic | KTable aggregation | KeyedStream state | **Different (but equivalent)** |
| State backend | RocksDB (Streams) | RocksDB (Flink) | **Different config, same tech** |
| Deployment | JAR on JVM | Flink cluster | **Different ops** |
| Producer code | N/A | N/A | **No changes** |
| Sink code | N/A | N/A | **No changes** |

### The Contract is the Schema

```
┌─────────────────────────────────────────┐
│  Producer (doesn't care about engine)  │
└──────────────┬──────────────────────────┘
               ▼
      orders.events.raw (Avro)
               │
               ├─────────────────────┐
               ▼                     ▼
        Kafka Streams           Flink Job
        (implements            (implements
         contract)              contract)
               │                     │
               └─────────┬───────────┘
                         ▼
             orders.orders.curated (Avro)
                         │
                         ▼
┌─────────────────────────────────────────┐
│   Sink (doesn't care about engine)     │
└─────────────────────────────────────────┘
```

**Both engines fulfill the same contract.**

---

## Schema Evolution & Compatibility

### Rules We Follow

Using Schema Registry's **FULL compatibility mode**:
- ✅ Can add fields with defaults
- ✅ Can remove optional fields
- ❌ Cannot remove required fields
- ❌ Cannot change field types
- ❌ Cannot rename fields

### Why FULL Compatibility?

**BACKWARD**: New schema can read old data
- Allows consumers to upgrade before producers

**FORWARD**: Old schema can read new data
- Allows producers to upgrade before consumers

**FULL = BACKWARD + FORWARD**
- Any component can upgrade independently

### Evolution Example

**v1 Schema** (current):
```json
{
  "name": "order_status",
  "type": {"type": "enum", "symbols": ["PENDING", "CONFIRMED", "CANCELLED", "COMPLETED"]}
}
```

**v2 Schema** (safe evolution):
```json
{
  "name": "order_status",
  "type": {"type": "enum", "symbols": ["PENDING", "CONFIRMED", "IN_PROGRESS", "CANCELLED", "COMPLETED"]}
}
```

Add new enum value at the end = backward compatible.

**v2 Schema** (unsafe evolution):
```json
{
  "name": "order_status",
  "type": "string"
}
```

Changing type = NOT compatible, would break existing consumers.

---

## Registering Schemas

Schemas are automatically registered by components on first use:

1. **Producer** registers `order-event-raw.avsc` on first publish
2. **Engine** reads from Schema Registry for deserialization
3. **Engine** registers `order-curated.avsc` on first output
4. **Sink** reads from Schema Registry for deserialization

### Manual Registration (Optional)

```bash
# Register raw event schema
curl -X POST http://localhost:8081/subjects/orders.events.raw-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d @- <<EOF
{
  "schema": $(cat order-event-raw.avsc | jq -c | jq -R)
}
EOF

# Register curated schema
curl -X POST http://localhost:8081/subjects/orders.orders.curated-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d @- <<EOF
{
  "schema": $(cat order-curated.avsc | jq -c | jq -R)
}
EOF
```

---

## Testing Compatibility

Before deploying a schema change:

```bash
# Test compatibility of new schema
curl -X POST http://localhost:8081/compatibility/subjects/orders.orders.curated-value/versions/latest \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"schema": "..."}'
```

Response:
- `{"is_compatible": true}` ✅ Safe to deploy
- `{"is_compatible": false}` ❌ Breaking change

---

## Why This Matters for Engine Swapping

### Traditional Approach (BAD)
```
Streams code → Custom serialization → Topic
                                       ↓
                                    Flink must reverse-engineer format
```

**Problem**: Flink team has to guess the schema from Streams code.

### Our Approach (GOOD)
```
Avro Schema (source of truth)
     ↓              ↓
  Streams        Flink
     ↓              ↓
  Both produce orders.orders.curated
```

**Solution**: Both engines implement the same contract.

### Real-World Impact

**Without stable schemas**:
- Engine swap requires rewriting producer AND sink
- No guarantee output will match
- Testing is a nightmare

**With stable schemas**:
- Engine swap changes one component
- Producer/sink unchanged
- Can run both engines in parallel for validation
- Schema Registry enforces compatibility at registration time

---

## Best Practices

1. **Always add fields with defaults**
   - Makes schema backward compatible
   - Old code can read new data

2. **Use unions for optional fields**
   ```json
   {"name": "estimated_delivery_ts", "type": ["null", "long"], "default": null}
   ```

3. **Document field semantics**
   - What does `updated_at` mean?
   - Event time or processing time?

4. **Version control schemas**
   - Git tag on schema changes
   - Reference version in `schema_version` field

5. **Test compatibility before deploying**
   - Use Schema Registry compatibility check
   - Run integration tests

6. **Never break the engine contract**
   - `order-curated.avsc` is sacred
   - Both Streams and Flink depend on it

---

## Files in This Directory

- `order-event-raw.avsc` - Raw event envelope (producer contract)
- `order-curated.avsc` - Curated output (engine contract)
- `README.md` - This file

---

## Next Steps

- ✅ Schemas defined
- 🔜 Implement Python producer using these schemas
- 🔜 Implement Kafka Streams engine honoring the contract
- 🔜 Implement Python sink consuming curated schema
- 🔜 (Later) Implement Flink engine with **identical output**

**The foundation is set. Now we build on stable contracts.**
