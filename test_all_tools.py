#!/usr/bin/env python3
"""
Comprehensive test script for Data Cloud MCP tools.
Tests read-only tools automatically, skips mutating operations.
"""
import json
import sys
import time
from datetime import datetime

# Import from modular tools package
from tools.org import list_orgs, set_target_org, get_target_org
from tools.query import query, list_tables, describe_table, validate_query, format_sql
from tools.metadata import (
    get_metadata, describe_table_full, get_relationships, explore_table, search_tables
)
from tools.insights import list_calculated_insights, query_calculated_insight
from tools.graphs import list_data_graphs, query_data_graph
from tools.identity import lookup_unified_id, list_identity_rulesets, get_identity_ruleset, run_identity_resolution
from tools.segments import (
    list_segments, get_segment, get_segment_members, count_segment,
    create_segment, update_segment, delete_segment, publish_segment
)
from tools.activations import (
    list_activations, get_activation, get_audience_records, list_activation_targets
)
from tools.streams import list_data_streams, get_data_stream, run_data_stream
from tools.transforms import (
    list_data_transforms, get_data_transform, get_transform_run_history, run_data_transform
)
from tools.connections import (
    list_connections, get_connection, get_connection_objects, preview_connection, list_connectors
)
from tools.dlo_dmo import (
    list_data_lake_objects, get_data_lake_object, create_data_lake_object,
    list_data_model_objects, get_data_model_object, get_dmo_mappings, create_data_model_object
)
from tools.dataspaces import list_data_spaces, get_data_space, get_data_space_members
from tools.ml import (
    list_ml_models, get_ml_model, get_prediction, list_model_artifacts,
    list_document_ai_configs, extract_document_data,
    list_semantic_searches, get_semantic_search, get_semantic_search_config
)
from tools.admin import (
    get_limits, list_data_actions, list_data_action_targets,
    list_private_network_routes, get_data_kit_status
)


class TestResults:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.skipped = 0

    def add(self, name: str, status: str, message: str = "", duration: float = 0):
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
                    print(f"  • {r['name']}{dur}{msg}")

        print("\n" + "-" * 70)
        print(f"TOTAL: {len(self.results)} | PASS: {self.passed} | FAIL: {self.failed} | SKIP: {self.skipped}")
        print("=" * 70)


def test_tool(results: TestResults, name: str, func, *args, **kwargs):
    """Run a tool test and record results."""
    start = time.time()
    try:
        result = func(*args, **kwargs)
        duration = time.time() - start

        # Check for error in result
        if isinstance(result, dict) and result.get("error"):
            results.add(name, "FAIL", str(result.get("error")), duration)
        elif isinstance(result, dict) and result.get("success") == False:
            results.add(name, "FAIL", str(result.get("error", "Unknown error")), duration)
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
        results.add(name, "FAIL", str(e)[:200], duration)
        return None


def skip_tool(results: TestResults, name: str, reason: str):
    """Mark a tool as skipped."""
    results.add(name, "SKIP", reason)


