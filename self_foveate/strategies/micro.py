"""
Micro foveation strategy for the Self-Foveate framework.

This strategy extracts individual words from content and generates
instructions based on those words. It corresponds to the "micro" level in the
multi-level foveation mechanism.
"""

import re
import json
import random
import logging
import argparse
import pandas as pd

from tqdm import tqdm
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from self_foveate.prompts import (
    MICRO_KEYWORDS_SYSTEM_PROMPT,
    MICRO_KEYWORDS_USER_PROMPT,
    MICRO_GENERATION_SYSTEM_PROMPT,
    MICRO_GENERATION_USER_PROMPT,
    MICRO_REGENERATION_SYSTEM_PROMPT,
    MICRO_REGENERATION_USER_PROMPT,
    generate_generation_json
)

from self_foveate.core.api import make_requests
from self_foveate.core.base import BaseFoveator
from self_foveate.core.constants import ProcessingConstants, LoggingConstants


def micro_keywords(content: str, num_micro: int) -> List[str]:
    """
    Extract keywords from the content for instruction generation.

    Args:
        content: The content to extract keywords from.
        num_micro: Number of keywords to extract.

    Returns:
        A list of keywords.
    """
    system_prompt = MICRO_KEYWORDS_SYSTEM_PROMPT.format(num_micro=num_micro)
    user_prompt = MICRO_KEYWORDS_USER_PROMPT.format(content=content)

    keywords = make_requests(system_prompt, user_prompt, "default")
    keyword_lines = [line.strip() for line in keywords.split('\n') if line.strip()]
    keywords = [re.sub(r'^\d+\.\s*', '', line).strip() for line in keyword_lines]
    random.shuffle(keywords)

    return keywords


def micro_generation(content: str, answers: List[str], num_micro: int) -> List[str]:
    """
    Generate instructions/questions based on content and keywords.

    Args:
        content: The article content to base instructions on
        answers: Answers to incorporate into instructions
        num_micro: Number of instructions to generate

    Returns:
        List of generated instructions/questions, where each instruction
        incorporates all keywords from its corresponding group
    """
    json_data = generate_generation_json(num_micro)
    system_prompt = MICRO_GENERATION_SYSTEM_PROMPT.format(num_micro=num_micro, json_data=json_data)
    user_prompt = MICRO_GENERATION_USER_PROMPT.format(content=content, answers=json.dumps(answers, ensure_ascii=False, indent=2), num_micro=num_micro)
    instructions = make_requests(system_prompt, user_prompt, "instruction_generation")
    try:
        instructions = json.loads(instructions)
    except Exception:
        logging.error(f"Error in micro_generation: {instructions}")
        raise
    return list(instructions)


def micro_regeneration(content: str, instructions: List[str], answers: List[str], generated_idxs: List[int], keyword_index: int) -> str:
    """
    Regenerate the instruction/question based on the content and keyword groups, using successful examples.

    Args:
        content: The article content
        instructions: The generated instructions/questions
        answers: Answers
        generated_idxs: The indices of the successful keyword groups
        keyword_index: The index of the keyword group to regenerate

    Returns:
        The regenerated instruction/question
    """
    system_prompt = MICRO_REGENERATION_SYSTEM_PROMPT
    target_answer = answers[keyword_index]
    user_prompt = MICRO_REGENERATION_USER_PROMPT.format(
        content=content,
        answer=target_answer
    )

    # Get successful examples
    example_instructions = [instructions[idx] for idx in generated_idxs]
    example_answers = [answers[idx] for idx in generated_idxs]

    # Shuffle examples while maintaining pairs
    example_pairs = list(zip(example_instructions, example_answers))
    random.shuffle(example_pairs)
    # Limit the number of examples to avoid token limit issues
    example_instructions, example_answers = zip(*example_pairs) if example_pairs else ([], [])

    # Prepare few-shot examples
    few_shot_examples = [
        {
            "user": f"""The background knowledge is:
{content}
The target answer is:
{answer}
""",
            "assistant": instruction
        }
        for instruction, answer in zip(example_instructions, example_answers)
    ]

    instruction = make_requests(system_prompt, user_prompt, "regeneration", few_shot_examples)
    return instruction.strip()


