"""
Admin and monitoring tools - limits, data actions, network routes, data kits.
"""
from pydantic import Field

from .base import mcp, ensure_session, get_connect_api, parse_json_param


# ============================================================
# API Limits and Monitoring
# ============================================================

@mcp.tool(description="Get API limits and usage statistics")
def get_limits() -> dict:
    """Get current API limits and usage."""
    ensure_session()
    return get_connect_api().get_limits()


# ============================================================
# Data Actions
# ============================================================

@mcp.tool(description="List all data actions")
def list_data_actions() -> dict:
    """List all event-driven data actions."""
    ensure_session()
    return get_connect_api().list_data_actions()


# ============================================================
# Data Action Targets
# ============================================================

@mcp.tool(description="List all data action targets")
def list_data_action_targets() -> dict:
    """List all webhook/external targets for data actions."""
    ensure_session()
    return get_connect_api().list_data_action_targets()


@mcp.tool(description="Get a data action target")
def get_data_action_target(
    api_name: str = Field(description="API name of the target"),
) -> dict:
    """Get data action target details."""
    ensure_session()
    return get_connect_api().get_data_action_target(api_name)


@mcp.tool(description="Delete a data action target")
def delete_data_action_target(
    api_name: str = Field(description="API name of the target to delete"),
) -> dict:
    """Delete a data action target."""
    ensure_session()
    return get_connect_api().delete_data_action_target(api_name)


@mcp.tool(description="Get signing key for a data action target")
def get_data_action_target_signing_key(
    api_name: str = Field(description="API name of the target"),
) -> dict:
    """Get the signing key for webhook authentication."""
    ensure_session()
    return get_connect_api().get_data_action_target_signing_key(api_name)


# ============================================================
# Data Kits
# ============================================================

@mcp.tool(description="Get data kit component dependencies")
def get_data_kit_component_dependencies(
    data_kit_name: str = Field(description="Name of the data kit"),
    component_name: str = Field(description="Name of the component"),
) -> dict:
    """Get dependencies for a data kit component."""
    ensure_session()
    return get_connect_api().get_data_kit_component_dependencies(data_kit_name, component_name)


@mcp.tool(description="Get data kit deployment status")
def get_data_kit_deployment_status(
    data_kit_name: str = Field(description="Name of the data kit"),
    component_name: str = Field(description="Name of the component"),
) -> dict:
    """Get detailed deployment status for a data kit component."""
    ensure_session()
    return get_connect_api().get_data_kit_deployment_status(data_kit_name, component_name)
