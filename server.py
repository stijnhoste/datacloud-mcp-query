import json
import logging
from typing import Optional
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import requests
import os
from oauth import OAuthConfig, OAuthSession
from connect_api_dc_sql import run_query
from direct_api import DirectAPISession
from query_validation import validate_sql_syntax, validate_query_with_metadata, format_query
from connect_api_segments import ConnectAPIClient

# Get logger for this module
logger = logging.getLogger(__name__)


# Create an MCP server
mcp = FastMCP("Demo")

# Global config and session
sf_org: OAuthConfig = OAuthConfig.from_env()
oauth_session: OAuthSession = OAuthSession(sf_org)
direct_api: DirectAPISession = DirectAPISession(oauth_session)
connect_api: ConnectAPIClient = ConnectAPIClient(oauth_session)

# Non-auth configuration
DEFAULT_LIST_TABLE_FILTER = os.getenv('DEFAULT_LIST_TABLE_FILTER', '%')


@mcp.tool(description="Executes a SQL query and returns the results")
def query(
    sql: str = Field(
        description="A SQL query in the PostgreSQL dialect make sure to always quote all identifies and use the exact casing. To formulate the query first verify which tables and fields to use through the suggest fields tool (or if it is broken through the list tables / describe tables call). Before executing the tool provide the user a succinct summary (targeted to low code users) on the semantics of the query"),
):
    # Returns both data and metadata
    return run_query(oauth_session, sql)


@mcp.tool(description="Lists the available tables in the database")
def list_tables() -> list[str]:
    sql = "SELECT c.relname AS TABLE_NAME FROM pg_catalog.pg_namespace n, pg_catalog.pg_class c LEFT JOIN pg_catalog.pg_description d ON (c.oid = d.objoid AND d.objsubid = 0  and d.classoid = 'pg_class'::regclass) WHERE c.relnamespace = n.oid AND c.relname LIKE '%s'" % DEFAULT_LIST_TABLE_FILTER
    result = run_query(oauth_session, sql)
    # Extract data from the result dictionary
    data = result.get("data", [])
    return [x[0] for x in data]


@mcp.tool(description="Describes the columns of a table")
def describe_table(
    table: str = Field(description="The table name"),
) -> list[str]:
    sql = f"SELECT a.attname FROM pg_catalog.pg_namespace n JOIN pg_catalog.pg_class c ON (c.relnamespace = n.oid) JOIN pg_catalog.pg_attribute a ON (a.attrelid = c.oid) JOIN pg_catalog.pg_type t ON (a.atttypid = t.oid) LEFT JOIN pg_catalog.pg_attrdef def ON (a.attrelid = def.adrelid AND a.attnum = def.adnum) LEFT JOIN pg_catalog.pg_description dsc ON (c.oid = dsc.objoid AND a.attnum = dsc.objsubid) LEFT JOIN pg_catalog.pg_class dc ON (dc.oid = dsc.classoid AND dc.relname = 'pg_class') LEFT JOIN pg_catalog.pg_namespace dn ON (dc.relnamespace = dn.oid AND dn.nspname = 'pg_catalog') WHERE a.attnum > 0 AND NOT a.attisdropped AND c.relname='{table}'"
    result = run_query(oauth_session, sql)
    # Extract data from the result dictionary
    data = result.get("data", [])
    return [x[0] for x in data]


# ========== Metadata Tools (Direct API) ==========

@mcp.tool(description="Get rich metadata for Data Cloud entities including fields, types, and relationships. Uses the faster Direct API.")
def get_metadata(
    entity_name: Optional[str] = Field(default=None, description="Filter by entity name (e.g., 'ssot__Individual__dlm')"),
    entity_type: Optional[str] = Field(default=None, description="Filter by entity type (e.g., 'dll', 'dlm')"),
    entity_category: Optional[str] = Field(default=None, description="Filter by category (e.g., 'Profile', 'Engagement')"),
) -> dict:
    """
    Returns metadata including:
    - Entity name, display name, category
    - Fields with names, types, and business types
    - Primary keys
    - Relationships to other entities
    """
    return direct_api.get_metadata(
        entity_name=entity_name,
        entity_type=entity_type,
        entity_category=entity_category
    )


@mcp.tool(description="Get detailed table schema with field types from the Metadata API. More detailed than describe_table.")
def describe_table_full(
    table: str = Field(description="The table/entity name (e.g., 'ssot__Individual__dlm')"),
) -> dict:
    """
    Returns detailed schema information including:
    - Field names and display names
    - Data types and business types
    - Primary key information
    """
    result = direct_api.get_metadata(entity_name=table)
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
    """
    Returns relationships including:
    - From/to entity names
    - Join field mappings
    - Cardinality (e.g., 'NTOONE', 'ONETOMANY')
    """
    result = direct_api.get_metadata(entity_name=entity_name)
    metadata_list = result.get('metadata', [])

    if not metadata_list:
        return []

    entity = metadata_list[0]
    return entity.get("relationships", [])


