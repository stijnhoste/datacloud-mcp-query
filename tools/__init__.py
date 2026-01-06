"""
MCP Tools for Salesforce Data Cloud.

This package contains domain-specific tool modules. When imported,
all tools are automatically registered with the shared `mcp` instance.
"""

# Import base to get mcp instance and helpers
from .base import mcp

# Import all tool modules to register their tools with mcp
from . import org
from . import query
from . import metadata
from . import segments
from . import activations
from . import streams
from . import transforms
from . import connections
from . import dlo_dmo
from . import dataspaces
from . import insights
from . import graphs
from . import identity
from . import ml
from . import admin
from . import profile

__all__ = ['mcp']
