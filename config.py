"""Application configuration module."""

import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

class Config:
    """Base application configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Request limits
    MAX_PROMPT_LENGTH = int(os.getenv("MAX_PROMPT_LENGTH", "1000"))
    MAX_SCHEMA_LENGTH = int(os.getenv("MAX_SCHEMA_LENGTH", "10000"))
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB max request payload
    
    # Rate limiting / anti-abuse limits
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
    
    # Supported database dialects
    ALLOWED_DIALECTS = {
        "postgresql",
        "mysql",
        "sqlite",
        "bigquery",
        "snowflake",
        "sqlserver",
        "oracle",
    }
    DEFAULT_DIALECT = "postgresql"

    # Default configurable database schema representation
    DEFAULT_SCHEMA = (
        "Table: customers\n"
        "Columns:\n"
        "- id INTEGER PRIMARY KEY\n"
        "- name VARCHAR\n"
        "- email VARCHAR\n"
        "- city VARCHAR\n"
        "- state VARCHAR\n"
        "- created_at TIMESTAMP\n\n"
        "Table: orders\n"
        "Columns:\n"
        "- id INTEGER PRIMARY KEY\n"
        "- customer_id INTEGER (Foreign Key -> customers.id)\n"
        "- order_date TIMESTAMP\n"
        "- total_amount DECIMAL\n"
        "- status VARCHAR\n\n"
        "Table: products\n"
        "Columns:\n"
        "- id INTEGER PRIMARY KEY\n"
        "- name VARCHAR\n"
        "- category VARCHAR\n"
        "- price DECIMAL\n\n"
        "Table: order_items\n"
        "Columns:\n"
        "- id INTEGER PRIMARY KEY\n"
        "- order_id INTEGER (Foreign Key -> orders.id)\n"
        "- product_id INTEGER (Foreign Key -> products.id)\n"
        "- quantity INTEGER\n"
        "- unit_price DECIMAL\n\n"
        "Relationships:\n"
        "- customers.id -> orders.customer_id\n"
        "- orders.id -> order_items.order_id\n"
        "- products.id -> order_items.product_id"
    )


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DEBUG = True
    GEMINI_API_KEY = "test-mock-api-key"


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False


# Map configuration environments
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
