# Producer (Python)

Generates order events and publishes to Kafka topic `orders.events.raw`.

## Key Features

- **Idempotent producer** (`enable.idempotence=True`)
- **Realistic order lifecycles** (5 patterns: happy path, cancellations, complex orders)
- **Edge case injection** (15% duplicates, 20% out-of-order, 10% late arrivals)
- **Avro serialization** via Schema Registry

## Output Contract

**Topic**: `orders.events.raw`  
**Key**: `order_id` (string)  
**Value**: Avro envelope with `event_id`, `event_type`, `event_ts`, `order_id`, `payload`, `schema_version`

## Usage

### Prerequisites
```bash
# From project root
docker-compose up -d
```

### Install & Run

**With uv (recommended):**
```bash
cd producer-python
uv sync
uv run python producer.py
```

**With pip:**
```bash
cd producer-python
pip install -r requirements.txt
python producer.py
```

## Configuration

Edit `config.py` to adjust:
- `num_orders` - Number of orders to generate (default: 20)
- `duplicate_probability` - Duplicate events (default: 0.15)
- `out_of_order_probability` - Shuffled events (default: 0.20)
- `late_arrival_probability` - Delayed events (default: 0.10)

## Architecture

```
producer.py
├── EventGenerator (event_generator.py)
│   └── Generates realistic order lifecycles
├── EdgeCaseInjector (edge_case_injector.py)
│   └── Injects duplicates, out-of-order, late arrivals
└── AvroSerializer
    └── Schema Registry integration
```

## Why Edge Cases?

The producer intentionally creates chaos to prove the downstream pipeline handles:
1. **Duplicates** → Engine must dedupe by `event_id`
2. **Out-of-order** → Engine must use `event_ts` for ordering
3. **Late arrivals** → Watermarks and windowing must handle lateness

## Modern Python Tooling

This project uses **uv** for dependency management (10-100x faster than pip).

See `README-UV.md` for details. Backwards compatible with pip via `requirements.txt`.
