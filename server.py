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

# Get logger for this module
logger = logging.getLogger(__name__)


# Create an MCP server
mcp = FastMCP("Demo")

# Global config and session
sf_org: OAuthConfig = OAuthConfig.from_env()
oauth_session: OAuthSession = OAuthSession(sf_org)
direct_api: DirectAPISession = DirectAPISession(oauth_session)

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


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logger.info("Starting MCP server")
    mcp.run()
