# Quick Start Guide

Get the producer running in 5 minutes.

## Prerequisites

- Docker installed and running
- Python 3.8+

## Step 1: Start Infrastructure (30 seconds)

```bash
cd /Users/kenneth/order-up
docker-compose up -d

# Wait for startup
sleep 30
```

## Step 2: Install Dependencies (30 seconds)

**Modern (uv - recommended):**
```bash
cd producer-python
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

**Legacy (pip):**
```bash
cd producer-python
pip install -r requirements.txt
```

## Step 3: Run Producer (2 minutes)

```bash
# With uv
uv run python producer.py

# Or with python
python producer.py
```

**Expected output:**
```
🚀 Order Event Producer
========================================
Kafka: localhost:9092
Topic: orders.events.raw
Orders: 20
Idempotent: True
========================================

📦 Order 1/20: order_0000
   Events: 5
  💥 DUPLICATE: event_id=abc123...

...

✅ Simulation Complete!
   Delivered: 112
   Failed: 0
```

## Step 4: Verify (30 seconds)

```bash
# Check messages
docker exec orderup-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic orders.events.raw \
  --from-beginning --max-messages 10

# Check schemas
curl http://localhost:8081/subjects
```

## Troubleshooting

**Connection refused?**
```bash
docker-compose ps  # Check status
docker-compose restart  # Restart if needed
```

**Schema file not found?**
```bash
cd /Users/kenneth/order-up/producer-python
```

**Module not found?**
```bash
uv sync  # or pip install -r requirements.txt
```

## Configuration

Edit `config.py`:
```python
SIMULATION_CONFIG = {
    'num_orders': 50,  # More orders
    'duplicate_probability': 0.30,  # More chaos
}
```

## Quick Commands

```bash
# Start everything
docker-compose up -d && cd producer-python && uv run python producer.py

# View logs
docker-compose logs -f

# Stop everything
docker-compose down
```

**You're ready to go!** 🚀
