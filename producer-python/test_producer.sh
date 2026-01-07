#!/bin/bash
# Quick test script for Producer

set -e

echo "🧪 Testing Producer"
echo "==================="
echo ""

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker is not running. Start Docker and run 'docker-compose up -d' first."
    exit 1
fi

# Check if Kafka is running
if ! docker ps | grep -q orderup-kafka; then
    echo "❌ Kafka is not running. Run 'docker-compose up -d' from project root."
    exit 1
fi

echo "✅ Docker and Kafka are running"
echo ""

# Check Python dependencies
echo "📦 Checking Python dependencies..."
if ! python3 -c "import confluent_kafka" 2>/dev/null; then
    echo "⚠️  Installing dependencies..."
    if command -v uv >/dev/null 2>&1; then
        echo "   Using uv (modern)..."
        uv sync
    else
        echo "   Using pip (legacy)..."
        pip install -r requirements.txt
    fi
else
    echo "✅ Dependencies installed"
fi
echo ""

# Check if schema exists
if [ ! -f "../schemas/order-event-raw.avsc" ]; then
    echo "❌ Schema file not found. Make sure you're in the producer-python directory."
    exit 1
fi
echo "✅ Schema file found"
echo ""

# Check Schema Registry
echo "🔍 Checking Schema Registry..."
if curl -s http://localhost:8081/subjects > /dev/null 2>&1; then
    echo "✅ Schema Registry is accessible"
else
    echo "❌ Schema Registry is not accessible at http://localhost:8081"
    exit 1
fi
echo ""

echo "🚀 Running producer..."
echo "=========================="
echo ""

if command -v uv >/dev/null 2>&1; then
    uv run python producer.py
else
    python3 producer.py
fi

echo ""
echo "=========================="
echo "✅ Producer test complete!"
echo ""
echo "Next steps:"
echo "  1. Check Kafka topic:"
echo "     docker exec orderup-kafka kafka-console-consumer \\"
echo "       --bootstrap-server localhost:9092 \\"
echo "       --topic orders.events.raw \\"
echo "       --from-beginning --max-messages 5"
echo ""
echo "  2. Check Schema Registry:"
echo "     curl http://localhost:8081/subjects"

