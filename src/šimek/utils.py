import asyncio
import datetime as dt
import logging
import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, TypeVar
from collections import defaultdict, Counter
import pickle
import random

T = TypeVar("T")
MARKOV_FILE = "data/šimek/markov_trigram.pkl"

# CPU-heavy věci budeme dělat v separátním threadu
executor = ThreadPoolExecutor(max_workers=1)

# Semaphore for save operations - ensures only one save at a time
_save_semaphore = threading.Semaphore(1)
# Cached trigram counts (initialized at module load)
_markov_cache: dict = {}
_cache_initialized = False

logger = logging.getLogger(__name__)


async def run_async(func: Callable[..., T], *args: Any) -> T:
    return await asyncio.get_running_loop().run_in_executor(executor, func, *args)


def truncate_emojis(text):
    # emojis are sometimes analyzed as noun
    emoji_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"  # emoticons
        "\U0001f300-\U0001f5ff"  # symbols & pictographs
        "\U0001f680-\U0001f6ff"  # transport & map symbols
        "\U0001f1e0-\U0001f1ff"  # flags (iOS)
        "\U00002702-\U000027b0"  # other symbols
        "\U000024c2-\U0001f251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r"", text)


def format_time_ago(time: dt.datetime) -> str:
    """Format a datetime as a relative time string (e.g., '2 hours, 15 minutes ago')."""
    now = dt.datetime.now()
    delta = now - time
    total_seconds = int(delta.total_seconds())
    is_future = total_seconds < 0
    total_seconds = abs(total_seconds)

    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0 or not parts:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

    time_ago = ", ".join(parts)
    if is_future:
        return f"in {time_ago}"
    else:
        return f"{time_ago} ago"


def build_trigram_counts(messages):
    words = " ".join(messages).lower().split()
    if len(words) < 3:
        return {}
    markov = defaultdict(list)
    for i in range(len(words) - 2):
        key = (words[i], words[i + 1])
        next_word = words[i + 2]
        markov[key].append(next_word)
    markov_counts = {k: Counter(v) for k, v in markov.items()}
    return markov_counts


def _save_trigram_counts_sync(markov_counts, filename=MARKOV_FILE):
    """Save trigram counts synchronously with semaphore protection."""
    acquired = _save_semaphore.acquire(blocking=False)
    if not acquired:
        # Another save is in progress, skip this one
        return
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as f:
            pickle.dump(markov_counts, f)
        print("saved trigrams to cache")
    except Exception as e:
        logger.warning(f"Failed to save trigram counts: {e}")
    finally:
        _save_semaphore.release()


def save_trigram_counts_async(markov_counts, filename=MARKOV_FILE):
    """Save trigram counts in a background thread, non-blocking."""
    # Make a copy to avoid race conditions
    counts_copy = dict(markov_counts)
    executor.submit(_save_trigram_counts_sync, counts_copy, filename)


def load_trigram_counts(filename=MARKOV_FILE):
    """Load trigram counts from file into global cache. Call once at bot start."""
    global _markov_cache, _cache_initialized
    if _cache_initialized:
        return _markov_cache
    try:
        with open(filename, "rb") as f:
            _markov_cache = pickle.load(f)
        print("loaded trigrams from cache")
    except Exception as e:
        print(f"Failed to load markov cache: {e}")
        _markov_cache = {}
    _cache_initialized = True
    return _markov_cache


def markov_chain(messages, max_words=20):
    global _markov_cache
    # Build new trigram counts from messages
    new_counts = build_trigram_counts(messages)
    # Update global cache in place
    for key, counter in new_counts.items():
        if key in _markov_cache:
            _markov_cache[key].update(counter)
        else:
            _markov_cache[key] = counter
    # Save asynchronously in background thread
    save_trigram_counts_async(_markov_cache)
    markov_counts = _markov_cache

    if not markov_counts:
        return "Not enough data for trigram Markov chain."

    start_key = random.choice(list(markov_counts.keys()))
    sentence = [start_key[0], start_key[1]]

    for _ in range(max_words - 2):
        if start_key in markov_counts:
            next_words, weights = zip(*markov_counts[start_key].items())
            next_word = random.choices(next_words, weights=weights)[0]
            sentence.append(next_word)
            if next_word.endswith((".", "!", "?:D", ":D", ":)", "😂", "🤣", ":kekw:")):
                break
            start_key = (start_key[1], next_word)
        else:
            break

    return " ".join(sentence).lower()


# Load trigram counts at module import (bot start)
load_trigram_counts()
