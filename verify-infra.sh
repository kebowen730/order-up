#!/bin/bash
# Quick script to verify infrastructure is running correctly

set -e

echo "🔍 Verifying Order-Up Infrastructure..."
echo ""

# Check if Docker Compose services are running
echo "1️⃣  Checking Docker services..."
if ! docker compose ps | grep -q "kafka"; then
    echo "❌ Kafka is not running. Start with: docker compose up -d"
    exit 1
fi
echo "✅ Kafka is running"

if ! docker compose ps | grep -q "schema-registry"; then
    echo "❌ Schema Registry is not running"
    exit 1
fi
echo "✅ Schema Registry is running"

# Wait a moment for services to be fully ready
sleep 2

# Check Kafka connectivity
echo ""
echo "2️⃣  Checking Kafka connectivity..."
if docker exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092 > /dev/null 2>&1; then
    echo "✅ Kafka is accessible on localhost:9092"
else
    echo "❌ Cannot connect to Kafka"
    exit 1
fi

# Check Schema Registry
echo ""
echo "3️⃣  Checking Schema Registry..."
if curl -s http://localhost:8081/ > /dev/null; then
    echo "✅ Schema Registry is accessible on localhost:8081"
    SUBJECT_COUNT=$(curl -s http://localhost:8081/subjects | jq '. | length')
    echo "   📋 Registered schemas: $SUBJECT_COUNT"
else
    echo "❌ Cannot connect to Schema Registry"
    exit 1
fi

# List topics
echo ""
echo "4️⃣  Listing Kafka topics..."
TOPICS=$(docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list 2>/dev/null | grep -v "^$" | wc -l | tr -d ' ')
echo "   📋 Total topics: $TOPICS"

# Show Kafka UI info
echo ""
echo "5️⃣  Optional UI tools..."
if docker compose ps | grep -q "kafka-ui"; then
    echo "✅ Kafka UI available at http://localhost:8080"
else
    echo "ℹ️  Kafka UI not running"
fi

echo ""
echo "✅ All infrastructure checks passed!"
echo ""
echo "📚 Next steps:"
echo "   - Create Avro schemas in schemas/"
echo "   - Implement producer in producer-python/"
echo "   - Implement Kafka Streams engine in engine-streams-java/"
echo "   - Implement sink in sink-python/"

