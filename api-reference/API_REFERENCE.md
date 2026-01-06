# Salesforce Data Cloud API Reference

This document provides a consolidated reference for Data Cloud APIs used by this MCP server.

## Authentication Overview

| API Type | Base URL | Auth Required | SF CLI Compatible |
|----------|----------|---------------|-------------------|
| **Connect API** | `{instance_url}/services/data/v63.0/ssot/` | Standard Salesforce token | Yes |
| **Direct API** | `{tenant_url}/api/v1/` | CDP tenant token (2-step) | No |

### When to Use Each

- **Connect API**: Use for most operations. Works with SF CLI auth out of the box.
- **Direct API**: Use only for high-performance bulk operations or when Connect API doesn't provide the endpoint.

---

## Connect API Endpoints (`/ssot/*`)

Works with standard Salesforce OAuth tokens (SF CLI compatible).

### Query & SQL

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ssot/query-sql` | Execute SQL query (PostgreSQL dialect) |
| `GET` | `/ssot/query-sql/:queryId` | Get query results |
| `GET` | `/ssot/query-sql/:queryId/rows` | Get query rows (pagination) |
| `DELETE` | `/ssot/query-sql/:queryId` | Cancel query |

### Metadata & Schema

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ssot/metadata` | Get all metadata |
| `GET` | `/ssot/profile/metadata` | Get profile metadata |
| `GET` | `/ssot/profile/metadata/:dataModelName` | Get DMO metadata |
| `GET` | `/ssot/insight/metadata` | Get calculated insight metadata |
| `GET` | `/ssot/insight/metadata/:ciName` | Get specific insight metadata |
| `GET` | `/ssot/data-graphs/metadata` | Get data graph metadata |

### Profile Queries

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ssot/profile/:dataModelName` | Query DMO records |
| `GET` | `/ssot/profile/:dataModelName/:id` | Get record by ID/search key |
| `GET` | `/ssot/profile/:dataModelName/:id/:childDataModelName` | Get record with children |
| `GET` | `/ssot/profile/:dataModelName/:id/calculated-insights/:ciName` | Get record with insight |

### Calculated Insights

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ssot/calculated-insights` | List all calculated insights |
| `POST` | `/ssot/calculated-insights` | Create calculated insight |
| `GET` | `/ssot/calculated-insights/:apiName` | Get insight definition |
| `PATCH` | `/ssot/calculated-insights/:apiName` | Update insight |
| `DELETE` | `/ssot/calculated-insights/:apiName` | Delete insight |
| `POST` | `/ssot/calculated-insights/:apiName/actions/run` | Run insight calculation |
| `GET` | `/ssot/insight/calculated-insights/:ciName` | **Query insight data** |

### Data Graphs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ssot/data-graphs/metadata` | Get all data graph metadata |
| `GET` | `/ssot/data-graphs/:dataGraphName` | Get data graph definition |
| `GET` | `/ssot/data-graphs/data/:dataGraphEntityName` | Query by lookup keys |
| `GET` | `/ssot/data-graphs/data/:dataGraphEntityName/:id` | Query by record ID |
| `POST` | `/ssot/data-graphs` | Create data graph |
| `DELETE` | `/ssot/data-graphs/:dataGraphName` | Delete data graph |
| `POST` | `/ssot/data-graphs/:dataGraphName/actions/refresh` | Refresh data graph |

### Universal ID Lookup

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ssot/universalIdLookup/:entityName/:dataSourceId/:dataSourceObjectId/:sourceRecordId` | Lookup unified ID |

### Segments

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ssot/segments` | List all segments |
| `POST` | `/ssot/segments` | Create segment |
| `GET` | `/ssot/segments/:segmentApiNameOrId` | Get segment |
| `PATCH` | `/ssot/segments/:segmentApiName` | Update segment |
| `DELETE` | `/ssot/segments/:segmentApiName` | Delete segment |
| `GET` | `/ssot/segments/:segmentApiName/members` | Get segment members |
| `POST` | `/ssot/segments/:segmentApiName/actions/count` | Count members |
| `POST` | `/ssot/segments/:segmentId/actions/publish` | Publish segment |
| `POST` | `/ssot/segments/:segmentApiName/actions/deactivate` | Deactivate segment |

