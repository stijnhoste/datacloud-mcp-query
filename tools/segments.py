"""
Segment tools - create, manage, and query segments.
"""
from typing import Optional
from pydantic import Field

from .base import mcp, ensure_session, get_connect_api, parse_json_param, resolve_field_default


@mcp.tool(description="List all segments in Data Cloud")
def list_segments() -> dict:
    """List all available segments."""
    ensure_session()
    return get_connect_api().list_segments()


@mcp.tool(description="Get details for a specific segment")
def get_segment(
    segment_name: str = Field(description="Name of the segment"),
) -> dict:
    """Get segment definition and metadata."""
    ensure_session()
    return get_connect_api().get_segment(segment_name)


@mcp.tool(description="Get members of a segment")
def get_segment_members(
    segment_name: str = Field(description="Name of the segment"),
    limit: int = Field(default=100, description="Maximum records to return"),
    offset: int = Field(default=0, description="Number of records to skip"),
) -> dict:
    """Get list of members belonging to a segment."""
    ensure_session()
    # Resolve Field defaults for direct Python calls
    resolved_limit = resolve_field_default(limit)
    resolved_offset = resolve_field_default(offset)
    return get_connect_api().get_segment_members(segment_name, limit=resolved_limit, offset=resolved_offset)


@mcp.tool(description="Count members in a segment")
def count_segment(
    segment_name: str = Field(description="Name of the segment"),
) -> dict:
    """Get the count of members in a segment."""
    ensure_session()
    return get_connect_api().count_segment(segment_name)


@mcp.tool(description="Create a new segment (API supports Dbt/Lookalike types only)")
def create_segment(
    segment_definition: str = Field(
        description="""JSON segment definition. Example:
{
  "developerName": "MySegment",
  "displayName": "My Test Segment",
  "description": "Segment description",
  "dataSpace": "default",
  "segmentOnApiName": "ssot__Individual__dlm",
  "segmentType": "Standard",
  "publishSchedule": "Manual"
}
NOTE: API only supports Dbt and Lookalike segment types. Standard segments should be created via the UI."""
    ),
) -> dict:
    """Create a new segment from JSON definition."""
    ensure_session()
    definition = parse_json_param(segment_definition, "segment_definition")
    return get_connect_api().create_segment(definition)


@mcp.tool(description="Update an existing segment")
def update_segment(
    segment_name: str = Field(description="Name of the segment to update"),
    updates: str = Field(description="JSON object with fields to update"),
) -> dict:
    """Update segment properties."""
    ensure_session()
    update_data = parse_json_param(updates, "updates")
    return get_connect_api().update_segment(segment_name, update_data)


@mcp.tool(description="Delete a segment")
def delete_segment(
    segment_name: str = Field(description="Name of the segment to delete"),
) -> dict:
    """Delete a segment permanently."""
    ensure_session()
    return get_connect_api().delete_segment(segment_name)


@mcp.tool(description="Publish a segment for activation")
def publish_segment(
    segment_name: str = Field(description="Name of the segment to publish"),
) -> dict:
    """Publish a segment to make it available for activation."""
    ensure_session()
    return get_connect_api().publish_segment(segment_name)


@mcp.tool(description="Deactivate a segment")
def deactivate_segment(
    segment_name: str = Field(description="Name of the segment to deactivate"),
) -> dict:
    """Deactivate a published segment."""
    ensure_session()
    return get_connect_api().deactivate_segment(segment_name)
