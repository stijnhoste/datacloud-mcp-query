# Data Cloud MCP - Feature Backlog

> **API Reference:** See `api-reference/` folder for Postman collections

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ⬜ | Not started |
| 🔄 | In progress |
| ✅ | Completed |

---

## Phase 0: Current Implementation ✅

| Tool | Status | API |
|------|--------|-----|
| `query(sql)` | ✅ | Connect API |
| `list_tables()` | ✅ | pg_catalog |
| `describe_table(table)` | ✅ | pg_catalog |
| Token caching | ✅ | Local |

---

## Phase 1: Core Improvements

### PR #1: Token Caching Security
**Branch:** `feature/token-caching`
**File:** `oauth.py`
**Status:** ✅

Changes:
- Add `os.chmod(self.TOKEN_CACHE_FILE, 0o600)` after saving token
- Add `client_id` to cache to detect config changes

### PR #2: Direct API Client (2-Step Auth)
**Branch:** `feature/direct-api`
**File:** `direct_api.py` (new)
**Status:** ✅

**2-Step Authentication Flow:**

```
Step 1: OAuth to Salesforce Platform (already implemented)
→ Returns: access_token, instance_url (e.g., https://myorg.my.salesforce.com)

Step 2: Exchange for Data 360 Tenant Token (NEW)
POST {instance_url}/services/a360/token
Content-Type: application/x-www-form-urlencoded

grant_type=urn:salesforce:grant-type:external:cdp
subject_token={platform_access_token}
subject_token_type=urn:ietf:params:oauth:token-type:access_token

→ Returns: {
    "access_token": "<dc_tenant_token>",
    "instance_url": "<dc_tenant_url>"  # DIFFERENT from Salesforce instance!
}
```

**Key insight:** Data 360 APIs use a **different base URL** (`dc_tenant_url`) than the Salesforce instance URL.

```python
class DirectAPISession:
    def __init__(self, oauth_session: OAuthSession):
        self.oauth_session = oauth_session
        self.tenant_token = None
        self.tenant_url = None

    def _get_tenant_token(self) -> str:
        """Exchange platform token for Data 360 tenant token"""
        # POST /services/a360/token
        pass

    def get_metadata(self, entity_name=None, entity_type=None, entity_category=None) -> dict:
        """GET /api/v1/metadata with optional filters"""
        pass
```

### PR #3: Metadata Tools
**Branch:** `feature/metadata-tools`
**File:** `server.py`
**Status:** ✅

| Tool | Description | Endpoint |
|------|-------------|----------|
| `get_metadata(entity_name, entity_type, entity_category)` | Rich metadata from API | `GET /api/v1/metadata` |
| `describe_table` (enhanced) | With field types | Uses get_metadata |
| `get_relationships(entity_name)` | Entity relationships for JOINs | From metadata response |

**Metadata Response Structure:**
```json
{
  "metadata": [{
    "name": "ssot__Individual__dlm",
    "displayName": "Individual",
    "category": "Profile",
    "fields": [{
      "name": "ssot__FirstName__c",
      "displayName": "First Name",
      "type": "STRING",
      "businessType": "TEXT"
    }],
    "primaryKeys": [{"name": "ssot__Id__c", "indexOrder": "1"}],
    "relationships": [{
      "fromEntity": "ssot__ContactPointEmail__dlm",
      "toEntity": "ssot__Individual__dlm",
      "fromEntityAttribute": "ssot__PartyId__c",
      "toEntityAttribute": "ssot__Id__c",
      "cardinality": "NTOONE"
    }]
  }]
}
```

### PR #4: Discovery Tools
**Branch:** `feature/discovery-tools`
**File:** `server.py`
**Status:** ✅

| Tool | Description |
|------|-------------|
| `explore_table(table)` | Schema + random sample + column profiles |
| `search_tables(keyword)` | Find tables/columns by keyword |

**`explore_table` returns:**
```python
{
    "schema": [...],           # From get_metadata - column names, types
    "row_count": 50000,
    "sample": [...],           # Random sample (ORDER BY RANDOM() LIMIT 10)
    "column_profiles": {
        "Status__c": {
            "distinct_values": ["Active", "Inactive", "Pending"],  # LIMIT 20
            "null_count": 150
        },
        "Amount__c": {
            "min": 0, "max": 9999, "avg": 450.23,
            "null_count": 50
        }
    }
}
```

### PR #5: Calculated Insights
**Branch:** `feature/calculated-insights`
**File:** `server.py`
**Status:** ✅

