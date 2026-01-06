"""
Salesforce CLI Authentication Integration

Integrates with SF CLI's existing auth storage to avoid duplicate credential management.
Users authenticate orgs via `sf org login web` and this module reads those credentials.
"""

import json
import logging
import subprocess
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class SFOrg:
    """Represents an authenticated Salesforce org from SF CLI."""
    username: str
    alias: Optional[str]
    instance_url: str
    access_token: str
    org_id: str
    is_sandbox: bool
    is_scratch: bool
    org_name: str
    connected_status: str

    @property
    def display_name(self) -> str:
        """Return alias if available, otherwise username."""
        return self.alias or self.username

    def to_dict(self) -> dict:
        """Return safe dict representation (no token)."""
        return {
            "username": self.username,
            "alias": self.alias,
            "instance_url": self.instance_url,
            "org_id": self.org_id,
            "is_sandbox": self.is_sandbox,
            "is_scratch": self.is_scratch,
            "org_name": self.org_name,
            "connected_status": self.connected_status,
        }


class SFCLIAuth:
    """
    Manages authentication by integrating with Salesforce CLI.

    Instead of storing credentials ourselves, we leverage SF CLI's
    existing encrypted auth storage. Users authenticate via:
        sf org login web --alias my-org

    Then this class reads those credentials.
    """

    def __init__(self):
        self._orgs_cache: Optional[list[SFOrg]] = None
        self._target_org: Optional[str] = None  # alias or username

    def _run_sf_command(self, args: list[str]) -> dict:
        """Run SF CLI command and return JSON output."""
        cmd = ["sf"] + args + ["--json"]
        logger.debug(f"Running SF CLI: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                logger.error(f"SF CLI error: {error_msg}")
                raise RuntimeError(f"SF CLI command failed: {error_msg}")

            return json.loads(result.stdout)

        except subprocess.TimeoutExpired:
            raise RuntimeError("SF CLI command timed out")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse SF CLI output: {e}")
        except FileNotFoundError:
            raise RuntimeError(
                "SF CLI not found. Install it with: npm install -g @salesforce/cli"
            )

    def list_orgs(self, refresh: bool = False) -> list[SFOrg]:
        """
        List all authenticated orgs from SF CLI.

        Args:
            refresh: Force refresh from SF CLI (bypass cache)

        Returns:
            List of SFOrg objects
        """
        if self._orgs_cache is not None and not refresh:
            return self._orgs_cache

        result = self._run_sf_command(["org", "list"])

        orgs = []
        org_data = result.get("result", {})

        # Combine all org types
        all_orgs = (
            org_data.get("nonScratchOrgs", []) +
            org_data.get("scratchOrgs", []) +
            org_data.get("sandboxes", []) +
            org_data.get("other", [])
        )

        for org in all_orgs:
            orgs.append(SFOrg(
                username=org.get("username", ""),
                alias=org.get("alias"),
                instance_url=org.get("instanceUrl", ""),
                access_token=org.get("accessToken", ""),
                org_id=org.get("orgId", ""),
                is_sandbox=org.get("isSandbox", False),
                is_scratch=org.get("isScratch", False),
                org_name=org.get("name", ""),
                connected_status=org.get("connectedStatus", "Unknown"),
            ))

        self._orgs_cache = orgs
        logger.info(f"Found {len(orgs)} authenticated orgs")
        return orgs

    def get_org(self, alias_or_username: str) -> Optional[SFOrg]:
        """
        Get a specific org by alias or username.

        Args:
            alias_or_username: The org alias or username

        Returns:
            SFOrg if found, None otherwise
        """
        orgs = self.list_orgs()

        for org in orgs:
            if org.alias == alias_or_username or org.username == alias_or_username:
                return org

        return None

    def set_target_org(self, alias_or_username: str) -> SFOrg:
        """
        Set the target org for subsequent operations.

        Args:
            alias_or_username: The org alias or username

        Returns:
            The selected SFOrg

        Raises:
            ValueError: If org not found
        """
        org = self.get_org(alias_or_username)

        if org is None:
            available = [o.display_name for o in self.list_orgs()]
            raise ValueError(
                f"Org '{alias_or_username}' not found. "
                f"Available orgs: {', '.join(available)}"
            )

        if org.connected_status != "Connected":
            logger.warning(
                f"Org '{alias_or_username}' status is '{org.connected_status}'. "
                "You may need to re-authenticate with: sf org login web"
            )

        self._target_org = alias_or_username
        logger.info(f"Target org set to: {org.display_name} ({org.org_name})")
        return org

    def get_target_org(self) -> Optional[SFOrg]:
        """
        Get the current target org.

        Returns:
            The current target SFOrg, or None if not set
        """
        if self._target_org is None:
            return None
        return self.get_org(self._target_org)

    def get_access_token(self, alias_or_username: Optional[str] = None) -> tuple[str, str]:
        """
        Get access token and instance URL for an org.

        Args:
            alias_or_username: Org to get token for. Uses target org if None.

        Returns:
            Tuple of (access_token, instance_url)

        Raises:
            ValueError: If no org specified and no target set
        """
        if alias_or_username is None:
            if self._target_org is None:
                raise ValueError(
                    "No target org set. Use set_target_org() first or specify an org."
                )
            alias_or_username = self._target_org

        org = self.get_org(alias_or_username)

        if org is None:
            raise ValueError(f"Org '{alias_or_username}' not found")

        if not org.access_token:
            # Token might have expired, try refreshing
            self._orgs_cache = None
            org = self.get_org(alias_or_username)

            if not org or not org.access_token:
                raise ValueError(
                    f"No access token for '{alias_or_username}'. "
                    "Re-authenticate with: sf org login web"
                )

        return org.access_token, org.instance_url


# Global instance for convenience
sf_cli = SFCLIAuth()
