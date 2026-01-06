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


@mcp.tool(description="Create a data action")
def create_data_action(
    action_definition: str = Field(description="JSON definition for the data action"),
) -> dict:
    """Create a new data action."""
    ensure_session()
    definition = parse_json_param(action_definition, "action_definition")
    return get_connect_api().create_data_action(definition)


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


@mcp.tool(description="Create a data action target")
def create_data_action_target(
    target_definition: str = Field(description="JSON definition for the target"),
) -> dict:
    """Create a new data action target."""
    ensure_session()
    definition = parse_json_param(target_definition, "target_definition")
    return get_connect_api().create_data_action_target(definition)


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
# Private Network Routes
# ============================================================

@mcp.tool(description="List all private network routes")
def list_private_network_routes() -> dict:
    """List all private network routes."""
    ensure_session()
    return get_connect_api().list_private_network_routes()


@mcp.tool(description="Get a private network route")
def get_private_network_route(
    route_id: str = Field(description="ID of the route"),
) -> dict:
    """Get private network route details."""
    ensure_session()
    return get_connect_api().get_private_network_route(route_id)


@mcp.tool(description="Create a private network route")
def create_private_network_route(
    route_definition: str = Field(description="JSON definition for the route"),
) -> dict:
    """Create a new private network route."""
    ensure_session()
    definition = parse_json_param(route_definition, "route_definition")
    return get_connect_api().create_private_network_route(definition)


@mcp.tool(description="Delete a private network route")
def delete_private_network_route(
    route_id: str = Field(description="ID of the route to delete"),
) -> dict:
    """Delete a private network route."""
    ensure_session()
    return get_connect_api().delete_private_network_route(route_id)


# ============================================================
# Data Kits
# ============================================================

@mcp.tool(description="Get status of a data kit component")
def get_data_kit_status(
    component_id: str = Field(description="ID of the data kit component"),
) -> dict:
    """Get deployment status for a data kit component."""
    ensure_session()
    return get_connect_api().get_data_kit_status(component_id)


@mcp.tool(description="Undeploy a data kit")
def undeploy_data_kit(
    data_kit_name: str = Field(description="Name of the data kit to undeploy"),
) -> dict:
    """Undeploy a data kit from the org."""
    ensure_session()
    return get_connect_api().undeploy_data_kit(data_kit_name)


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
