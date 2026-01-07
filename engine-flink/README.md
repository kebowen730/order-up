# Processing Engine: Flink (Placeholder)

## Status

🚧 **Not yet implemented** - This is a placeholder for future Flink implementation.

## Purpose

Alternative implementation of the processing engine using Apache Flink.

Will implement **identical logic** to Kafka Streams but using Flink's DataStream API.

## Why Flink Later?

Flink is more complex to operate but offers advantages for:
- ✅ Complex event processing (CEP)
- ✅ ML model inference integration
- ✅ Advanced windowing (session, custom)
- ✅ Massive scale (billions of events/day)
- ✅ Savepoints for version upgrades
- ✅ Flink SQL for ad-hoc queries

## The Engine Swap

When implementing this:

1. **Same Input**: Read from `orders.events.raw`
2. **Same Output**: Write to `orders.orders.curated`
3. **Same Schema**: Use exact same Avro schemas
4. **Same Logic**: Replicate Streams behavior

The producer and sink **never know the difference**.

## Migration Strategy

1. Implement Flink job with identical topology
2. Run in shadow mode (write to test topic)
3. Compare output with Streams for 48h
4. Route 10% traffic to Flink
5. Full cutover after validation

## Coming Soon

- Flink job implementation (Scala or Java)
- State backend configuration (RocksDB)
- Checkpointing strategy
- Deployment on Flink cluster

