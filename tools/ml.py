"""
Machine Learning and AI tools - models, predictions, Document AI, and semantic search.
"""
from typing import Optional
from pydantic import Field

from .base import mcp, ensure_session, get_connect_api, parse_json_param, resolve_field_default


# ============================================================
# ML Models
# ============================================================

@mcp.tool(description="List all ML models")
def list_ml_models() -> dict:
    """List all configured ML models."""
    ensure_session()
    return get_connect_api().list_ml_models()


@mcp.tool(description="Get details for a specific ML model")
def get_ml_model(
    model_name: str = Field(description="Name of the ML model"),
) -> dict:
    """Get ML model configuration and details."""
    ensure_session()
    return get_connect_api().get_ml_model(model_name)


@mcp.tool(description="Update an ML model")
def update_ml_model(
    model_name: str = Field(description="Name of the model to update"),
    updates: str = Field(description="JSON object with fields to update"),
) -> dict:
    """Update ML model configuration."""
    ensure_session()
    update_data = parse_json_param(updates, "updates")
    return get_connect_api().update_ml_model(model_name, update_data)


@mcp.tool(description="Delete an ML model")
def delete_ml_model(
    model_name: str = Field(description="Name of the model to delete"),
) -> dict:
    """Delete an ML model."""
    ensure_session()
    return get_connect_api().delete_ml_model(model_name)


@mcp.tool(description="Get predictions from an ML model")
def get_prediction(
    model_name: str = Field(description="Name of the ML model"),
    input_data: str = Field(description="JSON input data for prediction"),
) -> dict:
    """Get predictions from an ML model."""
    ensure_session()
    data = parse_json_param(input_data, "input_data")
    return get_connect_api().get_prediction(model_name, data)


# ============================================================
# Model Artifacts
# ============================================================

@mcp.tool(description="List all model artifacts")
def list_model_artifacts() -> dict:
    """List all ML model artifacts."""
    ensure_session()
    return get_connect_api().list_model_artifacts()


@mcp.tool(description="Get a specific model artifact")
def get_model_artifact(
    artifact_name: str = Field(description="Name of the artifact"),
) -> dict:
    """Get model artifact details."""
    ensure_session()
    return get_connect_api().get_model_artifact(artifact_name)


@mcp.tool(description="Update a model artifact")
def update_model_artifact(
    artifact_name: str = Field(description="Name of the artifact to update"),
    updates: str = Field(description="JSON object with fields to update"),
) -> dict:
    """Update a model artifact."""
    ensure_session()
    update_data = parse_json_param(updates, "updates")
    return get_connect_api().update_model_artifact(artifact_name, update_data)


@mcp.tool(description="Delete a model artifact")
def delete_model_artifact(
    artifact_name: str = Field(description="Name of the artifact to delete"),
) -> dict:
    """Delete a model artifact."""
    ensure_session()
    return get_connect_api().delete_model_artifact(artifact_name)


# ============================================================
# Document AI
# ============================================================

@mcp.tool(description="List all Document AI configurations")
def list_document_ai_configs() -> dict:
    """List all Document AI configurations."""
    ensure_session()
    return get_connect_api().list_document_ai_configs()


@mcp.tool(description="Get a Document AI configuration")
def get_document_ai_config(
    config_id: str = Field(description="ID of the Document AI configuration"),
) -> dict:
    """Get Document AI configuration details."""
    ensure_session()
    return get_connect_api().get_document_ai_config(config_id)


@mcp.tool(description="Create a Document AI configuration")
def create_document_ai_config(
    config_definition: str = Field(description="JSON definition for the configuration"),
) -> dict:
    """Create a new Document AI configuration."""
    ensure_session()
    definition = parse_json_param(config_definition, "config_definition")
    return get_connect_api().create_document_ai_config(definition)


@mcp.tool(description="Update a Document AI configuration")
def update_document_ai_config(
    config_id: str = Field(description="ID of the configuration to update"),
    updates: str = Field(description="JSON object with fields to update"),
) -> dict:
    """Update a Document AI configuration."""
    ensure_session()
    update_data = parse_json_param(updates, "updates")
    return get_connect_api().update_document_ai_config(config_id, update_data)


@mcp.tool(description="Delete a Document AI configuration")
def delete_document_ai_config(
    config_id: str = Field(description="ID of the configuration to delete"),
) -> dict:
    """Delete a Document AI configuration."""
    ensure_session()
    return get_connect_api().delete_document_ai_config(config_id)


@mcp.tool(description="Run Document AI extraction")
def run_document_ai(
    config_id: str = Field(description="ID of the Document AI configuration"),
) -> dict:
    """Run Document AI extraction job."""
    ensure_session()
    return get_connect_api().run_document_ai(config_id)


@mcp.tool(description="Extract data from a document using Document AI")
def extract_document_data(
    config_name: str = Field(description="Name of the Document AI configuration"),
    document_data: str = Field(description="JSON-encoded document content and metadata"),
) -> dict:
    """Extract structured data from a document."""
    ensure_session()
    data = parse_json_param(document_data, "document_data")
    return get_connect_api().extract_document_data(config_name, data)


@mcp.tool(description="Generate schema from a document")
def generate_document_schema(
    request_data: str = Field(description="JSON request for schema generation"),
) -> dict:
    """Generate a schema from a sample document."""
    ensure_session()
    data = parse_json_param(request_data, "request_data")
    return get_connect_api().generate_document_schema(data)


@mcp.tool(description="Get Document AI global configuration")
def get_document_ai_global_config() -> dict:
    """Get global Document AI settings."""
    ensure_session()
    return get_connect_api().get_document_ai_global_config()


# ============================================================
# Semantic Search
# ============================================================

@mcp.tool(description="List all semantic search configurations")
def list_semantic_searches() -> dict:
    """List all semantic search indexes."""
    ensure_session()
    return get_connect_api().list_semantic_searches()


@mcp.tool(description="Get details for a specific semantic search")
def get_semantic_search(
    search_name: str = Field(description="Name or ID of the semantic search"),
) -> dict:
    """Get semantic search configuration."""
    ensure_session()
    return get_connect_api().get_semantic_search(search_name)


@mcp.tool(description="Create a semantic search index")
def create_semantic_search(
    search_definition: str = Field(description="JSON definition for the search index"),
) -> dict:
    """Create a new semantic search index."""
    ensure_session()
    definition = parse_json_param(search_definition, "search_definition")
    return get_connect_api().create_semantic_search(definition)


@mcp.tool(description="Update a semantic search index")
def update_semantic_search(
    search_id: str = Field(description="ID of the search index to update"),
    updates: str = Field(description="JSON object with fields to update"),
) -> dict:
    """Update a semantic search index."""
    ensure_session()
    update_data = parse_json_param(updates, "updates")
    return get_connect_api().update_semantic_search(search_id, update_data)


@mcp.tool(description="Delete a semantic search index")
def delete_semantic_search(
    search_id: str = Field(description="ID of the search index to delete"),
) -> dict:
    """Delete a semantic search index."""
    ensure_session()
    return get_connect_api().delete_semantic_search(search_id)


@mcp.tool(description="Get global semantic search configuration")
def get_semantic_search_config() -> dict:
    """Get global semantic search settings."""
    ensure_session()
    return get_connect_api().get_semantic_search_config()
