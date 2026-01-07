#!/usr/bin/env python3
"""
Comprehensive test script for Data Cloud MCP tools.
Runs ALL tests including mutating operations - no skips allowed.
Uses parallel execution for faster results.
"""
import json
import sys
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Import ALL tools from modular tools package
from tools.org import list_orgs, set_target_org, get_target_org
from tools.query import query, list_tables, describe_table, validate_query, format_sql, cancel_sql_query
from tools.metadata import (
    get_metadata, describe_table_full, get_relationships, explore_table, search_tables
)
from tools.profile import (
    get_profile_metadata, query_profile, get_profile_record,
    get_profile_record_with_children, get_profile_record_with_insights
)
from tools.insights import (
    list_calculated_insights, get_calculated_insight, query_calculated_insight,
    get_insight_metadata, create_calculated_insight, update_calculated_insight,
    delete_calculated_insight, run_calculated_insight
)
from tools.graphs import (
    list_data_graphs, get_data_graph, query_data_graph,
    create_data_graph, delete_data_graph, refresh_data_graph
)
from tools.identity import (
    lookup_unified_id, list_identity_rulesets, get_identity_ruleset,
    create_identity_ruleset, update_identity_ruleset, delete_identity_ruleset,
    run_identity_resolution
)
from tools.segments import (
    list_segments, get_segment, get_segment_members, count_segment,
    create_segment, update_segment, delete_segment, publish_segment, deactivate_segment
)
from tools.activations import (
    list_activations, get_activation, get_audience_records, list_activation_targets,
    get_activation_target, create_activation_target, update_activation_target,
    create_activation, update_activation, delete_activation, list_activation_external_platforms
)
from tools.streams import (
    list_data_streams, get_data_stream, run_data_stream,
    create_data_stream, update_data_stream, delete_data_stream
)
from tools.transforms import (
    list_data_transforms, get_data_transform, get_transform_run_history, run_data_transform,
    create_data_transform, update_data_transform, delete_data_transform,
    cancel_data_transform, retry_data_transform, get_transform_schedule,
    update_transform_schedule, validate_data_transform
)
from tools.connections import (
    list_connections, get_connection, get_connection_objects, preview_connection, list_connectors,
    get_connector, create_connection, update_connection, delete_connection,
    get_connection_schema, get_connection_endpoints, get_connection_databases,
    get_connection_database_schemas
)
from tools.dlo_dmo import (
    list_data_lake_objects, get_data_lake_object, create_data_lake_object,
    update_data_lake_object, delete_data_lake_object,
    list_data_model_objects, get_data_model_object, get_dmo_mappings, create_data_model_object,
    update_data_model_object, delete_data_model_object,
    create_dmo_mapping, delete_dmo_mapping, get_dmo_relationships,
    create_dmo_relationship, delete_dmo_relationship
)
from tools.dataspaces import (
    list_data_spaces, get_data_space, get_data_space_members,
    create_data_space, update_data_space, update_data_space_members, get_data_space_member
)
from tools.ml import (
    list_ml_models, get_ml_model, get_prediction, list_model_artifacts,
    get_model_artifact, update_ml_model, delete_ml_model, update_model_artifact, delete_model_artifact,
    list_document_ai_configs, get_document_ai_config, create_document_ai_config,
    update_document_ai_config, delete_document_ai_config, extract_document_data,
    run_document_ai, generate_document_schema, get_document_ai_global_config,
    list_semantic_searches, get_semantic_search, get_semantic_search_config,
    create_semantic_search, update_semantic_search, delete_semantic_search
)
from tools.admin import (
    get_limits, list_data_actions, list_data_action_targets,
    list_private_network_routes, get_data_kit_status,
    get_data_action_target, create_data_action, create_data_action_target,
    delete_data_action_target, get_data_action_target_signing_key,
    get_private_network_route, create_private_network_route, delete_private_network_route,
    undeploy_data_kit, get_data_kit_component_dependencies, get_data_kit_deployment_status
)


class TestResults:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self._lock = threading.Lock()

    def add(self, name: str, status: str, message: str = "", duration: float = 0):
        with self._lock:
            self.results.append({
                "name": name,
                "status": status,
                "message": message[:200] if message else "",
                "duration": round(duration, 2)
            })
            if status == "PASS":
                self.passed += 1
            elif status == "FAIL":
                self.failed += 1
            else:
                self.skipped += 1
            # Print progress immediately
            symbol = "✓" if status == "PASS" else "✗" if status == "FAIL" else "○"
            print(f"  {symbol} {name} [{round(duration, 1)}s]")

    def print_summary(self):
        print("\n" + "=" * 70)
        print("TEST RESULTS SUMMARY")
        print("=" * 70)

        # Group by status
        for status in ["PASS", "FAIL", "SKIP"]:
            items = [r for r in self.results if r["status"] == status]
            if items:
                print(f"\n{status} ({len(items)}):")
                for r in items:
                    msg = f" - {r['message']}" if r['message'] else ""
                    dur = f" [{r['duration']}s]" if r['duration'] > 0 else ""
                    print(f"  - {r['name']}{dur}{msg}")

        print("\n" + "-" * 70)
        print(f"TOTAL: {len(self.results)} | PASS: {self.passed} | FAIL: {self.failed} | SKIP: {self.skipped}")
        print("=" * 70)


def test_tool(results: TestResults, name: str, func, *args, **kwargs):
    """Run a tool test and record results."""
    skip_errors = kwargs.pop("skip_errors", None)
    start = time.time()
    try:
        result = func(*args, **kwargs)
        duration = time.time() - start

        # Check for error in result
        if isinstance(result, dict) and result.get("error"):
            message = str(result.get("error"))
            if skip_errors and any(token in message for token in skip_errors):
                results.add(name, "SKIP", message, duration)
            else:
                results.add(name, "FAIL", message, duration)
        elif isinstance(result, dict) and result.get("success") == False:
            message = str(result.get("error", "Unknown error"))
            if skip_errors and any(token in message for token in skip_errors):
                results.add(name, "SKIP", message, duration)
            else:
                results.add(name, "FAIL", message, duration)
        else:
            # Summarize result
            if isinstance(result, list):
                msg = f"Returned {len(result)} items"
            elif isinstance(result, dict):
                keys = list(result.keys())[:3]
                msg = f"Keys: {keys}"
            elif isinstance(result, str):
                msg = f"Returned string ({len(result)} chars)"
            else:
                msg = str(type(result).__name__)
            results.add(name, "PASS", msg, duration)
        return result
    except Exception as e:
        duration = time.time() - start
        message = str(e)[:200]
        if skip_errors and any(token in message for token in skip_errors):
            results.add(name, "SKIP", message, duration)
        else:
            results.add(name, "FAIL", message, duration)
        return None


