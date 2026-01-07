# Data Cloud MCP Server (Enhanced Fork)

> Enhanced fork of [Salesforce's datacloud-mcp-query](https://github.com/forcedotcom/datacloud-mcp-query) with **137 tools**, SF CLI authentication, and full Connect API coverage.

## What's Different from Upstream

| Aspect | Original | This Fork |
|--------|----------|-----------|
| **Tools** | 3 | 137 |
| **Auth** | Connected App OAuth | SF CLI (no setup required) |
| **APIs** | Connect API (queries only) | Connect API (full coverage) |
| **Setup** | Create Connected App | Just `sf org login web` |

## Features

- **SQL Queries** - Execute PostgreSQL-dialect SQL against Data Cloud
- **Schema Discovery** - List tables, describe columns, explore metadata
- **Segments & Activations** - Manage audience segments and activations
- **Data Pipelines** - Work with data streams, transforms, and connections
- **Calculated Insights** - Query pre-aggregated metrics
- **Data Graphs** - Traverse unified customer profiles
- **AI & ML** - ML models, Document AI, and semantic search
- **Identity Resolution** - Manage rulesets and lookup unified IDs
- **Data Actions** - Event-driven automation and webhooks
- **Admin & Monitoring** - API limits, network routes, deployment status

## Quick Start

### Prerequisites

- Python 3.10+
- [Salesforce CLI](https://developer.salesforce.com/tools/salesforcecli) installed
- A Salesforce org with Data Cloud enabled

### Installation

```bash
git clone https://github.com/stijnhoste/datacloud-mcp-query.git
cd datacloud-mcp-query
pip install -r requirements.txt

# Authenticate with your Data Cloud org
sf org login web --alias my-dc-org
```

### Configure Your MCP Client

Add to your MCP client configuration file:

| Client | Config File |
|--------|-------------|
| Cursor | `~/.cursor/mcp.json` |
| Claude Code | `~/.claude/mcp.json` |

```json
{
  "mcpServers": {
    "datacloud": {
      "command": "python",
      "args": ["/absolute/path/to/datacloud-mcp-query/server.py"],
      "env": {
        "DC_DEFAULT_ORG": "my-dc-org"
      }
    }
  }
}
```

> **Note:** Replace `/absolute/path/to/` with the actual path where you cloned the repository.

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DC_DEFAULT_ORG` | No | - | SF CLI org alias to use by default |
| `DEFAULT_LIST_TABLE_FILTER` | No | `%` | SQL LIKE pattern for filtering tables |

### Multi-Org Support

If you don't set `DC_DEFAULT_ORG`, use these tools to select an org at runtime:

```
list_orgs()           # See all authenticated orgs
set_target_org(alias) # Switch to a specific org
get_target_org()      # See currently selected org
```

## API Limitations

The Salesforce Data Cloud **Connect API** is primarily read-oriented. Create operations for most resources are **not supported** via REST and require:

| Resource Type | Required API |
|--------------|--------------|
| Segments, DLOs, DMOs | **Metadata API** (deploy XML) |
| Data Actions, Activations | **Setup UI** or **Tooling API** |
| Connections, Network Routes | **Setup UI** only |
| Identity Rulesets, Transforms | **Metadata API** |

This MCP server uses the Connect API exclusively (works with SF CLI auth), so it supports **read, update, delete, and run** operations but not **create**.

## Available Tools (137 total)

### Org Management
| Tool | Description |
|------|-------------|
| `list_orgs()` | List all SF CLI authenticated orgs |
| `set_target_org(alias)` | Switch to a different org |
| `get_target_org()` | Get currently selected org |

### Query Tools
| Tool | Description |
|------|-------------|
| `query(sql)` | Execute SQL queries against Data Cloud |
| `validate_query(sql)` | Validate SQL syntax before execution |
| `format_sql(sql)` | Format SQL for readability |

### Schema Discovery
| Tool | Description |
|------|-------------|
| `list_tables()` | List available tables |
| `describe_table(table)` | Get column names |
| `describe_table_full(table)` | Get detailed schema with types |
| `get_metadata(...)` | Get rich entity metadata |
| `get_relationships(entity)` | Get relationships for JOINs |
| `explore_table(table)` | Schema + samples + profiles |
| `search_tables(keyword)` | Search tables/columns |

### Segments
| Tool | Description |
|------|-------------|
| `list_segments()` | List all segments |
| `get_segment(name)` | Get segment details |
| `get_segment_members(name)` | Get segment members |
| `count_segment(name)` | Count segment members |
| `update_segment(name, updates)` | Update segment |
| `delete_segment(name)` | Delete segment |
| `publish_segment(name)` | Publish for activation |

### Activations
| Tool | Description |
|------|-------------|
| `list_activations()` | List all activations |
| `get_activation(id)` | Get activation details |
| `get_audience_records(id)` | Get audience DMO records |
| `list_activation_targets()` | List activation targets |

### Data Streams
| Tool | Description |
|------|-------------|
| `list_data_streams()` | List all data streams |
| `get_data_stream(name)` | Get stream details |
| `run_data_stream(names)` | Run data streams |

### Data Transforms
| Tool | Description |
|------|-------------|
| `list_data_transforms()` | List all transforms |
| `get_data_transform(name)` | Get transform details |
| `get_transform_run_history(name)` | Get run history |
| `run_data_transform(name)` | Run transform |

### Connections
| Tool | Description |
|------|-------------|
| `list_connections()` | List all connections |
| `get_connection(name)` | Get connection details |
| `get_connection_objects(name)` | Get available objects |
| `preview_connection(name, object)` | Preview data |
| `list_connectors()` | List connector types |

### Data Lake Objects (DLOs)
| Tool | Description |
|------|-------------|
| `list_data_lake_objects()` | List all DLOs |
| `get_data_lake_object(name)` | Get DLO details |

### Data Model Objects (DMOs)
| Tool | Description |
|------|-------------|
| `list_data_model_objects()` | List all DMOs |
| `get_data_model_object(name)` | Get DMO details |
| `get_dmo_mappings(name)` | Get field mappings |

### Data Spaces
| Tool | Description |
|------|-------------|
| `list_data_spaces()` | List all data spaces |
| `get_data_space(name)` | Get data space details |
| `get_data_space_members(name)` | Get objects in space |

### Calculated Insights
| Tool | Description |
|------|-------------|
| `list_calculated_insights()` | List all insights |
| `query_calculated_insight(...)` | Query insight data |

### Data Graphs
| Tool | Description |
|------|-------------|
| `list_data_graphs()` | List all data graphs |
| `query_data_graph(...)` | Query unified profiles |

### Identity
| Tool | Description |
|------|-------------|
| `lookup_unified_id(...)` | Look up unified IDs |
| `list_identity_rulesets()` | List identity rulesets |
| `get_identity_ruleset(name)` | Get ruleset details |
| `run_identity_resolution(name)` | Run identity resolution |

### AI & ML
| Tool | Description |
|------|-------------|
| `list_ml_models()` | List all ML models |
| `get_ml_model(name)` | Get model details |
| `get_prediction(model, data)` | Get predictions |
| `list_model_artifacts()` | List model artifacts |
| `list_document_ai_configs()` | List Document AI configs |
| `extract_document_data(...)` | Extract document data |
| `list_semantic_searches()` | List semantic search indexes |
| `get_semantic_search(name)` | Get search index details |
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
| `list_private_network_routes()` | List network routes |
| `get_data_kit_status(id)` | Get deployment status |

## autoApprove Settings

For agentic workflows, auto-approve read-only tools:

```json
{
  "autoApprove": [
    "list_orgs", "get_target_org",
    "list_tables", "describe_table", "describe_table_full",
    "get_metadata", "get_relationships", "explore_table", "search_tables",
    "list_segments", "get_segment", "count_segment",
    "list_activations", "get_activation", "list_activation_targets",
    "list_data_streams", "get_data_stream",
    "list_data_transforms", "get_data_transform", "get_transform_run_history",
    "list_connections", "get_connection", "list_connectors",
    "list_data_lake_objects", "get_data_lake_object",
    "list_data_model_objects", "get_data_model_object", "get_dmo_mappings",
    "list_data_spaces", "get_data_space", "get_data_space_members",
    "list_calculated_insights", "list_data_graphs",
    "list_identity_rulesets", "get_identity_ruleset",
    "list_ml_models", "get_ml_model", "list_model_artifacts",
    "list_document_ai_configs",
    "list_semantic_searches", "get_semantic_search", "get_semantic_search_config",
    "get_limits", "list_data_actions", "list_data_action_targets",
    "list_private_network_routes",
    "validate_query", "format_sql"
  ]
}
```

## Authentication

This fork uses **SF CLI authentication** exclusively:

1. Authenticate via SF CLI: `sf org login web --alias my-org`
2. Set `DC_DEFAULT_ORG` environment variable, or use `set_target_org()` tool
3. The server reads credentials from SF CLI's secure token storage

**Benefits:**
- No Connected App setup required
- No client secrets to manage
- Multi-org support built-in
- Tokens managed by SF CLI

## API Architecture

All tools use the **Connect API** (`/services/data/v63.0/ssot/*`), which works with standard Salesforce OAuth tokens from SF CLI.

```
Connect API (/services/data/v63.0/ssot/*)
├── query-sql/*              → query()
├── metadata                 → get_metadata(), describe_table_full()
│
├── segments/*               → list_segments(), get_segment(), etc.
├── activations/*            → list_activations(), get_activation(), etc.
│
├── data-streams/*           → list_data_streams(), run_data_stream()
├── data-transforms/*        → list_data_transforms(), run_data_transform()
├── connections/*            → list_connections(), preview_connection()
│
├── data-lake-objects/*      → list_data_lake_objects(), get_data_lake_object()
├── data-model-objects/*     → list_data_model_objects(), get_dmo_mappings()
├── data-spaces/*            → list_data_spaces(), get_data_space_members()
│
├── calculated-insights/*    → list_calculated_insights(), query_calculated_insight()
├── data-graphs/*            → list_data_graphs(), query_data_graph()
├── identity-resolutions/*   → list_identity_rulesets(), run_identity_resolution()
├── universalIdLookup/*      → lookup_unified_id()
│
├── machine-learning/*       → list_ml_models(), get_prediction()        ─┐
├── document-processing/*    → list_document_ai_configs()                 │ AI & ML
├── search-index/*           → list_semantic_searches()                  ─┘
│
├── data-actions/*           → list_data_actions()                       ─┐ Data Actions
├── data-action-targets/*    → list_data_action_targets()                ─┘
│
└── /services/data/v63.0/limits → get_limits()                           ─ Admin
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

Apache 2.0 - See [LICENSE.txt](LICENSE.txt) for details.

Original work Copyright (c) 2024 Salesforce, Inc.
