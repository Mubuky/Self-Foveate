"""
OpenAI API client with retry logic for the Self-Foveate framework.

Supports multiple providers via environment variable configuration:
- OPENAI_API_KEY: API key for chat model (required)
- OPENAI_BASE_URL: Base URL for API (default: https://api.openai.com/v1)
- OPENAI_MODEL: Model name (default: gpt-4o-mini)
- EMBEDDING_API_KEY: API key for embedding model (defaults to OPENAI_API_KEY)
- EMBEDDING_BASE_URL: Base URL for embedding API (defaults to OPENAI_BASE_URL)
- EMBEDDING_MODEL: Embedding model name (default: text-embedding-3-small)
"""

import logging
import os
from openai import OpenAI
from typing import List, Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential


chat_model_config = {
    "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    "api_key": os.getenv("OPENAI_API_KEY"),
    "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
}

embedding_model_config = {
    "model": os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
    "api_key": os.getenv("EMBEDDING_API_KEY", os.getenv("OPENAI_API_KEY")),
    "base_url": os.getenv("EMBEDDING_BASE_URL", os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
}

if not chat_model_config["api_key"]:
    raise ValueError("OPENAI_API_KEY environment variable is required")

request_params = {
    "default": {
        "temperature": 1.0,
        "max_tokens": None,
        "frequency_penalty": 0.5
    },
    "instruction_generation": {
        "temperature": 1.0,
        "max_tokens": None,
        "frequency_penalty": 0.5
    },
    "regeneration": {
        "temperature": 1.0,
        "max_tokens": None,
        "frequency_penalty": 0.5
    },
    "baseline_self_qa": {
        "temperature": 0.7,
        "max_tokens": None,
        "frequency_penalty": 0.0
    }
}

chat_client: OpenAI = OpenAI(
    api_key=chat_model_config['api_key'],
    base_url=chat_model_config['base_url'],
)

embedding_client: OpenAI = OpenAI(
    api_key=embedding_model_config['api_key'],
    base_url=embedding_model_config['base_url'],
)


@retry(stop=stop_after_attempt(7), wait=wait_exponential(multiplier=8, min=1, max=64))
def make_requests(system_prompt: str, user_prompt: str, params_key: str, few_shot_examples: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Make a request to the OpenAI API with retry logic.

    Args:
        system_prompt: The system prompt to use
        user_prompt: The user prompt to use
        params_key: Key to look up request parameters
        few_shot_examples: Optional few-shot examples for the request

    Returns:
        The response content from the API
    """
    try:
        if system_prompt:
            messages: List[Dict[str, str]] = [
                {"role": "system", "content": system_prompt},
            ]
        else:
            messages: List[Dict[str, str]] = []

        if few_shot_examples:
            for example in few_shot_examples:
                messages.extend([
                    {"role": "user", "content": example["user"]},
                    {"role": "assistant", "content": example["assistant"]}
                ])
        messages.append({"role": "user", "content": user_prompt})

        params: Dict[str, Any] = request_params.get(params_key, request_params["default"])
        try:
            response = chat_client.chat.completions.create(
                model=chat_model_config['model'],
                messages=messages,
                temperature=params['temperature'],
                max_tokens=params['max_tokens'],
                frequency_penalty=params['frequency_penalty'],
                stream=False,
            )
            return response.choices[0].message.content
        except Exception as e:
            error_str = str(e)
            print(error_str)
            if "rate_limit_exceeded" in error_str:
                if "RPM" in error_str:
                    logging.warning("Rate limit exceeded (RPM) - Requests per minute limit reached")
                elif "TPM" in error_str:
                    logging.warning("Rate limit exceeded (TPM) - Tokens per minute limit reached")
            raise
    except Exception as e:
        logging.error(f"Error in make_requests: {str(e)}")
        raise


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=16, min=1, max=300))
def get_embedding(text: str) -> List[float]:
    """
    Get the embedding of a text.

    Args:
        text: The text to embed

    Returns:
        The embedding vector as a list of floats
    """
    try:
        response = embedding_client.embeddings.create(
            model=embedding_model_config['model'],
            input=text,
            encoding_format="float"
        )
        return response.data[0].embedding
    except Exception as e:
        logging.error(f"Error in get_embedding: {str(e)}")
        raise
