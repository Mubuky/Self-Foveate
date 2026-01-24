"""
Model evaluation pipeline with inference, traditional metrics, and LLM-based evaluation.

Supports multi-round evaluation with resume capability and comprehensive statistics.
All API credentials are loaded from environment variables for security.
"""

import os
import json
import argparse
import pandas as pd
from tqdm import tqdm
from typing import Dict, Any, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt, wait_exponential
import statistics

# Import shared utilities
from shared.api_client import APIClient, APIClientConfig
from shared.text_processing import normalize_answer, tokenize
from shared.evaluation_metrics import calculate_batch_metrics, calculate_macro_metrics
from shared.path_utils import ensure_output_dir


# Initialize API clients from environment variables
try:
    # Inference client (the model being tested, typically local vLLM)
    inference_config = APIClientConfig.from_env(
        prefix="INFERENCE",
        defaults={"model": "Model", "base_url": "http://localhost:55755/v1"}
    )
    inference_client = APIClient(inference_config)

    # Evaluation client (for LLM-based judging)
    evaluation_config = APIClientConfig.from_env(
        prefix="OPENAI",
        defaults={"model": "gpt-4o-mini", "base_url": "https://api.openai.com/v1"}
    )
    evaluation_client = APIClient(evaluation_config)

except ValueError as e:
    print(f"\nERROR: {e}")
    print("\nRequired environment variables:")
    print("  INFERENCE_API_KEY - API key for inference model (use 'EMPTY' for local vLLM)")
    print("  INFERENCE_MODEL - Model name for inference")
    print("  INFERENCE_BASE_URL - Base URL for inference API")
    print("  OPENAI_API_KEY - API key for evaluation model")
    print("\nPlease set these in your .env file or environment.")
    exit(1)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Multi-round model evaluation with inference, traditional metrics, and LLM judging"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="The dataset name to evaluate (e.g., SQuAD_2.5k)",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Directory name for output files (created under data/output_data/ModelEvaluation/)",
    )
    parser.add_argument(
        "--num_round",
        type=int,
        default=5,
        help="The number of evaluation rounds to run",
    )
    return parser.parse_args()


def make_inference_requests(system_prompt: str, user_prompt: str) -> str:
    """
    Make inference request to the model being tested.

    Args:
        system_prompt: System prompt (can be empty)
        user_prompt: User prompt with the question

    Returns:
        Model's generated response
    """
    return inference_client.make_request(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.5,
        top_p=0.95,
        max_tokens=256,
        extra_body={"repetition_penalty": 1.02}
    )


@retry(stop=stop_after_attempt(7), wait=wait_exponential(multiplier=4, min=1, max=64))
def make_evaluation_requests(system_prompt: str, user_prompt: str) -> str:
    """
    Make evaluation request to the LLM judge.

    Args:
        system_prompt: System prompt for the judge
        user_prompt: Evaluation prompt with question and answers

    Returns:
        Judge's verdict (should contain 'Correct' or 'Incorrect')
    """
    return evaluation_client.make_request(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0,
        max_tokens=10,
        top_p=1.0
    )


def evaluate_single_sample(args: Tuple[str, str, str]) -> bool:
    """
    Evaluate a single sample using LLM judge.

    Args:
        args: Tuple of (question, generated_answer, ground_truth)

    Returns:
        True if the answer is judged correct, False otherwise
    """
    question, generated, ground_truth = args

    system_prompt = """You are a fair judge. Your task is to determine if the generated answer correctly answers the question, even if it contains additional explanations.
Rules:
1. The generated answer is correct if it contains the key information from the ground truth
2. Additional explanations or context in the generated answer should not make it incorrect
3. Only respond with 'Correct' or 'Incorrect'"""

    user_prompt = f"""Compare the following answers:
Question: {question}
Ground Truth Answer: {ground_truth}
Generated Answer: {generated}

Is the generated answer correct, regardless of any additional explanation? Respond only with 'Correct' or 'Incorrect'."""

    try:
        result = make_evaluation_requests(system_prompt, user_prompt)
        return "Correct" in result
    except Exception as e:
        print(f"Error occurred with question: {question}")
        return False


