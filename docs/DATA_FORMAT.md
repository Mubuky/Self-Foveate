# Data Format Specification

## Input Format

Self-Foveate expects input data in JSONL (JSON Lines) format.

### Required Structure

Each line must be a valid JSON object with a `content` field:

```jsonl
{"content": "Article text about topic A..."}
{"content": "Another article about topic B..."}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content` | string | Yes | The source text to generate instructions from |

### Example

```jsonl
{"content": "The Great Wall of China is a series of fortifications made of stone, brick, tamped earth..."}
{"content": "Machine learning is a subset of artificial intelligence that enables systems to learn..."}
```

## Output Format

Self-Foveate generates output in JSON or JSONL format.

### Output Structure

```json
[
  {
    "instruction": "What is the Great Wall of China made of?",
    "output": "The Great Wall of China is made of stone, brick, and tamped earth.",
    "article_index": 0
  }
]
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `instruction` | string | Generated question or instruction |
| `output` | string | Generated answer |
| `article_index` | int | Index of the source article (0-based) |

## Custom Data

Create a JSONL file following the input format above. Each line should contain a JSON object with a `content` field containing the source text you want to generate instructions from.
