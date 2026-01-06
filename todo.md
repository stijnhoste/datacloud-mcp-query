# Data Cloud MCP - Full Connect API Coverage

> **API Reference:** See `api-reference/API_REFERENCE.md`
> **Target Org:** `mca-next-sdo`
> **Total Tools:** 153

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ⬜ | Not started |
| 🔄 | In progress |
| ✅ | Implemented |
| 🧪 | Tested on mca-next-sdo |

---

## Phase 1: Query & SQL ✅

| Tool | Status | Endpoint |
|------|--------|----------|
| `query(sql)` | ✅ | `POST /ssot/query-sql` |
| `list_tables()` | ✅ | SQL query |
| `describe_table(table)` | ✅ | SQL query |
| `validate_query(sql)` | ✅ | Local (sqlparse) |
| `format_sql(sql)` | ✅ | Local (sqlparse) |

---

## Phase 2: Metadata & Schema ✅

| Tool | Status | Endpoint |
|------|--------|----------|
| `get_metadata()` | ✅ | `GET /ssot/metadata` |
| `describe_table_full(table)` | ✅ | Uses metadata |
| `get_relationships(entity)` | ✅ | Uses metadata |
| `explore_table(table)` | ✅ | Combined query + metadata |
| `search_tables(keyword)` | ✅ | Uses metadata |

---

## Phase 3: Profile Queries ✅

| Tool | Status | Endpoint |
|------|--------|----------|
| `get_profile_metadata()` | ✅ | `GET /ssot/profile/metadata` |
| `query_profile(dmo_name)` | ✅ | `GET /ssot/profile/:dmoName` |
| `get_profile_record(dmo, id)` | ✅ | `GET /ssot/profile/:dmo/:id` |
| `get_profile_record_with_children(...)` | ✅ | `GET /ssot/profile/:dmo/:id/:childDmo` |
| `get_profile_record_with_insights(...)` | ✅ | `GET /ssot/profile/:dmo/:id/calculated-insights/:ci` |

---

## Phase 4: Calculated Insights ✅

| Tool | Status | Endpoint |
|------|--------|----------|
| `list_calculated_insights()` | ✅ | `GET /ssot/calculated-insights` |
| `get_calculated_insight(name)` | ✅ | `GET /ssot/calculated-insights/:apiName` |
| `create_calculated_insight(def)` | ✅ | `POST /ssot/calculated-insights` |
| `update_calculated_insight(name, updates)` | ✅ | `PATCH /ssot/calculated-insights/:apiName` |
| `delete_calculated_insight(name)` | ✅ | `DELETE /ssot/calculated-insights/:apiName` |
| `run_calculated_insight(name)` | ✅ | `POST /ssot/calculated-insights/:apiName/actions/run` |
| `query_calculated_insight(...)` | ✅ | `GET /ssot/insight/calculated-insights/:ciName` |
| `get_insight_metadata()` | ✅ | `GET /ssot/insight/metadata` |

---

## Phase 5: Data Graphs ✅

| Tool | Status | Endpoint |
|------|--------|----------|
| `list_data_graphs()` | ✅ | `GET /ssot/data-graphs/metadata` |
| `get_data_graph(name)` | ✅ | `GET /ssot/data-graphs/:dataGraphName` |
| `create_data_graph(def)` | ✅ | `POST /ssot/data-graphs` |
| `delete_data_graph(name)` | ✅ | `DELETE /ssot/data-graphs/:dataGraphName` |
| `refresh_data_graph(name)` | ✅ | `POST /ssot/data-graphs/:name/actions/refresh` |
| `query_data_graph(...)` | ✅ | `GET /ssot/data-graphs/data/:entity/:id` |

---

## Phase 6: Segments ✅

| Tool | Status | Endpoint |
|------|--------|----------|
| `list_segments()` | ✅ | `GET /ssot/segments` |
| `get_segment(name)` | ✅ | `GET /ssot/segments/:name` |
| `create_segment(def)` | ✅ | `POST /ssot/segments` |
| `update_segment(name, updates)` | ✅ | `PATCH /ssot/segments/:name` |
| `delete_segment(name)` | ✅ | `DELETE /ssot/segments/:name` |
| `get_segment_members(name)` | ✅ | `GET /ssot/segments/:name/members` |
| `count_segment(name)` | ✅ | `POST /ssot/segments/:name/actions/count` |
| `publish_segment(name)` | ✅ | `POST /ssot/segments/:id/actions/publish` |
| `deactivate_segment(name)` | ✅ | `POST /ssot/segments/:name/actions/deactivate` |

---

## Phase 7: Activations ✅

