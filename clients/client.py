"""
Connect API Client for Salesforce Data Cloud.

This module provides the main ConnectAPIClient class with methods for all
Data Cloud Connect API endpoints: segments, activations, data streams,
transforms, connections, DLOs, DMOs, and more.

Connect APIs use standard OAuth tokens (no second token exchange like Direct APIs).
"""

import logging
from typing import Optional

import requests

from .base import BaseClient

logger = logging.getLogger(__name__)


class ConnectAPIClient(BaseClient):
    """
    Client for Data Cloud Connect APIs.

    Provides methods for all /services/data/v63.0/ssot/* endpoints including:
    - Segments and activations
    - Data streams and transforms
    - Connections and connectors
    - Data Lake Objects (DLOs) and Data Model Objects (DMOs)
    - Data spaces
    - Calculated insights and data graphs
    - Identity resolution
    - ML models and predictions
    - Document AI and semantic search
    - Admin and monitoring
    """

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None
    ) -> dict:
        """
        Make an authenticated request to the Connect API.

        Wraps the base _request method to support json_data parameter name
        for backwards compatibility.
        """
        return super()._request(method, endpoint, params, json_body=json_data)

    # ========== Query API ==========

    def cancel_sql_query(self, query_id: str) -> dict:
        """
        Cancel a running SQL query.

        Args:
            query_id: The ID of the query to cancel (from query submission response)

        Returns:
            dict: Cancellation result
        """
        return self._request('DELETE', f'/query-sql/{query_id}')

    def query_v2(self, query_definition: dict) -> dict:
        """
        Execute a query using the V2 API.

        Args:
            query_definition: Query definition object

        Returns:
            dict: Query results with nextBatchId for pagination
        """
        return self._request('POST', '/queryv2', json_data=query_definition)

    def get_query_batch_v2(self, batch_id: str) -> dict:
        """
        Get the next batch of results from a V2 query.

        Args:
            batch_id: The nextBatchId from a previous V2 query response

        Returns:
            dict: Next batch of query results
        """
        return self._request('GET', f'/queryv2/{batch_id}')

    # ========== Segments API ==========

    def list_segments(self) -> dict:
        """
        List all segments.

        Returns:
            dict: List of segment metadata
        """
        return self._request('GET', '/segments')

    def get_segment(self, segment_name: str) -> dict:
        """
        Get details for a specific segment.

        Args:
            segment_name: Name of the segment

        Returns:
            dict: Segment details
        """
        return self._request('GET', f'/segments/{segment_name}')

    def get_segment_members(
        self,
        segment_name: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> dict:
        """
        Get members of a segment.

        Args:
            segment_name: Name of the segment
            limit: Maximum number of members to return
            offset: Offset for pagination

        Returns:
            dict: Segment members
        """
        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset

        return self._request('GET', f'/segments/{segment_name}/members', params=params or None)

    def count_segment(self, segment_name: str) -> dict:
        """
        Get the count of members in a segment.

        Args:
            segment_name: Name of the segment

        Returns:
            dict: Segment count result
        """
        # API requires an entity body for POST
        return self._request('POST', f'/segments/{segment_name}/actions/count', json_data={})

    def create_segment(self, segment_definition: dict) -> dict:
        """
        Create a new segment.

        Args:
            segment_definition: Segment configuration

        Returns:
            dict: Created segment details
        """
        return self._request('POST', '/segments', json_data=segment_definition)

    def update_segment(self, segment_name: str, segment_updates: dict) -> dict:
        """
        Update an existing segment.

        Args:
            segment_name: Name of the segment to update
            segment_updates: Fields to update

        Returns:
            dict: Updated segment details
        """
        return self._request('PATCH', f'/segments/{segment_name}', json_data=segment_updates)

    def delete_segment(self, segment_name: str) -> dict:
        """
        Delete a segment.

        Args:
            segment_name: Name of the segment to delete

        Returns:
            dict: Deletion result
        """
        return self._request('DELETE', f'/segments/{segment_name}')

    def publish_segment(self, segment_name: str) -> dict:
        """
        Publish a segment to make it available for activation.

        Args:
            segment_name: Name of the segment to publish

        Returns:
            dict: Publish result
        """
        return self._request('POST', f'/segments/{segment_name}/actions/publish')

    def deactivate_segment(self, segment_name: str) -> dict:
        """
        Deactivate a published segment.

        Args:
            segment_name: Name of the segment to deactivate

        Returns:
            dict: Deactivation result
        """
        return self._request('POST', f'/segments/{segment_name}/actions/deactivate')

    # ========== Activations API ==========

    def list_activations(self) -> dict:
        """
        List all activations.

        Returns:
            dict: List of activation metadata
        """
        return self._request('GET', '/activations')

    def get_activation(self, activation_id: str) -> dict:
        """
        Get details for a specific activation.

        Args:
            activation_id: ID of the activation

        Returns:
            dict: Activation details
        """
        return self._request('GET', f'/activations/{activation_id}')

    def get_audience_records(
        self,
        activation_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> dict:
        """
        Get audience DMO records for an activation.

        Args:
            activation_id: ID of the activation
            limit: Maximum number of records to return
            offset: Offset for pagination

        Returns:
            dict: Audience records
        """
        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset

        return self._request(
            'GET',
            f'/activations/{activation_id}/audience-dmo-records',
            params=params or None
        )

    def list_activation_targets(self) -> dict:
        """
        List all available activation targets.

        Returns:
            dict: List of activation targets
        """
        return self._request('GET', '/activation-targets')

    # ========== Data Streams API (Phase 3) ==========

    def list_data_streams(self) -> dict:
        """
        List all data streams.

        Returns:
            dict: List of data stream metadata
        """
        return self._request('GET', '/data-streams')

    def get_data_stream(self, stream_name: str) -> dict:
        """
        Get details for a specific data stream.

        Args:
            stream_name: Name of the data stream

        Returns:
            dict: Data stream details
        """
        return self._request('GET', f'/data-streams/{stream_name}')

    def run_data_stream(self, stream_names: list[str]) -> dict:
        """
        Run one or more data streams.

        Args:
            stream_names: List of data stream names to run

        Returns:
            dict: Run result
        """
        return self._request('POST', '/data-streams/actions/run', json_data={'dataStreamNames': stream_names})

    # ========== Data Transforms API (Phase 3) ==========

    def list_data_transforms(self) -> dict:
        """
        List all data transforms.

        Returns:
            dict: List of data transform metadata
        """
        return self._request('GET', '/data-transforms')

    def get_data_transform(self, transform_name: str) -> dict:
        """
        Get details for a specific data transform.

        Args:
            transform_name: Name of the data transform

        Returns:
            dict: Data transform details
        """
        return self._request('GET', f'/data-transforms/{transform_name}')

    def get_transform_run_history(self, transform_name: str) -> dict:
        """
        Get run history for a data transform.

        Args:
            transform_name: Name of the data transform

        Returns:
            dict: Run history
        """
        return self._request('GET', f'/data-transforms/{transform_name}/run-history')

    def run_data_transform(self, transform_name: str) -> dict:
        """
        Run a data transform.

        Args:
            transform_name: Name of the data transform to run

        Returns:
            dict: Run result
        """
        # API requires an entity body for POST
        return self._request('POST', f'/data-transforms/{transform_name}/actions/run', json_data={})

    # ========== Connections API (Phase 3) ==========

    def list_connections(self, connector_type: str = None) -> dict:
        """
        List all connections.

        Args:
            connector_type: Optional connector type to filter by (e.g., 'SalesforceMarketingCloud').
                          Use list_connectors() to see available types.

        Returns:
            dict: List of connection metadata
        """
        params = {}
        if connector_type:
            params['connectorType'] = connector_type
        return self._request('GET', '/connections', params=params if params else None)

    def get_connection(self, connection_name: str) -> dict:
        """
        Get details for a specific connection.

        Args:
            connection_name: Name of the connection

        Returns:
            dict: Connection details
        """
        return self._request('GET', f'/connections/{connection_name}')

    def get_connection_objects(self, connection_name: str) -> dict:
        """
        Get available objects for a connection.

        Args:
            connection_name: Name of the connection

        Returns:
            dict: Available objects
        """
        return self._request('POST', f'/connections/{connection_name}/objects')

    def preview_connection(
        self,
        connection_name: str,
        object_name: str,
        limit: Optional[int] = None
    ) -> dict:
        """
        Preview data from a connection object.

        Args:
            connection_name: Name of the connection
            object_name: Name of the object to preview
            limit: Maximum number of records to preview

        Returns:
            dict: Preview data
        """
        payload = {'objectName': object_name}
        if limit:
            payload['limit'] = limit
        return self._request('POST', f'/connections/{connection_name}/preview', json_data=payload)

    # ========== Connectors API (Phase 3) ==========

    def list_connectors(self) -> dict:
        """
        List all available connectors.

        Returns:
            dict: List of connector metadata
        """
        return self._request('GET', '/connectors')

    # ========== Data Lake Objects API (Phase 4) ==========

    def list_data_lake_objects(self) -> dict:
        """
        List all data lake objects (DLOs).

        Data Lake Objects represent raw data tables ingested from external sources
        before they are mapped to Data Model Objects.

        Returns:
            dict: List of data lake object metadata
        """
        return self._request('GET', '/data-lake-objects')

    def get_data_lake_object(self, object_name: str) -> dict:
        """
        Get details for a specific data lake object.

        Args:
            object_name: Name of the data lake object

        Returns:
            dict: Data lake object details including fields and settings
        """
        return self._request('GET', f'/data-lake-objects/{object_name}')

    def create_data_lake_object(self, object_definition: dict) -> dict:
        """
        Create a new data lake object.

        Args:
            object_definition: DLO configuration including name, fields, and settings

        Returns:
            dict: Created data lake object details
        """
        return self._request('POST', '/data-lake-objects', json_data=object_definition)

    # ========== Data Model Objects API (Phase 4) ==========

    def list_data_model_objects(self) -> dict:
        """
        List all data model objects (DMOs).

        Data Model Objects are the canonical entities in Data Cloud that follow
        the standard schema (e.g., Individual, Account, ContactPointEmail).

        Returns:
            dict: List of data model object metadata
        """
        return self._request('GET', '/data-model-objects')

    def get_data_model_object(self, object_name: str) -> dict:
        """
        Get details for a specific data model object.

        Args:
            object_name: Name of the data model object

        Returns:
            dict: Data model object details including fields and relationships
        """
        return self._request('GET', f'/data-model-objects/{object_name}')

    def get_dmo_mappings(self, object_name: str) -> dict:
        """
        Get field mappings for a data model object.

        Shows how DLO fields are mapped to DMO fields.

        Args:
            object_name: Name of the data model object

        Returns:
            dict: Field mapping configuration
        """
        return self._request('GET', f'/data-model-objects/{object_name}/mappings')

    def create_data_model_object(self, object_definition: dict) -> dict:
        """
        Create a new data model object.

        Args:
            object_definition: DMO configuration including name, fields, and relationships

        Returns:
            dict: Created data model object details
        """
        return self._request('POST', '/data-model-objects', json_data=object_definition)

    # ========== Data Spaces API (Phase 4) ==========

    def list_data_spaces(self) -> dict:
        """
        List all data spaces.

        Data Spaces provide logical groupings for data governance and access control,
        allowing you to partition data for different teams or use cases.

        Returns:
            dict: List of data space metadata
        """
        return self._request('GET', '/data-spaces')

    def get_data_space(self, space_name: str) -> dict:
        """
        Get details for a specific data space.

        Args:
            space_name: Name of the data space

        Returns:
            dict: Data space details including settings and permissions
        """
        return self._request('GET', f'/data-spaces/{space_name}')

    def get_data_space_members(self, space_name: str) -> dict:
        """
        Get members (objects) included in a data space.

        Args:
            space_name: Name of the data space

        Returns:
            dict: List of objects in the data space
        """
        return self._request('GET', f'/data-spaces/{space_name}/members')

    # ========== ML Models API (Phase 5) ==========

    def list_ml_models(self) -> dict:
        """
        List all machine learning models.

        Returns:
            dict: List of ML model metadata including names, types, and status
        """
        return self._request('GET', '/machine-learning/configured-models')

    def get_ml_model(self, model_name: str) -> dict:
        """
        Get details for a specific ML model.

        Args:
            model_name: Name of the ML model

        Returns:
            dict: ML model details including configuration and metrics
        """
        return self._request('GET', f'/machine-learning/configured-models/{model_name}')

    def get_prediction(
        self,
        model_name: str,
        input_data: Optional[dict] = None
    ) -> dict:
        """
        Get predictions from an ML model.

        Args:
            model_name: Name of the ML model
            input_data: Input data for prediction (optional)

        Returns:
            dict: Prediction results
        """
        payload = {"configuredModelId": model_name}
        if input_data:
            payload.update(input_data)
        return self._request('POST', '/machine-learning/predict', json_data=payload)

    def list_model_artifacts(self) -> dict:
        """
        List all ML model artifacts.

        Model artifacts contain trained model files and associated metadata.

        Returns:
            dict: List of model artifact metadata
        """
        return self._request('GET', '/machine-learning/model-artifacts')

    # ========== Document AI API (Phase 5) ==========

    def list_document_ai_configs(self) -> dict:
        """
        List all Document AI configurations.

        Document AI extracts structured data from documents like invoices,
        contracts, and forms.

        Returns:
            dict: List of Document AI configuration metadata
        """
        return self._request('GET', '/document-processing/configurations')

    def extract_document_data(
        self,
        config_name: str,
        document_data: dict
    ) -> dict:
        """
        Extract data from a document using Document AI.

        Args:
            config_name: Name of the Document AI configuration
            document_data: Document content and metadata for extraction

        Returns:
            dict: Extracted structured data
        """
        return self._request(
            'POST',
            '/document-processing/actions/extract-data',
            json_data={"configName": config_name, **document_data}
        )

    # ========== Semantic Search API (Phase 5) ==========

    def list_semantic_searches(self) -> dict:
        """
        List all semantic search configurations.

        Semantic search enables natural language queries over your data
        using vector embeddings.

        Returns:
            dict: List of semantic search metadata
        """
        return self._request('GET', '/search-index')

    def get_semantic_search(self, search_name: str) -> dict:
        """
        Get details for a specific semantic search configuration.

        Args:
            search_name: Name of the semantic search

        Returns:
            dict: Semantic search configuration details
        """
        return self._request('GET', f'/search-index/{search_name}')

    def get_semantic_search_config(self) -> dict:
        """
        Get the global semantic search configuration.

        Returns:
            dict: Global semantic search settings
        """
        return self._request('GET', '/search-index/config')

    # ========== Identity Resolution API (Phase 6) ==========

    def list_identity_rulesets(self) -> dict:
        """
        List all identity resolution rulesets.

        Identity resolution uses rules to match and merge duplicate profiles
        across different data sources.

        Returns:
            dict: List of identity resolution ruleset metadata
        """
        return self._request('GET', '/identity-resolutions')

    def get_identity_ruleset(self, ruleset_name: str) -> dict:
        """
        Get details for a specific identity resolution ruleset.

        Args:
            ruleset_name: Name of the identity resolution ruleset

        Returns:
            dict: Ruleset configuration including match rules and merge policies
        """
        return self._request('GET', f'/identity-resolutions/{ruleset_name}')

    def run_identity_resolution(self, ruleset_name: str) -> dict:
        """
        Run an identity resolution process.

        Args:
            ruleset_name: Name of the identity resolution ruleset to run

        Returns:
            dict: Run result including job ID
        """
        return self._request('POST', f'/identity-resolutions/{ruleset_name}/actions/run')

    # ========== Limits API (Phase 6) ==========

    def get_limits(self) -> dict:
        """
        Get Salesforce org limits and usage.

        Returns current API rate limits, storage quotas, and usage statistics.
        Note: This uses the standard Salesforce limits endpoint, not the /ssot/ path.

        Returns:
            dict: Limits and current usage
        """
        # Limits endpoint is at /services/data/vXX.0/limits (not under /ssot/)
        instance_url = self.oauth_session.get_instance_url()
        token = self.oauth_session.get_token()
        url = f"{instance_url}/services/data/{self.API_VERSION}/limits"

        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }

        response = requests.get(url, headers=headers, timeout=120)

        if response.status_code >= 400:
            logger.error(f"Limits API request failed: {response.status_code} {response.text}")
            response.raise_for_status()

        return response.json()

    # ========== Data Actions API (Phase 6) ==========

    def list_data_actions(self) -> dict:
        """
        List all data actions.

        Data actions are automated processes that run when specific
        conditions are met.

        Returns:
            dict: List of data action metadata
        """
        return self._request('GET', '/data-actions')

    def list_data_action_targets(self) -> dict:
        """
        List all data action targets.

        Returns:
            dict: List of available targets for data actions
        """
        return self._request('GET', '/data-action-targets')

    # ========== Network & Infrastructure API (Phase 6) ==========

    def list_private_network_routes(self) -> dict:
        """
        List all private network routes.

        Private network routes enable secure connectivity between
        Data Cloud and private data sources via VPN or private links.

        Returns:
            dict: List of private network route configurations
        """
        return self._request('GET', '/private-network-routes')

    def get_data_kit_status(self, component_id: str) -> dict:
        """
        Get status of a data kit component.

        Data kits are packaged solutions that can be installed into Data Cloud.

        Args:
            component_id: ID of the data kit component

        Returns:
            dict: Component status and details
        """
        return self._request('GET', f'/data-kit-components/{component_id}/status')

    # ========== Calculated Insights API (Connect API) ==========

    def list_calculated_insights(self) -> dict:
        """
        List all calculated insights.

        Returns:
            dict: List of calculated insight metadata including dimensions and measures
        """
        return self._request('GET', '/calculated-insights')

    def get_calculated_insight(self, api_name: str) -> dict:
        """
        Get details for a specific calculated insight.

        Args:
            api_name: API name of the calculated insight

        Returns:
            dict: Calculated insight definition
        """
        return self._request('GET', f'/calculated-insights/{api_name}')

    def query_calculated_insight(self, ci_name: str, dimensions: list = None,
                                  measures: list = None, filters: list = None,
                                  order_by: list = None, limit: int = None) -> dict:
        """
        Query calculated insight data.

        Args:
            ci_name: Name of the calculated insight
            dimensions: List of dimension fields to include
            measures: List of measure fields to include
            filters: List of filter conditions
            order_by: List of order by clauses
            limit: Maximum number of rows to return

        Returns:
            dict: Query results with aggregated data
        """
        params = {}
        if dimensions:
            params['dimensions'] = ','.join(dimensions)
        if measures:
            params['measures'] = ','.join(measures)
        if filters:
            params['filters'] = ','.join(filters)
        if order_by:
            params['orderBy'] = ','.join(order_by)
        if limit:
            params['limit'] = limit

        query_string = '&'.join(f'{k}={v}' for k, v in params.items())
        path = f'/insight/calculated-insights/{ci_name}'
        if query_string:
            path += f'?{query_string}'
        return self._request('GET', path)

    def get_insight_metadata(self, ci_name: str = None) -> dict:
        """
        Get metadata for calculated insights.

        Args:
            ci_name: Optional specific insight name. If not provided, returns all.

        Returns:
            dict: Insight metadata including dimensions, measures, and filters
        """
        if ci_name:
            return self._request('GET', f'/insight/metadata/{ci_name}')
        return self._request('GET', '/insight/metadata')

    # ========== Data Graphs API (Connect API) ==========

    def get_data_graph_metadata(self) -> dict:
        """
        Get metadata for all data graphs.

        Returns:
            dict: List of data graph metadata including entities and relationships
        """
        return self._request('GET', '/data-graphs/metadata')

    def get_data_graph(self, graph_name: str) -> dict:
        """
        Get details for a specific data graph.

        Args:
            graph_name: Name of the data graph

        Returns:
            dict: Data graph definition
        """
        return self._request('GET', f'/data-graphs/{graph_name}')

    def query_data_graph_by_id(self, entity_name: str, record_id: str) -> dict:
        """
        Query data graph by record ID.

        Args:
            entity_name: Name of the data graph entity
            record_id: ID of the record

        Returns:
            dict: Complete profile with related records
        """
        return self._request('GET', f'/data-graphs/data/{entity_name}/{record_id}')

    def query_data_graph_by_lookup(self, entity_name: str, lookup_keys: dict) -> dict:
        """
        Query data graph by lookup keys.

        Args:
            entity_name: Name of the data graph entity
            lookup_keys: Dictionary of lookup key fields and values

        Returns:
            dict: Complete profile with related records
        """
        import urllib.parse
        params = urllib.parse.urlencode(lookup_keys)
        return self._request('GET', f'/data-graphs/data/{entity_name}?{params}')

    # ========== Profile API (Connect API) ==========

    def get_profile_metadata(self, dmo_name: str = None) -> dict:
        """
        Get profile metadata.

        Args:
            dmo_name: Optional DMO name. If not provided, returns all.

        Returns:
            dict: Profile metadata
        """
        if dmo_name:
            return self._request('GET', f'/profile/metadata/{dmo_name}')
        return self._request('GET', '/profile/metadata')

    def query_profile(self, dmo_name: str, record_id: str = None,
                      child_dmo: str = None) -> dict:
        """
        Query profile data.

        Args:
            dmo_name: Name of the data model object
            record_id: Optional record ID or search key
            child_dmo: Optional child DMO to include

        Returns:
            dict: Profile data
        """
        if record_id and child_dmo:
            return self._request('GET', f'/profile/{dmo_name}/{record_id}/{child_dmo}')
        elif record_id:
            return self._request('GET', f'/profile/{dmo_name}/{record_id}')
        return self._request('GET', f'/profile/{dmo_name}')

    # ========== Universal ID Lookup API (Connect API) ==========

    def lookup_unified_id(self, entity_name: str, data_source_id: str,
                          data_source_object_id: str, source_record_id: str) -> dict:
        """
        Look up unified record ID from source record identifiers.

        Args:
            entity_name: Name of the entity
            data_source_id: ID of the data source
            data_source_object_id: ID of the data source object
            source_record_id: ID of the source record

        Returns:
            dict: Unified ID lookup result
        """
        return self._request(
            'GET',
            f'/universalIdLookup/{entity_name}/{data_source_id}/{data_source_object_id}/{source_record_id}'
        )

    # ========== Metadata API (Connect API) ==========

    def get_metadata(self, entity_name: str = None, entity_type: str = None,
                     entity_category: str = None) -> dict:
        """
        Get metadata for Data Cloud entities.

        Args:
            entity_name: Optional filter by entity name
            entity_type: Optional filter by entity type (dll, dlm)
            entity_category: Optional filter by category

        Returns:
            dict: Entity metadata
        """
        params = {}
        if entity_name:
            params['entityName'] = entity_name
        if entity_type:
            params['entityType'] = entity_type
        if entity_category:
            params['entityCategory'] = entity_category

        if params:
            query_string = '&'.join(f'{k}={v}' for k, v in params.items())
            return self._request('GET', f'/metadata?{query_string}')
        return self._request('GET', '/metadata')

    # ========== Additional Activation Target Endpoints ==========

    def get_activation_target(self, target_id: str) -> dict:
        """Get details for a specific activation target."""
        return self._request('GET', f'/activation-targets/{target_id}')

    def create_activation_target(self, target_definition: dict) -> dict:
        """Create a new activation target."""
        return self._request('POST', '/activation-targets', json_data=target_definition)

    def update_activation_target(self, target_id: str, updates: dict) -> dict:
        """Update an existing activation target."""
        return self._request('PATCH', f'/activation-targets/{target_id}', json_data=updates)

    # ========== Additional Activation Endpoints ==========

    def create_activation(self, activation_definition: dict) -> dict:
        """Create a new activation."""
        return self._request('POST', '/activations', json_data=activation_definition)

    def update_activation(self, activation_id: str, updates: dict) -> dict:
        """Update an existing activation."""
        return self._request('PUT', f'/activations/{activation_id}', json_data=updates)

    def delete_activation(self, activation_id: str) -> dict:
        """Delete an activation."""
        return self._request('DELETE', f'/activations/{activation_id}')

    def list_activation_external_platforms(self) -> dict:
        """List all external platforms available for activations."""
        return self._request('GET', '/activation-external-platforms')

    # ========== Additional Calculated Insight Endpoints ==========

    def create_calculated_insight(self, insight_definition: dict) -> dict:
        """Create a new calculated insight."""
        return self._request('POST', '/calculated-insights', json_data=insight_definition)

    def update_calculated_insight(self, api_name: str, updates: dict) -> dict:
        """Update an existing calculated insight."""
        return self._request('PATCH', f'/calculated-insights/{api_name}', json_data=updates)

    def delete_calculated_insight(self, api_name: str) -> dict:
        """Delete a calculated insight."""
        return self._request('DELETE', f'/calculated-insights/{api_name}')

    def run_calculated_insight(self, api_name: str) -> dict:
        """Run/refresh a calculated insight."""
        return self._request('POST', f'/calculated-insights/{api_name}/actions/run')

    # ========== Additional Connection Endpoints ==========

    def create_connection(self, connection_definition: dict) -> dict:
        """Create a new connection."""
        return self._request('POST', '/connections', json_data=connection_definition)

    def update_connection(self, connection_id: str, updates: dict) -> dict:
        """Update an existing connection."""
        return self._request('PATCH', f'/connections/{connection_id}', json_data=updates)

    def delete_connection(self, connection_id: str) -> dict:
        """Delete a connection."""
        return self._request('DELETE', f'/connections/{connection_id}')

    def get_connection_schema(self, connection_id: str) -> dict:
        """Get schema for a connection."""
        return self._request('GET', f'/connections/{connection_id}/schema')

    def get_connection_endpoints(self, connection_id: str) -> dict:
        """Get endpoints for a connection."""
        return self._request('GET', f'/connections/{connection_id}/endpoints')

    def get_connection_databases(self, connection_id: str) -> dict:
        """Get databases for a connection."""
        return self._request('POST', f'/connections/{connection_id}/databases')

    def get_connection_database_schemas(self, connection_id: str, database: str = None) -> dict:
        """Get database schemas for a connection."""
        data = {'database': database} if database else {}
        return self._request('POST', f'/connections/{connection_id}/database-schemas', json_data=data)

    def get_connector(self, connector_type: str) -> dict:
        """Get details for a specific connector type."""
        return self._request('GET', f'/connectors/{connector_type}')

    # ========== Additional Data Graph Endpoints ==========

    def create_data_graph(self, graph_definition: dict) -> dict:
        """Create a new data graph."""
        return self._request('POST', '/data-graphs', json_data=graph_definition)

    def get_data_graph(self, graph_name: str) -> dict:
        """Get details for a specific data graph."""
        return self._request('GET', f'/data-graphs/{graph_name}')

    def delete_data_graph(self, graph_name: str) -> dict:
        """Delete a data graph."""
        return self._request('DELETE', f'/data-graphs/{graph_name}')

    def refresh_data_graph(self, graph_name: str) -> dict:
        """Refresh a data graph."""
        return self._request('POST', f'/data-graphs/{graph_name}/actions/refresh')

    # ========== Additional Data Transform Endpoints ==========

    def create_data_transform(self, transform_definition: dict) -> dict:
        """Create a new data transform."""
        return self._request('POST', '/data-transforms', json_data=transform_definition)

    def update_data_transform(self, transform_name: str, updates: dict) -> dict:
        """Update an existing data transform."""
        return self._request('PUT', f'/data-transforms/{transform_name}', json_data=updates)

    def delete_data_transform(self, transform_name: str) -> dict:
        """Delete a data transform."""
        return self._request('DELETE', f'/data-transforms/{transform_name}')

    def cancel_data_transform(self, transform_name: str) -> dict:
        """Cancel a running data transform."""
        return self._request('POST', f'/data-transforms/{transform_name}/actions/cancel')

    def retry_data_transform(self, transform_name: str) -> dict:
        """Retry a failed data transform."""
        return self._request('POST', f'/data-transforms/{transform_name}/actions/retry')

    def get_transform_schedule(self, transform_name: str) -> dict:
        """Get schedule for a data transform."""
        return self._request('GET', f'/data-transforms/{transform_name}/schedule')

    def update_transform_schedule(self, transform_name: str, schedule: dict) -> dict:
        """Update schedule for a data transform."""
        return self._request('PUT', f'/data-transforms/{transform_name}/schedule', json_data=schedule)

    def validate_data_transform(self, transform_definition: dict) -> dict:
        """Validate a data transform definition."""
        return self._request('POST', '/data-transforms-validation', json_data=transform_definition)

    # ========== Additional Data Stream Endpoints ==========

    def create_data_stream(self, stream_definition: dict) -> dict:
        """Create a new data stream."""
        return self._request('POST', '/data-streams', json_data=stream_definition)

    def update_data_stream(self, stream_name: str, updates: dict) -> dict:
        """Update an existing data stream."""
        return self._request('PATCH', f'/data-streams/{stream_name}', json_data=updates)

    def delete_data_stream(self, stream_name: str) -> dict:
        """Delete a data stream."""
        return self._request('DELETE', f'/data-streams/{stream_name}')

    # ========== Additional DLO Endpoints ==========

    def update_data_lake_object(self, object_name: str, updates: dict) -> dict:
        """Update an existing data lake object."""
        return self._request('PATCH', f'/data-lake-objects/{object_name}', json_data=updates)

    def delete_data_lake_object(self, object_name: str) -> dict:
        """Delete a data lake object."""
        return self._request('DELETE', f'/data-lake-objects/{object_name}')

    # ========== Additional DMO Endpoints ==========

    def update_data_model_object(self, object_name: str, updates: dict) -> dict:
        """Update an existing data model object."""
        return self._request('PATCH', f'/data-model-objects/{object_name}', json_data=updates)

    def delete_data_model_object(self, object_name: str) -> dict:
        """Delete a data model object."""
        return self._request('DELETE', f'/data-model-objects/{object_name}')

    def create_dmo_mapping(self, mapping_definition: dict, dataspace: str = 'default') -> dict:
        """Create a DMO field mapping."""
        return self._request('POST', f'/data-model-object-mappings?dataspace={dataspace}', json_data=mapping_definition)

    def delete_dmo_mapping(self, mapping_name: str) -> dict:
        """Delete a DMO field mapping."""
        return self._request('DELETE', f'/data-model-object-mappings/{mapping_name}')

    def get_dmo_relationships(self, object_name: str) -> dict:
        """Get relationships for a data model object."""
        return self._request('GET', f'/data-model-objects/{object_name}/relationships')

    def create_dmo_relationship(self, object_name: str, relationship_definition: dict) -> dict:
        """Create a relationship for a data model object."""
        return self._request('POST', f'/data-model-objects/{object_name}/relationships', json_data=relationship_definition)

    def delete_dmo_relationship(self, relationship_name: str) -> dict:
        """Delete a DMO relationship."""
        return self._request('DELETE', f'/data-model-objects/relationships/{relationship_name}')

    # ========== Additional Data Space Endpoints ==========

    def create_data_space(self, space_definition: dict) -> dict:
        """Create a new data space."""
        return self._request('POST', '/data-spaces', json_data=space_definition)

    def update_data_space(self, space_name: str, updates: dict) -> dict:
        """Update an existing data space."""
        return self._request('PATCH', f'/data-spaces/{space_name}', json_data=updates)

    def update_data_space_members(self, space_name: str, members: dict) -> dict:
        """Update members of a data space."""
        return self._request('PUT', f'/data-spaces/{space_name}/members', json_data=members)

    def get_data_space_member(self, space_name: str, member_name: str) -> dict:
        """Get a specific member of a data space."""
        return self._request('GET', f'/data-spaces/{space_name}/members/{member_name}')

    # ========== Additional Document AI Endpoints ==========

    def create_document_ai_config(self, config_definition: dict) -> dict:
        """Create a new Document AI configuration."""
        return self._request('POST', '/document-processing/configurations', json_data=config_definition)

    def get_document_ai_config(self, config_id: str) -> dict:
        """Get a specific Document AI configuration."""
        return self._request('GET', f'/document-processing/configurations/{config_id}')

    def update_document_ai_config(self, config_id: str, updates: dict) -> dict:
        """Update a Document AI configuration."""
        return self._request('PATCH', f'/document-processing/configurations/{config_id}', json_data=updates)

    def delete_document_ai_config(self, config_id: str) -> dict:
        """Delete a Document AI configuration."""
        return self._request('DELETE', f'/document-processing/configurations/{config_id}')

    def run_document_ai(self, config_id: str) -> dict:
        """Run Document AI processing for a configuration."""
        return self._request('POST', f'/document-processing/configurations/{config_id}/actions/run')

    def generate_document_schema(self, request_data: dict) -> dict:
        """Generate schema from document samples."""
        return self._request('POST', '/document-processing/actions/generate-schema', json_data=request_data)

    def get_document_ai_global_config(self) -> dict:
        """Get Document AI global configuration."""
        return self._request('GET', '/document-processing/global-config')

    # ========== Additional Search Index Endpoints ==========

    def create_semantic_search(self, search_definition: dict) -> dict:
        """Create a new semantic search index."""
        return self._request('POST', '/search-index', json_data=search_definition)

    def update_semantic_search(self, search_id: str, updates: dict) -> dict:
        """Update a semantic search index."""
        return self._request('PATCH', f'/search-index/{search_id}', json_data=updates)

    def delete_semantic_search(self, search_id: str) -> dict:
        """Delete a semantic search index."""
        return self._request('DELETE', f'/search-index/{search_id}')

    # ========== Additional Identity Resolution Endpoints ==========

    def create_identity_ruleset(self, ruleset_definition: dict) -> dict:
        """Create a new identity resolution ruleset."""
        return self._request('POST', '/identity-resolutions', json_data=ruleset_definition)

    def update_identity_ruleset(self, ruleset_name: str, updates: dict) -> dict:
        """Update an identity resolution ruleset."""
        return self._request('PATCH', f'/identity-resolutions/{ruleset_name}', json_data=updates)

    def delete_identity_ruleset(self, ruleset_name: str) -> dict:
        """Delete an identity resolution ruleset."""
        return self._request('DELETE', f'/identity-resolutions/{ruleset_name}')

    # ========== Additional Private Network Route Endpoints ==========

    def get_private_network_route(self, route_id: str) -> dict:
        """Get a specific private network route."""
        return self._request('GET', f'/private-network-routes/{route_id}')

    def create_private_network_route(self, route_definition: dict) -> dict:
        """Create a new private network route."""
        return self._request('POST', '/private-network-routes', json_data=route_definition)

    def delete_private_network_route(self, route_id: str) -> dict:
        """Delete a private network route."""
        return self._request('DELETE', f'/private-network-routes/{route_id}')

    # ========== Additional Data Action Endpoints ==========

    def create_data_action(self, action_definition: dict) -> dict:
        """Create a new data action."""
        return self._request('POST', '/data-actions', json_data=action_definition)

    def create_data_action_target(self, target_definition: dict) -> dict:
        """Create a new data action target."""
        return self._request('POST', '/data-action-targets', json_data=target_definition)

    def get_data_action_target(self, api_name: str) -> dict:
        """Get a specific data action target."""
        return self._request('GET', f'/data-action-targets/{api_name}')

    def delete_data_action_target(self, api_name: str) -> dict:
        """Delete a data action target."""
        return self._request('DELETE', f'/data-action-targets/{api_name}')

    def get_data_action_target_signing_key(self, api_name: str) -> dict:
        """Get or generate signing key for a data action target."""
        return self._request('POST', f'/data-action-targets/{api_name}/signing-key')

    # ========== Profile Query Endpoints ==========

    def get_profile_metadata(self, dmo_name: str = None) -> dict:
        """Get profile metadata, optionally filtered by DMO."""
        if dmo_name:
            return self._request('GET', f'/profile/metadata/{dmo_name}')
        return self._request('GET', '/profile/metadata')

    def query_profile(self, dmo_name: str, limit: int = None, offset: int = None) -> dict:
        """Query profile records from a DMO."""
        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        return self._request('GET', f'/profile/{dmo_name}', params=params if params else None)

    def get_profile_record(self, dmo_name: str, record_id: str) -> dict:
        """Get a specific profile record by ID."""
        return self._request('GET', f'/profile/{dmo_name}/{record_id}')

    def get_profile_record_with_children(self, dmo_name: str, record_id: str, child_dmo_name: str) -> dict:
        """Get a profile record with its child records."""
        return self._request('GET', f'/profile/{dmo_name}/{record_id}/{child_dmo_name}')

    def get_profile_record_with_insights(self, dmo_name: str, record_id: str, ci_name: str) -> dict:
        """Get a profile record with its calculated insights."""
        return self._request('GET', f'/profile/{dmo_name}/{record_id}/calculated-insights/{ci_name}')

    # ========== Data Kit Endpoints ==========

    def undeploy_data_kit(self, data_kit_name: str) -> dict:
        """Undeploy a data kit."""
        return self._request('POST', f'/data-kits/{data_kit_name}/undeploy')

    def get_data_kit_component_dependencies(self, data_kit_name: str, component_name: str) -> dict:
        """Get dependencies for a data kit component."""
        return self._request('GET', f'/data-kits/{data_kit_name}/components/{component_name}/dependencies')

    def get_data_kit_deployment_status(self, data_kit_name: str, component_name: str) -> dict:
        """Get deployment status for a data kit component."""
        return self._request('GET', f'/data-kits/{data_kit_name}/components/{component_name}/deployment-status')

    # ========== Machine Learning Endpoints ==========

    def delete_ml_model(self, model_name: str) -> dict:
        """Delete an ML model."""
        return self._request('DELETE', f'/machine-learning/configured-models/{model_name}')

    def update_ml_model(self, model_name: str, updates: dict) -> dict:
        """Update an ML model configuration."""
        return self._request('PATCH', f'/machine-learning/configured-models/{model_name}', json_data=updates)

    def get_model_artifact(self, artifact_name: str) -> dict:
        """Get a specific model artifact."""
        return self._request('GET', f'/machine-learning/model-artifacts/{artifact_name}')

    def delete_model_artifact(self, artifact_name: str) -> dict:
        """Delete a model artifact."""
        return self._request('DELETE', f'/machine-learning/model-artifacts/{artifact_name}')

    def update_model_artifact(self, artifact_name: str, updates: dict) -> dict:
        """Update a model artifact."""
        return self._request('PATCH', f'/machine-learning/model-artifacts/{artifact_name}', json_data=updates)
