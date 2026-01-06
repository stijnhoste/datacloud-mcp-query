import json
import logging
import re
from typing import Optional
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import os
from connect_api_dc_sql import run_query
from query_validation import validate_sql_syntax, validate_query_with_metadata, format_query
from connect_api_segments import ConnectAPIClient
from sf_cli_auth import SFCLIAuth, sf_cli

# Get logger for this module
logger = logging.getLogger(__name__)


class SFCLISession:
    """
    Simple session adapter that wraps SF CLI auth to provide the interface
    expected by connect_api and run_query.
    """

    def __init__(self, sf_auth: SFCLIAuth, alias_or_username: str):
        self.sf_auth = sf_auth
        self.sf_auth.set_target_org(alias_or_username)

    def get_token(self) -> str:
        """Get access token from SF CLI."""
        token, _ = self.sf_auth.get_access_token()
        return token

    def get_instance_url(self) -> str:
        """Get instance URL from SF CLI."""
        _, instance_url = self.sf_auth.get_access_token()
        return instance_url


def _resolve_field_default(value):
    """
    Resolve Field() defaults when called directly (not through MCP).

    When functions with Field() defaults are called directly (not via MCP),
    the Field() returns a FieldInfo object instead of the actual default.
    This helper extracts the actual default value.
    """
    from pydantic.fields import FieldInfo
    if isinstance(value, FieldInfo):
        return value.default
    return value


def _validate_identifier(name: str, identifier_type: str = "identifier") -> str:
    """
    Validate and sanitize SQL identifier to prevent SQL injection.

    Allows: alphanumeric, underscores, and Data Cloud naming patterns (ssot__Name__c, etc.)
    Raises ValueError if invalid.
    """
    if not name:
        raise ValueError(f"Empty {identifier_type} name")

    # Data Cloud identifiers follow pattern: namespace__name__suffix (e.g., ssot__Individual__dlm)
    # Allow: letters, numbers, underscores, percent (for LIKE patterns)
    if not re.match(r'^[a-zA-Z0-9_%]+$', name):
        raise ValueError(f"Invalid {identifier_type} name: {name}. Only alphanumeric characters, underscores, and percent signs allowed.")

    # Prevent SQL keywords that could be used maliciously
    sql_keywords = {'DROP', 'DELETE', 'INSERT', 'UPDATE', 'TRUNCATE', 'ALTER', 'CREATE', 'EXEC', 'EXECUTE', '--', ';'}
    if name.upper() in sql_keywords or '--' in name or ';' in name:
        raise ValueError(f"Invalid {identifier_type} name: {name}. SQL keywords not allowed.")

    return name


# Create an MCP server
mcp = FastMCP("Data Cloud MCP Server")

# Optional: pre-select an org via environment variable
DEFAULT_ORG = os.getenv('DC_DEFAULT_ORG', None)

# Global session state (initialized lazily)
_session: Optional[SFCLISession] = None
_connect_api: Optional[ConnectAPIClient] = None
_current_org: Optional[str] = None

# Non-auth configuration
DEFAULT_LIST_TABLE_FILTER = os.getenv('DEFAULT_LIST_TABLE_FILTER', '%')


def _init_session(alias_or_username: str):
    """Initialize session using SF CLI credentials."""
    global _session, _connect_api, _current_org

    _session = SFCLISession(SFCLIAuth(), alias_or_username)
    _connect_api = ConnectAPIClient(_session)
    _current_org = alias_or_username
    logger.info(f"Connected to org: {alias_or_username}")


def _ensure_session():
    """Ensure we have an active session, prompting for org selection if needed."""
    if _session is not None:
        return

    if DEFAULT_ORG:
        _init_session(DEFAULT_ORG)
    else:
        raise RuntimeError(
            "No org selected. Use list_orgs() to see available orgs, then set_target_org(alias) to select one."
        )


# ========== Org Management Tools ==========

@mcp.tool(description="List all Salesforce orgs authenticated via SF CLI")
def list_orgs() -> list[dict]:
    """
    Returns a list of all orgs authenticated via SF CLI.
    Use this to see available orgs before selecting one with set_target_org().
    """
    orgs = sf_cli.list_orgs(refresh=True)
    return [org.to_dict() for org in orgs]


