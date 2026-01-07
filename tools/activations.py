"""
Activation tools - manage activations and activation targets.
"""
from typing import Optional
from pydantic import Field

from .base import mcp, ensure_session, get_connect_api, parse_json_param


# ============================================================
# Activation Targets
# ============================================================

@mcp.tool(description="List all activation targets")
def list_activation_targets() -> dict:
    """List available activation targets (destinations)."""
    ensure_session()
    return get_connect_api().list_activation_targets()


@mcp.tool(description="Get details for a specific activation target")
def get_activation_target(
    target_id: str = Field(description="ID of the activation target"),
) -> dict:
    """Get activation target configuration."""
    ensure_session()
    return get_connect_api().get_activation_target(target_id)


@mcp.tool(description="Update an activation target")
def update_activation_target(
    target_id: str = Field(description="ID of the activation target"),
    updates: str = Field(description="JSON object with fields to update"),
) -> dict:
    """Update activation target configuration."""
    ensure_session()
    update_data = parse_json_param(updates, "updates")
    return get_connect_api().update_activation_target(target_id, update_data)


# ============================================================
# Activations
# ============================================================

@mcp.tool(description="List all activations")
def list_activations() -> dict:
    """List all segment activations."""
    ensure_session()
    return get_connect_api().list_activations()


@mcp.tool(description="Get details for a specific activation")
def get_activation(
    activation_id: str = Field(description="ID of the activation"),
) -> dict:
    """Get activation configuration and status."""
    ensure_session()
    return get_connect_api().get_activation(activation_id)


@mcp.tool(description="Update an activation")
def update_activation(
    activation_id: str = Field(description="ID of the activation"),
    updates: str = Field(description="JSON object with fields to update"),
) -> dict:
    """Update activation configuration."""
    ensure_session()
    update_data = parse_json_param(updates, "updates")
    return get_connect_api().update_activation(activation_id, update_data)


@mcp.tool(description="Delete an activation")
def delete_activation(
    activation_id: str = Field(description="ID of the activation to delete"),
) -> dict:
    """Delete an activation permanently."""
    ensure_session()
    return get_connect_api().delete_activation(activation_id)


@mcp.tool(description="Get audience DMO records for an activation")
def get_audience_records(
    activation_id: str = Field(description="ID of the activation"),
    limit: int = Field(default=100, description="Maximum records to return"),
    offset: int = Field(default=0, description="Number of records to skip"),
) -> dict:
    """Get the audience records that will be sent to the activation target."""
    ensure_session()
    return get_connect_api().get_audience_records(activation_id, limit=limit, offset=offset)


@mcp.tool(description="List external activation platforms")
def list_activation_external_platforms() -> dict:
    """List available external platforms for activations."""
    ensure_session()
    return get_connect_api().list_activation_external_platforms()