def skip_test(results: TestResults, name: str, message: str):
    """Record a skipped test with a short reason."""
    results.add(name, "SKIP", message)


def run_parallel(results: TestResults, tests: list, max_workers: int = 10):
    """Run a list of tests in parallel. Each test is (name, func, args...)."""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for test in tests:
            name = test[0]
            func = test[1]
            args = test[2:] if len(test) > 2 else ()
            future = executor.submit(test_tool, results, name, func, *args)
            futures[future] = name

        # Wait for all to complete
        results_map = {}
        for future in as_completed(futures):
            name = futures[future]
            try:
                results_map[name] = future.result()
            except Exception as e:
                results_map[name] = None
        return results_map


def main():
    print("=" * 70)
    print("DATA CLOUD MCP SERVER - COMPREHENSIVE TOOL TEST")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Target Org: mca-next-sdo")
    print("Mode: ALL TESTS (no skips)")
    print("=" * 70)

    results = TestResults()
    test_prefix = f"MCPTest{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # ========== 1. ORG MANAGEMENT ==========
    print("\n[1/20] Testing Org Management tools...")

    test_tool(results, "list_orgs", list_orgs)
    test_tool(results, "set_target_org", set_target_org, "mca-next-sdo")
    test_tool(results, "get_target_org", get_target_org)

    # ========== 2. QUERY & SQL ==========
    print("[2/20] Testing Query & SQL tools...")

    tables_result = test_tool(results, "list_tables", list_tables)

    # Get a table for further tests
    test_table = None
    if tables_result and len(tables_result) > 0:
        for t in tables_result:
            if "Individual" in t or "Account" in t:
                test_table = t
                break
        if not test_table:
            test_table = tables_result[0]

    describe_result = None
    if test_table:
        describe_result = test_tool(results, "describe_table", describe_table, test_table)
        test_tool(results, "query", query, f'SELECT * FROM "{test_table}" LIMIT 5')
    else:
        describe_result = test_tool(results, "describe_table", describe_table, "ssot__Individual__dlm")
        test_tool(results, "query", query, 'SELECT * FROM "ssot__Individual__dlm" LIMIT 5')

    test_tool(results, "validate_query", validate_query, "SELECT * FROM test", False)
    test_tool(results, "format_sql", format_sql, "select * from test where id=1")
    # cancel_sql_query requires an active query ID - test with dummy
    test_tool(results, "cancel_sql_query", cancel_sql_query, "dummy-query-id")

    # ========== 3. METADATA ==========
    print("[3/20] Testing Metadata tools...")

    if test_table:
        test_tool(results, "get_metadata", get_metadata, test_table)
    else:
        test_tool(results, "get_metadata", get_metadata, "ssot__Individual__dlm")

    if test_table:
        test_tool(results, "describe_table_full", describe_table_full, test_table)
        test_tool(results, "get_relationships", get_relationships, test_table)
        test_tool(results, "explore_table", explore_table, test_table, 3)
    else:
        test_tool(results, "describe_table_full", describe_table_full, "ssot__Individual__dlm")
        test_tool(results, "get_relationships", get_relationships, "ssot__Individual__dlm")
        test_tool(results, "explore_table", explore_table, "ssot__Individual__dlm", 3)

    test_tool(results, "search_tables", search_tables, "Individual")

    # ========== 4. PROFILE ==========
    print("[4/20] Testing Profile tools...")

    profile_dmo = "Individual__dlm"
    test_tool(
        results,
        "get_profile_metadata",
        get_profile_metadata,
        profile_dmo
    )
    test_tool(
        results,
        "query_profile",
        query_profile,
        profile_dmo,
        1,
        0
    )

    profile_record_id = None
    id_field = None
    if isinstance(describe_result, list):
        for candidate in describe_result:
            candidate_lower = candidate.lower()
            if candidate_lower.endswith("__id__c") or candidate_lower.endswith("id"):
                id_field = candidate
                break

    if test_table and id_field:
        try:
            seed_result = query(
                f'SELECT "{id_field}" FROM "{test_table}" WHERE "{id_field}" IS NOT NULL LIMIT 1'
            )
            seed_rows = seed_result.get("data") if isinstance(seed_result, dict) else None
            if seed_rows and seed_rows[0]:
                profile_record_id = seed_rows[0][0]
        except Exception:
            profile_record_id = None

    if profile_record_id:
        test_tool(
            results,
            "get_profile_record",
            get_profile_record,
            profile_dmo,
            profile_record_id)
        test_tool(
            results,
            "get_profile_record_with_children",
            get_profile_record_with_children,
            profile_dmo,
            profile_record_id,
            "ContactPointEmail__dlm")
    else:
        # Test with dummy data - no skipping
        test_tool(results, "get_profile_record", get_profile_record, "ssot__Individual__dlm", "DummyRecordId")
        test_tool(results, "get_profile_record_with_children", get_profile_record_with_children, "ssot__Individual__dlm", "DummyRecordId", "ContactPointEmail__dlm")
        test_tool(results, "get_profile_record_with_insights", get_profile_record_with_insights, "ssot__Individual__dlm", "DummyRecordId", "Customer_Lifetime_Value__cio")

    # ========== 5. SEGMENTS ==========
    print("[5/20] Testing Segments tools...")

    segments_result = test_tool(results, "list_segments", list_segments)

    # Find a segment for further tests
    test_segment = None
    if segments_result and isinstance(segments_result, dict):
        segments_list = segments_result.get("segments", [])
        if segments_list:
            test_segment = (
                segments_list[0].get("apiName")
                or segments_list[0].get("developerName")
                or segments_list[0].get("name")
            )

    if test_segment:
        test_tool(results, "get_segment", get_segment, test_segment)
        test_tool(results, "get_segment_members", get_segment_members, test_segment, 5, 0)
        test_tool(
            results,
            "count_segment",
            count_segment,
            test_segment)
    else:
        # Test with dummy data - no skipping
        test_tool(results, "get_segment", get_segment, "DummySegment")
        test_tool(results, "get_segment_members", get_segment_members, "DummySegment", 5, 0)
        test_tool(results, "count_segment", count_segment, "DummySegment")

    # Test segment CRUD operations - Dbt type requires complex includeDbt.models structure
    # Postman shows "includeDbt": {} but this gives "Provide a non null sql value"
    # The exact SQL model structure is undocumented - CREATE will fail
    segment_name = f"{test_prefix}Segment"
    test_segment_def = json.dumps({
        "developerName": segment_name,
        "displayName": f"{test_prefix} Segment",
        "segmentOnApiName": "UnifiedIndividual__dlm",
        "segmentType": "Dbt",
        "includeDbt": {}
    })
    created_segment = test_tool(results, "create_segment", create_segment, test_segment_def)
    created_segment_name = None
    if isinstance(created_segment, dict):
        created_segment_name = (
            created_segment.get("developerName")
            or created_segment.get("apiName")
            or created_segment.get("name")
        )

    if created_segment_name:
        test_tool(
            results,
            "update_segment",
            update_segment,
            created_segment_name,
            json.dumps({"description": "Updated by test_all_tools"})
        )
        test_tool(results, "publish_segment", publish_segment, created_segment_name)
        test_tool(results, "deactivate_segment", deactivate_segment, created_segment_name)
        test_tool(results, "delete_segment", delete_segment, created_segment_name)
    else:
        # Test with dummy data - no skipping
        test_tool(results, "update_segment", update_segment, "DummySegment", json.dumps({"description": "Updated"}))
        test_tool(results, "publish_segment", publish_segment, "DummySegment")
        test_tool(results, "deactivate_segment", deactivate_segment, "DummySegment")
        test_tool(results, "delete_segment", delete_segment, "DummySegment")

    # ========== 6. ACTIVATIONS ==========
    print("[6/20] Testing Activations tools...")

    activations_result = test_tool(results, "list_activations", list_activations)
    targets_list_result = test_tool(results, "list_activation_targets", list_activation_targets)
    test_tool(
        results,
        "list_activation_external_platforms",
        list_activation_external_platforms
    )

    # Find an activation for further tests
    test_activation = None
    if activations_result and isinstance(activations_result, dict):
        activations_list = activations_result.get("activations", [])
        if activations_list:
            test_activation = activations_list[0].get("id") or activations_list[0].get("activationId")

    if test_activation:
        test_tool(results, "get_activation", get_activation, test_activation)
        test_tool(results, "get_audience_records", get_audience_records, test_activation, 5, 0)
    else:
        # Test with dummy data - no skipping
        test_tool(results, "get_activation", get_activation, "DummyActivationId")
        test_tool(results, "get_audience_records", get_audience_records, "DummyActivationId", 5, 0)

    # Activation target operations
    test_target = None
    if targets_list_result and isinstance(targets_list_result, dict):
        targets_list = targets_list_result.get("activationTargets", [])
        if targets_list:
            test_target = targets_list[0].get("id") or targets_list[0].get("name")

    if test_target:
        test_tool(results, "get_activation_target", get_activation_target, test_target)
    else:
        # Test with dummy data - no skipping
        test_tool(results, "get_activation_target", get_activation_target, "DummyTargetId")

    # Activation/target CRUD - uses name and platformType (not apiName, type, or label)
    # Note: platformType must be a configured external platform in the org
    activation_target_name = f"{test_prefix}Target"
    test_activation_target_def = json.dumps({
        "name": activation_target_name,
        "platformType": "S3"  # May fail if platform not configured
    })
    created_target = test_tool(results, "create_activation_target", create_activation_target, test_activation_target_def)
    created_target_name = None
    if isinstance(created_target, dict):
        created_target_name = created_target.get("name") or created_target.get("apiName")

    if created_target_name:
        test_tool(results, "update_activation_target", update_activation_target, created_target_name, json.dumps({"description": "Updated"}))
    else:
        test_tool(results, "update_activation_target", update_activation_target, "DummyTarget", json.dumps({"description": "Updated"}))

    # Activation CRUD - requires complex nested schema:
    # - activationTargetSubjectConfig with queryPathConfig
    # - attributesConfig array with deeply nested attributes
    # Schema is complex and undocumented - CREATE will fail with partial config
    activation_name = f"{test_prefix}Activation"
    test_activation_def = json.dumps({
        "name": activation_name,
        "activationTargetName": created_target_name or "DummyTarget",
        "segmentApiName": test_segment or "Non_Prescription_Eyewear_Buyers",
        "dataSpaceName": "default",
        "refreshType": "FULL_REFRESH",
        "activationTargetSubjectConfig": {
            "developerName": "UnifiedIndividual__dlm"
        }
    })
    created_activation = test_tool(results, "create_activation", create_activation, test_activation_def)
    created_activation_id = None
    if isinstance(created_activation, dict):
        created_activation_id = created_activation.get("id") or created_activation.get("activationId")

    if created_activation_id:
        test_tool(results, "update_activation", update_activation, created_activation_id, json.dumps({"description": "Updated"}))
        test_tool(results, "delete_activation", delete_activation, created_activation_id)
    else:
        test_tool(results, "update_activation", update_activation, "DummyActivation", json.dumps({"description": "Updated"}))
        test_tool(results, "delete_activation", delete_activation, "DummyActivation")

    # ========== 7. DATA STREAMS ==========
    print("[7/20] Testing Data Streams tools...")

    streams_result = test_tool(results, "list_data_streams", list_data_streams)

    test_stream = None
    if streams_result and isinstance(streams_result, dict):
        streams_list = streams_result.get("dataStreams", streams_result.get("data", []))
        if streams_list:
            test_stream = streams_list[0].get("name") or streams_list[0].get("dataStreamName")

    if test_stream:
        test_tool(results, "get_data_stream", get_data_stream, test_stream)
        test_tool(
            results,
            "run_data_stream",
            run_data_stream,
            test_stream)
    else:
        # Test with dummy data - no skipping
        test_tool(results, "get_data_stream", get_data_stream, "DummyStream")
        test_tool(results, "run_data_stream", run_data_stream, "DummyStream")

    # Stream CRUD - uses name/label (not developerName/displayName)
    stream_name = f"{test_prefix}Stream"
    test_stream_def = json.dumps({
        "name": stream_name,
        "label": f"{test_prefix} Stream",
        "dataSource": "Salesforce_Home",
        "sourceObjectName": "Account"
    })
    created_stream = test_tool(results, "create_data_stream", create_data_stream, test_stream_def)
    created_stream_name = None
    if isinstance(created_stream, dict):
        created_stream_name = created_stream.get("name") or created_stream.get("dataStreamName")

    if created_stream_name:
        test_tool(results, "update_data_stream", update_data_stream, created_stream_name, json.dumps({"label": "Updated Stream"}))
        test_tool(results, "delete_data_stream", delete_data_stream, created_stream_name)
    else:
        test_tool(results, "update_data_stream", update_data_stream, "DummyStream", json.dumps({"label": "Updated Stream"}))
        test_tool(results, "delete_data_stream", delete_data_stream, "DummyStream")

    # ========== 8. DATA TRANSFORMS ==========
    print("[8/20] Testing Data Transforms tools...")

    transforms_result = test_tool(results, "list_data_transforms", list_data_transforms)

    test_transform = None
    if transforms_result and isinstance(transforms_result, dict):
        transforms_list = transforms_result.get("dataTransforms", transforms_result.get("data", []))
        if transforms_list:
            test_transform = transforms_list[0].get("name") or transforms_list[0].get("transformName")

    if test_transform:
        test_tool(results, "get_data_transform", get_data_transform, test_transform)
        test_tool(results, "get_transform_run_history", get_transform_run_history, test_transform)
        test_tool(
            results,
            "run_data_transform",
            run_data_transform,
            test_transform)
        test_tool(results, "get_transform_schedule", get_transform_schedule, test_transform)
        test_tool(
            results,
            "cancel_data_transform",
            cancel_data_transform,
            test_transform)
        test_tool(
            results,
            "retry_data_transform",
            retry_data_transform,
            test_transform)
    else:
        # Test with dummy data - no skipping
        test_tool(results, "get_data_transform", get_data_transform, "DummyTransform")
        test_tool(results, "get_transform_run_history", get_transform_run_history, "DummyTransform")
        test_tool(results, "run_data_transform", run_data_transform, "DummyTransform")
        test_tool(results, "get_transform_schedule", get_transform_schedule, "DummyTransform")
        test_tool(results, "cancel_data_transform", cancel_data_transform, "DummyTransform")
        test_tool(results, "retry_data_transform", retry_data_transform, "DummyTransform")

    # Transform CRUD - requires definition field with nodes structure
    # Note: The API requires a specific 'type' property for polymorphic deserialization
    # The exact type value is undocumented; testing shows "BATCH" on outer level works
    transform_name = f"{test_prefix}Transform"
    test_transform_def = json.dumps({
        "name": transform_name,
        "label": f"{test_prefix} Transform",
        "type": "BATCH",
        "definition": {
            "nodes": {
                "LOAD_DATASET0": {
                    "action": "load",
                    "type": "DataModelObjectSourceNode",
                    "parameters": {
                        "dataset": {"name": "ssot__Individual__dlm", "type": "dataModelObject"},
                        "fields": ["ssot__Id__c"]
                    },
                    "sources": []
                }
            }
        }
    })
    test_tool(results, "validate_data_transform", validate_data_transform, test_transform_def)
    created_transform = test_tool(results, "create_data_transform", create_data_transform, test_transform_def)
    created_transform_name = None
    if isinstance(created_transform, dict):
        created_transform_name = created_transform.get("name") or created_transform.get("transformName")

    if created_transform_name:
        test_tool(results, "update_data_transform", update_data_transform, created_transform_name, json.dumps({"description": "Updated"}))
        test_tool(results, "update_transform_schedule", update_transform_schedule, created_transform_name, json.dumps({"frequency": "Daily"}))
        test_tool(results, "delete_data_transform", delete_data_transform, created_transform_name)
    else:
        test_tool(results, "update_data_transform", update_data_transform, "DummyTransform", json.dumps({"description": "Updated"}))
        test_tool(results, "update_transform_schedule", update_transform_schedule, "DummyTransform", json.dumps({"frequency": "Daily"}))
        test_tool(results, "delete_data_transform", delete_data_transform, "DummyTransform")

    # ========== 9. CONNECTIONS ==========
    print("[9/20] Testing Connections tools...")

    connectors_result = test_tool(results, "list_connectors", list_connectors)

    # Get a connector type from list if available, otherwise use SalesforceDotCom
    test_connector_type = "SalesforceDotCom"
    if connectors_result and isinstance(connectors_result, dict):
        connectors_list = connectors_result.get("connectors", [])
        if connectors_list:
            test_connector_type = connectors_list[0].get("connectorType") or connectors_list[0].get("name") or "SalesforceDotCom"

    test_tool(results, "get_connector", get_connector, test_connector_type)
    connections_result = test_tool(results, "list_connections", list_connections, test_connector_type)

    test_connection = None
    if connections_result and isinstance(connections_result, dict):
        connections_list = connections_result.get("connections", connections_result.get("data", []))
        if connections_list:
            test_connection = connections_list[0].get("id") or connections_list[0].get("name")

    if test_connection:
        test_tool(results, "get_connection", get_connection, test_connection)
        conn_objects = test_tool(results, "get_connection_objects", get_connection_objects, test_connection)
        test_tool(results, "get_connection_schema", get_connection_schema, test_connection)
        test_tool(results, "get_connection_endpoints", get_connection_endpoints, test_connection)
        test_tool(results, "get_connection_databases", get_connection_databases, test_connection)
        test_tool(results, "get_connection_database_schemas", get_connection_database_schemas, test_connection)

        # Try preview
        test_object = None
        if conn_objects and isinstance(conn_objects, dict):
            objects_list = conn_objects.get("objects", [])
            if objects_list:
                test_object = objects_list[0].get("name")

        if test_object:
            test_tool(results, "preview_connection", preview_connection, test_connection, test_object, 3)
        else:
            # Test with dummy data - no skipping
            test_tool(results, "preview_connection", preview_connection, test_connection, "DummyObject", 3)
    else:
        # Test with dummy data - no skipping
        test_tool(results, "get_connection", get_connection, "DummyConnection")
        test_tool(results, "get_connection_objects", get_connection_objects, "DummyConnection")
        test_tool(results, "get_connection_schema", get_connection_schema, "DummyConnection")
        test_tool(results, "get_connection_endpoints", get_connection_endpoints, "DummyConnection")
        test_tool(results, "get_connection_databases", get_connection_databases, "DummyConnection")
        test_tool(results, "get_connection_database_schemas", get_connection_database_schemas, "DummyConnection")
        test_tool(results, "preview_connection", preview_connection, "DummyConnection", "DummyObject", 3)

    # Connection CRUD - minimal payload (only 6 known properties)
    connection_name = f"{test_prefix}Connection"
    test_connection_def = json.dumps({
        "label": f"{test_prefix} Connection",
        "connectorType": "AmazonS3"
    })
    created_connection = test_tool(results, "create_connection", create_connection, test_connection_def)
    created_connection_id = None
    if isinstance(created_connection, dict):
        created_connection_id = created_connection.get("id") or created_connection.get("name")

    if created_connection_id:
        test_tool(results, "update_connection", update_connection, created_connection_id, json.dumps({"description": "Updated"}))
        test_tool(results, "delete_connection", delete_connection, created_connection_id)
    else:
        test_tool(results, "update_connection", update_connection, "DummyConnection", json.dumps({"description": "Updated"}))
        test_tool(results, "delete_connection", delete_connection, "DummyConnection")

    # ========== 10. DATA LAKE OBJECTS ==========
    print("[10/20] Testing Data Lake Objects tools...")

    dlo_result = test_tool(results, "list_data_lake_objects", list_data_lake_objects)

    test_dlo = None
    if dlo_result and isinstance(dlo_result, dict):
        dlo_list = dlo_result.get("dataLakeObjects", dlo_result.get("data", []))
        if dlo_list:
            test_dlo = dlo_list[0].get("name") or dlo_list[0].get("objectName")

    if test_dlo:
        test_tool(results, "get_data_lake_object", get_data_lake_object, test_dlo)
    else:
        # Test with dummy data - no skipping
        test_tool(results, "get_data_lake_object", get_data_lake_object, "DummyDLO")

    # DLO CRUD - no dataspace field needed (defaults to default dataspace)
    dlo_name = f"{test_prefix}DLO"
    test_dlo_def = json.dumps({
        "name": dlo_name,
        "label": f"{test_prefix} DLO",
        "category": "Other",
        "fields": [
            {"name": "Id__c", "label": "ID", "dataType": "Text", "isPrimaryKey": True},
            {"name": "Name__c", "label": "Name", "dataType": "Text"}
        ]
    })
    created_dlo = test_tool(results, "create_data_lake_object", create_data_lake_object, test_dlo_def)
    created_dlo_name = None
    if isinstance(created_dlo, dict):
        created_dlo_name = created_dlo.get("name") or created_dlo.get("developerName")

    if created_dlo_name:
        # Wait for DLO processing to complete before update/delete (15s needed)
        time.sleep(15)
        test_tool(results, "update_data_lake_object", update_data_lake_object, created_dlo_name, json.dumps({"label": "Updated DLO"}))
        test_tool(results, "delete_data_lake_object", delete_data_lake_object, created_dlo_name)
    else:
        # Test with dummy data - no skipping
        test_tool(results, "update_data_lake_object", update_data_lake_object, "DummyDLO", json.dumps({"label": "Updated DLO"}))
        test_tool(results, "delete_data_lake_object", delete_data_lake_object, "DummyDLO")

    # ========== 11. DATA MODEL OBJECTS ==========
    print("[11/20] Testing Data Model Objects tools...")

    dmo_result = test_tool(results, "list_data_model_objects", list_data_model_objects)

    test_dmo = None
    if dmo_result and isinstance(dmo_result, dict):
        dmo_list = dmo_result.get("dataModelObject", dmo_result.get("dataModelObjects", []))
        if dmo_list:
            test_dmo = (
                dmo_list[0].get("name")
                or dmo_list[0].get("developerName")
                or dmo_list[0].get("id")
            )

    if test_dmo:
        test_tool(results, "get_data_model_object", get_data_model_object, test_dmo)
        test_tool(results, "get_dmo_mappings", get_dmo_mappings, test_dmo)
        test_tool(results, "get_dmo_relationships", get_dmo_relationships, test_dmo)
    else:
        # Test with dummy data - no skipping
        test_tool(results, "get_data_model_object", get_data_model_object, "DummyDMO")
        test_tool(results, "get_dmo_mappings", get_dmo_mappings, "DummyDMO")
        test_tool(results, "get_dmo_relationships", get_dmo_relationships, "DummyDMO")

    # DMO CRUD - no dataspace field needed (defaults to default dataspace)
    dmo_name = f"{test_prefix}DMO"
    test_dmo_def = json.dumps({
        "name": dmo_name,
        "label": f"{test_prefix} DMO",
        "category": "Other",
        "fields": [
            {"name": "Id__c", "label": "ID", "dataType": "Text", "isPrimaryKey": True},
            {"name": "Name__c", "label": "Name", "dataType": "Text"}
        ]
    })
    created_dmo = test_tool(results, "create_data_model_object", create_data_model_object, test_dmo_def)
    created_dmo_name = None
    if isinstance(created_dmo, dict):
        created_dmo_name = created_dmo.get("name") or created_dmo.get("developerName")

    if created_dmo_name:
        test_tool(results, "update_data_model_object", update_data_model_object, created_dmo_name, json.dumps({"description": "Updated"}))
        test_tool(results, "delete_data_model_object", delete_data_model_object, created_dmo_name)
    else:
        # Test with dummy data - no skipping
        test_tool(results, "update_data_model_object", update_data_model_object, "DummyDMO", json.dumps({"description": "Updated"}))
        test_tool(results, "delete_data_model_object", delete_data_model_object, "DummyDMO")

    # DMO mappings and relationships - fixed field names
    test_mapping_def = json.dumps({
        "sourceObject": "TestSourceDLO__dll",
        "targetObject": "TestTargetDMO__dlm",
        "fieldMappings": [{"sourceField": "Id", "targetField": "ssot__Id__c"}]
    })
    test_tool(results, "create_dmo_mapping", create_dmo_mapping, test_mapping_def)
    test_tool(results, "delete_dmo_mapping", delete_dmo_mapping, "TestMapping")

    test_relationship_def = json.dumps({
        "name": "TestRelationship",
        "relatedObjectName": "ssot__ContactPointEmail__dlm",
        "cardinality": "OneToMany",
        "fieldMappings": [{"sourceField": "ssot__Id__c", "targetField": "ssot__PartyId__c"}]
    })
    test_tool(results, "create_dmo_relationship", create_dmo_relationship, test_dmo or "ssot__Individual__dlm", test_relationship_def)
    test_tool(results, "delete_dmo_relationship", delete_dmo_relationship, "TestRelationship")

    # ========== 12. DATA SPACES ==========
    print("[12/20] Testing Data Spaces tools...")

    spaces_result = test_tool(results, "list_data_spaces", list_data_spaces)

    test_space = None
    if spaces_result and isinstance(spaces_result, dict):
        spaces_list = spaces_result.get("dataSpaces", spaces_result.get("data", []))
        if spaces_list:
            test_space = spaces_list[0].get("name") or spaces_list[0].get("spaceName")

    space_members = None
    if test_space:
        test_tool(results, "get_data_space", get_data_space, test_space)
        space_members = test_tool(results, "get_data_space_members", get_data_space_members, test_space)
    else:
        # Test with dummy data - no skipping
        test_tool(results, "get_data_space", get_data_space, "DummySpace")
        space_members = test_tool(results, "get_data_space_members", get_data_space_members, "DummySpace")

    member_name = None
    if space_members and isinstance(space_members, dict):
        members_list = space_members.get("members", [])
        if members_list:
            member_name = members_list[0].get("memberName") or members_list[0].get("name")

    if test_space and member_name:
        test_tool(results, "get_data_space_member", get_data_space_member, test_space, member_name)
    else:
        # Test with dummy data - no skipping
        test_tool(results, "get_data_space_member", get_data_space_member, test_space or "DummySpace", "DummyMember")

    # Data space CRUD - uses label (name is derived)
    space_name = f"{test_prefix}Space"
    test_space_def = json.dumps({
        "label": f"{test_prefix} Space"
    })
    created_space = test_tool(results, "create_data_space", create_data_space, test_space_def)
    created_space_name = None
    if isinstance(created_space, dict):
        created_space_name = created_space.get("name") or created_space.get("apiName")

    if created_space_name:
        test_tool(results, "update_data_space", update_data_space, created_space_name, json.dumps({"description": "Updated"}))
        # API expects object with members array, not just array
        test_tool(results, "update_data_space_members", update_data_space_members, created_space_name, json.dumps({"members": [], "action": "REPLACE"}))
    else:
        test_tool(results, "update_data_space", update_data_space, "DummySpace", json.dumps({"description": "Updated"}))
        test_tool(results, "update_data_space_members", update_data_space_members, "DummySpace", json.dumps({"members": [], "action": "REPLACE"}))

    # ========== 13. CALCULATED INSIGHTS ==========
    print("[13/20] Testing Calculated Insights tools...")

    ci_result = test_tool(results, "list_calculated_insights", list_calculated_insights)
    test_tool(results, "get_insight_metadata", get_insight_metadata)

    test_ci = None
    if ci_result and isinstance(ci_result, dict):
        collection = ci_result.get("collection", {})
        ci_list = collection.get("items", ci_result.get("calculatedInsights", []))
        if ci_list:
            # Prefer ACTIVE status CIs for run_calculated_insight to succeed
            for ci in ci_list:
                status = ci.get("calculatedInsightStatus", "")
                if status == "ACTIVE":
                    test_ci = ci.get("apiName") or ci.get("name")
                    break
            if not test_ci:
                test_ci = ci_list[0].get("apiName") or ci_list[0].get("name")

    if test_ci:
        test_tool(results, "get_calculated_insight", get_calculated_insight, test_ci)
        test_tool(results, "query_calculated_insight", query_calculated_insight, test_ci)
        test_tool(results, "run_calculated_insight", run_calculated_insight, test_ci)
    else:
        # Test with dummy data - no skipping
        test_tool(results, "get_calculated_insight", get_calculated_insight, "DummyInsight")
        test_tool(results, "query_calculated_insight", query_calculated_insight, "DummyInsight")
        test_tool(results, "run_calculated_insight", run_calculated_insight, "DummyInsight")

    # CI CRUD - API uses apiName + displayName (from list response analysis)
    ci_name = f"{test_prefix}Insight__cio"
    test_ci_def = json.dumps({
        "apiName": ci_name,
        "displayName": f"{test_prefix} Insight",
        "expression": "SELECT COUNT(*) as count__c FROM ssot__Individual__dlm",
        "definitionType": "CALCULATED_METRIC",
        "dataSpaceName": "default",
        "publishScheduleInterval": "Streaming",
        "publishScheduleStartDateTime": datetime.utcnow().isoformat() + "Z"
    })
    created_ci = test_tool(
        results,
        "create_calculated_insight",
        create_calculated_insight,
        test_ci_def)
    created_ci_name = None
    if isinstance(created_ci, dict):
        created_ci_name = created_ci.get("apiName") or created_ci.get("developerName")

    if created_ci_name:
        test_tool(
            results,
            "update_calculated_insight",
            update_calculated_insight,
            created_ci_name,
            json.dumps({"description": "Updated by test_all_tools"})
        )
        test_tool(results, "delete_calculated_insight", delete_calculated_insight, created_ci_name)
    else:
        # Test with dummy data - no skipping (API requires __cio suffix)
        test_tool(results, "update_calculated_insight", update_calculated_insight, "DummyInsight__cio", json.dumps({"description": "Updated"}))
        test_tool(results, "delete_calculated_insight", delete_calculated_insight, "DummyInsight__cio")

    # ========== 14. DATA GRAPHS ==========
    print("[14/20] Testing Data Graphs tools...")

    dg_result = test_tool(results, "list_data_graphs", list_data_graphs)

    test_graph = None
    if dg_result and isinstance(dg_result, dict):
        # API returns dataGraphMetadata, not dataGraphs
        graph_list = dg_result.get("dataGraphMetadata", dg_result.get("dataGraphs", []))
        if graph_list:
            test_graph = graph_list[0].get("developerName") or graph_list[0].get("name")

    if test_graph:
        test_tool(results, "get_data_graph", get_data_graph, test_graph)
        test_tool(
            results,
            "refresh_data_graph",
            refresh_data_graph,
            test_graph)
    else:
        # Test with dummy data - no skipping
        test_tool(results, "get_data_graph", get_data_graph, "DummyGraph")
        test_tool(results, "refresh_data_graph", refresh_data_graph, "DummyGraph")

    # Query data graph - requires entity name and record ID
    if test_graph and profile_record_id:
        test_tool(results, "query_data_graph", query_data_graph, test_graph, profile_record_id)
    else:
        # Test with dummy data - no skipping
        test_tool(results, "query_data_graph", query_data_graph, test_graph or "DummyGraph", profile_record_id or "DummyRecordId")

    # Data graph CRUD - uses name/label (based on API response structure)
    graph_name = f"{test_prefix}Graph"
    test_graph_def = json.dumps({
        "name": graph_name,
        "label": f"{test_prefix} Graph",
        "dataspaceName": "default",
        "primaryObjectName": "IoT_Telemetry__dlm"
    })
    created_graph = test_tool(results, "create_data_graph", create_data_graph, test_graph_def)
    created_graph_name = None
    if isinstance(created_graph, dict):
        created_graph_name = created_graph.get("developerName") or created_graph.get("name")

    if created_graph_name:
        test_tool(results, "delete_data_graph", delete_data_graph, created_graph_name)
    else:
        test_tool(results, "delete_data_graph", delete_data_graph, "DummyGraph")

    # ========== 15. IDENTITY RESOLUTION ==========
    print("[15/20] Testing Identity Resolution tools...")

    ir_result = test_tool(results, "list_identity_rulesets", list_identity_rulesets)

    test_ruleset = None
    if ir_result and isinstance(ir_result, dict):
        ir_list = ir_result.get("identityResolutions", ir_result.get("identityRulesets", []))
        if ir_list:
            test_ruleset = ir_list[0].get("id") or ir_list[0].get("label") or ir_list[0].get("name")

    if test_ruleset:
        test_tool(results, "get_identity_ruleset", get_identity_ruleset, test_ruleset)
        test_tool(
            results,
            "run_identity_resolution",
            run_identity_resolution,
            test_ruleset)
    else:
        # Test with dummy data - no skipping
        test_tool(results, "get_identity_ruleset", get_identity_ruleset, "DummyRuleset")
        test_tool(results, "run_identity_resolution", run_identity_resolution, "DummyRuleset")

    # Test lookup_unified_id with sample parameters
    test_tool(results, "lookup_unified_id", lookup_unified_id, "ssot__Individual__dlm", "Salesforce_Home", "Contact_Home__dll", "003000000000001")

    # Identity ruleset CRUD - test with proper payloads
    ruleset_name = f"{test_prefix}Ruleset"
    test_ruleset_def = json.dumps({
        "label": ruleset_name,
        "configurationType": "individual",
        "dataSpaceName": "default",
        "matchRules": []
    })
    created_ruleset = test_tool(results, "create_identity_ruleset", create_identity_ruleset, test_ruleset_def)
    created_ruleset_id = None
    if isinstance(created_ruleset, dict):
        created_ruleset_id = created_ruleset.get("id") or created_ruleset.get("label")

    if created_ruleset_id:
        test_tool(results, "update_identity_ruleset", update_identity_ruleset, created_ruleset_id, json.dumps({"description": "Updated"}))
        test_tool(results, "delete_identity_ruleset", delete_identity_ruleset, created_ruleset_id)
    else:
        test_tool(results, "update_identity_ruleset", update_identity_ruleset, "DummyRuleset", json.dumps({"description": "Updated"}))
        test_tool(results, "delete_identity_ruleset", delete_identity_ruleset, "DummyRuleset")

    # ========== 16. ML & AI ==========
    print("[16/20] Testing ML & AI tools...")

    ml_result = test_tool(results, "list_ml_models", list_ml_models)

    test_model = None
    if ml_result and isinstance(ml_result, dict):
        # API returns configuredModels, not mlModels
        ml_list = ml_result.get("configuredModels", ml_result.get("mlModels", []))
        if ml_list:
            first = ml_list[0]
            # Model ID needs namespace prefix: namespace__name
            name = first.get("name")
            namespace = first.get("namespace", "")
            if namespace and name:
                test_model = f"{namespace}__{name}"
            else:
                test_model = first.get("id") or name or first.get("modelName")

    if test_model:
        test_tool(results, "get_ml_model", get_ml_model, test_model)
    else:
        # Test with dummy data - no skipping
        test_tool(results, "get_ml_model", get_ml_model, "DummyModel")

    # Prediction - test with sample payload
    test_prediction_input = json.dumps({
        "type": "individual",
        "recordId": "001000000000001",
        "features": {}
    })
    test_tool(results, "get_prediction", get_prediction, test_model or "DummyModel", test_prediction_input)

    # Model artifact operations - get real artifact from list
    artifacts_result = test_tool(results, "list_model_artifacts", list_model_artifacts)
    test_artifact = None
    if artifacts_result and isinstance(artifacts_result, dict):
        artifact_list = artifacts_result.get("modelArtifacts", [])
        if artifact_list:
            first = artifact_list[0]
            # Artifact ID needs namespace prefix: namespace__name
            name = first.get("name")
            namespace = first.get("namespace", "")
            if namespace and name:
                test_artifact = f"{namespace}__{name}"
            else:
                test_artifact = first.get("id") or name

    if test_artifact:
        test_tool(results, "get_model_artifact", get_model_artifact, test_artifact)
    else:
        # Test with dummy data - no skipping
        test_tool(results, "get_model_artifact", get_model_artifact, "DummyArtifact")

    # ML model CRUD - test with proper payloads
    test_tool(results, "update_model_artifact", update_model_artifact, test_artifact or "DummyArtifact", json.dumps({"description": "Updated"}))
    test_tool(results, "update_ml_model", update_ml_model, test_model or "DummyModel", json.dumps({"description": "Updated"}))
    test_tool(results, "delete_ml_model", delete_ml_model, "DummyModel")
    test_tool(results, "delete_model_artifact", delete_model_artifact, "DummyArtifact")

    # ========== 17. DOCUMENT AI ==========
    print("[17/20] Testing Document AI tools...")

    doc_ai_result = test_tool(results, "list_document_ai_configs", list_document_ai_configs)
    test_tool(results, "get_document_ai_global_config", get_document_ai_global_config)

    test_doc_config = None
    if doc_ai_result and isinstance(doc_ai_result, dict):
        config_list = doc_ai_result.get("configurations", doc_ai_result.get("data", []))
        if config_list:
            test_doc_config = config_list[0].get("id") or config_list[0].get("name")

    if test_doc_config:
        test_tool(results, "get_document_ai_config", get_document_ai_config, test_doc_config)
        test_tool(results, "run_document_ai", run_document_ai, test_doc_config)
    else:
        test_tool(results, "get_document_ai_config", get_document_ai_config, "TestConfig")
        test_tool(results, "run_document_ai", run_document_ai, "TestConfig")

    # Document extraction - test with sample data
    test_tool(results, "extract_document_data", extract_document_data, "TestConfig", "base64-encoded-document-data")
    test_tool(results, "generate_document_schema", generate_document_schema, json.dumps({"documentType": "invoice"}))

    # Document AI config CRUD - uses name/label
    test_doc_def = json.dumps({"name": "TestAPIDocConfig", "label": "Test API Doc Config"})
    test_tool(results, "create_document_ai_config", create_document_ai_config, test_doc_def)
    test_tool(results, "update_document_ai_config", update_document_ai_config, "TestAPIDocConfig", json.dumps({"description": "Updated"}))
    test_tool(results, "delete_document_ai_config", delete_document_ai_config, "TestAPIDocConfig")

    # ========== 18. SEMANTIC SEARCH ==========
    print("[18/20] Testing Semantic Search tools...")

    test_tool(results, "list_semantic_searches", list_semantic_searches)
    test_tool(results, "get_semantic_search_config", get_semantic_search_config)
    test_tool(results, "get_semantic_search", get_semantic_search, "TestSearch")

    # Semantic search CRUD - minimal payload
    test_search_def = json.dumps({
        "name": "TestAPISearch",
        "label": "Test API Search",
        "sourceDmoName": "ssot__Individual__dlm"
    })
    test_tool(results, "create_semantic_search", create_semantic_search, test_search_def)
    test_tool(results, "update_semantic_search", update_semantic_search, "TestAPISearch", json.dumps({"description": "Updated"}))
    test_tool(results, "delete_semantic_search", delete_semantic_search, "TestAPISearch")

    # ========== 19. DATA ACTIONS ==========
    print("[19/20] Testing Data Actions tools...")

    test_tool(results, "list_data_actions", list_data_actions)
    dat_result = test_tool(results, "list_data_action_targets", list_data_action_targets)

    # Get real data action target from list - find EXTERNAL_WEBHOOK type for signing key
    test_dat = None
    test_dat_for_signing_key = None
    if dat_result and isinstance(dat_result, dict):
        dat_list = dat_result.get("dataActionTargets", [])
        if dat_list:
            test_dat = dat_list[0].get("apiName")
            # Find an EXTERNAL_WEBHOOK type for signing key (CORE type doesn't support it)
            for target in dat_list:
                target_type = target.get("type", "")
                if target_type == "EXTERNAL_WEBHOOK":
                    test_dat_for_signing_key = target.get("apiName")
                    break

    if test_dat:
        test_tool(results, "get_data_action_target", get_data_action_target, test_dat)

    if test_dat_for_signing_key:
        test_tool(results, "get_data_action_target_signing_key", get_data_action_target_signing_key, test_dat_for_signing_key)
    else:
        # No EXTERNAL_WEBHOOK target found, test with dummy (will fail expectedly)
        test_tool(results, "get_data_action_target_signing_key", get_data_action_target_signing_key, test_dat or "TestTarget")

    if not test_dat:
        test_tool(results, "get_data_action_target", get_data_action_target, "TestTarget")

    # Data action CRUD - uses developerName and masterLabel, no dataspace field
    test_action_def = json.dumps({
        "developerName": "TestAPIAction__da",
        "masterLabel": "Test API Action"
    })
    test_tool(results, "create_data_action", create_data_action, test_action_def)

    # Data action target - type "Core" requires config with orgId
    # Note: CREATE operation has server-side limitations - testing anyway
    test_target_def = json.dumps({
        "developerName": "TestAPIActionTarget",
        "masterLabel": "Test API Action Target",
        "type": "Core"
    })
    test_tool(results, "create_data_action_target", create_data_action_target, test_target_def)
    test_tool(results, "delete_data_action_target", delete_data_action_target, "TestAPIActionTarget")

    # ========== 20. ADMIN & MONITORING ==========
    print("[20/20] Testing Admin & Monitoring tools...")

    test_tool(results, "get_limits", get_limits)
    test_tool(results, "list_private_network_routes", list_private_network_routes)
    test_tool(results, "get_private_network_route", get_private_network_route, "test-route-id")

    # Private network route CRUD
    test_route_def = json.dumps({"name": "TestAPIRoute"})
    test_tool(results, "create_private_network_route", create_private_network_route, test_route_def)
    test_tool(results, "delete_private_network_route", delete_private_network_route, "test-route-id")

    # Data kit operations
    test_tool(results, "get_data_kit_status", get_data_kit_status, "test-component-id")
    test_tool(results, "get_data_kit_component_dependencies", get_data_kit_component_dependencies, "test-kit", "test-component")
    test_tool(results, "get_data_kit_deployment_status", get_data_kit_deployment_status, "test-kit", "test-component")
    test_tool(results, "undeploy_data_kit", undeploy_data_kit, "test-kit")

    # ========== SUMMARY ==========
    results.print_summary()

    # Return exit code based on results
    return 0 if results.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
