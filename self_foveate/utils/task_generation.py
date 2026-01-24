"""
Task generation utilities for the Self-Foveate framework.

This module handles the generation of reading comprehension tasks
and the extraction of question-answer pairs.
"""

import re
import logging
from typing import Optional, Dict, List, Tuple, Pattern

from self_foveate.prompts import (
    READING_COMPREHENSION_SYSTEM_PROMPT,
    READING_COMPREHENSION_USER_PROMPT,
    REREADING_SYSTEM_PROMPT,
    REREADING_USER_PROMPT,
)

from self_foveate.core.api import make_requests


def task_generation(unsupervised_knowledge_data: str, instruction: str) -> str:
    """
    Generate an answer to an instruction/question based on provided knowledge data.

    Args:
        unsupervised_knowledge_data: The source text to base answers on
        instruction: The instruction or question to answer

    Returns:
        Generated answer formatted as a question-answer pair in the format:
            Question: [question]
            Answer: [detailed answer]
    """
    system_prompt = READING_COMPREHENSION_SYSTEM_PROMPT
    user_prompt = READING_COMPREHENSION_USER_PROMPT.format(
        unsupervised_knowledge_data=unsupervised_knowledge_data,
        instruction=instruction
    )
    output: str = make_requests(system_prompt, user_prompt, "default")
    return output


def task_rewriting(unsupervised_knowledge_data: str, instruction: str, output: str) -> str:
    """
    Improve an existing question-answer pair by rereading the source text.

    Args:
        unsupervised_knowledge_data: The source text to base answers on
        instruction: The original instruction/question
        output: The original question-answer pair to improve

    Returns:
        Improved answer formatted as a question-answer pair in the format:
            Question: [question]
            Answer: [detailed rewritten answer]
    """
    system_prompt = REREADING_SYSTEM_PROMPT
    user_prompt = REREADING_USER_PROMPT.format(
        unsupervised_knowledge_data=unsupervised_knowledge_data,
        instruction=instruction,
        output=output
    )
    output: str = make_requests(system_prompt, user_prompt, "default")
    return output


def extract_task(qa_pair: str) -> Optional[Dict[str, str]]:
    """
    Extract question-answer pairs from the given string.

    Args:
        qa_pair: The string containing question-answer pairs.

    Returns:
        A dictionary containing a question-answer pair,
        or None if extraction fails.
    """
    try:
        qa_pair = '\n'.join(line.strip() for line in qa_pair.split('\n') if line.strip())
        pattern: Pattern[str] = re.compile(r'Question:\s*(.*?)\nAnswer:\s*(.*?)$', re.DOTALL)
        matches: List[Tuple[str, str]] = pattern.findall(qa_pair)
        if len(matches) > 0:
            seed_task: Dict[str, str] = {
                'instruction': matches[0][0].strip(),
                'output': matches[0][1].strip()
            }
        else:
            logging.warning(f"No QA pairs extracted for {qa_pair}.")
            seed_task = None
        return seed_task
    except Exception as e:
        logging.error(f"Error in extract_task: {str(e)}")
        return None


def process_generated_task(output: str, article_index: int) -> Optional[Dict[str, str]]:
    """
    Process the generated seed task by extracting QA pairs and post-processing them.

    Args:
        output: The output containing QA pairs.
        article_index: The index of the article.

    Returns:
        A processed seed task, or None if extraction fails.
    """

    output = re.sub(r'\*\*', '', output)
    seed_task: Optional[Dict[str, str]] = extract_task(output)
    if not seed_task:
        logging.warning(f"No QA pairs extracted for {output}.")
        return None
    if "I don't know" in seed_task['output']:
        return None
    seed_task['article_index'] = article_index
    return seed_task


def process_task_generation(content: str, instruction: str, idx: int) -> Tuple[Optional[Dict[str, str]], str]:
    """
    Process the task generation of a single instruction/question.

    Args:
        content: The article content
        instruction: The instruction/question to generate
        idx: The index of the article

    Returns:
        A tuple containing the generated task and the instruction/question
    """
    output = task_generation(content, instruction)
    logging.info(f"Generated output for article {idx + 1}: {output}")
    generated_task = process_generated_task(output, idx)
    logging.info(f"Generated task for article {idx + 1}: {generated_task}")

    if generated_task:
        return generated_task, instruction

    return None, instruction
