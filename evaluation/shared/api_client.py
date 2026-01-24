"""
Unified API client for evaluation utilities.

Provides OpenAI-compatible API clients with retry logic and environment variable
configuration. Supports multiple API providers via base_url configuration.
"""

import logging
import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass
class APIClientConfig:
    """Configuration for an API client."""
    model: str
    api_key: str
    base_url: str

    @classmethod
    def from_env(cls, prefix: str = "OPENAI", defaults: Optional[Dict[str, str]] = None) -> "APIClientConfig":
        """
        Load configuration from environment variables.

        Args:
            prefix: Environment variable prefix (e.g., "OPENAI", "INFERENCE", "EMBEDDING")
            defaults: Optional default values for model and base_url

        Returns:
            APIClientConfig instance

        Raises:
            ValueError: If required API key is missing
        """
        defaults = defaults or {}

        api_key = os.getenv(f"{prefix}_API_KEY")
        if not api_key:
            raise ValueError(
                f"{prefix}_API_KEY environment variable is required. "
                f"Please set it in your .env file or environment."
            )

        model = os.getenv(f"{prefix}_MODEL", defaults.get("model", "gpt-4o-mini"))
        base_url = os.getenv(f"{prefix}_BASE_URL", defaults.get("base_url", "https://api.openai.com/v1"))

        return cls(model=model, api_key=api_key, base_url=base_url)


class APIClient:
    """
    Unified API client with retry logic for evaluation tasks.

    Supports inference and evaluation modes with different parameter configurations.
    """

    def __init__(self, config: APIClientConfig):
        """
        Initialize API client with configuration.

        Args:
            config: APIClientConfig instance
        """
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
        self.logger = logging.getLogger(__name__)

    @retry(stop=stop_after_attempt(7), wait=wait_exponential(multiplier=8, min=1, max=64))
    def make_request(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        extra_body: Optional[Dict[str, Any]] = None,
        few_shot_examples: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Make a request to the API with retry logic.

        Args:
            system_prompt: System prompt (can be empty string)
            user_prompt: User prompt
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty (-2 to 2)
            extra_body: Additional parameters (e.g., repetition_penalty)
            few_shot_examples: Optional list of few-shot examples

        Returns:
            Generated text response

        Raises:
            Exception: If API request fails after retries
        """
        try:
            # Build messages
            messages: List[Dict[str, str]] = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            # Add few-shot examples if provided
            if few_shot_examples:
                for example in few_shot_examples:
                    messages.extend([
                        {"role": "user", "content": example["user"]},
                        {"role": "assistant", "content": example["assistant"]}
                    ])

            messages.append({"role": "user", "content": user_prompt})

            # Make request
            kwargs: Dict[str, Any] = {
                "model": self.config.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
                "frequency_penalty": frequency_penalty,
                "stream": False
            }

            if extra_body:
                kwargs["extra_body"] = extra_body

            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content

        except Exception as e:
            error_str = str(e)
            self.logger.error(f"API request failed: {error_str}")

            # Log rate limit details
            if "rate_limit_exceeded" in error_str:
                if "RPM" in error_str:
                    self.logger.warning("Rate limit exceeded (RPM) - Requests per minute limit reached")
                elif "TPM" in error_str:
                    self.logger.warning("Rate limit exceeded (TPM) - Tokens per minute limit reached")

            raise

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=16, min=1, max=300))
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a text.

        Args:
            text: Input text

        Returns:
            Embedding vector as list of floats

        Raises:
            Exception: If embedding request fails after retries
        """
        try:
            response = self.client.embeddings.create(
                model=self.config.model,
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            self.logger.error(f"Error getting embedding: {str(e)}")
            raise