@mcp.tool(description="Set the target org for Data Cloud operations")
def set_target_org(
    alias_or_username: str = Field(description="Org alias (e.g., 'my-dc-org') or username"),
) -> dict:
    """
    Switch to a different Salesforce org for all subsequent Data Cloud operations.
    The org must be authenticated via SF CLI (use 'sf org login web --alias <name>' first).
    """
    try:
        _init_session(alias_or_username)
        org = sf_cli.get_org(alias_or_username)
        return {
            "success": True,
            "message": f"Now connected to: {org.display_name}",
            "org": org.to_dict() if org else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool(description="Get the currently selected org")
def get_target_org() -> dict:
    """
    Returns information about the currently selected Salesforce org.
    """
    if _current_org is None:
        return {
            "connected": False,
            "message": "No org selected. Use list_orgs() and set_target_org(alias) to connect."
        }

    org = sf_cli.get_org(_current_org)
    return {
        "connected": True,
        "org": org.to_dict() if org else None
    }


# ========== Query Tools ==========

@mcp.tool(description="Executes a SQL query and returns the results")
def query(
    sql: str = Field(
        description="A SQL query in the PostgreSQL dialect. Always quote identifiers and use exact casing."),
):
    _ensure_session()
    return run_query(_session, sql)


@mcp.tool(description="Lists the available tables in the database")
def list_tables() -> list[str]:
    _ensure_session()
    validated_filter = _validate_identifier(DEFAULT_LIST_TABLE_FILTER, "table filter")
    sql = f"SELECT c.relname AS TABLE_NAME FROM pg_catalog.pg_namespace n, pg_catalog.pg_class c LEFT JOIN pg_catalog.pg_description d ON (c.oid = d.objoid AND d.objsubid = 0  and d.classoid = 'pg_class'::regclass) WHERE c.relnamespace = n.oid AND c.relname LIKE '{validated_filter}'"
    result = run_query(_session, sql)
    data = result.get("data", [])
    return [x[0] for x in data]


@mcp.tool(description="Describes the columns of a table")
def describe_table(
    table: str = Field(description="The table name"),
) -> list[str]:
    _ensure_session()
    validated_table = _validate_identifier(table, "table")
    sql = f"SELECT a.attname FROM pg_catalog.pg_namespace n JOIN pg_catalog.pg_class c ON (c.relnamespace = n.oid) JOIN pg_catalog.pg_attribute a ON (a.attrelid = c.oid) JOIN pg_catalog.pg_type t ON (a.atttypid = t.oid) LEFT JOIN pg_catalog.pg_attrdef def ON (a.attrelid = def.adrelid AND a.attnum = def.adnum) LEFT JOIN pg_catalog.pg_description dsc ON (c.oid = dsc.objoid AND a.attnum = dsc.objsubid) LEFT JOIN pg_catalog.pg_class dc ON (dc.oid = dsc.classoid AND dc.relname = 'pg_class') LEFT JOIN pg_catalog.pg_namespace dn ON (dc.relnamespace = dn.oid AND dn.nspname = 'pg_catalog') WHERE a.attnum > 0 AND NOT a.attisdropped AND c.relname='{validated_table}'"
    result = run_query(_session, sql)
    data = result.get("data", [])
    return [x[0] for x in data]


# ========== Metadata Tools ==========

@mcp.tool(description="Get rich metadata for Data Cloud entities including fields, types, and relationships.")
def get_metadata(
    entity_name: Optional[str] = Field(default=None, description="Filter by entity name (e.g., 'ssot__Individual__dlm')"),
    entity_type: Optional[str] = Field(default=None, description="Filter by entity type (e.g., 'dll', 'dlm')"),
    entity_category: Optional[str] = Field(default=None, description="Filter by category (e.g., 'Profile', 'Engagement')"),
) -> dict:
    _ensure_session()
    return _connect_api.get_metadata(
        entity_name=_resolve_field_default(entity_name),
        entity_type=_resolve_field_default(entity_type),
        entity_category=_resolve_field_default(entity_category)
    )


@mcp.tool(description="Get detailed table schema with field types. More detailed than describe_table.")
def describe_table_full(
    table: str = Field(description="The table/entity name (e.g., 'ssot__Individual__dlm')"),
) -> dict:
    _ensure_session()
    result = _connect_api.get_metadata(entity_name=table)
    metadata_list = result.get('metadata', [])

    if not metadata_list:
        return {"error": f"No metadata found for table: {table}"}

    entity = metadata_list[0]
    return {
        "name": entity.get("name"),
        "displayName": entity.get("displayName"),
        "category": entity.get("category"),
        "fields": [
            {
                "name": f.get("name"),
                "displayName": f.get("displayName"),
                "type": f.get("type"),
                "businessType": f.get("businessType")
            }
            for f in entity.get("fields", [])
        ],
        "primaryKeys": entity.get("primaryKeys", [])
    }


@mcp.tool(description="Get relationships for an entity, useful for understanding how to JOIN tables")
def get_relationships(
    entity_name: str = Field(description="The entity name to get relationships for"),
) -> list[dict]:
    _ensure_session()
    result = _connect_api.get_metadata(entity_name=entity_name)
    metadata_list = result.get('metadata', [])

    if not metadata_list:
        return []

    entity = metadata_list[0]
    return entity.get("relationships", [])


# ========== Discovery Tools ==========

@mcp.tool(description="Comprehensive data exploration: schema, sample rows, row count, and column statistics.")
def explore_table(
    table: str = Field(description="The table name to explore"),
    sample_size: int = Field(default=10, description="Number of sample rows to return"),
) -> dict:
    _ensure_session()
    result = {
        "table": table,
        "schema": [],
        "row_count": 0,
        "sample": [],
        "column_profiles": {}
    }

    # Get schema from metadata API
    try:
        metadata_result = _connect_api.get_metadata(entity_name=table)
        metadata_list = metadata_result.get('metadata', [])
        if metadata_list:
            entity = metadata_list[0]
            result["schema"] = [
                {
                    "name": f.get("name"),
                    "type": f.get("type"),
                    "businessType": f.get("businessType")
                }
                for f in entity.get("fields", [])
            ]
    except Exception as e:
        logger.warning(f"Failed to get metadata for {table}: {e}")
        # Fall back to pg_catalog
        columns = describe_table(table)
        result["schema"] = [{"name": c, "type": "unknown"} for c in columns]

    # Get row count
    try:
        count_sql = f'SELECT COUNT(*) FROM "{table}"'
        count_result = run_query(_session, count_sql)
        count_data = count_result.get("data", [])
        if count_data:
            result["row_count"] = count_data[0][0]
    except Exception as e:
        logger.warning(f"Failed to get row count for {table}: {e}")

    # Get sample rows
    try:
        columns = [f["name"] for f in result["schema"]] if result["schema"] else ["*"]
        col_list = ", ".join([f'"{c}"' for c in columns[:20]])
        sample_sql = f'SELECT {col_list} FROM "{table}" ORDER BY RANDOM() LIMIT {sample_size}'
        sample_result = run_query(_session, sample_sql)
        result["sample"] = sample_result.get("data", [])
        result["sample_columns"] = [m.get("name") for m in sample_result.get("metadata", [])]
    except Exception as e:
        logger.warning(f"Failed to get sample for {table}: {e}")

    return result


@mcp.tool(description="Search for tables and columns by keyword.")
def search_tables(
    keyword: str = Field(description="Keyword to search for in table and column names"),
) -> dict:
    _ensure_session()
    keyword_lower = keyword.lower()
    result = {"matching_tables": [], "tables_with_matching_columns": []}

    try:
        metadata_result = _connect_api.get_metadata()
        metadata_list = metadata_result.get('metadata', [])

        for entity in metadata_list:
            entity_name = entity.get("name", "")
            display_name = entity.get("displayName", "")

            if keyword_lower in entity_name.lower() or keyword_lower in display_name.lower():
                result["matching_tables"].append({
                    "name": entity_name,
                    "displayName": display_name,
                    "category": entity.get("category")
                })

            matching_columns = []
            for field in entity.get("fields", []):
                field_name = field.get("name", "")
                field_display = field.get("displayName", "")
                if keyword_lower in field_name.lower() or keyword_lower in field_display.lower():
                    matching_columns.append({
                        "name": field_name,
                        "displayName": field_display,
                        "type": field.get("type")
                    })

            if matching_columns:
                result["tables_with_matching_columns"].append({
                    "table": entity_name,
                    "tableDisplayName": display_name,
                    "matchingColumns": matching_columns
                })

    except Exception as e:
        logger.error(f"Failed to search tables: {e}")
        result["error"] = str(e)

    return result


# ========== Query Assistance Tools ==========

@mcp.tool(description="Validate SQL query syntax before execution.")
def validate_query(
    sql: str = Field(description="The SQL query to validate"),
    check_metadata: bool = Field(default=False, description="If true, also validates table/column names against metadata"),
) -> dict:
    result = validate_sql_syntax(sql)

    if not result.get("valid") or not check_metadata:
        return result

    try:
        tables = list_tables()
        table_columns = {}
        metadata_result = _connect_api.get_metadata()
        for entity in metadata_result.get('metadata', []):
            entity_name = entity.get('name', '')
            columns = [f.get('name', '') for f in entity.get('fields', [])]
            table_columns[entity_name] = columns

        return validate_query_with_metadata(sql, tables, table_columns)
    except Exception as e:
        logger.warning(f"Metadata validation failed: {e}")
        return result


@mcp.tool(description="Format a SQL query for better readability")
def format_sql(
    sql: str = Field(description="The SQL query to format"),
) -> str:
    return format_query(sql)


# ========== Calculated Insights Tools ==========

@mcp.tool(description="List all available calculated insights (pre-aggregated metrics)")
def list_calculated_insights() -> dict:
    _ensure_session()
    return _connect_api.list_calculated_insights()


@mcp.tool(description="Query a calculated insight with specific dimensions, measures, and filters")
def query_calculated_insight(
    insight_name: str = Field(description="Name of the calculated insight to query"),
    dimensions: Optional[str] = Field(default=None, description="Comma-separated list of dimension fields"),
    measures: Optional[str] = Field(default=None, description="Comma-separated list of measure fields"),
    filters: Optional[str] = Field(default=None, description="JSON-encoded filter conditions"),
    limit: Optional[int] = Field(default=None, description="Maximum number of records to return"),
) -> dict:
    dim_list = dimensions.split(",") if dimensions else None
    meas_list = measures.split(",") if measures else None
    filter_list = None
    if filters:
        try:
            filter_list = json.loads(filters)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON in filters parameter"}

    _ensure_session()
    return _connect_api.query_calculated_insight(
        ci_name=insight_name,
        dimensions=dim_list,
        measures=meas_list,
        filters=filter_list,
        limit=limit
    )


# ========== Data Graph Tools ==========

@mcp.tool(description="List all available data graphs")
def list_data_graphs() -> dict:
    _ensure_session()
    return _connect_api.get_data_graph_metadata()


@mcp.tool(description="Query a data graph to get a complete profile with related records")
def query_data_graph(
    graph_name: str = Field(description="Name of the data graph entity"),
    record_id: Optional[str] = Field(default=None, description="ID of the record to retrieve"),
    lookup_keys: Optional[str] = Field(default=None, description="JSON-encoded object of lookup key fields and values"),
) -> dict:
    _ensure_session()
    if record_id:
        return _connect_api.query_data_graph_by_id(graph_name, record_id)
    elif lookup_keys:
        try:
            keys = json.loads(lookup_keys)
            return _connect_api.query_data_graph_by_lookup(graph_name, keys)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON in lookup_keys parameter"}
    else:
        return {"error": "Must provide either record_id or lookup_keys"}


# ========== Unified ID Lookup ==========

@mcp.tool(description="Look up unified record ID from source record identifiers")
def lookup_unified_id(
    entity_name: str = Field(description="Name of the entity"),
    data_source_id: str = Field(description="ID of the data source"),
    data_source_object_id: str = Field(description="ID of the data source object"),
    source_record_id: str = Field(description="ID of the source record"),
) -> dict:
    _ensure_session()
    return _connect_api.lookup_unified_id(
        entity_name=entity_name,
        data_source_id=data_source_id,
        data_source_object_id=data_source_object_id,
        source_record_id=source_record_id
    )


# ========== Segments Tools ==========

@mcp.tool(description="List all segments in Data Cloud")
def list_segments() -> dict:
    _ensure_session()
    return _connect_api.list_segments()


@mcp.tool(description="Get details for a specific segment")
def get_segment(
    segment_name: str = Field(description="Name of the segment"),
) -> dict:
    _ensure_session()
    return _connect_api.get_segment(segment_name)


@mcp.tool(description="Get members of a segment")
def get_segment_members(
    segment_name: str = Field(description="Name of the segment"),
    limit: Optional[int] = Field(default=None, description="Maximum number of members to return"),
    offset: Optional[int] = Field(default=None, description="Offset for pagination"),
) -> dict:
    _ensure_session()
    return _connect_api.get_segment_members(segment_name, limit=limit, offset=offset)


@mcp.tool(description="Count members in a segment")
def count_segment(
    segment_name: str = Field(description="Name of the segment"),
) -> dict:
    _ensure_session()
    return _connect_api.count_segment(segment_name)


@mcp.tool(description="Create a new segment (requires approval)")
def create_segment(
    segment_definition: str = Field(description="JSON-encoded segment definition"),
) -> dict:
    _ensure_session()
    try:
        definition = json.loads(segment_definition)
        return _connect_api.create_segment(definition)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in segment_definition parameter"}


@mcp.tool(description="Update an existing segment (requires approval)")
def update_segment(
    segment_name: str = Field(description="Name of the segment to update"),
    segment_updates: str = Field(description="JSON-encoded fields to update"),
) -> dict:
    _ensure_session()
    try:
        updates = json.loads(segment_updates)
        return _connect_api.update_segment(segment_name, updates)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in segment_updates parameter"}


@mcp.tool(description="Delete a segment (requires approval)")
def delete_segment(
    segment_name: str = Field(description="Name of the segment to delete"),
) -> dict:
    _ensure_session()
    return _connect_api.delete_segment(segment_name)


@mcp.tool(description="Publish a segment for activation (requires approval)")
def publish_segment(
    segment_name: str = Field(description="Name of the segment to publish"),
) -> dict:
    _ensure_session()
    return _connect_api.publish_segment(segment_name)


# ========== Activations Tools ==========

@mcp.tool(description="List all activations in Data Cloud")
def list_activations() -> dict:
    _ensure_session()
    return _connect_api.list_activations()


@mcp.tool(description="Get details for a specific activation")
def get_activation(
    activation_id: str = Field(description="ID of the activation"),
) -> dict:
    _ensure_session()
    return _connect_api.get_activation(activation_id)


@mcp.tool(description="Get audience DMO records for an activation")
def get_audience_records(
    activation_id: str = Field(description="ID of the activation"),
    limit: Optional[int] = Field(default=None, description="Maximum number of records to return"),
    offset: Optional[int] = Field(default=None, description="Offset for pagination"),
) -> dict:
    _ensure_session()
    return _connect_api.get_audience_records(activation_id, limit=limit, offset=offset)


@mcp.tool(description="List all available activation targets")
def list_activation_targets() -> dict:
    _ensure_session()
    return _connect_api.list_activation_targets()


# ========== Data Streams Tools ==========

@mcp.tool(description="List all data streams in Data Cloud")
def list_data_streams() -> dict:
    _ensure_session()
    return _connect_api.list_data_streams()


@mcp.tool(description="Get details for a specific data stream")
def get_data_stream(
    stream_name: str = Field(description="Name of the data stream"),
) -> dict:
    _ensure_session()
    return _connect_api.get_data_stream(stream_name)


@mcp.tool(description="Run data streams (requires approval)")
def run_data_stream(
    stream_names: str = Field(description="JSON-encoded array of data stream names to run"),
) -> dict:
    _ensure_session()
    try:
        names = json.loads(stream_names)
        return _connect_api.run_data_stream(names)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in stream_names parameter"}


# ========== Data Transforms Tools ==========

@mcp.tool(description="List all data transforms in Data Cloud")
def list_data_transforms() -> dict:
    _ensure_session()
    return _connect_api.list_data_transforms()


@mcp.tool(description="Get details for a specific data transform")
def get_data_transform(
    transform_name: str = Field(description="Name of the data transform"),
) -> dict:
    _ensure_session()
    return _connect_api.get_data_transform(transform_name)


@mcp.tool(description="Get run history for a data transform")
def get_transform_run_history(
    transform_name: str = Field(description="Name of the data transform"),
) -> dict:
    _ensure_session()
    return _connect_api.get_transform_run_history(transform_name)


@mcp.tool(description="Run a data transform (requires approval)")
def run_data_transform(
    transform_name: str = Field(description="Name of the data transform to run"),
) -> dict:
    _ensure_session()
    return _connect_api.run_data_transform(transform_name)


# ========== Connections Tools ==========

@mcp.tool(description="List all connections in Data Cloud")
def list_connections() -> dict:
    _ensure_session()
    return _connect_api.list_connections()


@mcp.tool(description="Get details for a specific connection")
def get_connection(
    connection_name: str = Field(description="Name of the connection"),
) -> dict:
    _ensure_session()
    return _connect_api.get_connection(connection_name)


@mcp.tool(description="Get available objects for a connection")
def get_connection_objects(
    connection_name: str = Field(description="Name of the connection"),
) -> dict:
    _ensure_session()
    return _connect_api.get_connection_objects(connection_name)


@mcp.tool(description="Preview data from a connection object")
def preview_connection(
    connection_name: str = Field(description="Name of the connection"),
    object_name: str = Field(description="Name of the object to preview"),
    limit: Optional[int] = Field(default=None, description="Maximum number of records to preview"),
) -> dict:
    _ensure_session()
    return _connect_api.preview_connection(connection_name, object_name, limit)


@mcp.tool(description="List all available connector types")
def list_connectors() -> dict:
    _ensure_session()
    return _connect_api.list_connectors()


# ========== Data Lake Objects Tools ==========

@mcp.tool(description="List all data lake objects (raw ingested data tables)")
def list_data_lake_objects() -> dict:
    _ensure_session()
    return _connect_api.list_data_lake_objects()


@mcp.tool(description="Get details for a specific data lake object")
def get_data_lake_object(
    object_name: str = Field(description="Name of the data lake object"),
) -> dict:
    _ensure_session()
    return _connect_api.get_data_lake_object(object_name)


@mcp.tool(description="Create a new data lake object (requires approval)")
def create_data_lake_object(
    object_definition: str = Field(description="JSON-encoded DLO definition"),
) -> dict:
    _ensure_session()
    try:
        definition = json.loads(object_definition)
        return _connect_api.create_data_lake_object(definition)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in object_definition parameter"}


# ========== Data Model Objects Tools ==========

@mcp.tool(description="List all data model objects (canonical entities)")
def list_data_model_objects() -> dict:
    _ensure_session()
    return _connect_api.list_data_model_objects()


@mcp.tool(description="Get details for a specific data model object")
def get_data_model_object(
    object_name: str = Field(description="Name of the data model object"),
) -> dict:
    _ensure_session()
    return _connect_api.get_data_model_object(object_name)


@mcp.tool(description="Get field mappings for a data model object")
def get_dmo_mappings(
    object_name: str = Field(description="Name of the data model object"),
) -> dict:
    _ensure_session()
    return _connect_api.get_dmo_mappings(object_name)


@mcp.tool(description="Create a new data model object (requires approval)")
def create_data_model_object(
    object_definition: str = Field(description="JSON-encoded DMO definition"),
) -> dict:
    _ensure_session()
    try:
        definition = json.loads(object_definition)
        return _connect_api.create_data_model_object(definition)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in object_definition parameter"}


# ========== Data Spaces Tools ==========

@mcp.tool(description="List all data spaces")
def list_data_spaces() -> dict:
    _ensure_session()
    return _connect_api.list_data_spaces()


@mcp.tool(description="Get details for a specific data space")
def get_data_space(
    space_name: str = Field(description="Name of the data space"),
) -> dict:
    _ensure_session()
    return _connect_api.get_data_space(space_name)


@mcp.tool(description="Get members (objects) of a data space")
def get_data_space_members(
    space_name: str = Field(description="Name of the data space"),
) -> dict:
    _ensure_session()
    return _connect_api.get_data_space_members(space_name)


# ========== ML Models Tools ==========

@mcp.tool(description="List all machine learning models")
def list_ml_models() -> dict:
    _ensure_session()
    return _connect_api.list_ml_models()


@mcp.tool(description="Get details for a specific ML model")
def get_ml_model(
    model_name: str = Field(description="Name of the ML model"),
) -> dict:
    _ensure_session()
    return _connect_api.get_ml_model(model_name)


@mcp.tool(description="Get predictions from an ML model")
def get_prediction(
    model_name: str = Field(description="Name of the ML model"),
    input_data: Optional[str] = Field(default=None, description="JSON-encoded input data for prediction"),
) -> dict:
    _ensure_session()
    if input_data:
        try:
            data = json.loads(input_data)
            return _connect_api.get_prediction(model_name, data)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON in input_data parameter"}
    return _connect_api.get_prediction(model_name)


@mcp.tool(description="List all ML model artifacts")
def list_model_artifacts() -> dict:
    _ensure_session()
    return _connect_api.list_model_artifacts()


# ========== Document AI Tools ==========

@mcp.tool(description="List all Document AI configurations")
def list_document_ai_configs() -> dict:
    _ensure_session()
    return _connect_api.list_document_ai_configs()


@mcp.tool(description="Extract data from a document using Document AI (requires approval)")
def extract_document_data(
    config_name: str = Field(description="Name of the Document AI configuration"),
    document_data: str = Field(description="JSON-encoded document content and metadata"),
) -> dict:
    _ensure_session()
    try:
        data = json.loads(document_data)
        return _connect_api.extract_document_data(config_name, data)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in document_data parameter"}


# ========== Semantic Search Tools ==========

@mcp.tool(description="List all semantic search configurations")
def list_semantic_searches() -> dict:
    _ensure_session()
    return _connect_api.list_semantic_searches()


@mcp.tool(description="Get details for a specific semantic search")
def get_semantic_search(
    search_name: str = Field(description="Name of the semantic search"),
) -> dict:
    _ensure_session()
    return _connect_api.get_semantic_search(search_name)


@mcp.tool(description="Get global semantic search configuration")
def get_semantic_search_config() -> dict:
    _ensure_session()
    return _connect_api.get_semantic_search_config()


# ========== Identity Resolution Tools ==========

@mcp.tool(description="List all identity resolution rulesets")
def list_identity_rulesets() -> dict:
    _ensure_session()
    return _connect_api.list_identity_rulesets()


@mcp.tool(description="Get details for a specific identity resolution ruleset")
def get_identity_ruleset(
    ruleset_name: str = Field(description="Name of the identity resolution ruleset"),
) -> dict:
    _ensure_session()
    return _connect_api.get_identity_ruleset(ruleset_name)


@mcp.tool(description="Run identity resolution (requires approval)")
def run_identity_resolution(
    ruleset_name: str = Field(description="Name of the identity resolution ruleset to run"),
) -> dict:
    _ensure_session()
    return _connect_api.run_identity_resolution(ruleset_name)


# ========== Admin Tools ==========

@mcp.tool(description="Get API limits and usage statistics")
def get_limits() -> dict:
    _ensure_session()
    return _connect_api.get_limits()


@mcp.tool(description="List all data actions")
def list_data_actions() -> dict:
    _ensure_session()
    return _connect_api.list_data_actions()


@mcp.tool(description="List all data action targets")
def list_data_action_targets() -> dict:
    _ensure_session()
    return _connect_api.list_data_action_targets()


@mcp.tool(description="List all private network routes")
def list_private_network_routes() -> dict:
    _ensure_session()
    return _connect_api.list_private_network_routes()


@mcp.tool(description="Get status of a data kit component")
def get_data_kit_status(
    component_id: str = Field(description="ID of the data kit component"),
) -> dict:
    _ensure_session()
    return _connect_api.get_data_kit_status(component_id)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logger.info("Starting Data Cloud MCP Server (SF CLI auth)")
    mcp.run()
