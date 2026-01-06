"""
Base client class with common HTTP request handling for Data Cloud Connect API.
"""
import json
import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class DataCloudAPIError(Exception):
    """Custom exception for Data Cloud API errors with structured information."""

    def __init__(self, status_code: int, reason: str, message: str):
        self.status_code = status_code
        self.reason = reason
        self.message = message
        super().__init__(f"[{status_code}] {reason}: {message}")


class BaseClient:
    """
    Base client for Salesforce Data Cloud Connect API.

    Provides common HTTP request handling for all domain-specific clients.
    Uses duck-typing for the session object - expects any object with
    get_token() and get_instance_url() methods.
    """

    # API version for Connect API endpoints
    API_VERSION = "v63.0"

    def __init__(self, oauth_session):
        """
        Initialize the client with an OAuth session.

        Args:
            oauth_session: Any object with get_token() and get_instance_url() methods.
                          Works with both OAuthSession (original) and SFCLISession (this fork).
        """
        self.oauth_session = oauth_session

    def _get_base_url(self) -> str:
        """Get the base URL for Connect API endpoints."""
        instance_url = self.oauth_session.get_instance_url()
        return f"{instance_url}/services/data/{self.API_VERSION}/ssot"

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        json_body: Optional[dict] = None,
        timeout: int = 120,
    ) -> dict:
        """
        Make an HTTP request to the Connect API.

        Args:
            method: HTTP method (GET, POST, PATCH, PUT, DELETE)
            endpoint: API endpoint path (without base URL)
            params: Query parameters
            json_body: JSON body for POST/PATCH/PUT requests
            timeout: Request timeout in seconds

        Returns:
            dict: Parsed JSON response or error dict

        Raises:
            DataCloudAPIError: On API errors (4xx, 5xx responses)
        """
        url = f"{self._get_base_url()}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.oauth_session.get_token()}",
            "Content-Type": "application/json",
        }

        logger.debug(f"API Request: {method} {url}")
        if params:
            logger.debug(f"Params: {params}")
        if json_body:
            logger.debug(f"Body: {json.dumps(json_body)[:500]}...")

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_body,
                timeout=timeout,
            )

            logger.debug(f"Response: {response.status_code} ({response.elapsed.total_seconds():.2f}s)")

            # Handle errors
            if response.status_code >= 400:
                error_message = self._parse_error_response(response)
                raise DataCloudAPIError(
                    status_code=response.status_code,
                    reason=response.reason,
                    message=error_message,
                )

            # Handle empty responses (DELETE, etc.)
            if response.status_code == 204 or not response.text:
                return {"success": True}

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise DataCloudAPIError(
                status_code=0,
                reason="RequestError",
                message=str(e),
            )

    def _parse_error_response(self, response: requests.Response) -> str:
        """Parse error message from API response."""
        try:
            payload = response.json()
            # Connect API error format: list with first element containing JSON string in "message"
            if isinstance(payload, list) and len(payload) > 0:
                structured_message = payload[0]
                try:
                    errors_details_json = structured_message.get("message", "")
                    details = json.loads(errors_details_json) if errors_details_json else None
                    if details:
                        return errors_details_json
                except json.JSONDecodeError:
                    return structured_message.get("message", response.text)
            elif isinstance(payload, dict):
                # Single error object
                return payload.get("message", payload.get("error", response.text))
        except json.JSONDecodeError:
            pass
        return response.text
