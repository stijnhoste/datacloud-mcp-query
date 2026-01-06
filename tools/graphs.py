"""
Data graph tools - query unified profiles across related entities.
"""
import json
from typing import Optional
from pydantic import Field

from .base import mcp, ensure_session, get_connect_api, parse_json_param, resolve_field_default


@mcp.tool(description="List all data graphs")
def list_data_graphs() -> dict:
    """List all available data graphs."""
    ensure_session()
    return get_connect_api().get_data_graph_metadata()


@mcp.tool(description="Get details for a specific data graph")
def get_data_graph(
    graph_name: str = Field(description="Name of the data graph"),
) -> dict:
    """Get data graph definition and configuration."""
    ensure_session()
    return get_connect_api().get_data_graph(graph_name)


@mcp.tool(description="Query a data graph for a complete profile with related records")
def query_data_graph(
    graph_name: str = Field(description="Name of the data graph entity"),
    record_id: Optional[str] = Field(default=None, description="ID of the record"),
    lookup_keys: Optional[str] = Field(default=None, description="JSON object of lookup key fields/values"),
) -> dict:
    """Query a unified profile from a data graph."""
    ensure_session()
    record_id = resolve_field_default(record_id)
    lookup_keys_str = resolve_field_default(lookup_keys)

    if record_id:
        return get_connect_api().query_data_graph_by_id(graph_name, record_id)
    elif lookup_keys_str:
        try:
            keys = json.loads(lookup_keys_str)
            return get_connect_api().query_data_graph_by_lookup(graph_name, keys)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON in lookup_keys parameter"}
    else:
        return {"error": "Must provide either record_id or lookup_keys"}


@mcp.tool(description="Create a data graph")
def create_data_graph(
    graph_definition: str = Field(description="JSON definition for the data graph"),
) -> dict:
    """Create a new data graph."""
    ensure_session()
    definition = parse_json_param(graph_definition, "graph_definition")
    return get_connect_api().create_data_graph(definition)


@mcp.tool(description="Delete a data graph")
def delete_data_graph(
    graph_name: str = Field(description="Name of the data graph to delete"),
) -> dict:
    """Delete a data graph."""
    ensure_session()
    return get_connect_api().delete_data_graph(graph_name)


@mcp.tool(description="Refresh a data graph")
def refresh_data_graph(
    graph_name: str = Field(description="Name of the data graph to refresh"),
) -> dict:
    """Trigger a refresh for a data graph."""
    ensure_session()
    return get_connect_api().refresh_data_graph(graph_name)
