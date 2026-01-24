"""
Parallel execution utilities for batch processing.

Provides a simplified interface for parallel task execution using
ThreadPoolExecutor with progress tracking.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Any, Optional
from tqdm import tqdm


def execute_parallel(
    func: Callable,
    tasks: List[Any],
    max_workers: int = 96,
    description: str = "Processing",
    maintain_order: bool = True,
    show_progress: bool = True
) -> List[Any]:
    """
    Execute tasks in parallel using ThreadPoolExecutor.

    Args:
        func: Function to apply to each task
        tasks: List of tasks (each task is passed to func)
        max_workers: Maximum number of parallel workers
        description: Description for progress bar
        maintain_order: If True, results maintain input order (slower).
                       If False, results are in completion order (faster).
        show_progress: Whether to show progress bar

    Returns:
        List of results in the same order as tasks (if maintain_order=True)
        or in completion order (if maintain_order=False)

    Examples:
        >>> def square(x): return x * x
        >>> results = execute_parallel(square, [1, 2, 3, 4], max_workers=2)
        >>> results
        [1, 4, 9, 16]
    """
    if not tasks:
        return []

    results: List[Any] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        if maintain_order:
            # Submit tasks and maintain order using indices
            future_to_index = {
                executor.submit(func, task): i
                for i, task in enumerate(tasks)
            }

            # Initialize results list with None placeholders
            results = [None] * len(tasks)

            # Collect results as they complete
            iterator = as_completed(future_to_index)
            if show_progress:
                iterator = tqdm(iterator, total=len(tasks), desc=description)

            for future in iterator:
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    # Store exception or None for failed tasks
                    results[index] = None
                    if show_progress:
                        tqdm.write(f"Task {index} failed: {str(e)}")

        else:
            # Submit all tasks without tracking order
            futures = [executor.submit(func, task) for task in tasks]

            # Collect results in completion order
            iterator = as_completed(futures)
            if show_progress:
                iterator = tqdm(iterator, total=len(tasks), desc=description)

            for future in iterator:
                try:
                    results.append(future.result())
                except Exception as e:
                    # Skip or store None for failed tasks
                    if show_progress:
                        tqdm.write(f"Task failed: {str(e)}")

    return results
