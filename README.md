# Order-Up 🚀

> **Kafka Streams first, Flink-ready by design**

A production-grade data pipeline where the **processing engine is a replaceable module**.

You are not "choosing Streams over Flink" — you are **deferring the engine choice** behind stable contracts.

---

## 🎯 The Core Idea

Build a pipeline where switching from Kafka Streams to Flink (or any other engine) requires **changing only one component**, not rewriting the entire system.

### Why This Matters

- **Start simple**: Kafka Streams for initial delivery
- **Scale when needed**: Swap to Flink for complex CEP, ML, or massive state
- **Minimize risk**: Same input/output contracts mean the rest of the pipeline is unaffected
- **Test both**: Run both engines simultaneously against the same data to validate behavior

---

## 🏗 Architecture

```
Python Producer
   ↓
Kafka: orders.events.raw (Avro, immutable)
   ↓
┌──────────────────────────────────────┐
│  Processing Engine (pluggable)      │
│  ├─ Kafka Streams (Java) ← Day 1    │
│  └─ Flink (later)                   │
└──────────────────────────────────────┘
   ↓
Kafka: orders.orders.curated (stable output schema)
   ↓
Python Sink
   ├─ Snowflake (fact table, idempotent)
   └─ Optional S3/Iceberg (raw archive)
```

### Key Design Rule

> **👉 Only the engine changes. Everything else stays the same.**

---

## 📐 Topic & Schema Strategy

### Raw Events (never rewritten)

**Topic**: `orders.events.raw`

**Schema** (Avro envelope):
```
event_id         : string (UUID)
event_type       : enum (ORDER_CREATED, ORDER_UPDATED, ...)
event_ts         : timestamp (event time)
order_id         : string (key)
payload          : union (nested record by event type)
schema_version   : int
```

- **Append-only forever**
- Immutable event log
- Complete audit trail

### Curated Output (engine contract)

**Topic**: `orders.orders.curated`

**Schema**: One row per order (or per order window)

- Designed for Snowflake consumption
- **This is the engine contract**
- Both Kafka Streams and Flink **must produce this exact shape**

---

## 📦 Repository Structure

```
order-up/
├── docker-compose.yml          # Kafka (KRaft) + Schema Registry
├── producer-python/            # Python event producer
├── engine-streams-java/        # Kafka Streams processor
├── engine-flink/               # Flink processor (placeholder)
├── sink-python/                # Python consumer → Snowflake
├── schemas/                    # Avro schemas (source of truth)
└── README.md                   # This file
```

---

## 🚀 Quick Start

### 1. Start Infrastructure

```bash
docker-compose up -d
```

This launches:
- **Kafka** (KRaft mode, no Zookeeper) on `localhost:9092`
- **Schema Registry** on `localhost:8081`
- **Kafka UI** on `localhost:8080` (optional, for debugging)

### 2. Verify Services

```bash
# Check Kafka
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --list

# Check Schema Registry
curl http://localhost:8081/subjects
```

### 3. Run Components

```bash
# Producer (generates events)
cd producer-python && python main.py

# Kafka Streams Engine
cd engine-streams-java && ./gradlew run

# Sink (to Snowflake)
cd sink-python && python main.py
```

---

## 🔄 Engine Swap Strategy

### Phase 1: Kafka Streams (Day 1)
- Implement Kafka Streams processor in Java
- Read from `orders.events.raw`
- Write to `orders.orders.curated`
- Validate end-to-end flow

### Phase 2: Flink (Later)
- Implement Flink job with **identical logic**
- Use **same input topic** (`orders.events.raw`)
- Use **same output topic** (`orders.orders.curated`)
- Use **same Avro schemas**

### Phase 3: Validation
- Run both engines in parallel
- Compare output for consistency
- Switch traffic when confident

### Phase 4: Cutover
- Replace Streams with Flink
- **Zero changes** to Producer or Sink
- Monitor and validate

---

## 🧪 Testing the Swap

Because the contract is stable, you can:

1. **Shadow Mode**: Run Flink alongside Streams, writing to different topic for comparison
2. **A/B Test**: Route 10% of traffic to Flink, 90% to Streams
3. **Full Cutover**: Replace Streams with Flink entirely

The producer and sink **never know the difference**.

---

## 📊 Monitoring

Each engine exposes metrics in its native format:
- **Kafka Streams**: JMX metrics
- **Flink**: Flink REST API + Prometheus

The pipeline itself is monitored via:
- Topic lag (consumer group lag)
- Schema evolution (Schema Registry compatibility)
- End-to-end latency (event_ts → sink write)

---

## 🎓 Design Principles

1. **Immutable Events**: Raw events are never updated or deleted
2. **Schema Evolution**: Use Avro with backward/forward compatibility
3. **Idempotent Sinks**: Snowflake writes use upsert/merge logic
4. **Event Time**: Processing based on `event_ts`, not ingestion time
5. **Exactly-Once Semantics**: Both engines configured for EOS
6. **Stable Contracts**: Input and output schemas are the API

---

## 🔮 Future Enhancements

- [ ] Add Flink implementation
- [ ] Implement S3/Iceberg archive sink
- [ ] Add dead-letter queue for malformed events
- [ ] Implement schema evolution testing
- [ ] Add metrics dashboard (Grafana)
- [ ] Kubernetes deployment manifests

---

## 📝 Notes

- **KRaft Mode**: Kafka runs without Zookeeper (production-ready as of Kafka 3.3+)
- **Schema Registry**: Stores Avro schemas for producer/consumer compatibility
- **Exactly-Once**: Requires transactional producers and consumers
- **Idempotency**: Essential for reliable pipeline behavior

---

## 📚 Resources

- [Kafka Streams Documentation](https://kafka.apache.org/documentation/streams/)
- [Apache Flink Documentation](https://flink.apache.org/)
- [Avro Schema Evolution](https://docs.confluent.io/platform/current/schema-registry/avro.html)
- [Snowflake COPY INTO](https://docs.snowflake.com/en/sql-reference/sql/copy-into-table.html)

---

**Built with ❤️ for pluggable, production-grade streaming pipelines**

