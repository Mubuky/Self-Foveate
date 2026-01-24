"""
Core module for the Self-Foveate framework.

This module provides the foundational components:
- API client for LLM interactions
- Data loading and saving utilities
- Base class for foveation strategies
- Configuration constants
"""

from self_foveate.core.api import (
    make_requests,
    get_embedding,
    chat_model_config,
    embedding_model_config,
    request_params,
)

from self_foveate.core.data import (
    load_data,
    save_seed_tasks,
)

from self_foveate.core.base import BaseFoveator

from self_foveate.core.constants import (
    ProcessingConstants,
    LoggingConstants,
)

__all__ = [
    # API
    "make_requests",
    "get_embedding",
    "chat_model_config",
    "embedding_model_config",
    "request_params",
    # Data
    "load_data",
    "save_seed_tasks",
    # Base
    "BaseFoveator",
    # Constants
    "ProcessingConstants",
    "LoggingConstants",
]
