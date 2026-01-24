"""
Prompts for task generation (reading comprehension and rewriting).

This module contains prompts for generating answers from instructions
and improving existing answers through rereading.
"""

import json


def generate_generation_json(num: int) -> str:
    """Generate a JSON template for instruction generation output format."""
    return json.dumps([f"Generated instruction {i+1}" for i in range(num)], indent=2)


READING_COMPREHENSION_SYSTEM_PROMPT = """You are an excellent reading comprehension assistant designed to help users answer the question based on provided background knowledge. Please carefully read the background knowledge and accurately answer the question posed based on its content.

- Do not alter key information from the original text.
- Avoid using phrases like "based on the above article."
- If the background knowledge lacks sufficient information to answer a question, respond with "I don't know."
- Ensure your answers are derived from the background knowledge, detailed, and accurate.
- Answer the question thoroughly.

Please generate the answer following this format strictly:
Question: [question]
Answer: [detailed and accurate answer]
"""

READING_COMPREHENSION_USER_PROMPT = """The background knowledge is:
{unsupervised_knowledge_data}

Please answer the following question based on the content of the article above:
{instruction}
"""

REREADING_SYSTEM_PROMPT = """You are a smart AI assistant. For a given question-answer pair, improve the answer by correcting errors, bolstering informativeness, aligning with the question, and providing comprehensive detail.

- Do not alter key information from the original text.
- Avoid using phrases like "based on the above article."
- Ensure your answers are derived from the background knowledge, detailed, and accurate.
- Answer the question thoroughly.

Please generate the rewritten answer following this format strictly:
Question: [question]
Answer: [detailed and accurate rewritten answer]
"""

REREADING_USER_PROMPT = """The background knowledge is:
{unsupervised_knowledge_data}

The question is:
{instruction}

The original answer is:
{output}

Please reread the background knowledge and generate a more detailed and accurate rewritten answer based on the content of the article above.
"""
