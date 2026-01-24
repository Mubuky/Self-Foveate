"""
Foveation strategies for the Self-Foveate framework.

This module provides three foveation strategies corresponding to the
multi-level foveation mechanism:
- Macro: Sentence-level foveation
- Micro: Word-level foveation
- Scatter: Multi-keyword combination foveation
"""

# Macro (sentence-level) strategy
from self_foveate.strategies.macro import (
    MacroFoveationStrategy,
    macro_process_single_article,
    macro_process_articles_parallel,
    macro_keywords,
    macro_generation,
    macro_regeneration,
)

# Micro (word-level) strategy
from self_foveate.strategies.micro import (
    MicroFoveationStrategy,
    micro_process_single_article,
    micro_process_articles_parallel,
    micro_keywords,
    micro_generation,
    micro_regeneration,
)

# Scatter (multi-keyword) strategy
from self_foveate.strategies.scatter import (
    ScatterFoveationStrategy,
    scatter_process_single_article,
    scatter_process_articles_parallel,
    scatter_keywords,
    scatter_generation,
    scatter_regeneration,
    scatter_important,
)

__all__ = [
    # Macro strategy
    "MacroFoveationStrategy",
    "macro_process_single_article",
    "macro_process_articles_parallel",
    "macro_keywords",
    "macro_generation",
    "macro_regeneration",
    # Micro strategy
    "MicroFoveationStrategy",
    "micro_process_single_article",
    "micro_process_articles_parallel",
    "micro_keywords",
    "micro_generation",
    "micro_regeneration",
    # Scatter strategy
    "ScatterFoveationStrategy",
    "scatter_process_single_article",
    "scatter_process_articles_parallel",
    "scatter_keywords",
    "scatter_generation",
    "scatter_regeneration",
    "scatter_important",
]
