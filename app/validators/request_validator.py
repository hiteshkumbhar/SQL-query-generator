"""Request validation for SQL generation endpoints."""

from typing import Any, Dict, Optional, Tuple
from config import Config


class ValidationError(Exception):
    """Exception raised when request payload fails validation."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def validate_generate_sql_request(data: Any, config: Optional[Config] = None) -> Tuple[str, str, str]:
    """Validate incoming JSON request for SQL generation.

    Args:
        data: The parsed JSON body.
        config: Application configuration instance or class.

    Returns:
        Tuple of (clean_prompt, clean_schema, clean_dialect).

    Raises:
        ValidationError: If input is invalid.
    """
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a valid JSON object.")

    if "prompt" not in data:
        raise ValidationError("Missing required field 'prompt'.")

    prompt = data["prompt"]
    if not isinstance(prompt, str):
        raise ValidationError("Field 'prompt' must be a string.")

    cleaned_prompt = prompt.strip()
    if not cleaned_prompt:
        raise ValidationError("Field 'prompt' cannot be empty or whitespace only.")

    max_prompt_len = getattr(config, "MAX_PROMPT_LENGTH", 1000) if config else 1000
    if len(cleaned_prompt) > max_prompt_len:
        raise ValidationError(
            f"Prompt exceeds maximum allowed length of {max_prompt_len} characters (received {len(cleaned_prompt)})."
        )

    # Validate Schema
    default_schema = getattr(config, "DEFAULT_SCHEMA", "") if config else ""
    schema = data.get("schema", default_schema)
    if not isinstance(schema, str):
        raise ValidationError("Field 'schema' must be a string if provided.")

    cleaned_schema = schema.strip()
    if not cleaned_schema:
        cleaned_schema = default_schema

    max_schema_len = getattr(config, "MAX_SCHEMA_LENGTH", 10000) if config else 10000
    if len(cleaned_schema) > max_schema_len:
        raise ValidationError(
            f"Schema exceeds maximum allowed length of {max_schema_len} characters."
        )

    # Validate Dialect
    allowed_dialects = (
        getattr(config, "ALLOWED_DIALECTS", {"postgresql", "mysql", "sqlite", "bigquery", "snowflake", "sqlserver"})
        if config
        else {"postgresql", "mysql", "sqlite", "bigquery", "snowflake", "sqlserver"}
    )
    default_dialect = getattr(config, "DEFAULT_DIALECT", "postgresql") if config else "postgresql"
    dialect = data.get("dialect", default_dialect)
    if not isinstance(dialect, str):
        raise ValidationError("Field 'dialect' must be a string if provided.")

    cleaned_dialect = dialect.strip().lower()
    if cleaned_dialect not in allowed_dialects:
        allowed_list = ", ".join(sorted(allowed_dialects))
        raise ValidationError(
            f"Unsupported SQL dialect '{cleaned_dialect}'. Allowed dialects: {allowed_list}."
        )

    return cleaned_prompt, cleaned_schema, cleaned_dialect
