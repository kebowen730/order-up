# Processing Engine: Kafka Streams (Java)

## Purpose

First implementation of the processing engine using Kafka Streams.

Transforms raw events from `orders.events.raw` into curated orders in `orders.orders.curated`.

## Responsibilities

- Consume from `orders.events.raw`
- Process events (aggregate, enrich, validate)
- Maintain order state in local RocksDB store
- Produce curated output to `orders.orders.curated`
- Handle late-arriving events using event time
- Exactly-once processing semantics

## Input Contract

**Topic**: `orders.events.raw` (Avro)

## Output Contract

**Topic**: `orders.orders.curated` (Avro)

**This is the engine contract** - Flink must produce the same output schema.

## Processing Logic

1. Deserialize Avro events
2. Group by order_id
3. Aggregate events into order state
4. Compute derived fields (e.g., total_amount, status)
5. Emit curated order records

## Configuration

- Application ID: `order-processing-streams`
- Exactly-once semantics enabled
- RocksDB state store
- Event-time processing with watermarks

## Why Kafka Streams First?

- ✅ Simple deployment (just a JAR)
- ✅ Built-in state management
- ✅ Exactly-once semantics
- ✅ Fast to implement
- ✅ Good enough for most use cases

**Later**: Swap to Flink for complex CEP, ML integration, or massive scale.

## Coming Soon

- Gradle build configuration
- Kafka Streams topology
- Unit tests with TopologyTestDriver
- Docker image for deployment

