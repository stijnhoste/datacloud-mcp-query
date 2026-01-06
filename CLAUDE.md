# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server that connects AI assistants (Cursor, Claude Code) to Salesforce Data Cloud (Data 360) for SQL querying, metadata exploration, calculated insights, data graphs, and data ingestion. It implements both Connect APIs and faster Direct APIs with 2-step authentication.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the MCP server (typically launched by Cursor/Claude Code, not manually)
python server.py

# Test the query API directly (requires SF_CLIENT_ID and SF_CLIENT_SECRET env vars)
python connect_api_dc_sql.py
```

## Architecture

```
server.py                  # MCP server entry point - defines all tools
    ├── oauth.py           # OAuth2 + PKCE flow, token caching (~/.datacloud_mcp_token.json)
    ├── connect_api_dc_sql.py  # Connect API client (query-sql endpoint)
    ├── direct_api.py      # Direct API client (2-step auth, metadata, insights, graphs)
    └── query_validation.py    # SQL validation with sqlparse
```

### API Architecture

```
Connect APIs (/services/data/v63.0/ssot/*)
├── query-sql    → query()
└── pg_catalog   → list_tables(), describe_table()

Direct APIs (/api/v1/*)  ← Faster, requires 2-step auth
├── metadata               → get_metadata(), describe_table_full(), get_relationships()
├── insight/*              → list_calculated_insights(), query_calculated_insight()
├── dataGraph/*            → list_data_graphs(), query_data_graph()
├── universalIdLookup/*    → lookup_unified_id()
└── ingest/*               → ingest_records(), delete_records()
```

### Key Flows

**Authentication (oauth.py)**:
- `OAuthSession.ensure_access()` checks cached token first, then runs browser-based OAuth flow
- Tokens expire after 110 minutes and are cached to `~/.datacloud_mcp_token.json`
- Token cache includes `client_id` to detect config changes
- File permissions set to 0600 for security

**2-Step Auth for Direct APIs (direct_api.py)**:
1. OAuth to Salesforce Platform → returns `access_token`, `instance_url`
2. Token exchange POST to `{instance_url}/services/a360/token` → returns `tenant_token`, `tenant_url`
3. Direct API calls use `tenant_url` (different from Salesforce instance URL)

**Query Execution (connect_api_dc_sql.py)**:
- Submits SQL to `/services/data/v63.0/ssot/query-sql`
- Polls for completion using long-polling (`waitTimeMs=10000`)
- Paginates through results
- Returns `{data: [], metadata: []}`

**Query Validation (query_validation.py)**:
- Client-side SQL validation using `sqlparse`
- Fuzzy matching for column/table name suggestions
- Structured error responses with line/column positions

## Environment Variables

Required:
- `SF_CLIENT_ID` - Salesforce connected app client ID
- `SF_CLIENT_SECRET` - Salesforce connected app client secret

Optional:
- `SF_LOGIN_URL` - Salesforce login URL (default: `login.salesforce.com`)
- `SF_CALLBACK_URL` - OAuth callback URL (default: `http://localhost:55556/Callback`)
- `DEFAULT_LIST_TABLE_FILTER` - SQL LIKE pattern for filtering tables (default: `%`)

## MCP Tools Exposed

### Core Query Tools
| Tool | Description |
|------|-------------|
| `query(sql)` | Execute PostgreSQL-dialect SQL against Data Cloud |
| `validate_query(sql, check_metadata)` | Validate SQL syntax before execution |
| `format_sql(sql)` | Format SQL for readability |

### Schema Discovery Tools
| Tool | Description |
|------|-------------|
| `list_tables()` | List tables matching `DEFAULT_LIST_TABLE_FILTER` |
| `describe_table(table)` | Get column names for a table (pg_catalog) |
| `describe_table_full(table)` | Get detailed schema with field types (Direct API) |
| `get_metadata(entity_name, entity_type, entity_category)` | Get rich metadata |
| `get_relationships(entity_name)` | Get entity relationships for JOINs |

### Data Exploration Tools
| Tool | Description |
|------|-------------|
| `explore_table(table, sample_size)` | Schema + samples + column profiles |
| `search_tables(keyword)` | Search tables/columns by keyword |

### Calculated Insights Tools
| Tool | Description |
|------|-------------|
| `list_calculated_insights()` | List available calculated insights |
| `query_calculated_insight(insight_name, dimensions, measures, filters)` | Query pre-aggregated metrics |

### Data Graph Tools
| Tool | Description |
|------|-------------|
| `list_data_graphs()` | List available data graphs |
| `query_data_graph(graph_name, record_id, lookup_keys)` | Query unified profiles |

### Identity Tools
| Tool | Description |
|------|-------------|
| `lookup_unified_id(entity_name, data_source_id, data_source_object_id, source_record_id)` | Look up unified IDs |

### Data Modification Tools
| Tool | Description |
|------|-------------|
| `ingest_records(source_name, object_name, records)` | Insert records (requires approval) |
| `delete_records(source_name, object_name, record_ids)` | Delete records (requires approval) |

## Agentic Workflow Tips

### autoApprove Settings
Safe to auto-approve (read-only):
- `list_tables`, `describe_table`, `describe_table_full`
- `get_metadata`, `get_relationships`
- `explore_table`, `search_tables`
- `list_calculated_insights`, `list_data_graphs`
- `validate_query`, `format_sql`

Requires approval:
- `query` - Executes SQL
- `query_calculated_insight`, `query_data_graph`, `lookup_unified_id` - Queries data
- `ingest_records`, `delete_records` - Modifies data

### Recommended Workflow
1. Use `search_tables(keyword)` or `list_tables()` to find relevant tables
2. Use `describe_table_full(table)` to understand schema and field types
3. Use `get_relationships(entity_name)` to understand how to JOIN tables
4. Use `validate_query(sql)` to check SQL before execution
5. Use `query(sql)` to execute the validated query

### Data Cloud SQL Tips
- Use PostgreSQL dialect
- Always quote identifiers: `SELECT "ssot__FirstName__c" FROM "ssot__Individual__dlm"`
- Field names follow pattern: `ssot__FieldName__c`
- Table names follow pattern: `ssot__EntityName__dlm` (Data Lake Model)
- Use `explore_table()` to see sample data and understand column distributions

## File Reference

| File | Purpose |
|------|---------|
| `server.py` | MCP server, tool definitions |
| `oauth.py` | OAuth2 + PKCE authentication, token caching |
| `connect_api_dc_sql.py` | Connect API client for SQL queries |
| `direct_api.py` | Direct API client (2-step auth, metadata, insights) |
| `query_validation.py` | SQL validation with sqlparse |
| `requirements.txt` | Python dependencies |
| `todo.md` | Feature backlog and implementation status |
| `api-reference/` | Postman collections for API reference |