class MicroFoveationStrategy(BaseFoveator):
    """
    Micro-level foveation strategy.

    This strategy extracts individual words from content and generates
    instructions based on those words.
    """

    def get_level_name(self) -> str:
        """Return the level name for logging."""
        return LoggingConstants.LEVEL_MICRO

    def extract_features(self, content: str, num_items: int, **kwargs) -> List[str]:
        """
        Extract individual words from content.

        Args:
            content: Article content
            num_items: Number of words to extract
            **kwargs: Not used for micro strategy

        Returns:
            List of extracted words
        """
        return micro_keywords(content, num_items)

    def generate_instructions(self, content: str, features: List[str], num_items: int) -> List[str]:
        """
        Generate instructions based on words.

        Args:
            content: Article content
            features: Extracted words
            num_items: Number of instructions to generate

        Returns:
            List of generated instructions
        """
        return micro_generation(content, features, num_items)

    def regenerate_instruction(
        self,
        content: str,
        instructions: List[str],
        features: List[str],
        generated_idxs: List[int],
        target_idx: int
    ) -> str:
        """
        Regenerate a failed instruction using successful examples.

        Args:
            content: Article content
            instructions: Current instructions
            features: Extracted words
            generated_idxs: Indices of successful instructions
            target_idx: Index to regenerate

        Returns:
            Regenerated instruction
        """
        return micro_regeneration(content, instructions, features, generated_idxs, target_idx)

    def validate_features(self, features: List[str], expected_count: int) -> bool:
        """
        Validate that extracted words meet requirements.

        Args:
            features: Words to validate
            expected_count: Expected number of words

        Returns:
            True if valid, False otherwise
        """
        return features and len(features) == expected_count


def micro_process_single_article(data_tuple: Tuple[int, Any], num_micro: int, max_retries: int) -> List[Dict[str, str]]:
    """
    Process a single article to generate seed tasks using micro foveation strategy.

    Args:
        data_tuple: Tuple containing (index, article_data)
        num_micro: Number of words to extract
        max_retries: Maximum number of retries for failed generations

    Returns:
        Generated seed tasks for this article
    """
    strategy = MicroFoveationStrategy()
    return strategy.process_article(data_tuple, num_micro, max_retries)


def micro_process_articles_parallel(data_df: pd.DataFrame, args: argparse.Namespace, threshold_counts: List[int]) -> List[Dict[str, str]]:
    """
    Process multiple articles in parallel to generate seed tasks.

    Args:
        data_df: DataFrame containing articles to process
        args: Arguments containing num_direct, num_keywords, and max_retries
        threshold_counts: List of counts above threshold for each article

    Returns:
        List of generated seed tasks from all articles
    """
    seed_tasks: List[Dict[str, str]] = []
    article_results: Dict[int, List[Dict[str, str]]] = {}

    with ThreadPoolExecutor(max_workers=ProcessingConstants.DEFAULT_MAX_WORKERS) as executor:
        # Create futures for each article
        future_to_article = {}
        for idx, data in enumerate(data_df.itertuples()):
            num_micro = threshold_counts[idx]

            future = executor.submit(
                micro_process_single_article,
                (idx, data),
                num_micro,
                args.max_retries
            )
            future_to_article[future] = idx

        # Process completed futures
        for future in tqdm(as_completed(future_to_article),
                         total=len(future_to_article),
                         desc="Processing Articles"):
            try:
                article_tasks = future.result()
                idx = future_to_article[future]
                article_results[idx] = article_tasks
            except Exception as e:
                idx = future_to_article[future]
                logging.error(f"Error processing article {idx}: {str(e)}")

    # Extend seed_tasks in order of article index
    for idx in range(len(data_df)):
        if idx in article_results:
            seed_tasks.extend(article_results[idx])

    return seed_tasks