def main():
    print("=" * 70)
    print("DATA CLOUD MCP SERVER - COMPREHENSIVE TOOL TEST")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Target Org: mca-next-sdo")
    print("=" * 70)

    results = TestResults()

    # ========== 1. ORG MANAGEMENT ==========
    print("\n[1/17] Testing Org Management tools...")

    test_tool(results, "list_orgs", list_orgs)
    test_tool(results, "set_target_org", set_target_org, "mca-next-sdo")
    test_tool(results, "get_target_org", get_target_org)

    # ========== 2. QUERY & SQL ==========
    print("[2/17] Testing Query & SQL tools...")

    tables_result = test_tool(results, "list_tables", list_tables)

    # Get a table for further tests
    test_table = None
    if tables_result and len(tables_result) > 0:
        # Find a good table for testing
        for t in tables_result:
            if "Individual" in t or "Account" in t:
                test_table = t
                break
        if not test_table:
            test_table = tables_result[0]

    if test_table:
        test_tool(results, "describe_table", describe_table, test_table)
        test_tool(results, "query", query, f'SELECT * FROM "{test_table}" LIMIT 5')
    else:
        skip_tool(results, "describe_table", "No tables found")
        skip_tool(results, "query", "No tables found")

    test_tool(results, "validate_query", validate_query, "SELECT * FROM test", False)
    test_tool(results, "format_sql", format_sql, "select * from test where id=1")

    # ========== 3. METADATA ==========
    print("[3/17] Testing Metadata tools...")

    test_tool(results, "get_metadata", get_metadata)

    if test_table:
        test_tool(results, "describe_table_full", describe_table_full, test_table)
        test_tool(results, "get_relationships", get_relationships, test_table)
        test_tool(results, "explore_table", explore_table, test_table, 3)
    else:
        skip_tool(results, "describe_table_full", "No tables found")
        skip_tool(results, "get_relationships", "No tables found")
        skip_tool(results, "explore_table", "No tables found")

    test_tool(results, "search_tables", search_tables, "Individual")

    # ========== 4. SEGMENTS ==========
    print("[4/17] Testing Segments tools...")

    segments_result = test_tool(results, "list_segments", list_segments)

    # Find a segment for further tests
    test_segment = None
    if segments_result and isinstance(segments_result, dict):
        segments_list = segments_result.get("segments", [])
        if segments_list:
            test_segment = segments_list[0].get("name") or segments_list[0].get("segmentName")

    if test_segment:
        test_tool(results, "get_segment", get_segment, test_segment)
        test_tool(results, "get_segment_members", get_segment_members, test_segment, 5, 0)
        test_tool(results, "count_segment", count_segment, test_segment)
    else:
        skip_tool(results, "get_segment", "No segments found")
        skip_tool(results, "get_segment_members", "No segments found")
        skip_tool(results, "count_segment", "No segments found")

    # Skip mutating segment operations
    skip_tool(results, "create_segment", "Skipped - mutating operation")
    skip_tool(results, "update_segment", "Skipped - mutating operation")
    skip_tool(results, "delete_segment", "Skipped - mutating operation")
    skip_tool(results, "publish_segment", "Skipped - mutating operation")

    # ========== 5. ACTIVATIONS ==========
    print("[5/17] Testing Activations tools...")

    activations_result = test_tool(results, "list_activations", list_activations)
    test_tool(results, "list_activation_targets", list_activation_targets)

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
        skip_tool(results, "get_activation", "No activations found")
        skip_tool(results, "get_audience_records", "No activations found")

    # ========== 6. DATA STREAMS ==========
    print("[6/17] Testing Data Streams tools...")

    streams_result = test_tool(results, "list_data_streams", list_data_streams)

    test_stream = None
    if streams_result and isinstance(streams_result, dict):
        streams_list = streams_result.get("dataStreams", streams_result.get("data", []))
        if streams_list:
            test_stream = streams_list[0].get("name") or streams_list[0].get("dataStreamName")

    if test_stream:
        test_tool(results, "get_data_stream", get_data_stream, test_stream)
    else:
        skip_tool(results, "get_data_stream", "No data streams found")

    skip_tool(results, "run_data_stream", "Skipped - mutating operation")

    # ========== 7. DATA TRANSFORMS ==========
    print("[7/17] Testing Data Transforms tools...")

    transforms_result = test_tool(results, "list_data_transforms", list_data_transforms)

    test_transform = None
    if transforms_result and isinstance(transforms_result, dict):
        transforms_list = transforms_result.get("dataTransforms", transforms_result.get("data", []))
        if transforms_list:
            test_transform = transforms_list[0].get("name") or transforms_list[0].get("transformName")

    if test_transform:
        test_tool(results, "get_data_transform", get_data_transform, test_transform)
        test_tool(results, "get_transform_run_history", get_transform_run_history, test_transform)
    else:
        skip_tool(results, "get_data_transform", "No data transforms found")
        skip_tool(results, "get_transform_run_history", "No data transforms found")

    skip_tool(results, "run_data_transform", "Skipped - mutating operation")

    # ========== 8. CONNECTIONS ==========
    print("[8/17] Testing Connections tools...")

    connectors_result = test_tool(results, "list_connectors", list_connectors)

    # list_connections requires a connector_type - get one from list_connectors
    test_connector_type = None
    if connectors_result and isinstance(connectors_result, dict):
        connector_list = connectors_result.get("connectorInfoList", [])
        if connector_list:
            # Field is 'name' not 'connectorType'
            test_connector_type = connector_list[0].get("name")

    connections_result = None
    if test_connector_type:
        connections_result = test_tool(results, "list_connections", list_connections, test_connector_type)
    else:
        skip_tool(results, "list_connections", "No connector types found")

    test_connection = None
    if connections_result and isinstance(connections_result, dict):
        connections_list = connections_result.get("connections", connections_result.get("data", []))
        if connections_list:
            test_connection = connections_list[0].get("id") or connections_list[0].get("name")

    if test_connection:
        test_tool(results, "get_connection", get_connection, test_connection)
        conn_objects = test_tool(results, "get_connection_objects", get_connection_objects, test_connection)

        # Try preview if we have objects
        test_object = None
        if conn_objects and isinstance(conn_objects, dict):
            objects_list = conn_objects.get("objects", [])
            if objects_list:
                test_object = objects_list[0].get("name")

        if test_object:
            test_tool(results, "preview_connection", preview_connection, test_connection, test_object, 3)
        else:
            skip_tool(results, "preview_connection", "No connection objects found")
    else:
        skip_tool(results, "get_connection", "No connections found")
        skip_tool(results, "get_connection_objects", "No connections found")
        skip_tool(results, "preview_connection", "No connections found")

    # ========== 9. DATA LAKE OBJECTS ==========
    print("[9/17] Testing Data Lake Objects tools...")

    dlo_result = test_tool(results, "list_data_lake_objects", list_data_lake_objects)

    test_dlo = None
    if dlo_result and isinstance(dlo_result, dict):
        dlo_list = dlo_result.get("dataLakeObjects", dlo_result.get("data", []))
        if dlo_list:
            test_dlo = dlo_list[0].get("name") or dlo_list[0].get("objectName")

    if test_dlo:
        test_tool(results, "get_data_lake_object", get_data_lake_object, test_dlo)
    else:
        skip_tool(results, "get_data_lake_object", "No DLOs found")

    skip_tool(results, "create_data_lake_object", "Skipped - mutating operation")

    # ========== 10. DATA MODEL OBJECTS ==========
    print("[10/17] Testing Data Model Objects tools...")

    dmo_result = test_tool(results, "list_data_model_objects", list_data_model_objects)

    test_dmo = None
    if dmo_result and isinstance(dmo_result, dict):
        dmo_list = dmo_result.get("dataModelObjects", dmo_result.get("data", []))
        if dmo_list:
            test_dmo = dmo_list[0].get("name") or dmo_list[0].get("objectName")

    if test_dmo:
        test_tool(results, "get_data_model_object", get_data_model_object, test_dmo)
        test_tool(results, "get_dmo_mappings", get_dmo_mappings, test_dmo)
    else:
        skip_tool(results, "get_data_model_object", "No DMOs found")
        skip_tool(results, "get_dmo_mappings", "No DMOs found")

    skip_tool(results, "create_data_model_object", "Skipped - mutating operation")

    # ========== 11. DATA SPACES ==========
    print("[11/17] Testing Data Spaces tools...")

    spaces_result = test_tool(results, "list_data_spaces", list_data_spaces)

    test_space = None
    if spaces_result and isinstance(spaces_result, dict):
        spaces_list = spaces_result.get("dataSpaces", spaces_result.get("data", []))
        if spaces_list:
            test_space = spaces_list[0].get("name") or spaces_list[0].get("spaceName")

    if test_space:
        test_tool(results, "get_data_space", get_data_space, test_space)
        test_tool(results, "get_data_space_members", get_data_space_members, test_space)
    else:
        skip_tool(results, "get_data_space", "No data spaces found")
        skip_tool(results, "get_data_space_members", "No data spaces found")

    # ========== 12. CALCULATED INSIGHTS ==========
    print("[12/17] Testing Calculated Insights tools...")

    ci_result = test_tool(results, "list_calculated_insights", list_calculated_insights)

    test_ci = None
    if ci_result and isinstance(ci_result, dict):
        ci_list = ci_result.get("calculatedInsights", ci_result.get("data", []))
        if ci_list:
            test_ci = ci_list[0].get("name") or ci_list[0].get("insightName")

    if test_ci:
        test_tool(results, "query_calculated_insight", query_calculated_insight, test_ci)
    else:
        skip_tool(results, "query_calculated_insight", "No calculated insights found")

    # ========== 13. DATA GRAPHS ==========
    print("[13/17] Testing Data Graphs tools...")

    dg_result = test_tool(results, "list_data_graphs", list_data_graphs)

    # query_data_graph requires specific record_id or lookup_keys
    skip_tool(results, "query_data_graph", "Requires specific record_id or lookup_keys")

    # ========== 14. IDENTITY RESOLUTION ==========
    print("[14/17] Testing Identity Resolution tools...")

    ir_result = test_tool(results, "list_identity_rulesets", list_identity_rulesets)

    test_ruleset = None
    if ir_result and isinstance(ir_result, dict):
        ir_list = ir_result.get("identityRulesets", ir_result.get("rulesets", ir_result.get("data", [])))
        if ir_list:
            test_ruleset = ir_list[0].get("name") or ir_list[0].get("rulesetName")

    if test_ruleset:
        test_tool(results, "get_identity_ruleset", get_identity_ruleset, test_ruleset)
    else:
        skip_tool(results, "get_identity_ruleset", "No identity rulesets found")

    skip_tool(results, "run_identity_resolution", "Skipped - mutating operation")
    skip_tool(results, "lookup_unified_id", "Requires specific source record identifiers")

    # ========== 15. ML & AI ==========
    print("[15/17] Testing ML & AI tools...")

    ml_result = test_tool(results, "list_ml_models", list_ml_models)
    test_tool(results, "list_model_artifacts", list_model_artifacts)

    test_model = None
    if ml_result and isinstance(ml_result, dict):
        ml_list = ml_result.get("mlModels", ml_result.get("models", ml_result.get("data", [])))
        if ml_list:
            test_model = ml_list[0].get("name") or ml_list[0].get("modelName")

    if test_model:
        test_tool(results, "get_ml_model", get_ml_model, test_model)
    else:
        skip_tool(results, "get_ml_model", "No ML models found")

    skip_tool(results, "get_prediction", "Requires specific input data")

    # ========== 16. DOCUMENT AI ==========
    print("[16/17] Testing Document AI tools...")

    doc_ai_result = test_tool(results, "list_document_ai_configs", list_document_ai_configs)
    skip_tool(results, "extract_document_data", "Requires document data")

    # ========== 17. SEMANTIC SEARCH ==========
    print("[17/17] Testing Semantic Search & Admin tools...")

    test_tool(results, "list_semantic_searches", list_semantic_searches)
    test_tool(results, "get_semantic_search_config", get_semantic_search_config)

    # Try to get a specific semantic search if available
    # skip_tool(results, "get_semantic_search", "Requires specific search name")

    # ========== ADMIN ==========
    test_tool(results, "get_limits", get_limits)
    test_tool(results, "list_data_actions", list_data_actions)
    test_tool(results, "list_data_action_targets", list_data_action_targets)
    test_tool(results, "list_private_network_routes", list_private_network_routes)
    skip_tool(results, "get_data_kit_status", "Requires specific component_id")

    # ========== SUMMARY ==========
    results.print_summary()

    # Return exit code based on results
    return 0 if results.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
