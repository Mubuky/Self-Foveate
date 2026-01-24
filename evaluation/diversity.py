"""Unified diversity evaluation for instruction datasets."""

import json
import argparse
import os
import sys

import nltk
import pandas as pd
import torch
from fast_bleu import SelfBLEU
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shared.path_utils import get_output_path


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Calculate diversity scores for instruction datasets"
    )
    parser.add_argument(
        "--input_path", type=str, required=True,
        help="Input JSONL with 'instruction' field"
    )
    parser.add_argument(
        "--metric", type=str, default="all",
        choices=["self_bleu", "embedding", "all"],
        help="Metric to calculate"
    )
    parser.add_argument(
        "--output_dir", type=str, default="./data/output_data",
        help="Base output directory"
    )
    parser.add_argument(
        "--model", type=str,
        default="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        help="Embedding model"
    )
    parser.add_argument(
        "--top_k", type=int, default=5,
        help="Similar pairs to report"
    )
    return parser.parse_args()


def load_instructions(input_path: str) -> list:
    """Load instructions from JSONL file."""
    data = pd.read_json(input_path, orient='records', lines=True)
    return data['instruction'].tolist()


def calculate_self_bleu(instructions: list) -> dict:
    """Calculate Self-BLEU diversity score."""
    list_of_references = [
        nltk.word_tokenize(ref)
        for ref in tqdm(instructions, desc="Tokenizing references")
    ]

    weights = {
        'bigram': (1/2., 1/2.),
        'trigram': (1/3., 1/3., 1/3.),
        'fourgram': (1/4., 1/4., 1/4., 1/4.),
        'fivegram': (1/5., 1/5., 1/5., 1/5., 1/5.)
    }

    self_bleu = SelfBLEU(list_of_references, weights)
    self_bleu_scores = self_bleu.get_score()

    total_score = sum(sum(scores) for scores in zip(*self_bleu_scores.values()))
    num_scores = len(self_bleu_scores) * len(next(iter(self_bleu_scores.values())))
    diversity = 1 - (total_score / num_scores)

    return {
        "diversity": diversity,
        "num_samples": len(instructions),
        "self_bleu_scores": self_bleu_scores
    }


def calculate_embedding_diversity(instructions: list, model: str, top_k: int) -> dict:
    """Calculate embedding-based diversity score."""
    torch.manual_seed(42)

    print(f"Loading model: {model}")
    encoder = SentenceTransformer(model)

    print("Calculating embeddings...")
    embeddings = encoder.encode(instructions, show_progress_bar=True)
    embeddings = torch.tensor(embeddings)

    print("Calculating cosine similarity matrix...")
    cosine_sim_matrix = torch.nn.functional.cosine_similarity(
        embeddings[:, None, :],
        embeddings[None, :, :],
        dim=-1
    )

    upper_tri = torch.triu(cosine_sim_matrix, diagonal=1)
    similarity_sum = upper_tri.sum().item()
    n = len(embeddings)
    num_elements = (n * (n - 1)) // 2
    avg_similarity = similarity_sum / num_elements
    diversity = 1 - avg_similarity

    print(f"Finding top {top_k} most similar pairs...")
    sim_matrix = cosine_sim_matrix.clone()
    sim_matrix.fill_diagonal_(-1)
    top_similar_pairs = []

    for _ in range(min(top_k, num_elements)):
        max_val, max_indices = sim_matrix.max(dim=1)
        i = max_val.argmax().item()
        j = max_indices[i].item()
        similarity = sim_matrix[i, j].item()
        top_similar_pairs.append((i, j, similarity))
        sim_matrix[i, j] = sim_matrix[j, i] = -1

    return {
        "diversity": diversity,
        "avg_similarity": avg_similarity,
        "num_samples": n,
        "model": model,
        "top_similar_pairs": [
            {
                "instruction1": instructions[i],
                "instruction2": instructions[j],
                "similarity": float(sim)
            } for i, j, sim in top_similar_pairs
        ]
    }


def main():
    args = parse_args()
    instructions = load_instructions(args.input_path)
    filename = os.path.basename(args.input_path)

    if args.metric in ["self_bleu", "all"]:
        print("Calculating Self-BLEU diversity...")
        results = calculate_self_bleu(instructions)
        output_path = get_output_path(args.output_dir, filename, "Diversity/SelfBleu", True)
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Self-BLEU Diversity: {results['diversity']:.4f}")
        print(f"Results saved to {output_path}")

    if args.metric in ["embedding", "all"]:
        print("Calculating embedding diversity...")
        results = calculate_embedding_diversity(instructions, args.model, args.top_k)
        output_path = get_output_path(args.output_dir, filename, "Diversity/Embedding", True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Embedding Diversity: {results['diversity']:.4f}")
        print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
