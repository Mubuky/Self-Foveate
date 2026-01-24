"""
Utility functions for the Self-Foveate framework.

This module provides:
- Thresholding utilities for calculating semantic similarity counts
- Task generation utilities for reading comprehension tasks
"""

from self_foveate.utils.thresholding import (
    boxcox_normalize_data,
    count_above_threshold,
)

from self_foveate.utils.task_generation import (
    task_generation,
    task_rewriting,
    extract_task,
    process_generated_task,
    process_task_generation,
)

__all__ = [
    # Thresholding
    "boxcox_normalize_data",
    "count_above_threshold",
    # Task generation
    "task_generation",
    "task_rewriting",
    "extract_task",
    "process_generated_task",
    "process_task_generation",
]
