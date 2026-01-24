"""
Configuration constants for the Self-Foveate framework.

This module centralizes all magic numbers and configuration values
to improve code maintainability and clarity.
"""


class ProcessingConstants:
    """Constants related to data processing and thresholds."""

    # Semantic similarity threshold for context relevance
    # Words with similarity >= this threshold are considered contextually relevant
    CONTEXT_THRESHOLD = 0.16

    # Scatter-level keyword grouping ratios
    # These ratios determine how keywords are distributed into groups:
    # SCATTER_RATIO_A: ratio for single-keyword groups
    # SCATTER_RATIO_B: ratio for two-keyword groups
    # The remainder forms three-keyword groups
    SCATTER_RATIO_A = 2.50  # Single keyword groups
    SCATTER_RATIO_B = 2.25  # Double keyword groups

    # Parallel processing configuration
    DEFAULT_MAX_WORKERS = 96  # Maximum concurrent workers for article processing
    EMBEDDING_MAX_WORKERS = 10  # Maximum concurrent workers for embedding generation

    # Retry configuration
    DEFAULT_MAX_RETRIES = 5  # Default maximum retry attempts for failed operations

    # Box-Cox normalization defaults
    DEFAULT_TARGET_MEAN = 8.0  # Target mean for normalized distributions
    DEFAULT_ALPHA = 1.0  # Scaling factor for Box-Cox transformation


class LoggingConstants:
    """Constants for logging messages to ensure consistency."""

    # Level names for different foveation strategies
    LEVEL_MACRO = "Macro"
    LEVEL_MICRO = "Micro"
    LEVEL_SCATTER = "Scatter"
