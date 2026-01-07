"""
Data stream tools - manage data ingestion streams.
"""
from pydantic import Field

from .base import mcp, ensure_session, get_connect_api, parse_json_param


@mcp.tool(description="List all data streams")
def list_data_streams() -> dict:
    """List all data ingestion streams."""
    ensure_session()
    return get_connect_api().list_data_streams()


@mcp.tool(description="Get details for a specific data stream")
def get_data_stream(
    stream_name: str = Field(description="Name or ID of the data stream"),
) -> dict:
    """Get data stream configuration and status."""
    ensure_session()
    return get_connect_api().get_data_stream(stream_name)


@mcp.tool(description="Update a data stream")
def update_data_stream(
    stream_name: str = Field(description="Name or ID of the data stream"),
    updates: str = Field(description="JSON object with fields to update"),
) -> dict:
    """Update data stream configuration."""
    ensure_session()
    update_data = parse_json_param(updates, "updates")
    return get_connect_api().update_data_stream(stream_name, update_data)


@mcp.tool(description="Delete a data stream")
def delete_data_stream(
    stream_name: str = Field(description="Name or ID of the data stream to delete"),
) -> dict:
    """Delete a data stream permanently."""
    ensure_session()
    return get_connect_api().delete_data_stream(stream_name)
