"""
Calculated insight tools - query pre-aggregated metrics.
"""
import json
from typing import Optional
from pydantic import Field

from .base import mcp, ensure_session, get_connect_api, parse_json_param, resolve_field_default


@mcp.tool(description="List all calculated insights (pre-aggregated metrics)")
def list_calculated_insights() -> dict:
    """List all available calculated insights."""
    ensure_session()
    return get_connect_api().list_calculated_insights()


@mcp.tool(description="Get details for a specific calculated insight")
def get_calculated_insight(
    api_name: str = Field(description="API name of the calculated insight"),
) -> dict:
    """Get calculated insight definition and configuration."""
    ensure_session()
    return get_connect_api().get_calculated_insight(api_name)


@mcp.tool(description="Query a calculated insight with dimensions, measures, and filters")
def query_calculated_insight(
    insight_name: str = Field(description="Name of the calculated insight"),
    dimensions: Optional[str] = Field(default=None, description="Comma-separated dimension fields"),
    measures: Optional[str] = Field(default=None, description="Comma-separated measure fields"),
    filters: Optional[str] = Field(default=None, description="JSON-encoded filter conditions"),
    limit: Optional[int] = Field(default=None, description="Maximum records to return"),
) -> dict:
    """Query pre-aggregated metrics from a calculated insight."""
    ensure_session()

    # Resolve Field defaults for direct Python calls
    dimensions = resolve_field_default(dimensions)
    measures = resolve_field_default(measures)
    filters = resolve_field_default(filters)

    dim_list = dimensions.split(",") if dimensions else None
    meas_list = measures.split(",") if measures else None
    filter_list = None
    if filters:
        try:
            filter_list = json.loads(filters)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON in filters parameter"}

    return get_connect_api().query_calculated_insight(
        ci_name=insight_name,
        dimensions=dim_list,
        measures=meas_list,
        filters=filter_list,
        limit=resolve_field_default(limit)
    )


@mcp.tool(description="Get metadata for calculated insights")
def get_insight_metadata(
    ci_name: Optional[str] = Field(default=None, description="Filter by insight name"),
) -> dict:
    """Get metadata about calculated insights."""
    ensure_session()
    return get_connect_api().get_insight_metadata(ci_name=resolve_field_default(ci_name))


@mcp.tool(description="Update a calculated insight")
def update_calculated_insight(
    api_name: str = Field(description="API name of the insight to update"),
    updates: str = Field(description="JSON object with fields to update"),
) -> dict:
    """Update a calculated insight configuration."""
    ensure_session()
    update_data = parse_json_param(updates, "updates")
    return get_connect_api().update_calculated_insight(api_name, update_data)


@mcp.tool(description="Delete a calculated insight")
def delete_calculated_insight(
    api_name: str = Field(description="API name of the insight to delete"),
) -> dict:
    """Delete a calculated insight."""
    ensure_session()
    return get_connect_api().delete_calculated_insight(api_name)


@mcp.tool(description="Run a calculated insight calculation")
def run_calculated_insight(
    api_name: str = Field(description="API name of the insight to run"),
) -> dict:
    """Trigger calculation for a calculated insight."""
    ensure_session()
    return get_connect_api().run_calculated_insight(api_name)
