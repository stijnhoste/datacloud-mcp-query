"""
Direct API Client for Salesforce Data Cloud (Data 360)

This module implements the 2-step authentication flow required for Data 360 Direct APIs:
1. OAuth to Salesforce Platform (handled by oauth.py)
2. Token exchange to get Data Cloud tenant token

Direct APIs (/api/v1/*) are faster than Connect APIs but require this additional auth step.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Optional
from urllib.parse import urlencode

import requests

from oauth import OAuthSession

logger = logging.getLogger(__name__)


class DirectAPISession:
    """Client for Data Cloud Direct APIs with 2-step authentication."""

    # Token cache file for tenant token
    TENANT_TOKEN_CACHE_KEY = 'tenant_token'

    def __init__(self, oauth_session: OAuthSession):
        self.oauth_session = oauth_session
        self.tenant_token: str | None = None
        self.tenant_url: str | None = None
        self.tenant_token_exp: datetime | None = None

    def _get_tenant_token(self) -> tuple[str, str]:
        """
        Exchange platform access token for Data Cloud tenant token.

        Returns:
            tuple: (tenant_token, tenant_url)
        """
        # Ensure we have a valid platform token
        platform_token = self.oauth_session.ensure_access()
        instance_url = self.oauth_session.get_instance_url()

        # Exchange for tenant token
        token_url = f"{instance_url}/services/a360/token"

        payload = {
            'grant_type': 'urn:salesforce:grant-type:external:cdp',
            'subject_token': platform_token,
            'subject_token_type': 'urn:ietf:params:oauth:token-type:access_token'
        }

        logger.info("Exchanging platform token for Data Cloud tenant token")

        response = requests.post(
            token_url,
            data=payload,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            },
            timeout=120
        )

        if response.status_code >= 400:
            logger.error(f"Tenant token exchange failed: {response.text}")
            response.raise_for_status()

        result = response.json()
        tenant_token = result['access_token']
        tenant_url = result['instance_url']

        logger.info(f"Successfully obtained tenant token for {tenant_url}")

        return tenant_token, tenant_url

    def ensure_tenant_access(self) -> tuple[str, str]:
        """
        Ensure we have a valid tenant token, refreshing if needed.

        Returns:
            tuple: (tenant_token, tenant_url)
        """
        # Check if current token is expired
        if self.tenant_token_exp is not None and datetime.now() > self.tenant_token_exp:
            logger.info("Tenant token expired, refreshing")
            self.tenant_token = None
            self.tenant_url = None

        if self.tenant_token is None:
            self.tenant_token, self.tenant_url = self._get_tenant_token()
            # Tenant tokens typically have same lifetime as platform tokens
            self.tenant_token_exp = datetime.now() + timedelta(minutes=110)

        return self.tenant_token, self.tenant_url

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
        data: Optional[dict] = None
    ) -> dict:
        """
        Make an authenticated request to the Direct API.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint (e.g., '/api/v1/metadata')
            params: Query parameters
            json_data: JSON body for POST requests
            data: Form data for POST requests

        Returns:
            dict: JSON response
        """
        token, base_url = self.ensure_tenant_access()

        url = f"{base_url}{endpoint}"

        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }

        if json_data:
            headers['Content-Type'] = 'application/json'

        logger.debug(f"Direct API request: {method} {url}")

        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
            data=data,
            headers=headers,
            timeout=120
        )

        if response.status_code >= 400:
            logger.error(f"Direct API request failed: {response.status_code} {response.text}")
            response.raise_for_status()

        return response.json()

    # ========== Metadata API ==========

    def get_metadata(
        self,
        entity_name: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_category: Optional[str] = None
    ) -> dict:
        """
        Get metadata for Data Cloud entities.

        Args:
            entity_name: Filter by entity name
            entity_type: Filter by type (e.g., 'dll', 'dlm')
            entity_category: Filter by category (e.g., 'Profile', 'Engagement')

        Returns:
            dict: Metadata response containing entity definitions
        """
        params = {}
        if entity_name:
            params['entityName'] = entity_name
        if entity_type:
            params['entityType'] = entity_type
        if entity_category:
            params['entityCategory'] = entity_category

        return self._request('GET', '/api/v1/metadata', params=params or None)

    # ========== Query API ==========

    def query(self, sql: str, limit: Optional[int] = None) -> dict:
        """
        Execute a SQL query against Data Cloud (sync, v1).

        Args:
            sql: PostgreSQL-dialect SQL query
            limit: Optional row limit

        Returns:
            dict: Query results with data and metadata
        """
        endpoint = '/api/v1/query'
        if limit:
            endpoint = f'{endpoint}?limit={limit}'

        return self._request('POST', endpoint, json_data={'sql': sql})

    def query_async(self, sql: str) -> dict:
        """
        Execute a SQL query asynchronously (v2).

        Returns initial batch and nextBatchId for pagination.

        Args:
            sql: PostgreSQL-dialect SQL query

        Returns:
            dict: Query results with data, metadata, and optional nextBatchId
        """
        return self._request('POST', '/api/v2/query', json_data={'sql': sql})

    def query_next_batch(self, next_batch_id: str) -> dict:
        """
        Get the next batch of results from an async query.

        Args:
            next_batch_id: The nextBatchId from previous response

        Returns:
            dict: Next batch of query results
        """
        return self._request('GET', f'/api/v2/query/{next_batch_id}')

    # ========== Calculated Insights API ==========

    def get_calculated_insights_metadata(self) -> dict:
        """
        Get metadata for all calculated insights.

        Returns:
            dict: List of calculated insight definitions
        """
        return self._request('GET', '/api/v1/insight/metadata')

    def query_calculated_insight(
        self,
        insight_name: str,
        dimensions: Optional[list[str]] = None,
        measures: Optional[list[str]] = None,
        filters: Optional[list[dict]] = None,
        batch_size: Optional[int] = None
    ) -> dict:
        """
        Query a calculated insight.

        Args:
            insight_name: Name of the calculated insight
            dimensions: List of dimension fields to include
            measures: List of measure fields to include
            filters: List of filter conditions
            batch_size: Number of records per batch

        Returns:
            dict: Calculated insight query results
        """
        params = {}
        if dimensions:
            params['dimensions'] = ','.join(dimensions)
        if measures:
            params['measures'] = ','.join(measures)
        if filters:
            # Filters are passed as JSON-encoded string
            import json
            params['filters'] = json.dumps(filters)
        if batch_size:
            params['batchSize'] = str(batch_size)

        return self._request(
            'GET',
            f'/api/v1/insight/calculated-insights/{insight_name}',
            params=params or None
        )

    # ========== Data Graph API ==========

    def get_data_graph_metadata(self) -> dict:
        """
        Get metadata for all data graphs.

        Returns:
            dict: List of data graph definitions
        """
        return self._request('GET', '/api/v1/dataGraph/metadata')

    def query_data_graph_by_id(self, graph_name: str, record_id: str) -> dict:
        """
        Query a data graph by record ID.

        Args:
            graph_name: Name of the data graph
            record_id: ID of the record to retrieve

        Returns:
            dict: Data graph record with related entities
        """
        return self._request('GET', f'/api/v1/dataGraph/{graph_name}/{record_id}')

    def query_data_graph_by_lookup(
        self,
        graph_name: str,
        lookup_keys: list[dict]
    ) -> dict:
        """
        Query a data graph by lookup keys.

        Args:
            graph_name: Name of the data graph
            lookup_keys: List of lookup key objects

        Returns:
            dict: Data graph records matching the lookup keys
        """
        import json
        params = {'lookupKeys': json.dumps(lookup_keys)}
        return self._request('GET', f'/api/v1/dataGraph/{graph_name}', params=params)

    # ========== Unified ID Lookup API ==========

    def lookup_unified_id(
        self,
        entity_name: str,
        data_source_id: str,
        data_source_object_id: str,
        source_record_id: str
    ) -> dict:
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
        endpoint = (
            f'/api/v1/universalIdLookup/{entity_name}/'
            f'{data_source_id}/{data_source_object_id}/{source_record_id}'
        )
        return self._request('GET', endpoint)

    # ========== Ingestion API ==========

    def ingest_records(
        self,
        source_name: str,
        object_name: str,
        records: list[dict]
    ) -> dict:
        """
        Ingest records into Data Cloud.

        Args:
            source_name: Name of the data source
            object_name: Name of the object to ingest into
            records: List of record dictionaries

        Returns:
            dict: Ingestion result
        """
        return self._request(
            'POST',
            f'/api/v1/ingest/sources/{source_name}/{object_name}',
            json_data={'data': records}
        )

    def delete_records(
        self,
        source_name: str,
        object_name: str,
        record_ids: list[str]
    ) -> dict:
        """
        Delete records from Data Cloud.

        Args:
            source_name: Name of the data source
            object_name: Name of the object
            record_ids: List of record IDs to delete

        Returns:
            dict: Deletion result
        """
        return self._request(
            'DELETE',
            f'/api/v1/ingest/sources/{source_name}/{object_name}',
            json_data={'ids': record_ids}
        )

    # ========== Profile API ==========

    def get_profile(self, profile_id: str) -> dict:
        """
        Get a unified profile by ID.

        Args:
            profile_id: ID of the profile

        Returns:
            dict: Profile data
        """
        return self._request('GET', f'/api/v1/profile/{profile_id}')

    def search_profiles(self, search_params: dict) -> dict:
        """
        Search for profiles.

        Args:
            search_params: Search parameters

        Returns:
            dict: Search results
        """
        return self._request('POST', '/api/v1/profile/search', json_data=search_params)
