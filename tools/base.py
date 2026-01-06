"""
Base module for MCP tools - session management, helpers, and shared state.
"""
import json
import logging
import os
import re
from typing import Optional

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

# ============================================================
# MCP Server Instance (shared across all tool modules)
# ============================================================
mcp = FastMCP("Data Cloud MCP Server")

# ============================================================
# Configuration
# ============================================================
DEFAULT_ORG = os.getenv('DC_DEFAULT_ORG', None)
DEFAULT_LIST_TABLE_FILTER = os.getenv('DEFAULT_LIST_TABLE_FILTER', '%')

# ============================================================
# Global Session State
# ============================================================
_session = None
_connect_api = None
_current_org: Optional[str] = None


class SFCLISession:
    """Session adapter wrapping SF CLI auth for connect_api and run_query."""

    def __init__(self, sf_auth, alias_or_username: str):
        self.sf_auth = sf_auth
        self.sf_auth.set_target_org(alias_or_username)

    def get_token(self) -> str:
        token, _ = self.sf_auth.get_access_token()
        return token

    def get_instance_url(self) -> str:
        _, instance_url = self.sf_auth.get_access_token()
        return instance_url


def init_session(alias_or_username: str):
    """Initialize session using SF CLI credentials."""
    global _session, _connect_api, _current_org

    from sf_cli_auth import SFCLIAuth
    from clients import ConnectAPIClient

    _session = SFCLISession(SFCLIAuth(), alias_or_username)
    _connect_api = ConnectAPIClient(_session)
    _current_org = alias_or_username
    logger.info(f"Connected to org: {alias_or_username}")


def ensure_session():
    """Ensure we have an active session."""
    if _session is not None:
        return
    if DEFAULT_ORG:
        init_session(DEFAULT_ORG)
    else:
        raise RuntimeError(
            "No org selected. Use list_orgs() to see available orgs, "
            "then set_target_org(alias) to select one."
        )


def get_session():
    """Get the current session."""
    ensure_session()
    return _session


def get_connect_api():
    """Get the Connect API client."""
    ensure_session()
    return _connect_api


def get_current_org() -> Optional[str]:
    """Get the current org alias."""
    return _current_org


# ============================================================
# Helper Functions
# ============================================================

def resolve_field_default(value):
    """
    Resolve Field() defaults when called directly (not through MCP).

    When functions with Field() defaults are called directly,
    the Field() returns a FieldInfo object instead of the actual default.
    """
    from pydantic.fields import FieldInfo
    from pydantic_core import PydanticUndefined
    if isinstance(value, FieldInfo):
        if value.default is PydanticUndefined:
            return None
        return value.default
    return value


def validate_identifier(name: str, identifier_type: str = "identifier") -> str:
    """Validate SQL identifier to prevent injection."""
    if not name:
        raise ValueError(f"Empty {identifier_type} name")

    if not re.match(r'^[a-zA-Z0-9_%]+$', name):
        raise ValueError(
            f"Invalid {identifier_type} name: {name}. "
            "Only alphanumeric, underscores, and percent signs allowed."
        )

    sql_keywords = {'DROP', 'DELETE', 'INSERT', 'UPDATE', 'TRUNCATE',
                   'ALTER', 'CREATE', 'EXEC', 'EXECUTE', '--', ';'}
    if name.upper() in sql_keywords or '--' in name or ';' in name:
        raise ValueError(f"Invalid {identifier_type} name: {name}. SQL keywords not allowed.")

    return name


def normalize_field_definitions(definition: dict) -> dict:
    """
    Normalize field definitions to use 'dataType' instead of 'type'.

    The Postman samples use 'type' but the API expects 'dataType'.
    """
    if 'fields' in definition and isinstance(definition['fields'], list):
        for field in definition['fields']:
            if 'type' in field and 'dataType' not in field:
                field['dataType'] = field.pop('type')
    return definition


def parse_json_param(param: str, param_name: str) -> dict:
    """Parse a JSON string parameter, returning error dict if invalid."""
    try:
        return json.loads(param)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {param_name}: {e}")
