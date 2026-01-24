"""
Text processing utilities for evaluation metrics.

Provides text normalization and tokenization functions used across
evaluation scripts for consistent text comparison.
"""

import re
import string
from typing import List


def normalize_answer(text: str) -> str:
    """
    Normalize answer text for evaluation.

    Performs the following normalization steps:
    1. Convert to lowercase
    2. Remove punctuation
    3. Remove articles (a, an, the)
    4. Normalize whitespace

    Args:
        text: Input text to normalize

    Returns:
        Normalized text string

    Examples:
        >>> normalize_answer("The quick brown fox!")
        'quick brown fox'
        >>> normalize_answer("A simple test.")
        'simple test'
    """
    def remove_articles(text: str) -> str:
        """Remove English articles (a, an, the)."""
        regex = re.compile(r'\b(a|an|the)\b', re.UNICODE)
        return re.sub(regex, ' ', text)

    def white_space_fix(text: str) -> str:
        """Normalize whitespace to single spaces."""
        return ' '.join(text.split())

    def remove_punc(text: str) -> str:
        """Remove all punctuation characters."""
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)

    def lower(text: str) -> str:
        """Convert to lowercase."""
        return text.lower()

    # Apply normalization pipeline
    return white_space_fix(remove_articles(remove_punc(lower(text))))


def tokenize(text: str) -> List[str]:
    """
    Tokenize text into words after normalization.

    Args:
        text: Input text to tokenize

    Returns:
        List of normalized word tokens

    Examples:
        >>> tokenize("The quick brown fox jumps!")
        ['quick', 'brown', 'fox', 'jumps']
    """
    normalized_text = normalize_answer(text)
    return normalized_text.split()
