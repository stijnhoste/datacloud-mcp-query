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


@mcp.tool(description="Create a new Data Lake Object")
def create_data_lake_object(
    object_definition: str = Field(
        description="""JSON DLO definition. Use 'dataType' (not 'type') for fields. Example:
{
  "name": "MyDLO__dll",
  "label": "My Data Lake Object",
  "description": "Description here",
  "dataSpaceName": "default",
  "category": "Other",
  "fields": [
    {"name": "Id__c", "label": "ID", "dataType": "Text", "isPrimaryKey": true},
    {"name": "Name__c", "label": "Name", "dataType": "Text"}
  ]
}"""
    ),
) -> dict:
    """Create a new Data Lake Object."""
    ensure_session()
    definition = parse_json_param(object_definition, "object_definition")
    definition = normalize_field_definitions(definition)
    return get_connect_api().create_data_lake_object(definition)


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


@mcp.tool(description="Create a new Data Model Object")
def create_data_model_object(
    object_definition: str = Field(
        description="""JSON DMO definition. Use 'dataType' (not 'type') for fields. Example:
{
  "name": "MyDMO__dlm",
  "label": "My Data Model Object",
  "description": "Description here",
  "dataSpaceName": "default",
  "category": "Other",
  "type": "DataModelObject",
  "fields": [
    {"name": "Id__c", "label": "ID", "dataType": "Text", "isPrimaryKey": true},
    {"name": "Name__c", "label": "Name", "dataType": "Text"}
  ]
}"""
    ),
) -> dict:
    """Create a new Data Model Object."""
    ensure_session()
    definition = parse_json_param(object_definition, "object_definition")
    definition = normalize_field_definitions(definition)
    return get_connect_api().create_data_model_object(definition)


@mcp.tool(description="Update a Data Model Object")
def update_data_model_object(
    object_name: str = Field(description="Name of the DMO to update"),
    updates: str = Field(description="JSON object with fields to update"),
) -> dict:
    """Update DMO properties."""
    ensure_session()
    update_data = parse_json_param(updates, "updates")
    return get_connect_api().update_data_model_object(object_name, update_data)


@mcp.tool(description="Delete a Data Model Object")
def delete_data_model_object(
    object_name: str = Field(description="Name of the DMO to delete"),
) -> dict:
    """Delete a DMO permanently."""
    ensure_session()
    return get_connect_api().delete_data_model_object(object_name)


@mcp.tool(description="Get field mappings for a DMO")
def get_dmo_mappings(
    object_name: Optional[str] = Field(default=None, description="Filter by DMO name"),
) -> dict:
    """Get field mappings between DLOs and DMOs."""
    ensure_session()
    return get_connect_api().get_dmo_mappings(resolve_field_default(object_name))


@mcp.tool(description="Create a field mapping for a DMO")
def create_dmo_mapping(
    mapping_definition: str = Field(description="JSON mapping definition"),
    dataspace: str = Field(default="default", description="Data space name"),
) -> dict:
    """Create a new field mapping."""
    ensure_session()
    definition = parse_json_param(mapping_definition, "mapping_definition")
    return get_connect_api().create_dmo_mapping(definition, dataspace=dataspace)


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


@mcp.tool(description="Create a relationship on a DMO")
def create_dmo_relationship(
    object_name: str = Field(description="Name of the DMO"),
    relationship_definition: str = Field(description="JSON relationship definition"),
) -> dict:
    """Create a new relationship on a DMO."""
    ensure_session()
    definition = parse_json_param(relationship_definition, "relationship_definition")
    return get_connect_api().create_dmo_relationship(object_name, definition)


@mcp.tool(description="Delete a relationship")
def delete_dmo_relationship(
    relationship_name: str = Field(description="Name of the relationship to delete"),
) -> dict:
    """Delete a relationship."""
    ensure_session()
    return get_connect_api().delete_dmo_relationship(relationship_name)
