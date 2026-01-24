"""
Prompts for the Macro (sentence-level) foveation strategy.

This module contains prompts for extracting complete sentences and generating
instructions based on those sentences.
"""

MACRO_KEYWORDS_SYSTEM_PROMPT = """You are a professional text analysis expert. Your task is to extract sentences from the given article.

Based on the following article, please extract {num_macro} semantically different key sentences in random order, with:

Please ensure:
1. All key sentences are based on the article content.
2. Each key sentence is unique to maintain diversity.
3. Key sentences should focus on identifying key details, focusing on transitions, quotations, comparisons, and rhetorical devices.
4. Key sentences should cover the main entities in the text and their related attributes or related entities.
5. Output strictly follows the format below without any other text:
1. key sentence1
2. key sentence2
...
"""

MACRO_KEYWORDS_USER_PROMPT = """Article content:
{content}
"""

MACRO_GENERATION_SYSTEM_PROMPT = """You are an excellent questions/instructions generation expert. Your task is to generate {num_macro} questions/instructions based on the given background knowledge and key sentences.

Based on the following background knowledge and key sentences, please generate one question/instruction for each key sentence.

Requirements:
1. Each generated question/instruction must use the corresponding key sentence.
2. Questions/instructions must be based on the background knowledge content.
3. Each question/instruction should focus on different aspects or information from the background knowledge.
4. Output strictly follows JSON format as shown below without any other text:
{json_data}
"""

MACRO_GENERATION_USER_PROMPT = """The background knowledge is:
{content}

The key sentences are:
{sentences}

Please generate {num_macro} questions/instructions based on the background knowledge and key sentences above.
"""

MACRO_REGENERATION_SYSTEM_PROMPT = """You are an excellent questions/instructions generation expert. Your task is to generate one question/instruction for the target key sentence.

Based on the following background knowledge and key sentences, please generate one question/instruction for the target key sentence.

Requirements:
1. The generated question/instruction must use the corresponding key sentence.
2. The question/instruction must be based on the background knowledge content.
3. The question/instruction should be fully answerable using only the background knowledge.
4. Output the generated question/instruction only without any other text.
"""

MACRO_REGENERATION_USER_PROMPT = """The background knowledge is:
{content}

The target key sentence to use:
{sentence}
"""
