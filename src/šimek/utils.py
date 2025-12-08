import asyncio
import datetime as dt
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, TypeVar
from collections import defaultdict, Counter
import pickle
import random

T = TypeVar("T")
MARKOV_FILE = "markov_trigram.pkl"

# CPU-heavy věci budeme dělat v separátním threadu
executor = ThreadPoolExecutor(max_workers=1)


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


def save_trigram_counts(markov_counts, filename=MARKOV_FILE):
    with open(filename, "wb") as f:
        pickle.dump(markov_counts, f)


def load_trigram_counts(filename=MARKOV_FILE):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except Exception:
        return {}


def markov_chain(messages, max_words=20):
    # Build and save trigram counts
    markov_counts = build_trigram_counts(messages)
    # save_trigram_counts(markov_counts)
    #
    # # Load trigram counts
    # markov_counts = load_trigram_counts()

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
