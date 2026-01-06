# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server that connects AI assistants (Cursor, Claude Code) to Salesforce Data Cloud (Data 360). It provides 68 tools for SQL querying, metadata exploration, segments, activations, data pipelines, schema management, ML/AI, and administration.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the MCP server (typically launched by Cursor/Claude Code, not manually)
python server.py

# Test the query API directly
python connect_api_dc_sql.py
```

## Architecture

```
server.py                      # MCP server entry point - defines all 68 tools
    ├── oauth.py               # OAuth2 + PKCE flow, token caching, SF CLI integration
    ├── sf_cli_auth.py         # SF CLI org discovery and authentication
    ├── connect_api_dc_sql.py  # Connect API client (query-sql endpoint)
    ├── connect_api_segments.py # Connect API client (all other endpoints)
    ├── direct_api.py          # Direct API client (ingestion only - requires CDP scopes)
    └── query_validation.py    # SQL validation with sqlparse
```

### API Architecture

Almost all tools use Connect API which works with SF CLI authentication:

```
Connect APIs (/services/data/v63.0/ssot/*) - Works with SF CLI auth
├── query-sql              → query()
├── metadata               → get_metadata(), describe_table_full(), get_relationships()
├── calculated-insights/*  → list_calculated_insights(), query_calculated_insight()
├── data-graphs/*          → list_data_graphs(), query_data_graph()
├── universalIdLookup/*    → lookup_unified_id()
├── profile/*              → Profile queries
├── segments/*             → list_segments(), get_segment(), create_segment(), etc.
├── activations/*          → list_activations(), get_activation(), etc.
├── data-streams/*         → list_data_streams(), run_data_stream(), etc.
├── data-transforms/*      → list_data_transforms(), run_data_transform(), etc.
├── connections/*          → list_connections(), preview_connection(), etc.
├── data-lake-objects/*    → list_data_lake_objects(), create_data_lake_object(), etc.
├── data-model-objects/*   → list_data_model_objects(), get_dmo_mappings(), etc.
├── data-spaces/*          → list_data_spaces(), get_data_space_members(), etc.
├── machine-learning/*     → list_ml_models(), get_prediction(), etc.
├── search-index/*         → list_semantic_searches(), get_semantic_search_config(), etc.
├── identity-resolutions/* → list_identity_rulesets(), run_identity_resolution(), etc.
└── limits                 → get_limits()

Direct APIs (/api/v1/*) - Requires Connected App with CDP scopes
└── ingest/*               → ingest_records(), delete_records()
```

See `api-reference/API_REFERENCE.md` for detailed endpoint documentation.

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

## Environment Variables

**For SF CLI Auth (recommended - no Connected App needed):**
No environment variables required! The server uses orgs authenticated via `sf org login web`.
Use `list_orgs()` and `set_target_org(alias)` to select which org to query.

**For Custom Connected App (only needed for data ingestion):**
- `SF_CLIENT_ID` - Salesforce connected app client ID
- `SF_CLIENT_SECRET` - Salesforce connected app client secret
- `SF_LOGIN_URL` - Salesforce login URL (default: `login.salesforce.com`)
- `SF_CALLBACK_URL` - OAuth callback URL (default: `http://localhost:55556/Callback`)

**Other Options:**
- `DEFAULT_LIST_TABLE_FILTER` - SQL LIKE pattern for filtering tables (default: `%`)

### Authentication Modes

| Mode | Setup | Features | Use Case |
|------|-------|----------|----------|
| **SF CLI** | `sf org login web` | 66/68 tools | Most users |
| **Connected App** | Create app with CDP scopes | All 68 tools | Data ingestion |

SF CLI auth works because most Data Cloud APIs use Connect API endpoints which only need standard Salesforce API scopes. Only the ingestion APIs (`ingest_records`, `delete_records`) require a Connected App with CDP scopes.

## MCP Tools (68 total)

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
| `query_calculated_insight(...)` | Query pre-aggregated metrics |

### Data Graph Tools
| Tool | Description |
|------|-------------|
| `list_data_graphs()` | List available data graphs |
| `query_data_graph(graph_name, record_id, lookup_keys)` | Query unified profiles |

### Identity Tools
| Tool | Description |
|------|-------------|
| `lookup_unified_id(...)` | Look up unified IDs from source records |

### Data Modification Tools
| Tool | Description |
|------|-------------|
| `ingest_records(source_name, object_name, records)` | Insert records (requires approval) |
| `delete_records(source_name, object_name, record_ids)` | Delete records (requires approval) |

### Segments Tools
| Tool | Description |
|------|-------------|
| `list_segments()` | List all segments |
| `get_segment(segment_name)` | Get segment details |
| `get_segment_members(segment_name, limit, offset)` | Get segment members |
| `count_segment(segment_name)` | Count segment members |
| `create_segment(segment_definition)` | Create segment (requires approval) |
| `update_segment(segment_name, updates)` | Update segment (requires approval) |
| `delete_segment(segment_name)` | Delete segment (requires approval) |
| `publish_segment(segment_name)` | Publish segment (requires approval) |

### Activations Tools
| Tool | Description |
|------|-------------|
| `list_activations()` | List all activations |
| `get_activation(activation_id)` | Get activation details |
| `get_audience_records(activation_id, limit, offset)` | Get audience DMO records |
| `list_activation_targets()` | List activation targets |

### Data Streams Tools
| Tool | Description |
|------|-------------|
| `list_data_streams()` | List all data streams |
| `get_data_stream(stream_name)` | Get data stream details |
| `run_data_stream(stream_names)` | Run data streams (requires approval) |

### Data Transforms Tools
| Tool | Description |
|------|-------------|
| `list_data_transforms()` | List all data transforms |
| `get_data_transform(transform_name)` | Get transform details |
| `get_transform_run_history(transform_name)` | Get transform run history |
| `run_data_transform(transform_name)` | Run transform (requires approval) |

### Connections Tools
| Tool | Description |
|------|-------------|
| `list_connections()` | List all connections |
| `get_connection(connection_name)` | Get connection details |
| `get_connection_objects(connection_name)` | Get available objects |
| `preview_connection(connection_name, object_name, limit)` | Preview connection data |
| `list_connectors()` | List available connector types |

### Data Lake Objects Tools
| Tool | Description |
|------|-------------|
| `list_data_lake_objects()` | List all DLOs (raw ingested data) |
| `get_data_lake_object(object_name)` | Get DLO details |
| `create_data_lake_object(definition)` | Create DLO (requires approval) |

### Data Model Objects Tools
| Tool | Description |
|------|-------------|
| `list_data_model_objects()` | List all DMOs (canonical entities) |
| `get_data_model_object(object_name)` | Get DMO details |
| `get_dmo_mappings(object_name)` | Get field mappings |
| `create_data_model_object(definition)` | Create DMO (requires approval) |

### Data Spaces Tools
| Tool | Description |
|------|-------------|
| `list_data_spaces()` | List all data spaces |
| `get_data_space(space_name)` | Get data space details |
| `get_data_space_members(space_name)` | Get objects in data space |

### ML Models Tools
| Tool | Description |
|------|-------------|
| `list_ml_models()` | List all ML models |
| `get_ml_model(model_name)` | Get ML model details |
| `get_prediction(model_name, input_data)` | Get predictions |
| `list_model_artifacts()` | List model artifacts |

### Document AI Tools
| Tool | Description |
|------|-------------|
| `list_document_ai_configs()` | List Document AI configurations |
| `extract_document_data(config_name, document_data)` | Extract data (requires approval) |

### Semantic Search Tools
| Tool | Description |
|------|-------------|
| `list_semantic_searches()` | List semantic search configurations |
| `get_semantic_search(search_name)` | Get semantic search details |
| `get_semantic_search_config()` | Get global search config |

### Identity Resolution Tools
| Tool | Description |
|------|-------------|
| `list_identity_rulesets()` | List identity resolution rulesets |
| `get_identity_ruleset(ruleset_name)` | Get ruleset details |
| `run_identity_resolution(ruleset_name)` | Run identity resolution (requires approval) |

### Admin Tools
| Tool | Description |
|------|-------------|
| `get_limits()` | Get API limits and usage |
| `list_data_actions()` | List data actions |
| `list_data_action_targets()` | List data action targets |
| `list_private_network_routes()` | List private network routes |
| `get_data_kit_status(component_id)` | Get data kit component status |

## Agentic Workflow Tips

### autoApprove Settings
Safe to auto-approve (read-only):
- All `list_*` tools
- All `get_*` tools (except `get_prediction`)
- `describe_table`, `describe_table_full`
- `search_tables`, `explore_table`
- `validate_query`, `format_sql`

Requires approval:
- `query` - Executes SQL
- `query_calculated_insight`, `query_data_graph` - Queries data
- `create_*`, `update_*`, `delete_*` - Modifies data
- `run_*` - Executes pipelines
- `ingest_records`, `delete_records` - Modifies data
- `extract_document_data`, `get_prediction` - Processes data

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
| `server.py` | MCP server, all 68 tool definitions |
| `oauth.py` | OAuth2 + PKCE authentication, token caching, SF CLI integration |
| `sf_cli_auth.py` | SF CLI org discovery and authentication |
| `connect_api_dc_sql.py` | Connect API client for SQL queries |
| `connect_api_segments.py` | Connect API client for all other endpoints |
| `direct_api.py` | Direct API client (ingestion only - requires CDP scopes) |
| `query_validation.py` | SQL validation with sqlparse |
| `requirements.txt` | Python dependencies |
| `api-reference/API_REFERENCE.md` | Consolidated API endpoint reference |
| `api-reference/*.json` | Postman collections for API reference |