### Activations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ssot/activations` | List all activations |
| `POST` | `/ssot/activations` | Create activation |
| `GET` | `/ssot/activations/:activationId` | Get activation |
| `PUT` | `/ssot/activations/:activationId` | Update activation |
| `DELETE` | `/ssot/activations/:activationId` | Delete activation |
| `GET` | `/ssot/activations/:activationId/data` | Get audience DMO records |
| `GET` | `/ssot/activation-targets` | List activation targets |

### Data Streams

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ssot/data-streams` | List all data streams |
| `POST` | `/ssot/data-streams` | Create data stream |
| `GET` | `/ssot/data-streams/:recordIdOrDeveloperName` | Get data stream |
| `PATCH` | `/ssot/data-streams/:recordIdOrDeveloperName` | Update data stream |
| `DELETE` | `/ssot/data-streams/:recordIdOrDeveloperName` | Delete data stream |
| `POST` | `/ssot/data-streams/:recordIdOrDeveloperName/actions/run` | Run data stream |

### Data Transforms

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ssot/data-transforms` | List all transforms |
| `POST` | `/ssot/data-transforms` | Create transform |
| `GET` | `/ssot/data-transforms/:dataTransformNameOrId` | Get transform |
| `PUT` | `/ssot/data-transforms/:dataTransformNameOrId` | Update transform |
| `DELETE` | `/ssot/data-transforms/:dataTransformNameOrId` | Delete transform |
| `POST` | `/ssot/data-transforms/:dataTransformNameOrId/actions/run` | Run transform |
| `GET` | `/ssot/data-transforms/:dataTransformNameOrId/run-history` | Get run history |

### Connections

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ssot/connections` | List all connections |
| `POST` | `/ssot/connections` | Create connection |
| `GET` | `/ssot/connections/:connectionId` | Get connection |
| `PATCH` | `/ssot/connections/:connectionId` | Update connection |
| `DELETE` | `/ssot/connections/:connectionId` | Delete connection |
| `POST` | `/ssot/connections/:connectionId/objects` | Get available objects |
| `POST` | `/ssot/connections/:connectionId/objects/:resourceName/preview` | Preview data |
| `GET` | `/ssot/connectors` | List connector types |

### Data Lake Objects (DLOs)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ssot/data-lake-objects` | List all DLOs |
| `POST` | `/ssot/data-lake-objects` | Create DLO |
| `GET` | `/ssot/data-lake-objects/:recordIdOrDeveloperName` | Get DLO |
| `PATCH` | `/ssot/data-lake-objects/:recordIdOrDeveloperName` | Update DLO |
| `DELETE` | `/ssot/data-lake-objects/:recordIdOrDeveloperName` | Delete DLO |

### Data Model Objects (DMOs)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ssot/data-model-objects` | List all DMOs |
| `POST` | `/ssot/data-model-objects` | Create DMO |
| `GET` | `/ssot/data-model-objects/:dataModelObjectName` | Get DMO |
| `PATCH` | `/ssot/data-model-objects/:dataModelObjectName` | Update DMO |
| `DELETE` | `/ssot/data-model-objects/:dataModelObjectName` | Delete DMO |
| `GET` | `/ssot/data-model-object-mappings` | Get field mappings |
| `GET` | `/ssot/data-model-objects/:dataModelObjectName/relationships` | Get relationships |

### Data Spaces

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ssot/data-spaces` | List all data spaces |
| `POST` | `/ssot/data-spaces` | Create data space |
| `GET` | `/ssot/data-spaces/:idOrName` | Get data space |
| `PATCH` | `/ssot/data-spaces/:idOrName` | Update data space |
| `GET` | `/ssot/data-spaces/:idOrName/members` | Get data space members |

### Machine Learning

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ssot/machine-learning/configured-models` | List ML models |
| `GET` | `/ssot/machine-learning/configured-models/:configuredModelIdOrName` | Get ML model |
| `GET` | `/ssot/machine-learning/model-artifacts` | List model artifacts |
| `POST` | `/ssot/machine-learning/predict` | Get predictions |

### Document AI

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ssot/document-processing/configurations` | List Document AI configs |
| `POST` | `/ssot/document-processing/actions/extract-data` | Extract document data |

### Semantic Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ssot/search-index` | List semantic searches |
| `GET` | `/ssot/search-index/:searchIndexApiNameOrId` | Get semantic search |
| `GET` | `/ssot/search-index/config` | Get global config |

