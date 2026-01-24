"""
Shared utilities for evaluation scripts.

This package provides common functionality used across multiple evaluation
utilities to eliminate code duplication and ensure consistency.

Modules:
    api_client: Unified API client with retry logic
    text_processing: Text normalization and tokenization
    evaluation_metrics: Precision, recall, F1 calculations
    parallel_executor: Simplified parallel execution
    path_utils: Consistent path management
"""

from .api_client import APIClient, APIClientConfig
from .text_processing import normalize_answer, tokenize
from .evaluation_metrics import (
    calculate_token_metrics,
    calculate_batch_metrics,
    calculate_macro_metrics,
    EvaluationResult
)
from .parallel_executor import execute_parallel
from .path_utils import (
    ensure_output_dir,
    get_output_path,
    get_project_root,
    resolve_data_path
)

__all__ = [
    # API client
    'APIClient',
    'APIClientConfig',
    # Text processing
    'normalize_answer',
    'tokenize',
    # Evaluation metrics
    'calculate_token_metrics',
    'calculate_batch_metrics',
    'calculate_macro_metrics',
    'EvaluationResult',
    # Parallel execution
    'execute_parallel',
    # Path utilities
    'ensure_output_dir',
    'get_output_path',
    'get_project_root',
    'resolve_data_path',
]
