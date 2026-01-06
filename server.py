#!/usr/bin/env python3
"""
Salesforce Data Cloud MCP Server

A Model Context Protocol (MCP) server that provides tools for interacting
with Salesforce Data Cloud via the Connect API.

Authentication: Uses SF CLI (no Connected App setup required)
API Coverage: Full Connect API (/services/data/v63.0/ssot/*)

Usage:
    # Run the server (typically launched by Cursor/Claude Code)
    python server.py

    # Or with a default org
    DC_DEFAULT_ORG=my-dc-org python server.py
"""

import logging

# Import mcp from tools package - this registers all tools
from tools import mcp

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting Data Cloud MCP Server (SF CLI auth)")
    mcp.run()
