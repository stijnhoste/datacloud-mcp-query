"""
Identity resolution tools - manage identity matching rulesets.
"""
from pydantic import Field

from .base import mcp, ensure_session, get_connect_api, parse_json_param


@mcp.tool(description="List all identity resolution rulesets")
def list_identity_rulesets() -> dict:
    """List all identity resolution rulesets."""
    ensure_session()
    return get_connect_api().list_identity_rulesets()


@mcp.tool(description="Get details for a specific identity resolution ruleset")
def get_identity_ruleset(
    ruleset_name: str = Field(description="Name of the ruleset"),
) -> dict:
    """Get identity resolution ruleset configuration."""
    ensure_session()
    return get_connect_api().get_identity_ruleset(ruleset_name)


@mcp.tool(description="Update an identity resolution ruleset")
def update_identity_ruleset(
    ruleset_name: str = Field(description="Name of the ruleset to update"),
    updates: str = Field(description="JSON object with fields to update"),
) -> dict:
    """Update an identity resolution ruleset."""
    ensure_session()
    update_data = parse_json_param(updates, "updates")
    return get_connect_api().update_identity_ruleset(ruleset_name, update_data)


@mcp.tool(description="Delete an identity resolution ruleset")
def delete_identity_ruleset(
    ruleset_name: str = Field(description="Name of the ruleset to delete"),
) -> dict:
    """Delete an identity resolution ruleset."""
    ensure_session()
    return get_connect_api().delete_identity_ruleset(ruleset_name)


@mcp.tool(description="Run identity resolution")
def run_identity_resolution(
    ruleset_name: str = Field(description="Name of the ruleset to run"),
) -> dict:
    """Trigger identity resolution for a ruleset."""
    ensure_session()
    return get_connect_api().run_identity_resolution(ruleset_name)


@mcp.tool(description="Look up unified record ID from source identifiers")
def lookup_unified_id(
    entity_name: str = Field(description="Name of the entity"),
    data_source_id: str = Field(description="ID of the data source"),
    data_source_object_id: str = Field(description="ID of the data source object"),
    source_record_id: str = Field(description="ID of the source record"),
) -> dict:
    """Look up the unified ID for a source record."""
    ensure_session()
    return get_connect_api().lookup_unified_id(
        entity_name=entity_name,
        data_source_id=data_source_id,
        data_source_object_id=data_source_object_id,
        source_record_id=source_record_id
    )
