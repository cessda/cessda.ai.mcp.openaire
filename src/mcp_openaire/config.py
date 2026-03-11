# SPDX-License-Identifier: Apache-2.0
"""Configuration management using environment variables."""

import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class Config(BaseModel):
    """Application configuration loaded from environment variables.

    Follows 12-factor app principle: configuration via environment.
    """

    # ScholExplorer API Configuration
    scholexplorer_base_url: str = Field(
        default="https://api.scholexplorer.openaire.eu/v3",
        description="Base URL for ScholExplorer API"
    )

    # OpenAIRE Graph API Configuration
    graph_api_base_url: str = Field(
        default="https://api.openaire.eu/graph/v2",
        description="Base URL for OpenAIRE Graph API"
    )

    api_timeout: int = Field(
        default=30,
        description="API request timeout in seconds"
    )

    api_max_retries: int = Field(
        default=3,
        description="Maximum number of API request retries"
    )

    # Logging Configuration
    log_level: str = Field(
        default="WARN",
        description="Default logging level (WARN per CESSDA guidelines)"
    )

    # Default search parameters
    default_links_limit: int = Field(
        default=200,
        description="Default number of related objects to return"
    )

    max_links_limit: int = Field(
        default=1000,
        description="Maximum allowed related objects per request"
    )

    links_page_size: int = Field(
        default=50,
        description="Number of results to fetch per API page request"
    )

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables.

        Environment variables:
            OPENAIRE_SCHOLEXPLORER_URL: Base URL for ScholExplorer API
            OPENAIRE_GRAPH_URL: Base URL for Graph API
            OPENAIRE_API_TIMEOUT: Request timeout in seconds
            OPENAIRE_API_MAX_RETRIES: Max retry attempts
            OPENAIRE_LOG_LEVEL: Logging level
            OPENAIRE_DEFAULT_LIMIT: Default links result limit
            OPENAIRE_MAX_LIMIT: Maximum links result limit
            OPENAIRE_PAGE_SIZE: Results per API page
        """
        return cls(
            scholexplorer_base_url=os.getenv("OPENAIRE_SCHOLEXPLORER_URL", "https://api.scholexplorer.openaire.eu/v3"),
            graph_api_base_url=os.getenv("OPENAIRE_GRAPH_URL", "https://api.openaire.eu/graph/v2"),
            api_timeout=int(os.getenv("OPENAIRE_API_TIMEOUT", "30")),
            api_max_retries=int(os.getenv("OPENAIRE_API_MAX_RETRIES", "3")),
            log_level=os.getenv("OPENAIRE_LOG_LEVEL", "WARN"),
            default_links_limit=int(os.getenv("OPENAIRE_DEFAULT_LIMIT", "200")),
            max_links_limit=int(os.getenv("OPENAIRE_MAX_LIMIT", "1000")),
            links_page_size=int(os.getenv("OPENAIRE_PAGE_SIZE", "50")),
        )


# Global config instance
config = Config.from_env()
