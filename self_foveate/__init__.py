"""
Self-Foveate: Multi-level foveation framework for generating domain-specific instructions.

This package provides a biologically-inspired multi-level foveation mechanism
(mimicking human visual perception) to create diverse, difficulty-varied instruction
datasets for LLM training.

Modules:
- core: Foundational components (API, data I/O, base class, constants)
- strategies: Three-level foveation strategies (macro, micro, scatter)
- prompts: LLM prompt templates for all generation tasks
- utils: Utility functions (thresholding, task generation)
"""

__version__ = "0.7.0"

# Core components
from self_foveate.core import (
    make_requests,
    get_embedding,
    load_data,
    save_seed_tasks,
    BaseFoveator,
    ProcessingConstants,
    LoggingConstants,
)

# Foveation strategies (new names)
from self_foveate.strategies import (
    MacroFoveationStrategy,
    MicroFoveationStrategy,
    ScatterFoveationStrategy,
    macro_process_articles_parallel,
    micro_process_articles_parallel,
    scatter_process_articles_parallel,
)


# Thresholding utilities
from self_foveate.utils import (
    boxcox_normalize_data,
    count_above_threshold,
)

__all__ = [
    # Version
    "__version__",
    # Core
    "make_requests",
    "get_embedding",
    "load_data",
    "save_seed_tasks",
    "BaseFoveator",
    "ProcessingConstants",
    "LoggingConstants",
    # Strategies
    "MacroFoveationStrategy",
    "MicroFoveationStrategy",
    "ScatterFoveationStrategy",
    "macro_process_articles_parallel",
    "micro_process_articles_parallel",
    "scatter_process_articles_parallel",
    # Utils
    "boxcox_normalize_data",
    "count_above_threshold",
]
