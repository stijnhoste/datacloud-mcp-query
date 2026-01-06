#!/usr/bin/env python3
"""
Test create, update, and delete operations on mca-next-sdo org.
Uses correct API JSON formats from Postman collection.
"""
import json
import time
from datetime import datetime

# Import from modular tools package
from tools.org import set_target_org
from tools.segments import create_segment, get_segment, update_segment, delete_segment
from tools.dlo_dmo import (
    create_data_lake_object, get_data_lake_object,
    create_data_model_object, get_data_model_object
)

# Generate unique test names
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
TEST_PREFIX = f"MCP_Test_{TIMESTAMP}"


def test_operation(name: str, func, *args, **kwargs):
    """Run a test and return the result."""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")

    try:
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start

        # Check for errors
        if isinstance(result, dict):
            if result.get("error"):
                print(f"FAIL [{duration:.2f}s]: {result.get('error')}")
                return None, "FAIL"
            if result.get("success") == False:
                print(f"FAIL [{duration:.2f}s]: {result.get('error', 'Unknown error')}")
                return None, "FAIL"

        print(f"PASS [{duration:.2f}s]")
        print(f"Result: {json.dumps(result, indent=2, default=str)[:1000]}...")
        return result, "PASS"
    except Exception as e:
        print(f"FAIL: {str(e)[:500]}")
        return None, "FAIL"


def main():
    print("=" * 70)
    print("DATA CLOUD MCP SERVER - CREATE OPERATIONS TEST")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Prefix: {TEST_PREFIX}")
    print("=" * 70)

    # Connect to org
    result = set_target_org("mca-next-sdo")
    print(f"Connected to org: {result}")

    results = {"PASS": 0, "FAIL": 0}

    # ==================== TEST SEGMENTS ====================
    print("\n" + "#" * 70)
    print("# SEGMENT TESTS")
    print("#" * 70)

    segment_name = f"MCPTest{TIMESTAMP.replace('_', '')}"

    # Create segment - using correct API format from Postman
    segment_definition = json.dumps({
        "developerName": segment_name,
        "displayName": f"MCP Test Segment {TIMESTAMP}",
        "description": "Test segment created by MCP test script",
        "dataSpace": "default",
        "segmentOnApiName": "ssot__Individual__dlm",
        "segmentType": "Standard",
        "publishSchedule": "Manual"
    })

    print(f"\nSegment Definition:\n{segment_definition}")

    segment_result, status = test_operation(
        "create_segment",
        create_segment,
        segment_definition
    )
    results[status] += 1

    # If segment was created, try to get, update, and delete it
    if segment_result and status == "PASS":
        created_segment_name = segment_result.get("developerName") or segment_result.get("name") or segment_name

        # Get segment
        _, status = test_operation("get_segment", get_segment, created_segment_name)
        results[status] += 1

        # Update segment
        update_def = json.dumps({"description": "Updated by MCP test script"})
        _, status = test_operation("update_segment", update_segment, created_segment_name, update_def)
        results[status] += 1

        # Delete segment (cleanup)
        _, status = test_operation("delete_segment", delete_segment, created_segment_name)
        results[status] += 1

    # ==================== TEST DATA LAKE OBJECTS ====================
    print("\n" + "#" * 70)
    print("# DATA LAKE OBJECT (DLO) TESTS")
    print("#" * 70)

    dlo_name = f"MCPTest{TIMESTAMP.replace('_', '')}DLO"

    # Create DLO - using correct API format from Postman
    dlo_definition = json.dumps({
        "name": dlo_name,
        "label": f"MCP Test DLO {TIMESTAMP}",
        "description": "Test DLO created by MCP test script",
        "dataSpaceName": "default",
        "category": "Other",
        "fields": [
            {
                "name": "Id__c",
                "label": "ID",
                "type": "Text",
                "isPrimaryKey": True
            },
            {
                "name": "Name__c",
                "label": "Name",
                "type": "Text"
            }
        ]
    })

    print(f"\nDLO Definition:\n{dlo_definition}")

    dlo_result, status = test_operation(
        "create_data_lake_object",
        create_data_lake_object,
        dlo_definition
    )
    results[status] += 1

    # If DLO was created, try to get it
    if dlo_result and status == "PASS":
        created_dlo_name = dlo_result.get("name") or dlo_result.get("developerName") or dlo_name
        _, status = test_operation("get_data_lake_object (after create)", get_data_lake_object, created_dlo_name)
        results[status] += 1

    # ==================== TEST DATA MODEL OBJECTS ====================
    print("\n" + "#" * 70)
    print("# DATA MODEL OBJECT (DMO) TESTS")
    print("#" * 70)

    dmo_name = f"MCPTest{TIMESTAMP.replace('_', '')}DMO"

    # Create DMO - using correct API format from Postman
    dmo_definition = json.dumps({
        "name": dmo_name,
        "label": f"MCP Test DMO {TIMESTAMP}",
        "description": "Test DMO created by MCP test script",
        "dataSpaceName": "default",
        "category": "Other",
        "type": "DataModelObject",
        "fields": [
            {
                "name": "Id__c",
                "label": "ID",
                "type": "Text",
                "isPrimaryKey": True
            },
            {
                "name": "Name__c",
                "label": "Name",
                "type": "Text"
            }
        ]
    })

    print(f"\nDMO Definition:\n{dmo_definition}")

    dmo_result, status = test_operation(
        "create_data_model_object",
        create_data_model_object,
        dmo_definition
    )
    results[status] += 1

    # If DMO was created, try to get it
    if dmo_result and status == "PASS":
        created_dmo_name = dmo_result.get("name") or dmo_result.get("developerName") or dmo_name
        _, status = test_operation("get_data_model_object (after create)", get_data_model_object, created_dmo_name)
        results[status] += 1

    # ==================== SUMMARY ====================
    print("\n" + "=" * 70)
    print("CREATE OPERATIONS TEST SUMMARY")
    print("=" * 70)
    print(f"PASS: {results['PASS']}")
    print(f"FAIL: {results['FAIL']}")
    print("=" * 70)

    return 0 if results['FAIL'] == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