# ========== Discovery Tools ==========

@mcp.tool(description="Comprehensive data exploration: schema, sample rows, row count, and column statistics. Useful for understanding table contents before querying.")
def explore_table(
    table: str = Field(description="The table name to explore"),
    sample_size: int = Field(default=10, description="Number of sample rows to return"),
) -> dict:
    """
    Returns comprehensive table exploration including:
    - Schema with field types
    - Random sample rows
    - Total row count
    - Column profiles (distinct values for strings, min/max/avg for numbers)
    """
    result = {
        "table": table,
        "schema": [],
        "row_count": 0,
        "sample": [],
        "column_profiles": {}
    }

    # Get schema from metadata API
    try:
        metadata_result = direct_api.get_metadata(entity_name=table)
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

    # Get row count
    try:
        count_sql = f'SELECT COUNT(*) FROM "{table}"'
        count_result = run_query(oauth_session, count_sql)
        count_data = count_result.get("data", [])
        if count_data:
            result["row_count"] = count_data[0][0]
    except Exception as e:
        logger.warning(f"Failed to get row count for {table}: {e}")

    # Get sample rows (random sample using TABLESAMPLE or ORDER BY RANDOM)
    try:
        # Get column names first
        columns = [f["name"] for f in result["schema"]] if result["schema"] else ["*"]
        col_list = ", ".join([f'"{c}"' for c in columns[:20]])  # Limit columns
        sample_sql = f'SELECT {col_list} FROM "{table}" ORDER BY RANDOM() LIMIT {sample_size}'
        sample_result = run_query(oauth_session, sample_sql)
        result["sample"] = sample_result.get("data", [])
        result["sample_columns"] = [m.get("name") for m in sample_result.get("metadata", [])]
    except Exception as e:
        logger.warning(f"Failed to get sample for {table}: {e}")

    # Get column profiles for first few columns
    try:
        for field in result["schema"][:10]:  # Limit to first 10 columns
            field_name = field["name"]
            field_type = field.get("type", "").upper()

            profile = {"null_count": 0}

            # Get null count
            null_sql = f'SELECT COUNT(*) FROM "{table}" WHERE "{field_name}" IS NULL'
            null_result = run_query(oauth_session, null_sql)
            null_data = null_result.get("data", [])
            if null_data:
                profile["null_count"] = null_data[0][0]

            # For string fields, get distinct values
            if field_type in ("STRING", "TEXT", "VARCHAR"):
                distinct_sql = f'SELECT DISTINCT "{field_name}" FROM "{table}" WHERE "{field_name}" IS NOT NULL LIMIT 20'
                distinct_result = run_query(oauth_session, distinct_sql)
                distinct_data = distinct_result.get("data", [])
                profile["distinct_values"] = [row[0] for row in distinct_data]

            # For numeric fields, get min/max/avg
            elif field_type in ("NUMBER", "INTEGER", "DECIMAL", "DOUBLE", "FLOAT", "BIGINT"):
                stats_sql = f'SELECT MIN("{field_name}"), MAX("{field_name}"), AVG("{field_name}") FROM "{table}"'
                stats_result = run_query(oauth_session, stats_sql)
                stats_data = stats_result.get("data", [])
                if stats_data:
                    profile["min"] = stats_data[0][0]
                    profile["max"] = stats_data[0][1]
                    profile["avg"] = stats_data[0][2]

            result["column_profiles"][field_name] = profile

    except Exception as e:
        logger.warning(f"Failed to get column profiles for {table}: {e}")

    return result


@mcp.tool(description="Search for tables and columns by keyword. Useful when you don't know the exact table name.")
def search_tables(
    keyword: str = Field(description="Keyword to search for in table and column names"),
) -> dict:
    """
    Searches across all metadata to find:
    - Tables with names matching the keyword
    - Tables with columns matching the keyword
    """
    keyword_lower = keyword.lower()

    result = {
        "matching_tables": [],
        "tables_with_matching_columns": []
    }

    try:
        # Get all metadata
        metadata_result = direct_api.get_metadata()
        metadata_list = metadata_result.get('metadata', [])

        for entity in metadata_list:
            entity_name = entity.get("name", "")
            display_name = entity.get("displayName", "")

            # Check if table name matches
            if keyword_lower in entity_name.lower() or keyword_lower in display_name.lower():
                result["matching_tables"].append({
                    "name": entity_name,
                    "displayName": display_name,
                    "category": entity.get("category")
                })

            # Check if any column matches
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


