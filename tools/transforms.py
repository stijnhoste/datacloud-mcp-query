"""
Data transform tools - manage data transformation jobs.
"""
from pydantic import Field

from .base import mcp, ensure_session, get_connect_api, parse_json_param


@mcp.tool(description="List all data transforms")
def list_data_transforms() -> dict:
    """List all data transformation jobs."""
    ensure_session()
    return get_connect_api().list_data_transforms()


@mcp.tool(description="Get details for a specific data transform")
def get_data_transform(
    transform_name: str = Field(description="Name or ID of the transform"),
) -> dict:
    """Get data transform configuration and status."""
    ensure_session()
    return get_connect_api().get_data_transform(transform_name)


@mcp.tool(description="Create a new data transform")
def create_data_transform(
    transform_definition: str = Field(description="JSON definition for the transform"),
) -> dict:
    """Create a new data transformation job."""
    ensure_session()
    definition = parse_json_param(transform_definition, "transform_definition")
    return get_connect_api().create_data_transform(definition)


@mcp.tool(description="Update a data transform")
def update_data_transform(
    transform_name: str = Field(description="Name or ID of the transform"),
    updates: str = Field(description="JSON object with fields to update"),
) -> dict:
    """Update data transform configuration."""
    ensure_session()
    update_data = parse_json_param(updates, "updates")
    return get_connect_api().update_data_transform(transform_name, update_data)


@mcp.tool(description="Delete a data transform")
def delete_data_transform(
    transform_name: str = Field(description="Name or ID of the transform to delete"),
) -> dict:
    """Delete a data transform permanently."""
    ensure_session()
    return get_connect_api().delete_data_transform(transform_name)


@mcp.tool(description="Run a data transform")
def run_data_transform(
    transform_name: str = Field(description="Name or ID of the transform to run"),
) -> dict:
    """Trigger data transform execution."""
    ensure_session()
    return get_connect_api().run_data_transform(transform_name)


@mcp.tool(description="Cancel a running data transform")
def cancel_data_transform(
    transform_name: str = Field(description="Name or ID of the transform to cancel"),
) -> dict:
    """Cancel a running data transform job."""
    ensure_session()
    return get_connect_api().cancel_data_transform(transform_name)


@mcp.tool(description="Retry a failed data transform")
def retry_data_transform(
    transform_name: str = Field(description="Name or ID of the transform to retry"),
) -> dict:
    """Retry a failed data transform job."""
    ensure_session()
    return get_connect_api().retry_data_transform(transform_name)


@mcp.tool(description="Get run history for a data transform")
def get_transform_run_history(
    transform_name: str = Field(description="Name or ID of the transform"),
) -> dict:
    """Get historical run information for a transform."""
    ensure_session()
    return get_connect_api().get_transform_run_history(transform_name)


@mcp.tool(description="Get schedule for a data transform")
def get_transform_schedule(
    transform_name: str = Field(description="Name or ID of the transform"),
) -> dict:
    """Get the schedule configuration for a transform."""
    ensure_session()
    return get_connect_api().get_transform_schedule(transform_name)


@mcp.tool(description="Update schedule for a data transform")
def update_transform_schedule(
    transform_name: str = Field(description="Name or ID of the transform"),
    schedule: str = Field(description="JSON schedule configuration"),
) -> dict:
    """Update the schedule for a transform."""
    ensure_session()
    schedule_data = parse_json_param(schedule, "schedule")
    return get_connect_api().update_transform_schedule(transform_name, schedule_data)


@mcp.tool(description="Validate a data transform definition")
def validate_data_transform(
    transform_definition: str = Field(description="JSON transform definition to validate"),
) -> dict:
    """Validate a transform definition without creating it."""
    ensure_session()
    definition = parse_json_param(transform_definition, "transform_definition")
    return get_connect_api().validate_data_transform(definition)
