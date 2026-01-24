"""
Base class for all foveation strategies.

This module implements the Template Method pattern to eliminate code duplication
across macro, micro, and scatter foveation modules. Common logic for retry,
validation, and task processing is centralized here.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Callable, Optional

from self_foveate.utils.task_generation import process_task_generation


class BaseFoveator(ABC):
    """
    Abstract base class for all foveation strategies.

    This class defines the common workflow for processing articles:
    1. Extract features (keywords/words/sentences) with retry logic
    2. Generate instructions with retry logic
    3. Process task generation with regeneration for failed tasks

    Subclasses must implement abstract methods to provide strategy-specific behavior.
    """

    @abstractmethod
    def get_level_name(self) -> str:
        """
        Return the name of this foveation level (Macro/Micro/Scatter).

        Returns:
            str: The level name for logging purposes
        """
        pass

    @abstractmethod
    def extract_features(self, content: str, num_items: int, **kwargs) -> List[Any]:
        """
        Extract features from content (keywords/words/sentences).

        Args:
            content: The article content to extract features from
            num_items: Number of features to extract
            **kwargs: Additional strategy-specific parameters

        Returns:
            List of extracted features (format depends on strategy)
        """
        pass

    @abstractmethod
    def generate_instructions(self, content: str, features: List[Any], num_items: int) -> List[str]:
        """
        Generate instructions based on content and extracted features.

        Args:
            content: The article content
            features: Extracted features from extract_features()
            num_items: Number of instructions to generate

        Returns:
            List of generated instructions
        """
        pass

    @abstractmethod
    def regenerate_instruction(
        self,
        content: str,
        instructions: List[str],
        features: List[Any],
        generated_idxs: List[int],
        target_idx: int
    ) -> str:
        """
        Regenerate a single failed instruction using successful examples.

        Args:
            content: The article content
            instructions: Current list of instructions
            features: Extracted features
            generated_idxs: Indices of successfully generated instructions
            target_idx: Index of the instruction to regenerate

        Returns:
            Regenerated instruction string
        """
        pass

    @abstractmethod
    def validate_features(self, features: List[Any], expected_count: int) -> bool:
        """
        Validate that extracted features meet requirements.

        Args:
            features: Extracted features to validate
            expected_count: Expected number of features

        Returns:
            True if features are valid, False otherwise
        """
        pass

    def _retry_with_validation(
        self,
        operation: Callable[[], Any],
        validation: Callable[[Any], bool],
        max_retries: int,
        error_msg: str,
        retry_msg: str
    ) -> Optional[Any]:
        """
        Execute an operation with retry logic and validation.

        This method encapsulates the common retry pattern used throughout
        the foveation modules, reducing code duplication.

        Args:
            operation: Function to execute (should return the result to validate)
            validation: Function to validate the result (returns bool)
            max_retries: Maximum number of retry attempts
            error_msg: Error message prefix for final failure
            retry_msg: Warning message prefix for retry attempts

        Returns:
            The validated result, or None if all retries failed
        """
        retry_count = 0
        while retry_count < max_retries:
            try:
                result = operation()
                if validation(result):
                    return result
                else:
                    raise ValueError("Validation failed")
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    logging.error(f"{error_msg}: {str(e)}")
                    return None
                logging.warning(f"{retry_msg} (attempt {retry_count}/{max_retries}): {str(e)}")
                continue
        return None

    def _extract_features_with_retry(
        self,
        content: str,
        num_items: int,
        max_retries: int,
        idx: int,
        **kwargs
    ) -> Optional[List[Any]]:
        """
        Extract features with retry logic.

        Args:
            content: Article content
            num_items: Number of features to extract
            max_retries: Maximum retry attempts
            idx: Article index (for logging)
            **kwargs: Strategy-specific parameters

        Returns:
            Extracted features or None if failed
        """
        level = self.get_level_name()

        def operation():
            return self.extract_features(content, num_items, **kwargs)

        def validation(features):
            return self.validate_features(features, num_items)

        features = self._retry_with_validation(
            operation=operation,
            validation=validation,
            max_retries=max_retries,
            error_msg=f"Failed to generate {level.lower()} features after {max_retries} attempts for article {idx + 1}",
            retry_msg=f"Retry for {level.lower()} features generation"
        )

        if features:
            logging.info(f"{level} Keywords for article {idx + 1}: {features}")

        return features

    def _generate_instructions_with_retry(
        self,
        content: str,
        features: List[Any],
        num_items: int,
        max_retries: int,
        idx: int
    ) -> Optional[List[str]]:
        """
        Generate instructions with retry logic.

        Args:
            content: Article content
            features: Extracted features
            num_items: Number of instructions to generate
            max_retries: Maximum retry attempts
            idx: Article index (for logging)

        Returns:
            Generated instructions or None if failed
        """
        level = self.get_level_name()

        def operation():
            return self.generate_instructions(content, features, num_items)

        def validation(instructions):
            return instructions and len(instructions) == num_items

        instructions = self._retry_with_validation(
            operation=operation,
            validation=validation,
            max_retries=max_retries,
            error_msg=f"Failed to generate {level.lower()} instructions after {max_retries} attempts for article {idx + 1}",
            retry_msg=f"Retry for {level.lower()} instruction generation"
        )

        if instructions:
            logging.info(f"{level} Instructions for article {idx + 1}: {instructions}")

        return instructions

    def _process_tasks_with_regeneration(
        self,
        content: str,
        instructions: List[str],
        features: List[Any],
        max_retries: int,
        idx: int
    ) -> List[Dict[str, str]]:
        """
        Process task generation with regeneration for failed tasks.

        This implements the common pattern of:
        1. First pass: try to generate tasks for all instructions
        2. Retry loop: regenerate instructions for failed tasks

        Args:
            content: Article content
            instructions: Generated instructions
            features: Extracted features
            max_retries: Maximum retry attempts for regeneration
            idx: Article index (for logging)

        Returns:
            List of successfully generated seed tasks
        """
        level = self.get_level_name()
        generated_idxs: List[int] = []
        ungenerated_idxs: List[int] = []
        generated_seed_tasks: List[Dict[str, str]] = []

        # First pass generation
        for feature_idx, instruction in enumerate(instructions):
            generated_task, instruction = process_task_generation(content, instruction, idx)

            if generated_task:
                generated_idxs.append(feature_idx)
                instructions[feature_idx] = instruction
                generated_seed_tasks.append(generated_task)
            else:
                ungenerated_idxs.append(feature_idx)

        # Retry failed generations with limit
        retry_count = 0
        while ungenerated_idxs and retry_count < max_retries:
            retry_count += 1
            remaining_idxs = ungenerated_idxs.copy()
            ungenerated_idxs = []

            for feature_idx in remaining_idxs:
                instruction = self.regenerate_instruction(
                    content, instructions, features, generated_idxs, feature_idx
                )
                generated_task, instruction = process_task_generation(content, instruction, idx)

                if generated_task:
                    generated_idxs.append(feature_idx)
                    instructions[feature_idx] = instruction
                    generated_seed_tasks.append(generated_task)
                else:
                    ungenerated_idxs.append(feature_idx)

        if ungenerated_idxs:
            logging.warning(
                f"{level} Article {idx + 1} has {len(ungenerated_idxs)} "
                f"failed generations after {max_retries} retries"
            )

        logging.info(f"{level} Article {idx + 1} final tasks: {len(generated_seed_tasks)}")
        return generated_seed_tasks

    def process_article(
        self,
        data_tuple: Tuple[int, Any],
        num_items: int,
        max_retries: int,
        **kwargs
    ) -> List[Dict[str, str]]:
        """
        Template method: process a single article through the complete pipeline.

        This defines the overall workflow that all strategies follow:
        1. Extract features with retry
        2. Generate instructions with retry
        3. Process tasks with regeneration

        Args:
            data_tuple: Tuple of (index, article_data)
            num_items: Number of items to generate
            max_retries: Maximum retry attempts
            **kwargs: Strategy-specific parameters

        Returns:
            List of generated seed tasks
        """
        idx, data = data_tuple
        content = data.content
        level = self.get_level_name()

        logging.info(f"{level} Processing article {idx + 1}: {content}")

        # Step 1: Extract features with retry
        features = self._extract_features_with_retry(
            content, num_items, max_retries, idx, **kwargs
        )
        if not features:
            return []

        # Step 2: Generate instructions with retry
        instructions = self._generate_instructions_with_retry(
            content, features, num_items, max_retries, idx
        )
        if not instructions:
            return []

        # Step 3: Process task generation with regeneration
        seed_tasks = self._process_tasks_with_regeneration(
            content, instructions, features, max_retries, idx
        )

        return seed_tasks
