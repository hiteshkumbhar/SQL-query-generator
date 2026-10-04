"""Gemini AI provider service.

Handles server-side communication with Google Gemini API.
"""

import json
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

class GeminiServiceError(Exception):
    """Base error for Gemini service operations."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class GeminiAuthError(GeminiServiceError):
    """Raised when Gemini API key is missing or invalid."""

    def __init__(self, message: str = "Gemini API key is missing or invalid.") -> None:
        super().__init__(message, status_code=401)


class GeminiRateLimitError(GeminiServiceError):
    """Raised when Gemini API rate limit is exceeded."""

    def __init__(self, message: str = "Gemini API rate limit exceeded. Please try again later.") -> None:
        super().__init__(message, status_code=429)


class GeminiService:
    """Service client for calling Gemini API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.5-flash",
        timeout_seconds: int = 30,
    ) -> None:
        self.api_key = api_key or ""
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds

    def generate_content(
        self,
        user_prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
    ) -> str:
        """Send prompt to Gemini API and return raw response text.

        Args:
            user_prompt: The prompt text to process.
            system_instruction: Optional system instruction for the model.
            temperature: Model temperature (low temperature for deterministic SQL).

        Returns:
            String containing the model's text response.

        Raises:
            GeminiAuthError: Missing or invalid API key.
            GeminiRateLimitError: Rate limit 429 response.
            GeminiServiceError: Any other API or network failure.
        """
        if not self.api_key or not self.api_key.strip():
            raise GeminiAuthError("Gemini API key is missing. Please configure GEMINI_API_KEY.")

        # Try using google.genai SDK if available
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            config = types.GenerateContentConfig(
                temperature=temperature,
                response_mime_type="application/json",
            )
            if system_instruction:
                config.system_instruction = system_instruction

            response = client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=config,
            )
            if not response or not response.text:
                raise GeminiServiceError("Empty response received from Gemini API.")
            return response.text.strip()

        except ImportError:
            # Fallback to direct HTTP endpoint using standard library urllib
            return self._call_gemini_rest(user_prompt, system_instruction, temperature)
        except Exception as exc:
            # Check for rate limiting / auth issues
            err_str = str(exc).lower()
            if "429" in err_str or "quota" in err_str or "rate" in err_str:
                raise GeminiRateLimitError() from exc
            if "401" in err_str or "api_key" in err_str or "permission" in err_str:
                raise GeminiAuthError("Invalid Gemini API credentials.") from exc
            raise GeminiServiceError("Failed to communicate with AI provider.") from exc

    def _call_gemini_rest(
        self,
        user_prompt: str,
        system_instruction: Optional[str],
        temperature: float,
    ) -> str:
        """Call Gemini REST API directly using standard urllib."""
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

        payload: Dict[str, Any] = {
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json",
            },
        }

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data_bytes,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "aistudio-build",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                candidates = resp_data.get("candidates", [])
                if not candidates:
                    raise GeminiServiceError("No candidates returned from Gemini.")
                parts = candidates[0].get("content", {}).get("parts", [])
                if not parts:
                    raise GeminiServiceError("Empty content parts in Gemini response.")
                return parts[0].get("text", "").strip()

        except urllib.error.HTTPError as http_err:
            if http_err.code == 429:
                raise GeminiRateLimitError() from http_err
            if http_err.code in (401, 403):
                raise GeminiAuthError("Invalid Gemini API credentials or unauthorized access.") from http_err
            error_body = ""
            try:
                error_body = http_err.read().decode("utf-8")
            except Exception:
                pass
            raise GeminiServiceError("AI provider returned an error.") from http_err
        except urllib.error.URLError as url_err:
            raise GeminiServiceError("Network timeout connecting to AI provider.") from url_err
