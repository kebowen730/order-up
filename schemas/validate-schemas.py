#!/usr/bin/env python3
"""
Validate Avro schemas against requirements.
"""

import json
import sys
from pathlib import Path

def check_field(schema, field_name, field_type=None):
    """Check if a field exists in schema, optionally validate type."""
    fields = schema.get('fields', [])
    for field in fields:
        if field['name'] == field_name:
            if field_type and field['type'] != field_type:
                return False, f"Field '{field_name}' has type {field['type']}, expected {field_type}"
            return True, f"✅ {field_name}"
    return False, f"❌ Missing field: {field_name}"

def validate_raw_event_schema(schema):
    """Validate order-event-raw.avsc against requirements."""
    print("\n📋 Validating order-event-raw.avsc")
    print("=" * 60)
    
    required_fields = ['event_id', 'event_type', 'event_ts', 'order_id', 'payload', 'schema_version']
    
    results = []
    for field_name in required_fields:
        success, msg = check_field(schema, field_name)
        results.append((success, msg))
        print(msg)
    
    # Check event_type is enum
    event_type_field = next((f for f in schema['fields'] if f['name'] == 'event_type'), None)
    if event_type_field and isinstance(event_type_field['type'], dict) and event_type_field['type'].get('type') == 'enum':
        print(f"✅ event_type is enum with {len(event_type_field['type']['symbols'])} symbols")
        results.append((True, "event_type enum"))
    else:
        print("❌ event_type is not an enum")
        results.append((False, "event_type enum"))
    
    # Check payload is union
    payload_field = next((f for f in schema['fields'] if f['name'] == 'payload'), None)
    if payload_field and isinstance(payload_field['type'], list):
        print(f"✅ payload is union with {len(payload_field['type'])} types")
        results.append((True, "payload union"))
    else:
        print("❌ payload is not a union")
        results.append((False, "payload union"))
    
    return all(r[0] for r in results)

def validate_curated_schema(schema):
    """Validate order-curated.avsc against requirements."""
    print("\n📋 Validating order-curated.avsc")
    print("=" * 60)
    
    required_fields = [
        'order_id',
        'customer_id',
        'restaurant_id',
        'order_status',
        'items',
        'total_amount',
        'created_at',
        'updated_at',
        'last_event_id',
        'processing_ts'
    ]
    
    results = []
    for field_name in required_fields:
        success, msg = check_field(schema, field_name)
        results.append((success, msg))
        print(msg)
    
    # Check items is array
    items_field = next((f for f in schema['fields'] if f['name'] == 'items'), None)
    if items_field and isinstance(items_field['type'], dict) and items_field['type'].get('type') == 'array':
        print(f"✅ items is array")
        results.append((True, "items array"))
    else:
        print("❌ items is not an array")
        results.append((False, "items array"))
    
    return all(r[0] for r in results)

def main():
    schemas_dir = Path(__file__).parent
    
    print("🔍 Schema Validation")
    print("=" * 60)
    
    # Load and validate raw event schema
    raw_event_file = schemas_dir / 'order-event-raw.avsc'
    try:
        with open(raw_event_file) as f:
            raw_schema = json.load(f)
        print(f"✅ Loaded {raw_event_file.name}")
        raw_valid = validate_raw_event_schema(raw_schema)
    except Exception as e:
        print(f"❌ Error loading {raw_event_file.name}: {e}")
        raw_valid = False
    
    # Load and validate curated schema
    curated_file = schemas_dir / 'order-curated.avsc'
    try:
        with open(curated_file) as f:
            curated_schema = json.load(f)
        print(f"✅ Loaded {curated_file.name}")
        curated_valid = validate_curated_schema(curated_schema)
    except Exception as e:
        print(f"❌ Error loading {curated_file.name}: {e}")
        curated_valid = False
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    if raw_valid:
        print("✅ order-event-raw.avsc: VALID")
    else:
        print("❌ order-event-raw.avsc: INVALID")
    
    if curated_valid:
        print("✅ order-curated.avsc: VALID")
    else:
        print("❌ order-curated.avsc: INVALID")
    
    # Check documentation
    readme_file = schemas_dir / 'README.md'
    if readme_file.exists():
        print("✅ README.md exists")
        with open(readme_file) as f:
            content = f.read()
            if "Compatibility" in content or "compatibility" in content:
                print("✅ README documents compatibility rules")
            else:
                print("❌ README missing compatibility documentation")
            
            if "engine-agnostic" in content or "Engine" in content:
                print("✅ README explains engine-agnostic design")
            else:
                print("❌ README missing engine-agnostic explanation")
    else:
        print("❌ README.md missing")
    
    print("=" * 60)
    
    if raw_valid and curated_valid:
        print("\n🎉 All schemas valid!")
        return 0
    else:
        print("\n⚠️  Some validations failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())