### Identity Resolution

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ssot/identity-resolutions` | List identity rulesets |
| `GET` | `/ssot/identity-resolutions/:identityResolution` | Get ruleset |
| `POST` | `/ssot/identity-resolutions/:identityResolution/actions/run-now` | Run identity resolution |

### Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ssot/limits` | Get API limits and usage |
| `GET` | `/ssot/data-actions` | List data actions |
| `GET` | `/ssot/data-action-targets` | List data action targets |
| `GET` | `/ssot/private-network-routes` | List private network routes |

---

## Direct API Endpoints (`/api/v1/*`)

Requires CDP tenant token obtained via 2-step authentication. Use only when Connect API doesn't provide the functionality.

### Metadata

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/metadata` | Get all metadata (faster than Connect) |
| `GET` | `/api/v1/metadata?entityType=dlm` | Filter by entity type |
| `GET` | `/api/v1/metadata?entityName=ssot__Individual__dlm` | Filter by entity |

### Calculated Insights (Query)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/insight/metadata` | Get all insight metadata |
| `GET` | `/api/v1/insight/metadata/:ci_name` | Get specific insight metadata |
| `GET` | `/api/v1/insight/calculated-insights/:ci_name` | Query insight data |

### Data Graphs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/dataGraph/metadata` | Get all data graph metadata |
| `GET` | `/api/v1/dataGraph/:dataGraphName/:dataGraphRecordId` | Query by record ID |
| `GET` | `/api/v1/dataGraph/:dataGraphName?lookupKeys=...` | Query by lookup keys |

### Universal ID Lookup

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/universalIdLookup/:entityName/:dataSourceId__c/:dataSourceObjectId__c/:sourceRecordId__c` | Lookup unified ID |

### Ingestion (Streaming)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/ingest/sources/:sourceName/:objectName` | Insert records |
| `DELETE` | `/api/v1/ingest/sources/:sourceName/:objectName` | Delete records |

### Ingestion (Bulk)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/ingest/jobs` | Create bulk job |
| `PUT` | `/api/v1/ingest/jobs/:jobId/batches` | Upload batch data |
| `PATCH` | `/api/v1/ingest/jobs/:jobId` | Close/abort job |
| `GET` | `/api/v1/ingest/jobs/:jobId` | Get job status |
| `GET` | `/api/v1/ingest/jobs` | List all jobs |

### Profile API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/profile/metadata` | Get profile metadata |
| `GET` | `/api/v1/profile/:dmoApiName` | Query DMO records |
| `GET` | `/api/v1/profile/:dmoApiName/:dmoRecordId` | Get by ID |
| `GET` | `/api/v1/profile/:dmoParentApiName/:id/:dmoChildApiName` | Get with children |

### Query API (Alternative to Connect SQL)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/query` | Execute query |
| `POST` | `/api/v2/query` | Execute query (v2) |
| `GET` | `/api/v2/query/:nextBatchId` | Get next batch |

---

## Feature Availability by Auth Method

| Feature | SF CLI Auth | Connected App |
|---------|:-----------:|:-------------:|
| SQL Queries (`query-sql`) | Yes | Yes |
| Segments | Yes | Yes |
| Activations | Yes | Yes |
| Data Streams | Yes | Yes |
| Data Transforms | Yes | Yes |
| Connections | Yes | Yes |
| DLOs/DMOs | Yes | Yes |
| Data Spaces | Yes | Yes |
| ML Models | Yes | Yes |
| Document AI | Yes | Yes |
| Semantic Search | Yes | Yes |
| Identity Resolution | Yes | Yes |
| Calculated Insights (list/manage) | Yes | Yes |
| Calculated Insights (query data) | Yes | Yes |
| Data Graphs (list/manage) | Yes | Yes |
| Data Graphs (query data) | Yes | Yes |
| Profile Queries | Yes | Yes |
| Universal ID Lookup | Yes | Yes |
| Admin/Limits | Yes | Yes |
| Direct API Metadata | No | Yes |
| Streaming Ingestion | No | Yes |
| Bulk Ingestion | No | Yes |

**Note**: The only features requiring a Connected App with CDP scopes are:
- Direct API metadata (faster, more detailed)
- Data ingestion (streaming and bulk)