| Tool | Endpoint |
|------|----------|
| `list_calculated_insights()` | `GET /api/v1/insight/metadata` |
| `query_calculated_insight(insight_name, dimensions, measures, filters)` | `GET /api/v1/insight/calculated-insights/:ci_name` |

### PR #6: Data Graph
**Branch:** `feature/data-graph`
**File:** `server.py`
**Status:** ✅

| Tool | Endpoint |
|------|----------|
| `list_data_graphs()` | `GET /api/v1/dataGraph/metadata` |
| `query_data_graph(graph_name, record_id, lookup_keys)` | `GET /api/v1/dataGraph/:name/:recordId` |

### PR #7: Unified Record ID
**Branch:** `feature/unified-id`
**File:** `server.py`
**Status:** ✅

| Tool | Endpoint |
|------|----------|
| `lookup_unified_id(entity_name, data_source_id, data_source_object_id, source_record_id)` | `GET /api/v1/universalIdLookup/:entityName/:dataSourceId/:dataSourceObjectId/:sourceRecordId` |

### PR #8: Ingestion API
**Branch:** `feature/ingestion`
**File:** `server.py`
**Status:** ✅

| Tool | Endpoint | Auto-approve |
|------|----------|--------------|
| `ingest_records(source_name, object_name, records)` | `POST /api/v1/ingest/sources/:source/:object` | ❌ |
| `delete_records(source_name, object_name, record_ids)` | `DELETE /api/v1/ingest/sources/:source/:object` | ❌ |

### PR #9: Query Assistance
**Branch:** `feature/query-assistance`
**Files:** `server.py`, `query_validation.py`, `requirements.txt`
**Status:** ✅

- Add `validate_query(sql)` - Local SQL validation with `sqlparse`
- Enhanced error messages with suggestions
- Add `sqlparse>=0.5.0` to requirements

**Error Response Structure:**
```python
{
    "error_type": "INVALID_COLUMN",
    "message": "Column 'FirstName' not found",
    "suggestion": "Did you mean 'ssot__FirstName__c'?",
    "position": {"line": 1, "column": 15}
}
```

### PR #10: Documentation
**Branch:** `feature/docs`
**Files:** `README.md`, `CLAUDE.md`
**Status:** ✅

- Claude Code configuration section
- autoApprove settings
- Agentic workflow examples

---

## Phase 2: Audience & Segmentation ✅

| Tool | Status | Endpoint |
|------|--------|----------|
| `list_segments()` | ✅ | `GET /ssot/segments` |
| `get_segment(name)` | ✅ | `GET /ssot/segments/{name}` |
| `get_segment_members(name, limit)` | ✅ | `GET /ssot/segments/{name}/members` |
| `count_segment(name)` | ✅ | `POST /ssot/segments/{name}/actions/count` |
| `list_activations()` | ✅ | `GET /ssot/activations` |
| `get_activation(id)` | ✅ | `GET /ssot/activations/{id}` |
| `get_audience_records(activation_id)` | ✅ | `GET /ssot/activations/{id}/audience-dmo-records` |
| `list_activation_targets()` | ✅ | `GET /ssot/activation-targets` |
| `create_segment(...)` | ✅ | `POST /ssot/segments` |
| `update_segment(...)` | ✅ | `PATCH /ssot/segments/{name}` |
| `delete_segment(...)` | ✅ | `DELETE /ssot/segments/{name}` |
| `publish_segment(...)` | ✅ | `POST /ssot/segments/{name}/actions/publish` |

---

## Phase 3: Data Pipeline Visibility

| Tool | Status | Endpoint |
|------|--------|----------|
| `list_data_streams()` | ⬜ | `GET /ssot/data-streams` |
| `get_data_stream(name)` | ⬜ | `GET /ssot/data-streams/{name}` |
| `list_data_transforms()` | ⬜ | `GET /ssot/data-transforms` |
| `get_data_transform(name)` | ⬜ | `GET /ssot/data-transforms/{name}` |
| `get_transform_run_history(name)` | ⬜ | `GET /ssot/data-transforms/{name}/run-history` |
| `list_connections()` | ⬜ | `GET /ssot/connections` |
| `get_connection(name)` | ⬜ | `GET /ssot/connections/{name}` |
| `list_connectors()` | ⬜ | `GET /ssot/connectors` |
| `get_connection_objects(name)` | ⬜ | `POST /ssot/connections/{name}/objects` |
| `preview_connection(name, object)` | ⬜ | `POST /ssot/connections/{name}/preview` |
| `run_data_stream(...)` | ⬜ | `POST /ssot/data-streams/actions/run` |
| `run_data_transform(...)` | ⬜ | `POST /ssot/data-transforms/{name}/actions/run` |