def calculate_average_results(all_results: List[Dict]) -> Dict:
    """
    Calculate average results across multiple rounds.

    Args:
        all_results: List of result dictionaries from each round

    Returns:
        Dictionary with averaged traditional and LLM metrics
    """
    avg_traditional = {
        "macro_precision": sum(r["traditional"]["macro_precision"] for r in all_results) / len(all_results),
        "macro_recall": sum(r["traditional"]["macro_recall"] for r in all_results) / len(all_results),
        "macro_f1": sum(r["traditional"]["macro_f1"] for r in all_results) / len(all_results)
    }

    avg_llm = {
        "acc": sum(r["llm"]["acc"] for r in all_results) / len(all_results),
        "correct_count": sum(r["llm"]["correct_count"] for r in all_results) / len(all_results),
        "total_count": all_results[0]["llm"]["total_count"]  # Should be same for all rounds
    }

    return {"traditional": avg_traditional, "llm": avg_llm}


def calculate_statistics_results(all_results: List[Dict]) -> Dict:
    """
    Calculate extended statistics (mean and standard deviation) for each metric
    across evaluation rounds. These statistics can be used to plot error bands.

    Args:
        all_results: List of result dictionaries from each round

    Returns:
        Dictionary with mean and std for each metric
    """
    def compute_stats(values: List[float]) -> Dict[str, float]:
        avg_val = sum(values) / len(values)
        std_val = statistics.stdev(values) if len(values) > 1 else 0.0
        return {"avg": avg_val, "std": std_val}

    stats_traditional = {
        "macro_precision": compute_stats([r["traditional"]["macro_precision"] for r in all_results]),
        "macro_recall": compute_stats([r["traditional"]["macro_recall"] for r in all_results]),
        "macro_f1": compute_stats([r["traditional"]["macro_f1"] for r in all_results]),
    }

    stats_llm = {
        "acc": compute_stats([r["llm"]["acc"] for r in all_results]),
        "correct_count": compute_stats([r["llm"]["correct_count"] for r in all_results]),
    }

    return {"traditional": stats_traditional, "llm": stats_llm}


def get_last_completed_round(output_dir: str) -> int:
    """
    Check the output directory to find the last completed round.

    Args:
        output_dir: Path to output directory

    Returns:
        Last completed round number (0-based), or -1 if no rounds found
    """
    last_round = -1
    while True:
        round_dir = os.path.join(output_dir, f"round_{last_round + 2}")
        if not os.path.exists(round_dir):
            break

        # Check if all required files exist and are non-empty
        required_files = [
            "inference_results.jsonl",
            "traditional_eval_results.json",
            "llm_eval_results.json"
        ]

        files_complete = all(
            os.path.exists(os.path.join(round_dir, f)) and
            os.path.getsize(os.path.join(round_dir, f)) > 0
            for f in required_files
        )

        if not files_complete:
            break

        last_round += 1

    return last_round