| Tool | Status | Endpoint |
|------|--------|----------|
| `list_activations()` | ✅ | `GET /ssot/activations` |
| `get_activation(id)` | ✅ | `GET /ssot/activations/:id` |
| `create_activation(def)` | ✅ | `POST /ssot/activations` |
| `update_activation(id, updates)` | ✅ | `PUT /ssot/activations/:id` |
| `delete_activation(id)` | ✅ | `DELETE /ssot/activations/:id` |
| `get_audience_records(id)` | ✅ | `GET /ssot/activations/:id/data` |
| `list_activation_targets()` | ✅ | `GET /ssot/activation-targets` |
| `get_activation_target(name)` | ✅ | `GET /ssot/activation-targets/:apiName` |
| `create_activation_target(def)` | ✅ | `POST /ssot/activation-targets` |
| `update_activation_target(name, updates)` | ✅ | `PATCH /ssot/activation-targets/:apiName` |
| `list_activation_external_platforms()` | ✅ | `GET /ssot/activations/external-platforms` |

---

## Phase 8: Data Streams ✅

| Tool | Status | Endpoint |
|------|--------|----------|
| `list_data_streams()` | ✅ | `GET /ssot/data-streams` |
| `get_data_stream(name)` | ✅ | `GET /ssot/data-streams/:name` |
| `create_data_stream(def)` | ✅ | `POST /ssot/data-streams` |
| `update_data_stream(name, updates)` | ✅ | `PATCH /ssot/data-streams/:name` |
| `delete_data_stream(name)` | ✅ | `DELETE /ssot/data-streams/:name` |
| `run_data_stream(names)` | ✅ | `POST /ssot/data-streams/actions/run` |

---

## Phase 9: Data Transforms ✅

| Tool | Status | Endpoint |
|------|--------|----------|
| `list_data_transforms()` | ✅ | `GET /ssot/data-transforms` |
| `get_data_transform(name)` | ✅ | `GET /ssot/data-transforms/:name` |
| `create_data_transform(def)` | ✅ | `POST /ssot/data-transforms` |
| `update_data_transform(name, updates)` | ✅ | `PUT /ssot/data-transforms/:name` |
| `delete_data_transform(name)` | ✅ | `DELETE /ssot/data-transforms/:name` |
| `run_data_transform(name)` | ✅ | `POST /ssot/data-transforms/:name/actions/run` |
| `get_transform_run_history(name)` | ✅ | `GET /ssot/data-transforms/:name/run-history` |
| `cancel_data_transform(name)` | ✅ | `POST /ssot/data-transforms/:name/actions/cancel` |
| `retry_data_transform(name)` | ✅ | `POST /ssot/data-transforms/:name/actions/retry` |
| `get_transform_schedule(name)` | ✅ | `GET /ssot/data-transforms/:name/schedule` |
| `update_transform_schedule(name, schedule)` | ✅ | `PUT /ssot/data-transforms/:name/schedule` |
| `validate_data_transform(def)` | ✅ | `POST /ssot/data-transforms-validation` |

---

## Phase 10: Connections ✅

| Tool | Status | Endpoint |
|------|--------|----------|
| `list_connections()` | ✅ | `GET /ssot/connections` |
| `get_connection(name)` | ✅ | `GET /ssot/connections/:id` |
| `create_connection(def)` | ✅ | `POST /ssot/connections` |
| `update_connection(id, updates)` | ✅ | `PATCH /ssot/connections/:id` |
| `delete_connection(id)` | ✅ | `DELETE /ssot/connections/:id` |
| `get_connection_objects(name)` | ✅ | `POST /ssot/connections/:id/objects` |
| `preview_connection(name, object)` | ✅ | `POST /ssot/connections/:id/objects/:name/preview` |
| `get_connection_schema(id)` | ✅ | `GET /ssot/connections/:id/schema` |
| `get_connection_endpoints(id)` | ✅ | `GET /ssot/connections/:id/endpoints` |
| `get_connection_databases(id)` | ✅ | `POST /ssot/connections/:id/databases` |
| `get_connection_database_schemas(id)` | ✅ | `POST /ssot/connections/:id/database-schemas` |
| `list_connectors()` | ✅ | `GET /ssot/connectors` |
| `get_connector(type)` | ✅ | `GET /ssot/connectors/:type` |

---

## Phase 11: Data Lake Objects (DLOs) ✅

| Tool | Status | Endpoint |
|------|--------|----------|
| `list_data_lake_objects()` | ✅ | `GET /ssot/data-lake-objects` |
| `get_data_lake_object(name)` | ✅ | `GET /ssot/data-lake-objects/:name` |
| `create_data_lake_object(def)` | ✅ | `POST /ssot/data-lake-objects` |
| `update_data_lake_object(name, updates)` | ✅ | `PATCH /ssot/data-lake-objects/:name` |
| `delete_data_lake_object(name)` | ✅ | `DELETE /ssot/data-lake-objects/:name` |