# ========== Calculated Insights Tools ==========

@mcp.tool(description="List all available calculated insights (pre-aggregated metrics)")
def list_calculated_insights() -> dict:
    """
    Returns metadata for all calculated insights including:
    - Insight names and descriptions
    - Available dimensions and measures
    - Filter options
    """
    return direct_api.get_calculated_insights_metadata()


@mcp.tool(description="Query a calculated insight with specific dimensions, measures, and filters")
def query_calculated_insight(
    insight_name: str = Field(description="Name of the calculated insight to query"),
    dimensions: Optional[str] = Field(default=None, description="Comma-separated list of dimension fields"),
    measures: Optional[str] = Field(default=None, description="Comma-separated list of measure fields"),
    filters: Optional[str] = Field(default=None, description="JSON-encoded filter conditions"),
    batch_size: Optional[int] = Field(default=None, description="Number of records per batch"),
) -> dict:
    """
    Query pre-aggregated metrics from a calculated insight.
    Calculated insights are pre-computed aggregations that are faster than ad-hoc queries.
    """
    dim_list = dimensions.split(",") if dimensions else None
    meas_list = measures.split(",") if measures else None

    filter_list = None
    if filters:
        try:
            filter_list = json.loads(filters)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON in filters parameter"}

    return direct_api.query_calculated_insight(
        insight_name=insight_name,
        dimensions=dim_list,
        measures=meas_list,
        filters=filter_list,
        batch_size=batch_size
    )


# ========== Data Graph Tools ==========

@mcp.tool(description="List all available data graphs")
def list_data_graphs() -> dict:
    """
    Returns metadata for all data graphs including:
    - Graph names and descriptions
    - Available entities and relationships
    """
    return direct_api.get_data_graph_metadata()


@mcp.tool(description="Query a data graph to get a complete profile with related records")
def query_data_graph(
    graph_name: str = Field(description="Name of the data graph"),
    record_id: Optional[str] = Field(default=None, description="ID of the record to retrieve"),
    lookup_keys: Optional[str] = Field(default=None, description="JSON-encoded array of lookup key objects"),
) -> dict:
    """
    Get a complete profile from a data graph, including all related records.
    Use either record_id OR lookup_keys (not both).
    """
    if record_id:
        return direct_api.query_data_graph_by_id(graph_name, record_id)
    elif lookup_keys:
        try:
            keys = json.loads(lookup_keys)
            return direct_api.query_data_graph_by_lookup(graph_name, keys)
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
    """
    Find the unified profile ID from a source system's record identifiers.
    Useful for identity resolution and cross-system lookups.
    """
    return direct_api.lookup_unified_id(
        entity_name=entity_name,
        data_source_id=data_source_id,
        data_source_object_id=data_source_object_id,
        source_record_id=source_record_id
    )


# ========== Ingestion API ==========

@mcp.tool(description="Ingest records into Data Cloud (requires explicit approval - modifies data)")
def ingest_records(
    source_name: str = Field(description="Name of the data source"),
    object_name: str = Field(description="Name of the object to ingest into"),
    records: str = Field(description="JSON-encoded array of record objects to ingest"),
) -> dict:
    """
    Insert records into Data Cloud for testing or data loading.
    WARNING: This modifies data and requires explicit approval.
    """
    try:
        record_list = json.loads(records)
        return direct_api.ingest_records(source_name, object_name, record_list)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in records parameter"}


@mcp.tool(description="Delete records from Data Cloud (requires explicit approval - modifies data)")
def delete_records(
    source_name: str = Field(description="Name of the data source"),
    object_name: str = Field(description="Name of the object"),
    record_ids: str = Field(description="JSON-encoded array of record IDs to delete"),
) -> dict:
    """
    Delete records from Data Cloud.
    WARNING: This modifies data and requires explicit approval.
    """
    try:
        id_list = json.loads(record_ids)
        return direct_api.delete_records(source_name, object_name, id_list)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in record_ids parameter"}


# ========== Query Assistance Tools ==========

@mcp.tool(description="Validate SQL query syntax before execution. Catches errors early and provides helpful suggestions.")
def validate_query(
    sql: str = Field(description="The SQL query to validate"),
    check_metadata: bool = Field(default=False, description="If true, also validates table/column names against metadata"),
) -> dict:
    """
    Validate SQL query syntax and optionally check against metadata.

    Returns:
    - valid: bool - whether the query is valid
    - error_type: str - type of error (if invalid)
    - message: str - error description (if invalid)
    - suggestion: str - suggested fix (if available)
    - position: dict - line/column of error (if available)
    """
    # Basic syntax validation
    result = validate_sql_syntax(sql)

    if not result.get("valid") or not check_metadata:
        return result

    # If metadata check requested, get table list and validate
    try:
        tables = list_tables()
        table_columns = {}

        # Build column map for referenced tables
        metadata_result = direct_api.get_metadata()
        for entity in metadata_result.get('metadata', []):
            entity_name = entity.get('name', '')
            columns = [f.get('name', '') for f in entity.get('fields', [])]
            table_columns[entity_name] = columns

        return validate_query_with_metadata(sql, tables, table_columns)
    except Exception as e:
        logger.warning(f"Metadata validation failed: {e}")
        # Return basic validation result if metadata fetch fails
        return result


