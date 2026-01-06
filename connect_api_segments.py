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
        return self._request('GET', '/ml-models')

    def get_ml_model(self, model_name: str) -> dict:
        """
        Get details for a specific ML model.

        Args:
            model_name: Name of the ML model

        Returns:
            dict: ML model details including configuration and metrics
        """
        return self._request('GET', f'/ml-models/{model_name}')

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
        if input_data:
            return self._request('POST', f'/ml-models/{model_name}/predictions', json_data=input_data)
        return self._request('GET', f'/ml-models/{model_name}/predictions')

    def list_model_artifacts(self) -> dict:
        """
        List all ML model artifacts.

        Model artifacts contain trained model files and associated metadata.

        Returns:
            dict: List of model artifact metadata
        """
        return self._request('GET', '/ml-model-artifacts')

    # ========== Document AI API (Phase 5) ==========

    def list_document_ai_configs(self) -> dict:
        """
        List all Document AI configurations.

        Document AI extracts structured data from documents like invoices,
        contracts, and forms.

        Returns:
            dict: List of Document AI configuration metadata
        """
        return self._request('GET', '/document-ai-configurations')

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
            f'/document-ai-configurations/{config_name}/actions/extract-data',
            json_data=document_data
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
        return self._request('GET', '/semantic-searches')

    def get_semantic_search(self, search_name: str) -> dict:
        """
        Get details for a specific semantic search configuration.

        Args:
            search_name: Name of the semantic search

        Returns:
            dict: Semantic search configuration details
        """
        return self._request('GET', f'/semantic-searches/{search_name}')

    def get_semantic_search_config(self) -> dict:
        """
        Get the global semantic search configuration.

        Returns:
            dict: Global semantic search settings
        """
        return self._request('GET', '/semantic-search-config')
