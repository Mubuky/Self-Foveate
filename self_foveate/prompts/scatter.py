"""
Prompts for the Scatter (multi-keyword combination) foveation strategy.

This module contains prompts for extracting keywords and generating instructions
based on multiple keyword groups (1, 2, or 3 keywords per group).
"""

SCATTER_IMPORTANT_SYSTEM_PROMPT = """You are a professional text analysis expert. Your task is to identify the most important keywords from the given background knowledge.

Please analyze the given keywords and select:
1. {num_core} core keywords that are absolutely critical (primary keywords)
2. {num_major} major keywords that are highly important but secondary (secondary keywords)

For selecting the core keyword (select exactly {num_core}):
- Must be the most essential concept that captures the central theme
- Should be impossible to understand the text without this keyword
- Removing this keyword would make the text lose its main focus

For selecting major keywords (select exactly {num_major}):
- Should be key supporting concepts that elaborate on the core keyword
- Must be directly relevant to explaining or contextualizing the main topic
- Should cover different important aspects of the content

Please output strictly in this format without any other text:
Core keyword:
1. [first core keyword]
2. [second core keyword]
...

Major keywords:
1. [first major keyword]
2. [second major keyword]
...
"""

SCATTER_IMPORTANT_USER_PROMPT = """Background knowledge:
{content}

Keywords:
{keywords}
"""

SCATTER_KEYWORDS_SYSTEM_PROMPT = """You are a professional text analysis expert. Your task is to extract keywords from the given article.

Based on the following article, please extract {num_keywords} semantically different keywords in random order, with:

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

SCATTER_KEYWORDS_USER_PROMPT = """Article content:
{content}
"""

SCATTER_GENERATION_SYSTEM_PROMPT = """You are an excellent questions/instructions generation expert. Your task is to generate {num_scatter} questions/instructions based on the given background knowledge and keyword groups.

Based on the following background knowledge and keyword groups, please generate one question/instruction for each keyword group that incorporates ALL keywords from that group.

Requirements:
1. Each generated question/instruction must use ALL keywords from its corresponding group
2. Questions/instructions must be based on the background knowledge content
3. Each question/instruction should focus on different aspects or information from the background knowledge
4. Output strictly follows JSON format as shown below without any other text:
{json_data}
"""

SCATTER_GENERATION_USER_PROMPT = """The background knowledge is:
{content}

The keyword groups are:
{keyword_groups}

Please generate {num_scatter} questions/instructions based on the background knowledge and keyword groups above.
"""

SCATTER_REGENERATION_SYSTEM_PROMPT = """You are an excellent questions/instructions generation expert. Your task is to generate one question/instruction for the target keyword group that incorporates ALL keywords from that group.

Based on the following background knowledge and keyword groups, please generate one question/instruction for the target keyword group that incorporates ALL keywords from that group.

Requirements:
1. The generated question/instruction must use ALL keywords from its corresponding group.
2. The question/instruction must be based on the background knowledge content.
3. The question/instruction should be fully answerable using only the background knowledge.
4. Output the generated question/instruction only without any other text.
"""

SCATTER_REGENERATION_USER_PROMPT = """The background knowledge is:
{content}

The target keyword group to use:
{keyword_group}
"""
