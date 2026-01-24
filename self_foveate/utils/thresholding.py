"""
Threshold calculation utilities for the Self-Foveate framework.

This module provides functions for calculating semantic similarity thresholds
and normalizing counts using Box-Cox transformation.
"""

import numpy as np
from tqdm import tqdm
from scipy import stats
from concurrent.futures import ThreadPoolExecutor
from sklearn.metrics.pairwise import cosine_similarity

from self_foveate.core.api import get_embedding
from self_foveate.core.constants import ProcessingConstants


def boxcox_normalize_data(data, target_mean=8.0, alpha=1.0):
    """
    Normalize data using Box-Cox transformation and round to integers.

    Args:
        data: List or array of values to normalize
        target_mean: Target mean for the normalized distribution
        alpha: Scaling factor for the transformation

    Returns:
        List of normalized integer values
    """
    array = np.array(data)

    # Ensure all values are positive (Box-Cox requirement)
    offset = abs(min(array)) + 1 if min(array) <= 0 else 0
    shifted_data = array + offset

    # Find optimal lambda for Box-Cox transformation
    transformed_data, _ = stats.boxcox(shifted_data)

    # Standardize transformed data
    transformed_mean = np.mean(transformed_data)
    transformed_std = np.std(transformed_data)
    normalized = target_mean + alpha * (transformed_data - transformed_mean) / transformed_std

    # Round to integers
    rounded = np.round(normalized)

    return rounded.astype(int).tolist()


def count_above_threshold(texts, context_threshold=None):
    """
    Calculate the number of words in each text that have similarity above the threshold.

    Args:
        texts: List of text strings to process
        context_threshold: Similarity threshold (default: ProcessingConstants.CONTEXT_THRESHOLD)

    Returns:
        List of counts for each text
    """
    if context_threshold is None:
        context_threshold = ProcessingConstants.CONTEXT_THRESHOLD

    threshold_counts = []

    for text in tqdm(texts):
        text_embedding = get_embedding(text)

        words = list(dict.fromkeys(''.join(c for c in text if c.isalnum() or c.isspace()).split()))

        def process_word(word):
            word_embedding = get_embedding(word)

            similarity = cosine_similarity(
                np.array(text_embedding).reshape(1, -1),
                np.array(word_embedding).reshape(1, -1)
            )[0][0]

            return (word, similarity)

        with ThreadPoolExecutor(max_workers=ProcessingConstants.EMBEDDING_MAX_WORKERS) as executor:
            word_similarities = list(executor.map(process_word, words))

        threshold_counts.append(sum(1 for _, similarity in word_similarities if similarity >= context_threshold))

    return threshold_counts
