"""
Profile query tools - query DMO records directly.
"""
from typing import Optional
from pydantic import Field

from .base import mcp, ensure_session, get_connect_api, resolve_field_default


@mcp.tool(description="Query profile records from a DMO")
def query_profile(
    dmo_name: str = Field(description="Name of the DMO to query"),
    limit: Optional[int] = Field(default=None, description="Maximum records to return"),
    offset: Optional[int] = Field(default=None, description="Number of records to skip"),
) -> dict:
    """Query records from a DMO profile."""
    ensure_session()
    return get_connect_api().query_profile(
        dmo_name=dmo_name,
        limit=resolve_field_default(limit),
        offset=resolve_field_default(offset)
    )


@mcp.tool(description="Get a specific profile record by ID")
def get_profile_record(
    dmo_name: str = Field(description="Name of the DMO"),
    record_id: str = Field(description="ID of the record"),
) -> dict:
    """Get a single profile record by its ID."""
    ensure_session()
    return get_connect_api().get_profile_record(dmo_name, record_id)


@mcp.tool(description="Get a profile record with its child records")
def get_profile_record_with_children(
    dmo_name: str = Field(description="Name of the parent DMO"),
    record_id: str = Field(description="ID of the parent record"),
    child_dmo_name: str = Field(description="Name of the child DMO"),
) -> dict:
    """Get a profile record along with related child records."""
    ensure_session()
    return get_connect_api().get_profile_record_with_children(dmo_name, record_id, child_dmo_name)


@mcp.tool(description="Get a profile record with calculated insights")
def get_profile_record_with_insights(
    dmo_name: str = Field(description="Name of the DMO"),
    record_id: str = Field(description="ID of the record"),
    ci_name: str = Field(description="Name of the calculated insight"),
) -> dict:
    """Get a profile record with its calculated insight values."""
    ensure_session()
    return get_connect_api().get_profile_record_with_insights(dmo_name, record_id, ci_name)
