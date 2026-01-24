"""Difficulty comparison evaluation for instruction sets."""

import argparse
import json
import os
import random

import pandas as pd

from shared.api_client import APIClient, APIClientConfig
from shared.parallel_executor import execute_parallel
from shared.path_utils import get_output_path


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Compare difficulty of baseline vs method-generated instructions"
    )
    parser.add_argument(
        "--baseline_path", type=str, required=True,
        help="Baseline instruction data (JSONL)"
    )
    parser.add_argument(
        "--method_path", type=str, required=True,
        help="Method instruction data (JSONL)"
    )
    parser.add_argument(
        "--input_path", type=str, required=True,
        help="Input content data (JSONL)"
    )
    parser.add_argument(
        "--output_dir", type=str, default="./data/output_data",
        help="Base output directory"
    )
    return parser.parse_args()


def create_api_client() -> APIClient:
    """Create API client from environment variables."""
    try:
        config = APIClientConfig.from_env(
            prefix="OPENAI",
            defaults={"model": "gpt-4o", "base_url": "https://api.openai.com/v1"}
        )
        return APIClient(config)
    except ValueError as e:
        print(f"\nERROR: {e}")
        print("\nRequired environment variables:")
        print("  OPENAI_API_KEY - API key for difficulty evaluation")
        print("  OPENAI_MODEL - (optional) Model name, default: gpt-4o")
        print("  OPENAI_BASE_URL - (optional) Base URL, default: https://api.openai.com/v1")
        exit(1)


# Module-level client initialized in main()
api_client: APIClient = None


COMPARISON_SYSTEM_PROMPT = """Please compare two sets of instructions/questions for a given content to determine which set is more difficult for a language model to generate coherent and accurate responses. A set of instructions is considered more difficult if it requires:
1. More complex reasoning or multi-step analysis
2. Integration of multiple concepts or contexts
3. Explanation of nuanced relationships or processes
4. Handling of ambiguous or less-documented information
5. Synthesis of information from diverse sources or time periods

Please respond with '1' if the first set of instructions is more difficult, or '2' if the second set of instructions is more difficult.
Please respond with the number only, no other text or characters."""


def process_article_instructions(args: tuple) -> dict:
    """Process a single article's instruction comparison."""
    article_idx, content, baseline_insts, method_insts = args

    instruction_sets = [("baseline", baseline_insts), ("method", method_insts)]
    random.shuffle(instruction_sets)

    user_prompt = (
        f"Content: {content}\n"
        f"Instruction Set 1: {'; '.join(instruction_sets[0][1])}\n"
        f"Instruction Set 2: {'; '.join(instruction_sets[1][1])}\n"
    )

    winner = None
    try:
        comparison = api_client.make_request(
            system_prompt=COMPARISON_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.5,
            max_tokens=256
        ).strip()

        if comparison == "1":
            winner = instruction_sets[0][0]
        elif comparison == "2":
            winner = instruction_sets[1][0]
        else:
            print(f"Invalid comparison output for article {article_idx}: {comparison}")
    except Exception as e:
        print(f"Error processing article_index {article_idx}: {e}")

    return {
        "article_index": article_idx,
        "baseline_instructions": baseline_insts,
        "method_instructions": method_insts,
        "winner": winner,
    }


def group_instructions_by_article(data: pd.DataFrame) -> dict:
    """Group instructions by article index."""
    result = {}
    for inst, idx in zip(data['instruction'], data['article_index']):
        result.setdefault(idx, []).append(inst)
    return result


def main():
    global api_client
    args = parse_args()

    api_client = create_api_client()

    data_baseline = pd.read_json(args.baseline_path, orient='records', lines=True)
    data_method = pd.read_json(args.method_path, orient='records', lines=True)
    data_input = pd.read_json(args.input_path, orient='records', lines=True)

    baseline_dict = group_instructions_by_article(data_baseline)
    method_dict = group_instructions_by_article(data_method)

    tasks = []
    for article_idx, content in enumerate(data_input['content']):
        baseline_insts = baseline_dict.get(article_idx, [])
        method_insts = method_dict.get(article_idx, [])

        if not baseline_insts or not method_insts:
            print(f"Warning: Missing instructions for article_index {article_idx}. Skipping.")
            continue

        min_len = min(len(baseline_insts), len(method_insts))
        tasks.append((article_idx, content, baseline_insts[:min_len], method_insts[:min_len]))

    results = execute_parallel(
        func=process_article_instructions,
        tasks=tasks,
        max_workers=160,
        description="Processing Articles",
        maintain_order=False,
        show_progress=True
    )

    valid_results = [r for r in results if r is not None]
    baseline_wins = sum(1 for r in valid_results if r['winner'] == 'baseline')
    method_wins = sum(1 for r in valid_results if r['winner'] == 'method')
    total = len(valid_results)

    if total > 0:
        baseline_win_rate = (baseline_wins / total) * 100
        method_win_rate = (method_wins / total) * 100
        print(f"Baseline win-rate: {baseline_win_rate:.2f}%")
        print(f"Method win-rate: {method_win_rate:.2f}%")
    else:
        print("No comparisons were made.")
        baseline_win_rate = None
        method_win_rate = None

    win_rates = {
        "baseline_win_rate": baseline_win_rate,
        "method_win_rate": method_win_rate,
        "total": total if total > 0 else None,
        "baseline_wins": baseline_wins if total > 0 else None,
        "method_wins": method_wins if total > 0 else None
    }

    baseline_name = os.path.splitext(os.path.basename(args.baseline_path))[0]
    method_name = os.path.splitext(os.path.basename(args.method_path))[0]
    output_filename = f"{baseline_name}_vs_{method_name}.json"

    output_path = get_output_path(args.output_dir, output_filename, "Difficulty", True)
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump({
            "win_rates": win_rates,
            "results": valid_results
        }, f, ensure_ascii=False, indent=2)

    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
