"""
SQL Query Validation for Data Cloud

Provides client-side SQL validation with helpful error messages and suggestions.
Uses sqlparse for syntax validation and metadata for column/table suggestions.
"""

import re
from difflib import get_close_matches
from typing import Optional

import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Where, Parenthesis
from sqlparse.tokens import Keyword, DML


class QueryValidationError:
    """Structured error response for query validation failures."""

    def __init__(
        self,
        error_type: str,
        message: str,
        suggestion: Optional[str] = None,
        position: Optional[dict] = None
    ):
        self.error_type = error_type
        self.message = message
        self.suggestion = suggestion
        self.position = position

    def to_dict(self) -> dict:
        result = {
            "error_type": self.error_type,
            "message": self.message,
            "valid": False
        }
        if self.suggestion:
            result["suggestion"] = self.suggestion
        if self.position:
            result["position"] = self.position
        return result


def _extract_identifiers(parsed) -> list[str]:
    """Extract all identifiers (table/column names) from parsed SQL."""
    identifiers = []

    def _recurse(token):
        if isinstance(token, Identifier):
            # Get the real name without quotes
            name = token.get_real_name()
            if name:
                identifiers.append(name)
        elif isinstance(token, IdentifierList):
            for item in token.get_identifiers():
                _recurse(item)
        elif hasattr(token, 'tokens'):
            for sub_token in token.tokens:
                _recurse(sub_token)

    for statement in parsed:
        _recurse(statement)

    return identifiers


def _find_position(sql: str, identifier: str) -> Optional[dict]:
    """Find the line and column position of an identifier in SQL."""
    # Search for the identifier (may be quoted or unquoted)
    patterns = [
        rf'"{re.escape(identifier)}"',  # Double-quoted
        rf"'{re.escape(identifier)}'",  # Single-quoted (though unusual for identifiers)
        rf'\b{re.escape(identifier)}\b'  # Unquoted
    ]

    for pattern in patterns:
        match = re.search(pattern, sql, re.IGNORECASE)
        if match:
            start = match.start()
            # Calculate line and column
            lines = sql[:start].split('\n')
            line = len(lines)
            column = len(lines[-1]) + 1
            return {"line": line, "column": column}

    return None


def _suggest_similar(name: str, valid_names: list[str], cutoff: float = 0.4) -> Optional[str]:
    """Find a similar name from the valid names list."""
    # Try exact match first (case-insensitive)
    name_lower = name.lower()
    for valid in valid_names:
        if valid.lower() == name_lower:
            return valid

    # Try fuzzy matching
    matches = get_close_matches(name.lower(), [v.lower() for v in valid_names], n=1, cutoff=cutoff)
    if matches:
        # Return the original case version
        for valid in valid_names:
            if valid.lower() == matches[0]:
                return valid

    # Try matching just the last part (after __)
    if '__' in name:
        short_name = name.split('__')[-1]
        for valid in valid_names:
            if valid.lower().endswith(f'__{short_name.lower()}') or valid.lower().endswith(f'__{short_name.lower()}__c'):
                return valid

    return None


def validate_sql_syntax(sql: str) -> dict:
    """
    Validate SQL syntax using sqlparse.

    Returns a dict with:
    - valid: bool
    - error_type, message, suggestion, position if invalid
    """
    if not sql or not sql.strip():
        return QueryValidationError(
            error_type="EMPTY_QUERY",
            message="SQL query is empty"
        ).to_dict()

    # Parse the SQL
    try:
        parsed = sqlparse.parse(sql)
    except Exception as e:
        return QueryValidationError(
            error_type="PARSE_ERROR",
            message=f"Failed to parse SQL: {str(e)}"
        ).to_dict()

    if not parsed or not parsed[0].tokens:
        return QueryValidationError(
            error_type="PARSE_ERROR",
            message="Failed to parse SQL statement"
        ).to_dict()

    # Check for basic statement type
    statement = parsed[0]
    statement_type = statement.get_type()

    if statement_type is None:
        return QueryValidationError(
            error_type="INVALID_STATEMENT",
            message="Could not determine SQL statement type",
            suggestion="Ensure your query starts with SELECT, INSERT, UPDATE, or DELETE"
        ).to_dict()

    # Data Cloud only supports SELECT queries
    if statement_type.upper() not in ('SELECT', 'UNKNOWN'):
        return QueryValidationError(
            error_type="UNSUPPORTED_STATEMENT",
            message=f"Statement type '{statement_type}' is not supported",
            suggestion="Data Cloud Query API only supports SELECT statements"
        ).to_dict()

    # Check for common syntax issues
    sql_upper = sql.upper()

    # Missing FROM clause for non-trivial queries
    if 'SELECT' in sql_upper and 'FROM' not in sql_upper:
        # Allow simple expressions like SELECT 1, SELECT CURRENT_DATE, etc.
        identifiers = _extract_identifiers(parsed)
        if identifiers:
            return QueryValidationError(
                error_type="MISSING_FROM",
                message="SELECT query appears to reference columns but is missing FROM clause",
                suggestion="Add a FROM clause to specify the table"
            ).to_dict()

    return {"valid": True}


def validate_query_with_metadata(
    sql: str,
    available_tables: list[str],
    table_columns: dict[str, list[str]]
) -> dict:
    """
    Validate SQL query with metadata for better error messages.

    Args:
        sql: The SQL query to validate
        available_tables: List of available table names
        table_columns: Dict mapping table names to their column lists

    Returns:
        dict with validation result and any errors/suggestions
    """
    # First do basic syntax validation
    syntax_result = validate_sql_syntax(sql)
    if not syntax_result.get("valid"):
        return syntax_result

    # Parse the SQL to extract identifiers
    parsed = sqlparse.parse(sql)

    # Extract table references (simplified - looks for identifiers after FROM/JOIN)
    sql_upper = sql.upper()

    # Find table references
    from_match = re.search(r'\bFROM\s+["\']?(\w+)["\']?', sql, re.IGNORECASE)
    if from_match:
        table_name = from_match.group(1)

        # Check if table exists
        if table_name not in available_tables:
            suggestion = _suggest_similar(table_name, available_tables)
            error = QueryValidationError(
                error_type="INVALID_TABLE",
                message=f"Table '{table_name}' not found",
                position=_find_position(sql, table_name)
            )
            if suggestion:
                error.suggestion = f"Did you mean '{suggestion}'?"
            return error.to_dict()

        # If we have column info for this table, validate columns
        if table_name in table_columns:
            columns = table_columns[table_name]
            identifiers = _extract_identifiers(parsed)

            for ident in identifiers:
                # Skip if it's the table name or an alias
                if ident == table_name:
                    continue
                # Skip common SQL functions/keywords
                if ident.upper() in ('COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'DISTINCT',
                                      'AS', 'NULL', 'TRUE', 'FALSE', 'RANDOM'):
                    continue

                if ident not in columns:
                    suggestion = _suggest_similar(ident, columns)
                    error = QueryValidationError(
                        error_type="INVALID_COLUMN",
                        message=f"Column '{ident}' not found in table '{table_name}'",
                        position=_find_position(sql, ident)
                    )
                    if suggestion:
                        error.suggestion = f"Did you mean '{suggestion}'?"
                    return error.to_dict()

    return {"valid": True}


def format_query(sql: str, reindent: bool = True) -> str:
    """Format SQL query for better readability."""
    return sqlparse.format(
        sql,
        reindent=reindent,
        keyword_case='upper',
        identifier_case='lower'
    )
