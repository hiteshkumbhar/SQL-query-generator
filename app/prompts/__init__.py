"""Prompt templates package."""
from app.prompts.text_to_sql_prompt import SYSTEM_INSTRUCTION, build_user_prompt

__all__ = ["SYSTEM_INSTRUCTION", "build_user_prompt"]
