"""
Backwards compatibility module - imports from clients package.

This module re-exports ConnectAPIClient from clients/ for backwards compatibility.
New code should import from clients directly:

    from clients import ConnectAPIClient
"""

from clients.client import ConnectAPIClient

__all__ = ['ConnectAPIClient']
