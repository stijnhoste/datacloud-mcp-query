"""
Org management tools - list, select, and manage Salesforce orgs.
"""
from pydantic import Field
from sf_cli_auth import sf_cli

from .base import mcp, init_session, get_current_org


@mcp.tool(description="List all Salesforce orgs authenticated via SF CLI")
def list_orgs() -> list[dict]:
    """Returns a list of all orgs authenticated via SF CLI."""
    orgs = sf_cli.list_orgs(refresh=True)
    return [org.to_dict() for org in orgs]


@mcp.tool(description="Set the target org for Data Cloud operations")
def set_target_org(
    alias_or_username: str = Field(description="Org alias (e.g., 'my-dc-org') or username"),
) -> dict:
    """Switch to a different Salesforce org for all subsequent operations."""
    try:
        init_session(alias_or_username)
        org = sf_cli.get_org(alias_or_username)
        return {
            "success": True,
            "message": f"Now connected to: {org.display_name}",
            "org": org.to_dict() if org else None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool(description="Get the currently selected org")
def get_target_org() -> dict:
    """Returns information about the currently selected Salesforce org."""
    current = get_current_org()
    if current is None:
        return {
            "connected": False,
            "message": "No org selected. Use list_orgs() and set_target_org(alias) to connect."
        }
    org = sf_cli.get_org(current)
    return {"connected": True, "org": org.to_dict() if org else None}
