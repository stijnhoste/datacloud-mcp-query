"""
Data Lake Object (DLO) and Data Model Object (DMO) tools.
"""
from typing import Optional
from pydantic import Field

from .base import (
    mcp, ensure_session, get_connect_api, parse_json_param,
    normalize_field_definitions, resolve_field_default
)


# ============================================================
# Data Lake Objects (DLOs) - Raw ingested data
# ============================================================

@mcp.tool(description="List all Data Lake Objects (raw ingested data)")
def list_data_lake_objects() -> dict:
    """List all DLOs in the Data Cloud instance."""
    ensure_session()
    return get_connect_api().list_data_lake_objects()


@mcp.tool(description="Get details for a specific Data Lake Object")
def get_data_lake_object(
    object_name: str = Field(description="Name of the DLO"),
) -> dict:
    """Get DLO schema and configuration."""
    ensure_session()
    return get_connect_api().get_data_lake_object(object_name)


@mcp.tool(description="Update a Data Lake Object")
def update_data_lake_object(
    object_name: str = Field(description="Name of the DLO to update"),
    updates: str = Field(description="JSON object with fields to update"),
) -> dict:
    """Update DLO properties."""
    ensure_session()
    update_data = parse_json_param(updates, "updates")
    return get_connect_api().update_data_lake_object(object_name, update_data)


@mcp.tool(description="Delete a Data Lake Object")
def delete_data_lake_object(
    object_name: str = Field(description="Name of the DLO to delete"),
) -> dict:
    """Delete a DLO permanently."""
    ensure_session()
    return get_connect_api().delete_data_lake_object(object_name)


# ============================================================
# Data Model Objects (DMOs) - Canonical entities
# ============================================================

@mcp.tool(description="List all Data Model Objects (canonical entities)")
def list_data_model_objects() -> dict:
    """List all DMOs in the Data Cloud instance."""
    ensure_session()
    return get_connect_api().list_data_model_objects()


@mcp.tool(description="Get details for a specific Data Model Object")
def get_data_model_object(
    object_name: str = Field(description="Name of the DMO"),
) -> dict:
    """Get DMO schema and configuration."""
    ensure_session()
    return get_connect_api().get_data_model_object(object_name)


@mcp.tool(description="Delete a field mapping")
def delete_dmo_mapping(
    mapping_name: str = Field(description="Name of the mapping to delete"),
) -> dict:
    """Delete a field mapping."""
    ensure_session()
    return get_connect_api().delete_dmo_mapping(mapping_name)


@mcp.tool(description="Get relationships for a DMO")
def get_dmo_relationships(
    object_name: str = Field(description="Name of the DMO"),
) -> dict:
    """Get relationships defined on a DMO."""
    ensure_session()
    return get_connect_api().get_dmo_relationships(object_name)


@mcp.tool(description="Delete a relationship")
def delete_dmo_relationship(
    relationship_name: str = Field(description="Name of the relationship to delete"),
) -> dict:
    """Delete a relationship."""
    ensure_session()
    return get_connect_api().delete_dmo_relationship(relationship_name)