---

## Phase 4: Schema Management

| Tool | Status | Endpoint |
|------|--------|----------|
| `list_data_lake_objects()` | ⬜ | `GET /ssot/data-lake-objects` |
| `get_data_lake_object(name)` | ⬜ | `GET /ssot/data-lake-objects/{name}` |
| `list_data_model_objects()` | ⬜ | `GET /ssot/data-model-objects` |
| `get_data_model_object(name)` | ⬜ | `GET /ssot/data-model-objects/{name}` |
| `get_dmo_mappings(name)` | ⬜ | `GET /ssot/data-model-objects/{name}/mappings` |
| `list_data_spaces()` | ⬜ | `GET /ssot/data-spaces` |
| `get_data_space(name)` | ⬜ | `GET /ssot/data-spaces/{name}` |
| `get_data_space_members(name)` | ⬜ | `GET /ssot/data-spaces/{name}/members` |
| `create_data_lake_object(...)` | ⬜ | `POST /ssot/data-lake-objects` |
| `create_data_model_object(...)` | ⬜ | `POST /ssot/data-model-objects` |

---

## Phase 5: ML & AI

| Tool | Status | Endpoint |
|------|--------|----------|
| `list_ml_models()` | ⬜ | `GET /ssot/ml-models` |
| `get_ml_model(name)` | ⬜ | `GET /ssot/ml-models/{name}` |
| `get_prediction(model, input)` | ⬜ | `GET /ssot/ml-models/{name}/predictions` |
| `list_model_artifacts()` | ⬜ | `GET /ssot/ml-model-artifacts` |
| `list_document_ai_configs()` | ⬜ | `GET /ssot/document-ai-configurations` |
| `extract_document_data(config, doc)` | ⬜ | `POST /ssot/document-ai-configurations/{name}/actions/extract-data` |
| `list_semantic_searches()` | ⬜ | `GET /ssot/semantic-searches` |
| `get_semantic_search(name)` | ⬜ | `GET /ssot/semantic-searches/{name}` |
| `get_semantic_search_config()` | ⬜ | `GET /ssot/semantic-search-config` |

---

## Phase 6: Admin & Config

| Tool | Status | Endpoint |
|------|--------|----------|
| `list_identity_rulesets()` | ⬜ | `GET /ssot/identity-resolutions` |
| `get_identity_ruleset(name)` | ⬜ | `GET /ssot/identity-resolutions/{name}` |
| `get_limits()` | ⬜ | `GET /ssot/limits` |
| `run_identity_resolution(...)` | ⬜ | `POST /ssot/identity-resolutions/{name}/actions/run` |
| `list_data_actions()` | ⬜ | `GET /ssot/data-actions` |
| `list_data_action_targets()` | ⬜ | `GET /ssot/data-action-targets` |
| `list_private_network_routes()` | ⬜ | `GET /ssot/private-network-routes` |
| `get_data_kit_status(id)` | ⬜ | `GET /ssot/data-kit-components/{id}/status` |

---

## API Reference

| API Type | Base Path | Auth | Performance |
|----------|-----------|------|-------------|
| **Direct APIs** | `/api/v1/*` | 2-step (OAuth → tenant token) | Faster |
| **Connect APIs** | `/services/data/v{version}/ssot/*` | Standard OAuth | Standard |

**Direct API Endpoints (use dc_tenant_url):**
- Metadata: `GET /api/v1/metadata`
- Metadata filtered: `GET /api/v1/metadata?entityName=...&entityType=...&entityCategory=...`
- Query V1: `POST /api/v1/query` (sync)
- Query V1 limited: `POST /api/v1/query?limit=N`
- Query V2: `POST /api/v2/query` (async, returns nextBatchId)
- Query V2 next: `GET /api/v2/query/{nextBatchId}`
- Data Graph: `GET /api/v1/dataGraph/metadata`

**Files to modify:**

| File | Changes |
|------|---------|
| `oauth.py` | Add chmod + client_id validation |
| `direct_api.py` | **NEW** - Data 360 API client (2-step auth) |
| `server.py` | Add new tools |
| `connect_api_dc_sql.py` | Structured error responses |
| `requirements.txt` | Add sqlparse |
| `README.md` | Claude Code config docs |
| `CLAUDE.md` | Update with new tools |
