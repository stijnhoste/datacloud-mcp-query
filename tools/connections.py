"""
Connection tools - manage data source connections.
"""
from typing import Optional
from pydantic import Field

from .base import mcp, ensure_session, get_connect_api, parse_json_param, resolve_field_default


@mcp.tool(description="List all connections")
def list_connections(
    connector_type: str = Field(description="Connector type (required). Use list_connectors() to see available types."),
) -> dict:
    """List all data source connections of a specific type."""
    ensure_session()
    if not connector_type:
        return {"error": "connector_type is required. Use list_connectors() to see available types."}
    return get_connect_api().list_connections(connector_type=connector_type)


@mcp.tool(description="Get details for a specific connection")
def get_connection(
    connection_id: str = Field(description="ID of the connection"),
) -> dict:
    """Get connection configuration and status."""
    ensure_session()
    return get_connect_api().get_connection(connection_id)


@mcp.tool(description="Update a connection")
def update_connection(
    connection_id: str = Field(description="ID of the connection"),
    updates: str = Field(description="JSON object with fields to update"),
) -> dict:
    """Update connection configuration."""
    ensure_session()
    update_data = parse_json_param(updates, "updates")
    return get_connect_api().update_connection(connection_id, update_data)


@mcp.tool(description="Delete a connection")
def delete_connection(
    connection_id: str = Field(description="ID of the connection to delete"),
) -> dict:
    """Delete a connection permanently."""
    ensure_session()
    return get_connect_api().delete_connection(connection_id)


@mcp.tool(description="Get available objects from a connection")
def get_connection_objects(
    connection_id: str = Field(description="ID of the connection"),
) -> dict:
    """List objects available from this connection."""
    ensure_session()
    return get_connect_api().get_connection_objects(connection_id)


@mcp.tool(description="Preview data from a connection object")
def preview_connection(
    connection_id: str = Field(description="ID of the connection"),
    object_name: str = Field(description="Name of the object to preview"),
    limit: int = Field(default=10, description="Maximum rows to return"),
) -> dict:
    """Preview sample data from a connection object."""
    ensure_session()
    return get_connect_api().preview_connection(connection_id, object_name, limit=limit)


@mcp.tool(description="Get schema for a connection")
def get_connection_schema(
    connection_id: str = Field(description="ID of the connection"),
) -> dict:
    """Get the schema information for a connection."""
    ensure_session()
    return get_connect_api().get_connection_schema(connection_id)


@mcp.tool(description="Get endpoints for a connection")
def get_connection_endpoints(
    connection_id: str = Field(description="ID of the connection"),
) -> dict:
    """Get available endpoints for a connection."""
    ensure_session()
    return get_connect_api().get_connection_endpoints(connection_id)


@mcp.tool(description="Get databases for a connection")
def get_connection_databases(
    connection_id: str = Field(description="ID of the connection"),
) -> dict:
    """List databases available from this connection."""
    ensure_session()
    return get_connect_api().get_connection_databases(connection_id)


@mcp.tool(description="Get database schemas for a connection")
def get_connection_database_schemas(
    connection_id: str = Field(description="ID of the connection"),
    database: Optional[str] = Field(default=None, description="Database name to filter by"),
) -> dict:
    """List schemas in a database from this connection."""
    ensure_session()
    return get_connect_api().get_connection_database_schemas(
        connection_id,
        database=resolve_field_default(database)
    )


# ============================================================
# Connectors
# ============================================================

@mcp.tool(description="List available connector types")
def list_connectors() -> dict:
    """List all available connector types that can be used to create connections."""
    ensure_session()
    return get_connect_api().list_connectors()


@mcp.tool(description="Get details for a specific connector type")
def get_connector(
    connector_type: str = Field(description="The connector type"),
) -> dict:
    """Get configuration schema and details for a connector type."""
    ensure_session()
    return get_connect_api().get_connector(connector_type)
