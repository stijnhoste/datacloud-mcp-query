import json
import logging
from typing import Dict, List, Optional, Union

import requests

# Note: This module uses duck-typing for the session object.
# It expects any object with get_token() and get_instance_url() methods.
# Works with both OAuthSession (original) and SFCLISession (this fork).

# Get logger for this module
logger = logging.getLogger(__name__)


class DataCloudQueryError(Exception):
    """Custom exception for Data Cloud query errors with structured information."""

    def __init__(self, status_code: int, reason: str, message: str):
        self.status_code = status_code
        self.reason = reason
        self.message = message
        super().__init__(f"[{status_code}] {reason}: {message}")


def _handle_error_response(response: requests.Response):
    if response.status_code >= 300:
        # Parse error message from response
        message = response.text
        try:
            payload = json.loads(response.text)
            # Connect API error format: list with first element containing JSON string in "message"
            if isinstance(payload, list) and len(payload) > 0:
                structured_message = payload[0]
                try:
                    errors_details_json = structured_message.get("message", "")
                    details = json.loads(
                        errors_details_json) if errors_details_json else None
                    if details:
                        message = errors_details_json
                except json.JSONDecodeError:
                    # Keep original message if JSON parsing fails
                    pass
        except json.JSONDecodeError:
            # Keep original message if response isn't JSON
            pass

        # Raise custom exception with structured error information
        raise DataCloudQueryError(
            status_code=response.status_code,
            reason=response.reason,
            message=message,
        )


def run_query(
    oauth_session,  # Any object with get_token() and get_instance_url() methods
    sql: str,
    dataspace: str = "default",
    workload_name: str | None = "data-360-mcp-query-oss",
    pagination_batch_size: int = 100000,
) -> Dict[str, Union[List, str]]:
    """
    Execute a SQL query using the Data Cloud Query Connect API, handling long-running queries
    and paginated result retrieval.

    Returns a dictionary containing:
    - 'data': the complete list of rows (aggregated across all pages) or "(empty)" if no rows
    - 'metadata': the schema/metadata of the result columns
    """
    base_url = oauth_session.get_instance_url()
    token = oauth_session.get_token()

    headers = {"Authorization": f"Bearer {token}"}
    url_base = base_url + "/services/data/v63.0/ssot/query-sql"
    common_params: dict[str, str] = {"dataspace": dataspace}
    if workload_name:
        common_params["workloadName"] = workload_name

    # Step 1: submit the query
    submit_body = {"sql": sql}
    logger.info(
        f"Submitting SQL query to {url_base}, with params: {common_params}")

    submit_response = requests.post(
        url_base, json=submit_body, params=common_params, headers=headers, timeout=120)

    logger.info(
        f"Query submission response: status={submit_response.status_code}, elapsed={submit_response.elapsed.total_seconds():.2f}s")
    _handle_error_response(submit_response)

    submit_payload = submit_response.json()
    status_obj = submit_payload.get("status", {})
    query_id = status_obj.get("queryId") or submit_payload.get("queryId")
    if not query_id:
        raise DataCloudQueryError(
            status_code=500,
            reason="MissingQueryId",
            message="Query ID not returned by the API."
        )

    # Collect initial rows and metadata if present
    rows: list = submit_payload.get("data", []) or []
    metadata = submit_payload.get("metadata", [])
    completion = status_obj.get("completionStatus")
    row_count_val = status_obj.get("rowCount")
    total_row_count = int(row_count_val) if row_count_val is not None else 0

    # Step 2: poll for completion when needed (long-polling via waitTimeMs)
    poll_count = 0
    while completion not in ["Finished", "ResultsProduced"]:
        poll_count += 1
        poll_url = f"{url_base}/{query_id}"
        logger.debug(
            f"Polling query status (attempt {poll_count}): {poll_url}")

        poll_params = dict(common_params)
        # Signal that we want to do long-polling to get best latency for query end notification and minimize RPC calls
        poll_params.update({
            "waitTimeMs": 10000,
        })
        poll_response = requests.get(
            poll_url, params=poll_params, headers=headers, timeout=120)

        logger.debug(
            f"Poll response: status={poll_response.status_code}, elapsed={poll_response.elapsed.total_seconds():.2f}s")
        _handle_error_response(poll_response)
        poll_payload = poll_response.json()
        completion = poll_payload.get("completionStatus")
        poll_row_count = poll_payload.get("rowCount")
        total_row_count = int(poll_row_count) if poll_row_count is not None else total_row_count

    # Step 3: retrieve remaining rows via pagination
    while len(rows) < total_row_count:
        rows_params = dict(common_params)
        rows_params.update({
            "rowLimit": pagination_batch_size,
            "offset": len(rows),
            "omitSchema": "true",
        })

        rows_url = f"{url_base}/{query_id}/rows"
        logger.debug(
            f"Fetching rows: offset={rows_params.get('offset')}, limit={rows_params.get('rowLimit')}")

        rows_response = requests.get(
            rows_url, params=rows_params, headers=headers, timeout=120)

        logger.debug(
            f"Rows fetch response: status={rows_response.status_code}, elapsed={rows_response.elapsed.total_seconds():.2f}s")
        _handle_error_response(rows_response)

        chunk = rows_response.json()
        chunk_rows = chunk.get("data", []) or []
        returned_rows = int(chunk.get("returnedRows", len(chunk_rows)))

        if returned_rows == 0:
            raise DataCloudQueryError(
                status_code=500,
                reason="MissingRows",
                message="Expected rows to be returned, but received 0."
            )

        rows.extend(chunk_rows)
        logger.debug(
            f"Retrieved {returned_rows} rows, total so far: {len(rows)}")

    logger.info(f"Query completed: retrieved {len(rows)} total rows")
    return {
        "data": rows,
        "metadata": metadata
    }


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Set debug level for this module during testing
    logger.setLevel(logging.DEBUG)

    # Use SF CLI authentication
    from sf_cli_auth import SFCLIAuth
    import os

    class SimpleSFCLISession:
        """Simple session adapter for standalone testing."""
        def __init__(self, alias: str):
            self.sf_auth = SFCLIAuth()
            self.sf_auth.set_target_org(alias)

        def get_token(self) -> str:
            token, _ = self.sf_auth.get_access_token()
            return token

        def get_instance_url(self) -> str:
            _, instance_url = self.sf_auth.get_access_token()
            return instance_url

    # Get org from environment or use default
    org_alias = os.getenv('DC_DEFAULT_ORG', 'mca-next-sdo')
    session = SimpleSFCLISession(org_alias)

    result = run_query(session, "SELECT 1 as test_col")
    print(f"Query result: {len(result['data'])} rows returned")
    print(result)
