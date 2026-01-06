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


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logger.info("Starting MCP server")
    mcp.run()
