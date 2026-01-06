"""
Metadata and schema discovery tools.
"""
import logging
from typing import Optional
from pydantic import Field

from connect_api_dc_sql import run_query

from .base import (
    mcp, ensure_session, get_session, get_connect_api, resolve_field_default
)

logger = logging.getLogger(__name__)


@mcp.tool(description="Get rich metadata for Data Cloud entities")
def get_metadata(
    entity_name: Optional[str] = Field(default=None, description="Filter by entity name"),
    entity_type: Optional[str] = Field(default=None, description="Filter by type (dll, dlm)"),
    entity_category: Optional[str] = Field(default=None, description="Filter by category"),
) -> dict:
    """Get metadata including fields, types, and relationships."""
    ensure_session()
    return get_connect_api().get_metadata(
        entity_name=resolve_field_default(entity_name),
        entity_type=resolve_field_default(entity_type),
        entity_category=resolve_field_default(entity_category)
    )


@mcp.tool(description="Get detailed table schema with field types")
def describe_table_full(
    table: str = Field(description="The table/entity name"),
) -> dict:
    """Get detailed schema with field names, types, and business types."""
    ensure_session()
    result = get_connect_api().get_metadata(entity_name=table)
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


@mcp.tool(description="Get relationships for an entity (useful for JOINs)")
def get_relationships(
    entity_name: str = Field(description="The entity name"),
) -> list[dict]:
    """Get relationships showing how to JOIN with other tables."""
    ensure_session()
    result = get_connect_api().get_metadata(entity_name=entity_name)
    metadata_list = result.get('metadata', [])
    if not metadata_list:
        return []
    return metadata_list[0].get("relationships", [])


@mcp.tool(description="Comprehensive data exploration: schema, samples, and statistics")
def explore_table(
    table: str = Field(description="The table name to explore"),
    sample_size: int = Field(default=10, description="Number of sample rows"),
) -> dict:
    """Get schema, row count, sample data, and column profiles."""
    ensure_session()
    result = {
        "table": table,
        "schema": [],
        "row_count": 0,
        "sample": [],
        "column_profiles": {}
    }

    # Get schema from metadata API
    try:
        metadata_result = get_connect_api().get_metadata(entity_name=table)
        metadata_list = metadata_result.get('metadata', [])
        if metadata_list:
            entity = metadata_list[0]
            result["schema"] = [
                {"name": f.get("name"), "type": f.get("type"), "businessType": f.get("businessType")}
                for f in entity.get("fields", [])
            ]
    except Exception as e:
        logger.warning(f"Failed to get metadata for {table}: {e}")

    # Get row count
    try:
        count_sql = f'SELECT COUNT(*) FROM "{table}"'
        count_result = run_query(get_session(), count_sql)
        if count_result.get("data"):
            result["row_count"] = count_result["data"][0][0]
    except Exception as e:
        logger.warning(f"Failed to get row count: {e}")

    # Get sample rows
    try:
        columns = [f["name"] for f in result["schema"]] if result["schema"] else ["*"]
        col_list = ", ".join([f'"{c}"' for c in columns[:20]])
        sample_sql = f'SELECT {col_list} FROM "{table}" ORDER BY RANDOM() LIMIT {sample_size}'
        sample_result = run_query(get_session(), sample_sql)
        result["sample"] = sample_result.get("data", [])
        result["sample_columns"] = [m.get("name") for m in sample_result.get("metadata", [])]
    except Exception as e:
        logger.warning(f"Failed to get sample: {e}")

    return result


@mcp.tool(description="Search for tables and columns by keyword")
def search_tables(
    keyword: str = Field(description="Keyword to search for"),
) -> dict:
    """Search table and column names for a keyword."""
    ensure_session()
    keyword_lower = keyword.lower()
    result = {"matching_tables": [], "tables_with_matching_columns": []}

    try:
        metadata_result = get_connect_api().get_metadata()
        for entity in metadata_result.get('metadata', []):
            entity_name = entity.get("name", "")
            display_name = entity.get("displayName", "")

            if keyword_lower in entity_name.lower() or keyword_lower in display_name.lower():
                result["matching_tables"].append({
                    "name": entity_name,
                    "displayName": display_name,
                    "category": entity.get("category")
                })

            matching_columns = [
                {"name": f.get("name"), "displayName": f.get("displayName"), "type": f.get("type")}
                for f in entity.get("fields", [])
                if keyword_lower in f.get("name", "").lower() or keyword_lower in f.get("displayName", "").lower()
            ]
            if matching_columns:
                result["tables_with_matching_columns"].append({
                    "table": entity_name,
                    "matchingColumns": matching_columns
                })
    except Exception as e:
        result["error"] = str(e)

    return result