---

## Phase 12: Data Model Objects (DMOs) ✅

| Tool | Status | Endpoint |
|------|--------|----------|
| `list_data_model_objects()` | ✅ | `GET /ssot/data-model-objects` |
| `get_data_model_object(name)` | ✅ | `GET /ssot/data-model-objects/:name` |
| `create_data_model_object(def)` | ✅ | `POST /ssot/data-model-objects` |
| `update_data_model_object(name, updates)` | ✅ | `PATCH /ssot/data-model-objects/:name` |
| `delete_data_model_object(name)` | ✅ | `DELETE /ssot/data-model-objects/:name` |
| `get_dmo_mappings(name)` | ✅ | `GET /ssot/data-model-object-mappings` |
| `create_dmo_mapping(def)` | ✅ | `POST /ssot/data-model-object-mappings` |
| `delete_dmo_mapping(name)` | ✅ | `DELETE /ssot/data-model-object-mappings/:name` |
| `get_dmo_relationships(name)` | ✅ | `GET /ssot/data-model-objects/:name/relationships` |
| `create_dmo_relationship(name, def)` | ✅ | `POST /ssot/data-model-objects/:name/relationships` |
| `delete_dmo_relationship(name)` | ✅ | `DELETE /ssot/data-model-objects/relationships/:name` |

---

## Phase 13: Data Spaces ✅

| Tool | Status | Endpoint |
|------|--------|----------|
| `list_data_spaces()` | ✅ | `GET /ssot/data-spaces` |
| `get_data_space(name)` | ✅ | `GET /ssot/data-spaces/:name` |
| `create_data_space(def)` | ✅ | `POST /ssot/data-spaces` |
| `update_data_space(name, updates)` | ✅ | `PATCH /ssot/data-spaces/:name` |
| `get_data_space_members(name)` | ✅ | `GET /ssot/data-spaces/:name/members` |
| `update_data_space_members(name, members)` | ✅ | `PUT /ssot/data-spaces/:name/members` |
| `get_data_space_member(space, member)` | ✅ | `GET /ssot/data-spaces/:name/members/:member` |

---

## Phase 14: Machine Learning ✅

| Tool | Status | Endpoint |
|------|--------|----------|
| `list_ml_models()` | ✅ | `GET /ssot/machine-learning/configured-models` |
| `get_ml_model(name)` | ✅ | `GET /ssot/machine-learning/configured-models/:name` |
| `update_ml_model(name, updates)` | ✅ | `PATCH /ssot/machine-learning/configured-models/:name` |
| `delete_ml_model(name)` | ✅ | `DELETE /ssot/machine-learning/configured-models/:name` |
| `get_prediction(model, input)` | ✅ | `POST /ssot/machine-learning/predict` |
| `list_model_artifacts()` | ✅ | `GET /ssot/machine-learning/model-artifacts` |
| `get_model_artifact(name)` | ✅ | `GET /ssot/machine-learning/model-artifacts/:name` |
| `update_model_artifact(name, updates)` | ✅ | `PATCH /ssot/machine-learning/model-artifacts/:name` |
| `delete_model_artifact(name)` | ✅ | `DELETE /ssot/machine-learning/model-artifacts/:name` |

---

## Phase 15: Document AI ✅

| Tool | Status | Endpoint |
|------|--------|----------|
| `list_document_ai_configs()` | ✅ | `GET /ssot/document-processing/configurations` |
| `get_document_ai_config(id)` | ✅ | `GET /ssot/document-processing/configurations/:id` |
| `create_document_ai_config(def)` | ✅ | `POST /ssot/document-processing/configurations` |
| `update_document_ai_config(id, updates)` | ✅ | `PATCH /ssot/document-processing/configurations/:id` |
| `delete_document_ai_config(id)` | ✅ | `DELETE /ssot/document-processing/configurations/:id` |
| `extract_document_data(config, doc)` | ✅ | `POST /ssot/document-processing/actions/extract-data` |
| `run_document_ai(config)` | ✅ | `POST /ssot/document-processing/configurations/:id/actions/run` |
| `generate_document_schema(request)` | ✅ | `POST /ssot/document-processing/actions/generate-schema` |
| `get_document_ai_global_config()` | ✅ | `GET /ssot/document-processing/global-config` |

---

## Phase 16: Semantic Search ✅

