<div align="center">

# Self-Foveate: Enhancing Diversity and Difficulty of Synthesized Instructions from Unsupervised Text via Multi-Level Foveation

<a href='https://arxiv.org/abs/2507.23440'><img src='https://img.shields.io/badge/arXiv-2507.23440-b31b1b.svg'></a>
<a href='https://huggingface.co/papers/2507.23440'><img src='https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Paper-yellow'></a>
<a href='https://aclanthology.org/2025.findings-acl.380/'><img src='https://img.shields.io/badge/ACL%202025-Findings-blue'></a>
<a href='LICENSE'><img src='https://img.shields.io/badge/License-MIT-green.svg'></a>
<a href='https://www.python.org/'><img src='https://img.shields.io/badge/python-3.8+-blue.svg'></a>

English | [中文](README_zh.md)

</div>

## 🎊 News

- [2025.07] 📄 Paper accepted at *ACL 2025 (Findings)*. [[Paper](https://aclanthology.org/2025.findings-acl.380/)]
- [2025.07] 📄 Paper available on arXiv. [[arXiv](https://arxiv.org/abs/2507.23440)]

## 📌 Table of Contents

- [Introduction](#-introduction)
- [Installation](#-installation)
- [Usage](#-usage)
- [Evaluation](#-evaluation)
- [Foveation Strategies](#-foveation-strategies)
- [Citation](#-citation)
- [License](#-license)

## 📜 Introduction

Self-Foveate is an automated framework for synthesizing high-quality, diverse instructions from unsupervised text data. Inspired by human visual perception's foveation mechanism—where the eye focuses on different regions with varying levels of detail—this framework guides LLMs to extract and process textual information at multiple granularities.

**🤖 Automated LLM-Driven Framework** — Self-Foveate leverages LLMs to automatically generate domain-specific instruction datasets from raw unsupervised text, eliminating the need for manual annotation or seed instructions while maintaining high quality and relevance.

**🔬 Micro-Scatter-Macro Foveation** — We introduce a novel multi-level foveation methodology that guides LLMs to extract fine-grained and diverse information: *Micro* focuses on individual words, *Scatter* combines multiple keywords, and *Macro* captures complete sentences as contextual features.

**📈 Superior Cross-Domain Performance** — Extensive experiments demonstrate that Self-Foveate consistently outperforms existing methods across multiple unsupervised corpora (SQuAD, HotpotQA, FilmWiki) and model architectures, achieving higher diversity and difficulty in synthesized instructions.

<div align="center">
<img src="assets/acl25_self-foveate.png" width="80%" alt="Self-Foveate Framework">
</div>

## 🛠️ Installation

### Requirements
- Python 3.8+
- OpenAI API key (or compatible API)

### Setup

```bash
git clone https://github.com/Mubuky/Self-Foveate.git
cd Self-Foveate
pip install -r requirements.txt
```

### Configuration

Copy the environment template and add your API credentials:
```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o  # Optional
OPENAI_BASE_URL=https://api.openai.com/v1  # Optional
```

### Data Format

Input data should be in JSONL format with a `content` field. See [docs/DATA_FORMAT.md](docs/DATA_FORMAT.md) for detailed specification.

## 💻 Usage

### Run Self-Foveate

```bash
# Basic usage
python self_foveate.py --data_path ./data/input_data/content.jsonl

# Full parameters
python self_foveate.py \
    --data_path ./data/input_data/content.jsonl \
    --output_path ./data/output_data/output.json \
    --mu 8.0 \
    --alpha 0.0 \
    --max_retries 5 \
    --num_sample 100 \
    --log_level INFO

# With important keywords feature
python self_foveate.py \
    --data_path ./data/input_data/content.jsonl \
    --num_important 2 3
```

#### CLI Arguments
| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--data_path` | str | required | Input JSONL data file |
| `--output_path` | str | auto | Output JSON file (auto-generated if not specified) |
| `--mu` | float | 8.0 | Box-Cox target mean |
| `--alpha` | float | 0.0 | Box-Cox scaling factor |
| `--max_retries` | int | 5 | Max API retries |
| `--num_sample` | int | None | Sample size (optional) |
| `--num_important` | int[2] | None | Important keywords [core, major] (optional) |
| `--log_level` | str | INFO | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `--log_dir` | str | ./log | Log directory |

## 📊 Evaluation

### Diversity Metrics
```bash
# All metrics (Self-BLEU + Embedding)
python evaluation/diversity.py --input_path ./data/output_data/output.json --metric all

# Self-BLEU only
python evaluation/diversity.py --input_path ./data/output_data/output.json --metric self_bleu

# Embedding diversity only
python evaluation/diversity.py --input_path ./data/output_data/output.json --metric embedding
```

### Difficulty Evaluation
```bash
python evaluation/difficulty.py \
    --baseline_path ./data/output_data/baseline.json \
    --method_path ./data/output_data/method.json \
    --input_path ./data/input_data/content.jsonl \
    --output_dir ./data/output_data
```

### Model Evaluation
```bash
python evaluation/model_evaluation.py --dataset datasetname --output exp_name --num_round 5
```

## 🔍 Foveation Strategies

| Strategy | Level | Description | Feature Type |
|----------|-------|-------------|--------------|
| **Macro** | Sentence | Extracts complete sentences as contextual features | Full sentences |
| **Micro** | Word | Extracts individual words for fine-grained features | Single words |
| **Scatter** | Multi-keyword | Combines 1-3 keywords into diverse feature groups | Keyword combinations |

## 🔎 Citation

If you use this code or method in your research, please cite our paper:

```bibtex
@inproceedings{li2025self,
  title={Self-Foveate: Enhancing Diversity and Difficulty of Synthesized Instructions from Unsupervised Text via Multi-Level Foveation},
  author={Li, Mingzhe and Lu, Xin and Zhao, Yanyan},
  booktitle={Findings of the Association for Computational Linguistics: ACL 2025},
  pages={7274--7289},
  year={2025}
}
```

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
