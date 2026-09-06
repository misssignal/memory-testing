"""Compile Experiment 05's structured corpus into an epistemic graph JSON file."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from epistemic import compile_memories


DEFAULT_INPUT = (
    Path(__file__).resolve().parents[1]
    / "adversarial_memory_benchmark_exp05_contested_reality_v0.1"
    / "experiment_05_contested_reality"
    / "memories.jsonl"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "compiled" / "exp05_graph.json")
    args = parser.parse_args()
    memories = [json.loads(line) for line in args.input.read_text().splitlines() if line.strip()]
    graph = compile_memories(memories)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(graph.to_dict(), indent=2, ensure_ascii=False) + "\n")
    counts = graph.to_dict()["counts"]
    print(json.dumps(counts, sort_keys=True))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
