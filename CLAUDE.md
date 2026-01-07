# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Enhanced fork of [Salesforce's datacloud-mcp-query](https://github.com/forcedotcom/datacloud-mcp-query). This MCP server connects AI assistants (Cursor, Claude Code) to Salesforce Data Cloud.

| Aspect | Original | This Fork |
|--------|----------|-----------|
| **Tools** | 3 | 121 |
| **Auth** | Connected App OAuth | SF CLI (no setup required) |
| **APIs** | Connect API (queries only) | Connect API (full coverage) |

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Authenticate with SF CLI
sf org login web --alias my-dc-org

# Run the MCP server (typically launched by Cursor/Claude Code, not manually)
python server.py

# Test the query API directly
python -m clients.sql
```

## Architecture

```
server.py                      # Thin entry point - imports tools package and runs MCP
├── tools/                     # Domain-specific tool modules (auto-registered)
│   ├── __init__.py            # Imports all modules to register tools with mcp
│   ├── base.py                # Shared mcp instance, session management, helpers
│   ├── org.py                 # Org management (list_orgs, set_target_org)
│   ├── query.py               # SQL query tools (query, list_tables, describe_table)
│   ├── metadata.py            # Metadata discovery (describe_table_full, get_relationships)
│   ├── segments.py            # Segment CRUD operations
│   ├── activations.py         # Activation and target management
│   ├── streams.py             # Data stream operations
│   ├── transforms.py          # Data transform operations
│   ├── connections.py         # Connection and connector management
│   ├── dlo_dmo.py             # DLO and DMO operations
│   ├── dataspaces.py          # Data space management
│   ├── insights.py            # Calculated insights
│   ├── graphs.py              # Data graph operations
│   ├── identity.py            # Identity resolution
│   ├── ml.py                  # ML models, Document AI, semantic search
│   ├── admin.py               # Admin, limits, data actions, network routes
│   └── profile.py             # Profile query tools
├── clients/                   # API client implementations
│   ├── __init__.py            # Package init
│   ├── base.py                # Base HTTP client with request handling
│   ├── client.py              # Full ConnectAPIClient with all API methods
│   └── sql.py                 # SQL query client (run_query)
├── sf_cli_auth.py             # SF CLI org discovery and authentication
└── query_validation.py        # SQL validation with sqlparse
```

### API Architecture

All tools use the Connect API which works with SF CLI authentication:

```
Connect API (/services/data/v63.0/ssot/*)
├── query-sql/*              → query()
├── metadata                 → get_metadata(), describe_table_full()
│
├── segments/*               → list_segments(), get_segment(), etc.
├── activations/*            → list_activations(), get_activation(), etc.
│
├── data-streams/*           → list_data_streams(), get_data_stream()
├── data-transforms/*        → list_data_transforms(), run_data_transform()
├── connections/*            → list_connections(), get_connection()
│
├── data-lake-objects/*      → list_data_lake_objects(), get_data_lake_object()
├── data-model-objects/*     → list_data_model_objects(), get_data_model_object()
├── data-spaces/*            → list_data_spaces(), get_data_space_members()
│
├── calculated-insights/*    → list_calculated_insights(), query_calculated_insight()
├── data-graphs/*            → list_data_graphs(), query_data_graph()
├── identity-resolutions/*   → list_identity_rulesets(), get_identity_ruleset()
├── universalIdLookup/*      → lookup_unified_id()
│
├── machine-learning/*       → list_ml_models(), get_prediction()
├── document-processing/*    → list_document_ai_configs()
├── search-index/*           → list_semantic_searches()
│
├── data-actions/*           → list_data_actions()
├── data-action-targets/*    → list_data_action_targets()
│
└── /services/data/v63.0/limits → get_limits()
```

See `api-reference/API_REFERENCE.md` for detailed endpoint documentation.

### Key Flows

**Authentication (sf_cli_auth.py)**:
- Uses SF CLI's secure token storage (`sf org display`)
- No client secrets or Connected App setup required
- Multi-org support via `list_orgs()`, `set_target_org(alias)`
- Environment variable `DC_DEFAULT_ORG` for default org

**Query Execution (clients/sql.py)**:
- Submits SQL to `/services/data/v63.0/ssot/query-sql`
- Polls for completion using long-polling (`waitTimeMs=10000`)
- Paginates through results
- Returns `{data: [], metadata: []}`

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DC_DEFAULT_ORG` | No | - | SF CLI org alias to use by default |
| `DEFAULT_LIST_TABLE_FILTER` | No | `%` | SQL LIKE pattern for filtering tables |

## MCP Tools (121 total)

### Org Management
| Tool | Description |
|------|-------------|
| `list_orgs()` | List all SF CLI authenticated orgs |
| `set_target_org(alias)` | Switch to a different org |
| `get_target_org()` | Get currently selected org |

### Query & SQL
| Tool | Description |
|------|-------------|
| `query(sql)` | Execute PostgreSQL-dialect SQL against Data Cloud |
| `validate_query(sql)` | Validate SQL syntax before execution |
| `format_sql(sql)` | Format SQL for readability |

### Schema Discovery
| Tool | Description |
|------|-------------|
| `list_tables()` | List tables matching `DEFAULT_LIST_TABLE_FILTER` |
| `describe_table(table)` | Get column names for a table |
| `describe_table_full(table)` | Get detailed schema with field types |
| `get_metadata(entity_name, entity_type, entity_category)` | Get rich metadata |
| `get_relationships(entity_name)` | Get entity relationships for JOINs |
| `explore_table(table, sample_size)` | Schema + samples + column profiles |
| `search_tables(keyword)` | Search tables/columns by keyword |

### Segments
| Tool | Description |
|------|-------------|
| `list_segments()` | List all segments |
| `get_segment(segment_name)` | Get segment details |
| `get_segment_members(segment_name, limit, offset)` | Get segment members |
| `count_segment(segment_name)` | Count segment members |
| `update_segment(segment_name, updates)` | Update segment |
| `delete_segment(segment_name)` | Delete segment |

### Activations
| Tool | Description |
|------|-------------|
| `list_activations()` | List all activations |
| `get_activation(activation_id)` | Get activation details |
| `list_activation_targets()` | List activation targets |

### Data Streams
| Tool | Description |
|------|-------------|
| `list_data_streams()` | List all data streams |
| `get_data_stream(stream_name)` | Get data stream details |

### Data Transforms
| Tool | Description |
|------|-------------|
| `list_data_transforms()` | List all data transforms |
| `get_data_transform(transform_name)` | Get transform details |
| `get_transform_run_history(transform_name)` | Get transform run history |
| `run_data_transform(transform_name)` | Run transform |

### Connections
| Tool | Description |
|------|-------------|
| `list_connections()` | List all connections |
| `get_connection(connection_name)` | Get connection details |
| `get_connection_objects(connection_name)` | Get available objects |
| `list_connectors()` | List available connector types |

### Data Lake Objects (DLOs)
| Tool | Description |
|------|-------------|
| `list_data_lake_objects()` | List all DLOs (raw ingested data) |
| `get_data_lake_object(object_name)` | Get DLO details |

### Data Model Objects (DMOs)
| Tool | Description |
|------|-------------|
| `list_data_model_objects()` | List all DMOs (canonical entities) |
| `get_data_model_object(object_name)` | Get DMO details |

### Data Spaces
| Tool | Description |
|------|-------------|
| `list_data_spaces()` | List all data spaces |
| `get_data_space(space_name)` | Get data space details |
| `get_data_space_members(space_name)` | Get objects in data space |

### Calculated Insights
| Tool | Description |
|------|-------------|
| `list_calculated_insights()` | List available calculated insights |
| `query_calculated_insight(...)` | Query pre-aggregated metrics |

### Data Graphs
| Tool | Description |
|------|-------------|
| `list_data_graphs()` | List available data graphs |
| `query_data_graph(graph_name, record_id, lookup_keys)` | Query unified profiles |

### Identity Resolution
| Tool | Description |
|------|-------------|
| `lookup_unified_id(...)` | Look up unified IDs from source records |
| `list_identity_rulesets()` | List identity resolution rulesets |
| `get_identity_ruleset(ruleset_name)` | Get ruleset details |

### AI & ML
| Tool | Description |
|------|-------------|
| `list_ml_models()` | List all ML models |
| `get_ml_model(model_name)` | Get ML model details |
| `get_prediction(model_name, input_data)` | Get predictions |
| `list_model_artifacts()` | List model artifacts |
| `list_document_ai_configs()` | List Document AI configurations |
| `extract_document_data(config_name, document_data)` | Extract document data |
| `list_semantic_searches()` | List semantic search indexes |
| `get_semantic_search(search_name)` | Get semantic search details |
| `get_semantic_search_config()` | Get global search config |

### Data Actions
| Tool | Description |
|------|-------------|
| `list_data_actions()` | List event-driven automation rules |
| `list_data_action_targets()` | List webhook/external targets |

### Admin & Monitoring
| Tool | Description |
|------|-------------|
| `get_limits()` | Get API limits and usage |

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
- `update_*`, `delete_*` - Modifies data
- `run_*` - Executes pipelines
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

| File/Directory | Purpose |
|----------------|---------|
| `server.py` | Thin MCP entry point (imports tools package) |
| `tools/` | Domain-specific tool modules (121 tools total) |
| `tools/base.py` | Shared mcp instance, session management |
| `clients/` | API client implementations |
| `clients/client.py` | Full ConnectAPIClient with all API methods |
| `sf_cli_auth.py` | SF CLI org discovery and authentication |
| `clients/sql.py` | SQL query client (run_query) |
| `query_validation.py` | SQL validation with sqlparse |
| `requirements.txt` | Python dependencies |
| `api-reference/API_REFERENCE.md` | Consolidated API endpoint reference |