| Tool | Status | Endpoint |
|------|--------|----------|
| `list_semantic_searches()` | ✅ | `GET /ssot/search-index` |
| `get_semantic_search(name)` | ✅ | `GET /ssot/search-index/:name` |
| `create_semantic_search(def)` | ✅ | `POST /ssot/search-index` |
| `update_semantic_search(id, updates)` | ✅ | `PATCH /ssot/search-index/:id` |
| `delete_semantic_search(id)` | ✅ | `DELETE /ssot/search-index/:id` |
| `get_semantic_search_config()` | ✅ | `GET /ssot/search-index/config` |

---

## Phase 17: Identity Resolution ✅

| Tool | Status | Endpoint |
|------|--------|----------|
| `list_identity_rulesets()` | ✅ | `GET /ssot/identity-resolutions` |
| `get_identity_ruleset(name)` | ✅ | `GET /ssot/identity-resolutions/:name` |
| `create_identity_ruleset(def)` | ✅ | `POST /ssot/identity-resolutions` |
| `update_identity_ruleset(name, updates)` | ✅ | `PATCH /ssot/identity-resolutions/:name` |
| `delete_identity_ruleset(name)` | ✅ | `DELETE /ssot/identity-resolutions/:name` |
| `run_identity_resolution(name)` | ✅ | `POST /ssot/identity-resolutions/:name/actions/run-now` |
| `lookup_unified_id(...)` | ✅ | `GET /ssot/universalIdLookup/:entity/:dsId/:dsObjId/:srcId` |

---

## Phase 18: Data Actions ✅

| Tool | Status | Endpoint |
|------|--------|----------|
| `list_data_actions()` | ✅ | `GET /ssot/data-actions` |
| `create_data_action(def)` | ✅ | `POST /ssot/data-actions` |
| `list_data_action_targets()` | ✅ | `GET /ssot/data-action-targets` |
| `get_data_action_target(name)` | ✅ | `GET /ssot/data-action-targets/:apiName` |
| `create_data_action_target(def)` | ✅ | `POST /ssot/data-action-targets` |
| `delete_data_action_target(name)` | ✅ | `DELETE /ssot/data-action-targets/:apiName` |
| `get_data_action_target_signing_key(name)` | ✅ | `GET /ssot/data-action-targets/:apiName/signing-key` |

---

## Phase 19: Admin & Monitoring ✅

| Tool | Status | Endpoint |
|------|--------|----------|
| `get_limits()` | ✅ | `GET /limits` |
| `list_private_network_routes()` | ✅ | `GET /ssot/private-network-routes` |
| `get_private_network_route(id)` | ✅ | `GET /ssot/private-network-routes/:id` |
| `create_private_network_route(def)` | ✅ | `POST /ssot/private-network-routes` |
| `delete_private_network_route(id)` | ✅ | `DELETE /ssot/private-network-routes/:id` |
| `get_data_kit_status(id)` | ✅ | `GET /ssot/data-kit-components/:id/status` |
| `get_data_kit_component_dependencies(kit, comp)` | ✅ | `GET /ssot/data-kits/:kit/components/:comp/dependencies` |
| `get_data_kit_deployment_status(kit, comp)` | ✅ | `GET /ssot/data-kits/:kit/components/:comp/deployment-status` |
| `undeploy_data_kit(name)` | ✅ | `POST /ssot/data-kits/:name/actions/undeploy` |

---

## Summary

| Phase | Category | Status |
|-------|----------|--------|
| 1 | Query & SQL | ✅ 100% |
| 2 | Metadata & Schema | ✅ 100% |
| 3 | Profile Queries | ✅ 100% |
| 4 | Calculated Insights | ✅ 100% |
| 5 | Data Graphs | ✅ 100% |
| 6 | Segments | ✅ 100% |
| 7 | Activations | ✅ 100% |
| 8 | Data Streams | ✅ 100% |
| 9 | Data Transforms | ✅ 100% |
| 10 | Connections | ✅ 100% |
| 11 | DLOs | ✅ 100% |
| 12 | DMOs | ✅ 100% |
| 13 | Data Spaces | ✅ 100% |
| 14 | Machine Learning | ✅ 100% |
| 15 | Document AI | ✅ 100% |
| 16 | Semantic Search | ✅ 100% |
| 17 | Identity Resolution | ✅ 100% |
| 18 | Data Actions | ✅ 100% |
| 19 | Admin & Monitoring | ✅ 100% |

**Total: 153 tools - Full Connect API Coverage ✅**

---

## Next Steps

1. 🧪 Run comprehensive tests on `mca-next-sdo` org
2. 📝 Update CLAUDE.md with accurate tool count
3. 🚀 Commit and push changes