def main():
    """Main evaluation pipeline."""
    args = parse_args()
    args.input_path = f"data/input_data/{args.dataset}/qas.jsonl"
    args.output = os.path.join("./data/output_data/ModelEvaluation/", args.output)
    ensure_output_dir(args.output)

    # Check for existing evaluation rounds
    last_completed_round = get_last_completed_round(args.output)
    start_round = last_completed_round + 1

    if start_round > 0:
        print(f"Resuming evaluation from round {start_round + 1} (found {start_round} completed rounds)")
        # Load existing results
        avg_output_path = os.path.join(args.output, "average_results.json")
        if os.path.exists(avg_output_path):
            with open(avg_output_path, 'r') as f:
                existing_data = json.load(f)
                all_results = existing_data.get('round_results', [])
        else:
            all_results = []
    else:
        all_results = []

    for round_num in range(start_round, args.num_round):
        round_dir = os.path.join(args.output, f"round_{round_num + 1}")
        ensure_output_dir(round_dir)

        # Step 1: Inference
        print(f"Round {round_num + 1}/{args.num_round}: Step1-Running Inference...")
        inference_output_path = os.path.join(round_dir, "inference_results.jsonl")

        data = pd.read_json(args.input_path, orient='records', lines=True)
        instructions = data['instruction'].tolist()
        results = [None] * len(instructions)
        system_prompt = ""

        def process_instruction(args_tuple: Tuple[str, int]) -> Tuple[int, Dict]:
            instruction, index = args_tuple
            output = make_inference_requests(system_prompt, instruction)
            return index, {"instruction": instruction, "output": output}

        with ThreadPoolExecutor(max_workers=128) as executor:
            future_to_instruction = {
                executor.submit(process_instruction, (instruction, i)): i
                for i, instruction in enumerate(instructions)
            }
            for future in tqdm(as_completed(future_to_instruction), total=len(instructions), desc="Generating answers"):
                index, result = future.result()
                results[index] = result

        with open(inference_output_path, "w") as f:
            for record in results:
                json.dump(record, f)
                f.write('\n')

        # Step 2: Traditional Evaluation
        print(f"Round {round_num + 1}/{args.num_round}: Step2-Running Traditional Evaluation...")
        traditional_eval_output_path = os.path.join(round_dir, "traditional_eval_results.json")

        data_generated = pd.read_json(inference_output_path, orient='records', lines=True)
        data_ground_truth = pd.read_json(args.input_path, orient='records', lines=True)

        # Tokenize outputs and ground truths
        output_tokens = [tokenize(data) for data in data_generated['output'].tolist()]
        ground_truth_tokens = [tokenize(data) for data in data_ground_truth['output'].tolist()]

        # Calculate metrics using shared utility
        precision_scores, recall_scores, f1_scores = calculate_batch_metrics(
            ground_truth_tokens, output_tokens
        )

        # Calculate macro averages
        traditional_results = calculate_macro_metrics(precision_scores, recall_scores, f1_scores)

        with open(traditional_eval_output_path, "w") as f:
            json.dump(traditional_results, f, indent=2)

        # Step 3: LLM Evaluation
        print(f"Round {round_num + 1}/{args.num_round}: Step3-Running LLM Evaluation...")
        llm_eval_output_path = os.path.join(round_dir, "llm_eval_results.json")

        data_question = data_ground_truth['instruction'].tolist()
        data_generated = data_generated['output'].tolist()
        data_ground_truth_output = data_ground_truth['output'].tolist()

        correct_count = 0
        samples = list(zip(data_question, data_generated, data_ground_truth_output))
        detailed_results = [None] * len(samples)

        error_count = 0
        with ThreadPoolExecutor(max_workers=48) as executor:
            future_to_index = {
                executor.submit(evaluate_single_sample, sample): i
                for i, sample in enumerate(samples)
            }

            for future in tqdm(as_completed(future_to_index), total=len(samples), desc="Evaluating samples"):
                idx = future_to_index[future]
                sample = samples[idx]
                try:
                    is_correct = future.result()
                    if is_correct:
                        correct_count += 1
                except Exception as e:
                    print(f"Future execution failed for sample {idx}: {str(e)}")
                    is_correct = False
                    error_count += 1

                detailed_results[idx] = {
                    "question": sample[0],
                    "generated_answer": sample[1],
                    "ground_truth": sample[2],
                    "is_correct": is_correct
                }

        acc = correct_count / len(data_question)
        llm_results = {
            "acc": acc,
            "correct_count": correct_count,
            "total_count": len(data_question),
            "error_count": error_count,
            "detailed_results": detailed_results
        }

        with open(llm_eval_output_path, "w", encoding='utf-8') as f:
            json.dump(llm_results, f, indent=2, ensure_ascii=False)

        # Store results for this round
        round_results = {
            "traditional": traditional_results,
            "llm": {k: v for k, v in llm_results.items() if k != 'detailed_results'}
        }
        all_results.append(round_results)

        # Print round results (only showing macro_recall for traditional evaluation)
        print(f"\nRound {round_num + 1} Results:")
        print("Traditional Evaluation:", {"macro_recall": traditional_results["macro_recall"]})
        print("LLM Evaluation:", round_results["llm"])

    # Calculate and save average and extended statistics
    avg_results = calculate_average_results(all_results)
    extended_stats = calculate_statistics_results(all_results)
    avg_output_path = os.path.join(args.output, "average_results.json")
    with open(avg_output_path, "w") as f:
        json.dump({
            "round_results": all_results,
            "average_results": avg_results,
            "extended_statistics": extended_stats
        }, f, indent=2)

    # Print final average and extended statistics (only showing macro_recall for traditional evaluation)
    print(f"\nAverage Results Across {args.num_round} Rounds:")
    print("Traditional Evaluation (average):", {"macro_recall": avg_results["traditional"]["macro_recall"]})
    print("Traditional Evaluation (extended stats):", {"macro_recall": extended_stats["traditional"]["macro_recall"]})
    print("LLM Evaluation (average):", avg_results["llm"])
    print("LLM Evaluation (extended stats):", extended_stats["llm"])
    print(f"\nAll results saved to {args.output}")


if __name__ == "__main__":
    main()
