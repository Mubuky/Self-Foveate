"""
Path management utilities for evaluation scripts.

Provides consistent path handling and output directory management
across all evaluation utilities.
"""

import os
from pathlib import Path
from typing import Optional


def ensure_output_dir(path: str) -> str:
    """
    Ensure output directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure exists

    Returns:
        The same path (for chaining)

    Examples:
        >>> output_dir = ensure_output_dir("./output/results")
        >>> os.path.exists(output_dir)
        True
    """
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def get_output_path(
    base_dir: str,
    filename: str,
    subdir: Optional[str] = None,
    create_dir: bool = True
) -> str:
    """
    Construct output file path with optional subdirectory.

    Args:
        base_dir: Base output directory
        filename: Output filename
        subdir: Optional subdirectory within base_dir
        create_dir: Whether to create directory if it doesn't exist

    Returns:
        Full path to output file

    Examples:
        >>> path = get_output_path("./output", "results.json")
        >>> path
        './output/results.json'
        >>> path = get_output_path("./output", "data.json", subdir="diversity")
        >>> path
        './output/diversity/data.json'
    """
    if subdir:
        output_dir = os.path.join(base_dir, subdir)
    else:
        output_dir = base_dir

    if create_dir:
        ensure_output_dir(output_dir)

    return os.path.join(output_dir, filename)


def get_project_root() -> str:
    """
    Get the project root directory.

    Returns:
        Absolute path to project root directory
    """
    # Assume utils/shared is 2 levels deep from project root
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    return str(project_root)


def resolve_data_path(relative_path: str) -> str:
    """
    Resolve a relative data path to absolute path from project root.

    Args:
        relative_path: Relative path from project root (e.g., "./data/output_data/xxx.json")

    Returns:
        Absolute path

    Examples:
        >>> path = resolve_data_path("./data/input.json")
        >>> os.path.isabs(path)
        True
    """
    if os.path.isabs(relative_path):
        return relative_path

    project_root = get_project_root()
    return os.path.join(project_root, relative_path.lstrip("./"))
