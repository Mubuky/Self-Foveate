import os
import sys
import random
import logging
import argparse

from datetime import datetime

from self_foveate.core.data import load_data, save_seed_tasks
from self_foveate.strategies.scatter import scatter_process_articles_parallel
from self_foveate.strategies.micro import micro_process_articles_parallel
from self_foveate.strategies.macro import macro_process_articles_parallel
from self_foveate.utils.thresholding import count_above_threshold, boxcox_normalize_data

random.seed(42)


def main():
    parser = argparse.ArgumentParser(
        description='Self-Foveate: Multi-level foveation for instruction generation'
    )
    parser.add_argument('--data_path', type=str, required=True,
                        help='Input JSONL data file')
    parser.add_argument('--output_path', type=str, default=None,
                        help='Output JSON file (auto-generated if not specified)')
    parser.add_argument('--mu', type=float, default=8.0,
                        help='Box-Cox target mean (default: 8.0)')
    parser.add_argument('--alpha', type=float, default=0.0,
                        help='Box-Cox scaling factor (default: 0.0)')
    parser.add_argument('--max_retries', type=int, default=5,
                        help='Max API retries (default: 5)')
    parser.add_argument('--num_sample', type=int, default=None,
                        help='Sample size (optional)')
    parser.add_argument('--num_important', type=int, nargs=2, default=None,
                        help='Important keywords [core, major] (optional)')
    parser.add_argument('--log_level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='Logging level (default: INFO)')
    parser.add_argument('--log_dir', type=str, default='./log',
                        help='Log directory (default: ./log)')
    args = parser.parse_args()

    # Set up logging
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    os.makedirs(args.log_dir, exist_ok=True)

    log_filename = os.path.join(
        args.log_dir,
        f"sf_{args.mu}_{args.alpha}_{current_datetime}.log"
    )

    logging.basicConfig(
        filename=log_filename,
        level=getattr(logging, args.log_level),
        format="%(asctime)s - [Thread-%(thread)d] - %(levelname)s - %(message)s",
        encoding="utf-8"
    )

    # Auto-generate output path if not specified
    if args.output_path is None:
        os.makedirs('./data/output_data', exist_ok=True)
        args.output_path = f"./data/output_data/sf_{args.mu}_{args.alpha}_{current_datetime}.json"

    # Convert num_important to list format for compatibility
    args.num_important_list = list(args.num_important) if args.num_important else []

    print("Start.")
    # Load data
    try:
        data_df = load_data(args.data_path)
    except Exception as e:
        logging.error("Failed to load data", exc_info=True)
        sys.exit(1)

    # Sample data if specified
    if args.num_sample is not None:
        data_df = data_df[:args.num_sample]

    # Calculate threshold values
    if args.alpha == 0:
        normalized_count_above_threshold = [args.mu] * len(data_df["content"])
        logging.info(f"Using uniform threshold: mu={args.mu}")
    else:
        threshold_counts = count_above_threshold(data_df["content"])
        normalized_count_above_threshold = boxcox_normalize_data(
            threshold_counts, args.mu, args.alpha
        )
        logging.info(f"Calculated threshold data: mu={args.mu}, alpha={args.alpha}")

    # Process articles in parallel
    seed_tasks = []
    seed_tasks.extend(scatter_process_articles_parallel(data_df, args, normalized_count_above_threshold))
    seed_tasks.extend(micro_process_articles_parallel(data_df, args, normalized_count_above_threshold))
    seed_tasks.extend(macro_process_articles_parallel(data_df, args, normalized_count_above_threshold))

    logging.info(f"len(seed_tasks): {len(seed_tasks)}")

    # Save results
    save_seed_tasks(seed_tasks, args.output_path)
    print("Finished.")


if __name__ == '__main__':
    main()
