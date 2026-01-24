"""
Prompts for the Micro (word-level) foveation strategy.

This module contains prompts for extracting individual words and generating
instructions based on those words.
"""

MICRO_KEYWORDS_SYSTEM_PROMPT = """You are a professional text analysis expert. Your task is to extract keywords from the given article.

Based on the following article, please extract {num_micro} semantically different keywords in random order, with:

Please ensure:
1. All keywords are based on the article content.
2. Each keyword is unique to maintain diversity.
3. Keywords can be single words or meaningful phrases.
4. Keywords should cover the main entities in the text and their related attributes or related entities.
5. Output strictly follows the format below without any other text:
1. keyword1
2. keyword2
...
"""

MICRO_KEYWORDS_USER_PROMPT = """Article content:
{content}
"""

MICRO_GENERATION_SYSTEM_PROMPT = """You are an excellent questions/instructions generation expert. Your task is to generate {num_micro} questions/instructions based on the given background knowledge and answers.

Based on the following background knowledge and answers, please generate one question/instruction for each answer.

Requirements:
1. Each generated question must be answerable by its corresponding answer
2. Questions/instructions must be based on the background knowledge content
3. Each question/instruction should focus on different aspects or information from the background knowledge
4. Output strictly follows JSON format as shown below without any other text:
{json_data}
"""

MICRO_GENERATION_USER_PROMPT = """The background knowledge is:
{content}

The answers are:
{answers}

Please generate {num_micro} questions/instructions based on the background knowledge and answers above.
"""

MICRO_REGENERATION_SYSTEM_PROMPT = """You are an excellent questions/instructions generation expert. Your task is to generate one question/instruction for the target answer.

Based on the following background knowledge and answers, please generate one question/instruction for the target answer.

Requirements:
1. The generated question/instruction must be answerable by its corresponding answer.
2. The question/instruction must be based on the background knowledge content.
3. The question/instruction should be fully answerable using only the background knowledge.
4. Output the generated question/instruction only without any other text.
"""

MICRO_REGENERATION_USER_PROMPT = """The background knowledge is:
{content}

The target answer is:
{answer}
"""
