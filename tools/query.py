"""
SQL query tools - execute, validate, and format queries.
"""
from typing import Optional
from pydantic import Field

from connect_api_dc_sql import run_query
from query_validation import validate_sql_syntax, validate_query_with_metadata, format_query

from .base import (
    mcp, ensure_session, get_session, get_connect_api,
    validate_identifier, DEFAULT_LIST_TABLE_FILTER
)


@mcp.tool(description="Execute a SQL query against Data Cloud (PostgreSQL dialect)")
def query(
    sql: str = Field(description="SQL query. Always quote identifiers and use exact casing."),
) -> dict:
    """Execute a SQL query and return results."""
    ensure_session()
    return run_query(get_session(), sql)


@mcp.tool(description="List available tables in Data Cloud")
def list_tables() -> list[str]:
    """List tables matching the DEFAULT_LIST_TABLE_FILTER pattern."""
    ensure_session()
    validated_filter = validate_identifier(DEFAULT_LIST_TABLE_FILTER, "table filter")
    sql = f"""SELECT c.relname AS TABLE_NAME
              FROM pg_catalog.pg_namespace n, pg_catalog.pg_class c
              LEFT JOIN pg_catalog.pg_description d ON (c.oid = d.objoid AND d.objsubid = 0 AND d.classoid = 'pg_class'::regclass)
              WHERE c.relnamespace = n.oid AND c.relname LIKE '{validated_filter}'"""
    result = run_query(get_session(), sql)
    return [x[0] for x in result.get("data", [])]


@mcp.tool(description="Get column names for a table")
def describe_table(
    table: str = Field(description="The table name"),
) -> list[str]:
    """Returns list of column names for the specified table."""
    ensure_session()
    validated_table = validate_identifier(table, "table")
    sql = f"""SELECT a.attname FROM pg_catalog.pg_namespace n
              JOIN pg_catalog.pg_class c ON (c.relnamespace = n.oid)
              JOIN pg_catalog.pg_attribute a ON (a.attrelid = c.oid)
              WHERE a.attnum > 0 AND NOT a.attisdropped AND c.relname='{validated_table}'"""
    result = run_query(get_session(), sql)
    return [x[0] for x in result.get("data", [])]


@mcp.tool(description="Validate SQL query syntax before execution")
def validate_query(
    sql: str = Field(description="The SQL query to validate"),
    check_metadata: bool = Field(default=False, description="Also validate table/column names"),
) -> dict:
    """Validate SQL syntax and optionally check against metadata."""
    result = validate_sql_syntax(sql)

    if not result.get("valid") or not check_metadata:
        return result

    try:
        ensure_session()
        tables = list_tables()
        table_columns = {}
        metadata_result = get_connect_api().get_metadata()
        for entity in metadata_result.get('metadata', []):
            entity_name = entity.get('name', '')
            columns = [f.get('name', '') for f in entity.get('fields', [])]
            table_columns[entity_name] = columns
        return validate_query_with_metadata(sql, tables, table_columns)
    except Exception:
        return result


@mcp.tool(description="Format a SQL query for readability")
def format_sql(
    sql: str = Field(description="The SQL query to format"),
) -> str:
    """Format SQL query with proper indentation."""
    return format_query(sql)
