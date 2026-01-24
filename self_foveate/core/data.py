"""
Data loading and saving utilities for the Self-Foveate framework.

Supports CSV, JSON, and JSONL file formats.
"""

import os
import logging
import pandas as pd
from typing import List, Dict


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load data from a CSV or JSON file.

    Args:
        file_path: Path to the CSV or JSON file.

    Returns:
        Loaded data as a pandas DataFrame.

    Raises:
        ValueError: If the file format is not supported.
        Exception: If there's an error during data loading.
    """
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == '.csv':
            data_df: pd.DataFrame = pd.read_csv(file_path)
        elif file_extension in ['.json', '.jsonl']:
            data_df: pd.DataFrame = pd.read_json(file_path, orient='records', lines=True)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

        logging.info(f"Loaded {len(data_df)} records.")
        return data_df
    except Exception as e:
        logging.error(f"Error loading data ({file_path}): {str(e)}")
        raise


def save_seed_tasks(seed_tasks: List[Dict[str, str]], file_path: str) -> None:
    """
    Save seed tasks to a file.

    Args:
        seed_tasks: The list of seed tasks to save.
        file_path: The path to save the seed tasks.

    Raises:
        ValueError: If the file format is not supported.
        Exception: If there's an error during the saving process.
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        save_df: pd.DataFrame = pd.DataFrame(seed_tasks)
        file_extension: str = os.path.splitext(file_path)[1].lower()

        if file_extension in ['.json', '.jsonl']:
            save_df.to_json(file_path, orient='records', lines=True, force_ascii=False)
        elif file_extension == '.csv':
            save_df.to_csv(file_path, index=False, encoding='utf-8')
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

        logging.info(f"Saved {len(seed_tasks)} seed tasks to {file_path}.")
    except Exception as e:
        logging.error(f"Error saving seed tasks: {str(e)}")
        raise
