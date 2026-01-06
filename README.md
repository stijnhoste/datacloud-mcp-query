# Data Cloud MCP Server

This MCP server provides a seamless integration between AI assistants (Cursor, Claude Code) and Salesforce Data Cloud, allowing you to execute SQL queries, explore metadata, work with calculated insights, and manage data directly from your development environment.

## Features

- **SQL Queries** - Execute PostgreSQL-dialect SQL against Data Cloud
- **Schema Discovery** - List tables, describe columns, search by keyword
- **Rich Metadata** - Access field types, relationships, and entity categories
- **Calculated Insights** - Query pre-aggregated metrics
- **Data Graphs** - Traverse unified customer profiles
- **Identity Resolution** - Look up unified IDs from source records
- **Data Ingestion** - Insert and delete records (with approval)
- **Query Validation** - Client-side SQL validation with suggestions

## Quick Start

1. Clone this repository:
   ```bash
   git clone https://github.com/salesforce/datacloud-mcp-query.git
   cd datacloud-mcp-query
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Salesforce connected app (see [Connected App Setup](CONNECTED_APP_SETUP.md))

4. Configure in your MCP client (Cursor or Claude Code)

## Adding to Cursor

Add to your Cursor settings (`~/.cursor/mcp.json` or through Cursor Settings → MCP):

```json
{
  "mcpServers": {
    "datacloud": {
      "command": "python",
      "args": ["/path/to/datacloud-mcp-query/server.py"],
      "env": {
        "SF_CLIENT_ID": "<your-client-id>",
        "SF_CLIENT_SECRET": "<your-client-secret>"
      },
      "autoApprove": [
        "list_tables",
        "describe_table",
        "describe_table_full",
        "get_metadata",
        "get_relationships",
        "explore_table",
        "search_tables",
        "list_calculated_insights",
        "list_data_graphs",
        "validate_query",
        "format_sql"
      ]
    }
  }
}
```

## Adding to Claude Code

Add to your Claude Code MCP settings:

```json
{
  "mcpServers": {
    "datacloud": {
      "command": "python",
      "args": ["/path/to/datacloud-mcp-query/server.py"],
      "env": {
        "SF_CLIENT_ID": "<your-client-id>",
        "SF_CLIENT_SECRET": "<your-client-secret>"
      }
    }
  }
}
```

## Configuration

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `SF_CLIENT_ID` | Salesforce connected app client ID |
| `SF_CLIENT_SECRET` | Salesforce connected app client secret |

### Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SF_LOGIN_URL` | `login.salesforce.com` | Salesforce login URL |
| `SF_CALLBACK_URL` | `http://localhost:55556/Callback` | OAuth callback URL |
| `DEFAULT_LIST_TABLE_FILTER` | `%` | SQL LIKE pattern for filtering tables |

## Available Tools

### Core Query Tools

| Tool | Description |
|------|-------------|
| `query(sql)` | Execute SQL queries against Data Cloud |
| `validate_query(sql, check_metadata)` | Validate SQL syntax before execution |
| `format_sql(sql)` | Format SQL for readability |

### Schema Discovery Tools

| Tool | Description |
|------|-------------|
| `list_tables()` | List available tables |
| `describe_table(table)` | Get column names for a table |
| `describe_table_full(table)` | Get detailed schema with field types |
| `get_metadata(entity_name, entity_type, entity_category)` | Get rich metadata from Direct API |
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

### Data Modification Tools (Require Approval)

| Tool | Description |
|------|-------------|
| `ingest_records(source_name, object_name, records)` | Insert records into Data Cloud |
| `delete_records(source_name, object_name, record_ids)` | Delete records from Data Cloud |

## autoApprove Settings

For agentic workflows, you can auto-approve read-only tools. Recommended settings:

**Safe to auto-approve** (read-only):
- `list_tables`, `describe_table`, `describe_table_full`
- `get_metadata`, `get_relationships`
- `explore_table`, `search_tables`
- `list_calculated_insights`, `list_data_graphs`
- `validate_query`, `format_sql`

**Requires explicit approval** (executes queries or modifies data):
- `query` - Executes SQL against Data Cloud
- `query_calculated_insight` - Queries calculated insights
- `query_data_graph` - Queries data graphs
- `lookup_unified_id` - Queries identity resolution
- `ingest_records` - Inserts data
- `delete_records` - Deletes data

## Authentication

The server implements OAuth2 with PKCE:
- Opens a browser window for Salesforce authentication
- Caches tokens to `~/.datacloud_mcp_token.json`
- Tokens expire after 110 minutes and are auto-refreshed
- For Direct APIs, performs a second token exchange for tenant-specific access

## API Architecture

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

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

See [LICENSE](LICENSE) for details.
