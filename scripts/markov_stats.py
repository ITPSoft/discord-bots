#!/usr/bin/env python3
"""Print statistics about the markov trigram pickle file."""

import pickle
import sys
from collections import Counter
from pathlib import Path

MARKOV_FILE = Path(__file__).parent.parent / "data" / "šimek" / "markov_trigram.pkl"


def load_trigram_counts(filename: Path) -> dict:
    with open(filename, "rb") as f:
        return pickle.load(f)


def print_stats(markov_counts: dict) -> None:
    if not markov_counts:
        print("Empty markov model.")
        return

    total_keys = len(markov_counts)
    total_transitions = sum(sum(counter.values()) for counter in markov_counts.values())
    unique_next_words = set()
    for counter in markov_counts.values():
        unique_next_words.update(counter.keys())

    avg_next_per_key = total_transitions / total_keys if total_keys else 0

    # Most common bigram keys by total count
    key_counts = [(k, sum(v.values())) for k, v in markov_counts.items()]
    top_keys = sorted(key_counts, key=lambda x: x[1], reverse=True)[:10]

    # Most common next words overall
    all_next_words = Counter()
    for counter in markov_counts.values():
        all_next_words.update(counter)
    top_next_words = all_next_words.most_common(10)

    print("=" * 50)
    print("MARKOV TRIGRAM STATISTICS")
    print("=" * 50)
    print(f"Total bigram keys:        {total_keys:,}")
    print(f"Total transitions:        {total_transitions:,}")
    print(f"Unique next words:        {len(unique_next_words):,}")
    print(f"Avg transitions per key:  {avg_next_per_key:.2f}")
    print()
    print("Top 10 most common bigram keys:")
    for i, (key, count) in enumerate(top_keys, 1):
        print(f"  {i:2}. {key[0]!r} {key[1]!r} -> {count:,} transitions")
    print()
    print("Top 10 most common next words:")
    for i, (word, count) in enumerate(top_next_words, 1):
        print(f"  {i:2}. {word!r} -> {count:,} occurrences")


def main():
    filename = Path(sys.argv[1]) if len(sys.argv) > 1 else MARKOV_FILE
    if not filename.exists():
        print(f"File not found: {filename}")
        sys.exit(1)

    markov_counts = load_trigram_counts(filename)
    print_stats(markov_counts)


if __name__ == "__main__":
    main()
