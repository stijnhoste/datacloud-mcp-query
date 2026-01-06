"""
API Clients for Salesforce Data Cloud Connect API.

This package provides domain-specific client modules that wrap the
/services/data/v63.0/ssot/* endpoints.
"""

from .base import BaseClient, DataCloudAPIError
from .client import ConnectAPIClient

__all__ = [
    'BaseClient',
    'DataCloudAPIError',
    'ConnectAPIClient',
]
