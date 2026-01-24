"""
Scatter foveation strategy for the Self-Foveate framework.

This strategy extracts keyword groups (1, 2, or 3 keywords per group) and generates
instructions based on those groups. It corresponds to the "scatter" level in the
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
    SCATTER_IMPORTANT_SYSTEM_PROMPT,
    SCATTER_IMPORTANT_USER_PROMPT,
    SCATTER_KEYWORDS_SYSTEM_PROMPT,
    SCATTER_KEYWORDS_USER_PROMPT,
    SCATTER_GENERATION_SYSTEM_PROMPT,
    SCATTER_GENERATION_USER_PROMPT,
    SCATTER_REGENERATION_SYSTEM_PROMPT,
    SCATTER_REGENERATION_USER_PROMPT,
    generate_generation_json
)

from self_foveate.core.api import make_requests
from self_foveate.core.base import BaseFoveator
from self_foveate.core.constants import ProcessingConstants, LoggingConstants


def scatter_important(content: str, keywords: str, num_important_list: List[int]) -> List[str]:
    """
    Select important keywords from the content.

    Args:
        content: The content to extract important keywords from.
        keywords: The keywords to generate important keywords for.
        num_important_list: The number of important keywords to select.

    Returns:
        The selected important keywords.
    """
    system_prompt = SCATTER_IMPORTANT_SYSTEM_PROMPT.format(num_core=num_important_list[0], num_major=num_important_list[1])
    user_prompt = SCATTER_IMPORTANT_USER_PROMPT.format(content=content, keywords=keywords)

    output = make_requests(system_prompt, user_prompt, "default")
    keywords = []

    core_pattern = r"Core keywords?:\s*((?:\d+\.\s*.+\n?)+)"
    major_pattern = r"Major keywords?:\s*((?:\d+\.\s*.+\n?)+)"

    core_match = re.search(core_pattern, output, re.MULTILINE)
    major_match = re.search(major_pattern, output, re.MULTILINE)

    if core_match and major_match:
        core_section = core_match.group(1)
        major_section = major_match.group(1)

        # Extract all core keywords
        core_keywords = [match.strip() for match in re.findall(r'\d+\.\s*(.+)', core_section)]

        # Extract all major keywords
        major_keywords = [match.strip() for match in re.findall(r'\d+\.\s*(.+)', major_section)]

        keywords = core_keywords + major_keywords
    else:
        logging.error("Failed to parse keywords from output")
        keywords = []

    return keywords


def scatter_keywords(content: str, num_keywords: int, num_important_list: List[int], num_keywords_list: List[int]) -> List[str]:
    """
    Extract and group keywords from the content for instruction generation.

    Args:
        content: The content to extract keywords from.
        num_keywords: Number of keywords to extract.
        num_important_list: Number of important keywords to select.
        num_keywords_list: Distribution of keyword groups [single, double, triple].

    Returns:
        A list of keyword groups.
    """
    system_prompt = SCATTER_KEYWORDS_SYSTEM_PROMPT.format(num_keywords=num_keywords)
    user_prompt = SCATTER_KEYWORDS_USER_PROMPT.format(content=content)

    keywords = make_requests(system_prompt, user_prompt, "default")

    if num_important_list:
        important_keywords = scatter_important(content, keywords, num_important_list)
    else:
        important_keywords = []

    if num_important_list and not important_keywords:
        important_keywords = random.sample(keywords, sum(num_important_list))

    logging.info(f"Important keywords: {important_keywords}")

    keyword_lines = [line.strip() for line in keywords.split('\n') if line.strip()]
    keywords = [re.sub(r'^\d+\.\s*', '', line).strip() for line in keyword_lines]
    if important_keywords:
        keywords.extend(important_keywords)
        keywords.append(important_keywords[0])
    random.shuffle(keywords)

    logging.info(f"Keywords: {keywords}")

    # Create keyword groups according to the pattern:
    # num_keywords_list[0] groups of 1 keyword
    # num_keywords_list[1] groups of 2 keywords
    # num_keywords_list[2] groups of 3 keywords
    keyword_groups = (
        # First num_keywords_list[0] groups with 1 keyword each
        [[kw] for kw in keywords[:num_keywords_list[0]]] +
        # Next num_keywords_list[1] groups with 2 keywords each
        [keywords[i:i+2] for i in range(num_keywords_list[0], num_keywords_list[0] + num_keywords_list[1] * 2, 2)] +
        # Last num_keywords_list[2] groups with 3 keywords each
        [keywords[i:i+3] for i in range(num_keywords_list[0] + num_keywords_list[1] * 2, num_keywords_list[0] + num_keywords_list[1] * 2 + num_keywords_list[2] * 3, 3)]
    )

    return keyword_groups


def scatter_generation(content: str, keywords: List[List[str]], num_scatter: int) -> List[List[str]]:
    """
    Generate instructions/questions based on content and keyword groups.

    Args:
        content: The article content to base instructions on
        keywords: Groups of keywords to incorporate into instructions
        num_scatter: Number of instructions to generate

    Returns:
        List of generated instructions/questions, where each instruction
        incorporates all keywords from its corresponding group
    """
    json_data = generate_generation_json(num_scatter)
    system_prompt = SCATTER_GENERATION_SYSTEM_PROMPT.format(num_core=num_scatter, json_data=json_data)
    user_prompt = SCATTER_GENERATION_USER_PROMPT.format(content=content, keyword_groups=json.dumps(keywords, ensure_ascii=False, indent=2), num_core=num_scatter)
    instructions = make_requests(system_prompt, user_prompt, "instruction_generation")
    try:
        instructions = json.loads(instructions)
    except Exception:
        logging.error(f"Error in scatter_generation: {instructions}")
        raise
    return list(instructions)


def scatter_regeneration(content: str, instructions: List[str], keywords: List[List[str]], generated_idxs: List[int], keyword_index: int) -> str:
    """
    Regenerate the instruction/question based on the content and keyword groups, using successful examples.

    Args:
        content: The article content
        instructions: The generated instructions/questions
        keywords: Groups of keywords
        generated_idxs: The indices of the successful keyword groups
        keyword_index: The index of the keyword group to regenerate

    Returns:
        The regenerated instruction/question
    """
    system_prompt = SCATTER_REGENERATION_SYSTEM_PROMPT
    keyword_group = keywords[keyword_index]
    user_prompt = SCATTER_REGENERATION_USER_PROMPT.format(
        content=content,
        keyword_group=json.dumps(keyword_group, ensure_ascii=False, indent=2)
    )
    example_instructions = [instructions[idx] for idx in generated_idxs]
    example_groups = [keywords[idx] for idx in generated_idxs]

    # Shuffle examples while maintaining pairs
    example_pairs = list(zip(example_instructions, example_groups))
    random.shuffle(example_pairs)
    example_instructions, example_groups = zip(*example_pairs)
    # Prepare few-shot examples
    few_shot_examples = [
        {
            "user": f"""The background knowledge is:
{content}
The target keyword group to use:
{json.dumps(group, ensure_ascii=False, indent=2)}
""",
            "assistant": instruction
        }
        for instruction, group in zip(example_instructions, example_groups)
    ]

    instruction = make_requests(system_prompt, user_prompt, "regeneration", few_shot_examples)
    return instruction.strip()


class ScatterFoveationStrategy(BaseFoveator):
    """
    Scatter-level foveation strategy.

    This strategy extracts keyword groups and generates instructions
    based on those groups. Keywords are organized into groups of 1, 2, or 3 keywords.
    """

    def __init__(self, num_important_list: List[int], num_keywords_list: List[int]):
        """
        Initialize the scatter foveation strategy.

        Args:
            num_important_list: List specifying number of core and major important keywords
            num_keywords_list: List specifying distribution of keyword groups [single, double, triple]
        """
        self.num_important_list = num_important_list
        self.num_keywords_list = num_keywords_list

    def get_level_name(self) -> str:
        """Return the level name for logging."""
        return LoggingConstants.LEVEL_SCATTER

    def extract_features(self, content: str, num_items: int, **kwargs) -> List[List[str]]:
        """
        Extract keyword groups from content.

        Args:
            content: Article content
            num_items: Total number of keywords to extract
            **kwargs: Not used for scatter strategy

        Returns:
            List of keyword groups (each group is a list of 1-3 keywords)
        """
        num_keywords = kwargs.get('num_keywords', num_items)
        return scatter_keywords(content, num_keywords, self.num_important_list, self.num_keywords_list)

    def generate_instructions(self, content: str, features: List[List[str]], num_items: int) -> List[str]:
        """
        Generate instructions based on keyword groups.

        Args:
            content: Article content
            features: Keyword groups
            num_items: Number of instructions to generate

        Returns:
            List of generated instructions
        """
        return scatter_generation(content, features, num_items)

    def regenerate_instruction(
        self,
        content: str,
        instructions: List[str],
        features: List[List[str]],
        generated_idxs: List[int],
        target_idx: int
    ) -> str:
        """
        Regenerate a failed instruction using successful examples.

        Args:
            content: Article content
            instructions: Current instructions
            features: Keyword groups
            generated_idxs: Indices of successful instructions
            target_idx: Index to regenerate

        Returns:
            Regenerated instruction
        """
        return scatter_regeneration(content, instructions, features, generated_idxs, target_idx)

    def validate_features(self, features: List[List[str]], expected_count: int) -> bool:
        """
        Validate that keyword groups meet requirements.

        Args:
            features: Keyword groups to validate
            expected_count: Expected number of groups

        Returns:
            True if valid, False otherwise
        """
        return features and len(features) == expected_count


def scatter_process_single_article(data_tuple: Tuple[int, Any], num_scatter: int, num_keywords: int, max_retries: int, num_important_list: List[int], num_keywords_list: List[int]) -> List[Dict[str, str]]:
    """
    Process a single article to generate seed tasks using scatter foveation strategy.

    Args:
        data_tuple: Tuple containing (index, article_data)
        num_scatter: Number of direct instructions to generate
        num_keywords: Number of keywords to extract
        max_retries: Maximum number of retries for failed generations
        num_important_list: Number of important keywords to select
        num_keywords_list: Distribution of keyword groups

    Returns:
        Generated seed tasks for this article
    """
    strategy = ScatterFoveationStrategy(num_important_list, num_keywords_list)
    return strategy.process_article(
        data_tuple,
        num_scatter,
        max_retries,
        num_keywords=num_keywords
    )


def scatter_process_articles_parallel(data_df: pd.DataFrame, args: argparse.Namespace, threshold_counts: List[int]) -> List[Dict[str, str]]:
    """
    Process multiple articles in parallel to generate seed tasks.

    Args:
        data_df: DataFrame containing articles to process
        args: Arguments containing num_scatter, num_keywords, and max_retries
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
            num_scatter = threshold_counts[idx]
            # Calculate keyword group distribution using configuration constants
            num_keywords_a = int(num_scatter // ProcessingConstants.SCATTER_RATIO_A)
            num_keywords_b = int(num_scatter // ProcessingConstants.SCATTER_RATIO_B)
            num_keywords_c = int(num_scatter - num_keywords_a - num_keywords_b)
            num_keywords_list = [num_keywords_a, num_keywords_b, num_keywords_c]
            num_keywords = num_keywords_a + num_keywords_b * 2 + num_keywords_c * 3

            future = executor.submit(
                scatter_process_single_article,
                (idx, data),
                num_scatter,
                num_keywords,
                args.max_retries,
                args.num_important_list,
                num_keywords_list,
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