@mcp.tool(description="Format a SQL query for better readability")
def format_sql(
    sql: str = Field(description="The SQL query to format"),
) -> str:
    """
    Format SQL query with proper indentation and keyword casing.
    Useful for cleaning up messy queries.
    """
    return format_query(sql)


# ========== Segments Tools (Phase 2) ==========

@mcp.tool(description="List all segments in Data Cloud")
def list_segments() -> dict:
    """
    Returns a list of all segments with their metadata.
    """
    return connect_api.list_segments()


@mcp.tool(description="Get details for a specific segment")
def get_segment(
    segment_name: str = Field(description="Name of the segment"),
) -> dict:
    """
    Returns detailed information about a segment including its definition.
    """
    return connect_api.get_segment(segment_name)


@mcp.tool(description="Get members of a segment")
def get_segment_members(
    segment_name: str = Field(description="Name of the segment"),
    limit: Optional[int] = Field(default=None, description="Maximum number of members to return"),
    offset: Optional[int] = Field(default=None, description="Offset for pagination"),
) -> dict:
    """
    Returns the list of member records in a segment.
    """
    return connect_api.get_segment_members(segment_name, limit=limit, offset=offset)


@mcp.tool(description="Count members in a segment")
def count_segment(
    segment_name: str = Field(description="Name of the segment"),
) -> dict:
    """
    Returns the count of members in a segment.
    Useful for understanding segment size before retrieving members.
    """
    return connect_api.count_segment(segment_name)


@mcp.tool(description="Create a new segment (requires approval - creates data)")
def create_segment(
    segment_definition: str = Field(description="JSON-encoded segment definition"),
) -> dict:
    """
    Create a new segment in Data Cloud.
    WARNING: This creates data and requires explicit approval.
    """
    try:
        definition = json.loads(segment_definition)
        return connect_api.create_segment(definition)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in segment_definition parameter"}


@mcp.tool(description="Update an existing segment (requires approval - modifies data)")
def update_segment(
    segment_name: str = Field(description="Name of the segment to update"),
    segment_updates: str = Field(description="JSON-encoded fields to update"),
) -> dict:
    """
    Update an existing segment in Data Cloud.
    WARNING: This modifies data and requires explicit approval.
    """
    try:
        updates = json.loads(segment_updates)
        return connect_api.update_segment(segment_name, updates)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in segment_updates parameter"}


@mcp.tool(description="Delete a segment (requires approval - deletes data)")
def delete_segment(
    segment_name: str = Field(description="Name of the segment to delete"),
) -> dict:
    """
    Delete a segment from Data Cloud.
    WARNING: This deletes data and requires explicit approval.
    """
    return connect_api.delete_segment(segment_name)


@mcp.tool(description="Publish a segment for activation (requires approval - modifies data)")
def publish_segment(
    segment_name: str = Field(description="Name of the segment to publish"),
) -> dict:
    """
    Publish a segment to make it available for activation.
    WARNING: This modifies data and requires explicit approval.
    """
    return connect_api.publish_segment(segment_name)


# ========== Activations Tools (Phase 2) ==========

@mcp.tool(description="List all activations in Data Cloud")
def list_activations() -> dict:
    """
    Returns a list of all activations with their metadata.
    """
    return connect_api.list_activations()


@mcp.tool(description="Get details for a specific activation")
def get_activation(
    activation_id: str = Field(description="ID of the activation"),
) -> dict:
    """
    Returns detailed information about an activation.
    """
    return connect_api.get_activation(activation_id)


@mcp.tool(description="Get audience DMO records for an activation")
def get_audience_records(
    activation_id: str = Field(description="ID of the activation"),
    limit: Optional[int] = Field(default=None, description="Maximum number of records to return"),
    offset: Optional[int] = Field(default=None, description="Offset for pagination"),
) -> dict:
    """
    Returns audience records for an activation.
    """
    return connect_api.get_audience_records(activation_id, limit=limit, offset=offset)


@mcp.tool(description="List all available activation targets")
def list_activation_targets() -> dict:
    """
    Returns a list of available activation targets (e.g., marketing clouds, ad platforms).
    """
    return connect_api.list_activation_targets()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logger.info("Starting MCP server")
    mcp.run()
