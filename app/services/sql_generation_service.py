"""SQL generation service orchestrator."""

import json
from typing import Any, Dict, List, Optional
from app.prompts.text_to_sql_prompt import SYSTEM_INSTRUCTION, build_user_prompt
from app.services.gemini_service import GeminiService, GeminiServiceError



def clean_markdown_fences(text: str) -> str:
    """Safely strip markdown code fences from AI response."""
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```sql"):
        cleaned = cleaned[6:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    return cleaned.strip()


def validate_sql(sql: str) -> None:
    """Validate that the SQL query is a valid non-empty string."""
    if not sql or not sql.strip():
        raise ValueError("Generated SQL cannot be empty.")


class SQLGenerationService:
    """Service orchestrating prompt construction, Gemini call, and output parsing."""

    def __init__(self, gemini_service: GeminiService) -> None:
        self.gemini_service = gemini_service

    def generate_sql(self, prompt: str, schema: str, dialect: str) -> Dict[str, Any]:
        """Generate SQL query for the given user request, schema, and dialect.

        Args:
            prompt: User natural language request.
            schema: Database schema representation.
            dialect: SQL dialect (e.g. postgresql).

        Returns:
            Structured dictionary with keys: success, sql, explanation, dialect, tables_used, error.
        """
        user_prompt_content = build_user_prompt(prompt, schema, dialect)

        raw_response = self.gemini_service.generate_content(
            user_prompt=user_prompt_content,
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.1,
        )

        return self._process_model_output(raw_response, dialect)

    def _process_model_output(self, raw_output: str, fallback_dialect: str) -> Dict[str, Any]:
        """Parse, clean, and validate Gemini's output into the standard response format."""
        cleaned_text = clean_markdown_fences(raw_output)

        parsed_json: Optional[Dict[str, Any]] = None
        try:
            parsed_json = json.loads(cleaned_text)
        except json.JSONDecodeError:
            # If the model returned pure SQL instead of JSON
            if cleaned_text and not cleaned_text.lower().startswith("i am") and not cleaned_text.lower().startswith("sorry"):
                try:
                    validate_sql(cleaned_text)
                    return {
                        "success": True,
                        "sql": cleaned_text,
                        "explanation": "Query generated successfully based on user request and provided schema.",
                        "dialect": fallback_dialect,
                        "tables_used": [],
                        "error": None,
                    }
                except ValueError as val_err:
                    return {
                        "success": False,
                        "sql": None,
                        "explanation": str(val_err),
                        "dialect": fallback_dialect,
                        "tables_used": [],
                        "error": "EMPTY_SQL",
                    }
            raise GeminiServiceError("Model did not return valid structured output.")

        # Ensure parsed_json is a dict
        if not isinstance(parsed_json, dict):
            raise GeminiServiceError("Model response was not a structured dictionary.")

        success = bool(parsed_json.get("success", False))
        sql = parsed_json.get("sql")
        explanation = parsed_json.get("explanation", "")
        dialect = parsed_json.get("dialect", fallback_dialect)
        tables_used = parsed_json.get("tables_used", [])
        error_code = parsed_json.get("error")

        if not isinstance(tables_used, list):
            tables_used = []

        if success and sql:
            clean_sql = clean_markdown_fences(str(sql))
            try:
                validate_sql(clean_sql)
            except ValueError as val_err:
                return {
                    "success": False,
                    "sql": None,
                    "explanation": str(val_err),
                    "dialect": dialect,
                    "tables_used": [],
                    "error": "EMPTY_SQL",
                }

            return {
                "success": True,
                "sql": clean_sql,
                "explanation": explanation or "Query generated successfully based on user request and schema.",
                "dialect": dialect,
                "tables_used": tables_used,
                "error": None,
            }
        else:
            return {
                "success": False,
                "sql": None,
                "explanation": explanation or "Unable to generate SQL for the requested operation.",
                "dialect": dialect,
                "tables_used": tables_used,
                "error": error_code or "INSUFFICIENT_SCHEMA",
            }
