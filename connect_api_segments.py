"""
Connect API Client for Salesforce Data Cloud Segments and Activations

This module provides methods for working with segments, activations, and audience
management through the Connect API endpoints.

Connect APIs use standard OAuth tokens (no second token exchange like Direct APIs).
"""

import json
import logging
from typing import Any, Optional

import requests

from oauth import OAuthSession

logger = logging.getLogger(__name__)

# API version for Connect APIs
API_VERSION = "63.0"


class ConnectAPIClient:
    """Client for Data Cloud Connect APIs (segments, activations, etc.)."""

    def __init__(self, oauth_session: OAuthSession):
        self.oauth_session = oauth_session

    def _get_base_url(self) -> str:
        """Get the base URL for Connect API requests."""
        instance_url = self.oauth_session.get_instance_url()
        return f"{instance_url}/services/data/v{API_VERSION}/ssot"

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None
    ) -> dict:
        """
        Make an authenticated request to the Connect API.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint (e.g., '/segments')
            params: Query parameters
            json_data: JSON body for POST/PATCH requests

        Returns:
            dict: JSON response
        """
        token = self.oauth_session.get_token()
        base_url = self._get_base_url()
        url = f"{base_url}{endpoint}"

        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }

        if json_data:
            headers['Content-Type'] = 'application/json'

        logger.debug(f"Connect API request: {method} {url}")

        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
            headers=headers,
            timeout=120
        )

        if response.status_code >= 400:
            logger.error(f"Connect API request failed: {response.status_code} {response.text}")
            response.raise_for_status()

        # Handle empty responses (204 No Content)
        if response.status_code == 204 or not response.text:
            return {"success": True}

        return response.json()

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
        return self._request('POST', f'/segments/{segment_name}/actions/count')

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
        return self._request('POST', f'/data-transforms/{transform_name}/actions/run')

    # ========== Connections API (Phase 3) ==========

    def list_connections(self) -> dict:
        """
        List all connections.

        Returns:
            dict: List of connection metadata
        """
        return self._request('GET', '/connections')

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
        url = f"{instance_url}/services/data/v{API_VERSION}/limits"

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
