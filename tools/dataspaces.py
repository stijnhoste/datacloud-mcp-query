"""
Data space tools - manage logical data partitions.
"""
from pydantic import Field

from .base import mcp, ensure_session, get_connect_api, parse_json_param


@mcp.tool(description="List all data spaces")
def list_data_spaces() -> dict:
    """List all data spaces in the instance."""
    ensure_session()
    return get_connect_api().list_data_spaces()


@mcp.tool(description="Get details for a specific data space")
def get_data_space(
    space_name: str = Field(description="Name or ID of the data space"),
) -> dict:
    """Get data space configuration."""
    ensure_session()
    return get_connect_api().get_data_space(space_name)


@mcp.tool(description="Update a data space")
def update_data_space(
    space_name: str = Field(description="Name or ID of the data space"),
    updates: str = Field(description="JSON object with fields to update"),
) -> dict:
    """Update data space configuration."""
    ensure_session()
    update_data = parse_json_param(updates, "updates")
    return get_connect_api().update_data_space(space_name, update_data)


@mcp.tool(description="Get members (objects) in a data space")
def get_data_space_members(
    space_name: str = Field(description="Name or ID of the data space"),
) -> dict:
    """List all objects belonging to a data space."""
    ensure_session()
    return get_connect_api().get_data_space_members(space_name)


@mcp.tool(description="Update members in a data space")
def update_data_space_members(
    space_name: str = Field(description="Name or ID of the data space"),
    members: str = Field(description="JSON object defining member updates"),
) -> dict:
    """Update which objects belong to a data space."""
    ensure_session()
    members_data = parse_json_param(members, "members")
    return get_connect_api().update_data_space_members(space_name, members_data)


@mcp.tool(description="Get a specific member in a data space")
def get_data_space_member(
    space_name: str = Field(description="Name or ID of the data space"),
    member_name: str = Field(description="Name of the member object"),
) -> dict:
    """Get details for a specific member in a data space."""
    ensure_session()
    return get_connect_api().get_data_space_member(space_name, member_name)
