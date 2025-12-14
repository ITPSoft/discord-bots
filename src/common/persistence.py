"""Common persistence utilities for async file saving.

Provides thread-safe, non-blocking file persistence with one semaphore per file.
"""

import json
import logging
import pickle
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Shared executor for all background file operations
_executor = ThreadPoolExecutor(max_workers=1)

# One semaphore per file path to prevent concurrent writes to the same file
_file_semaphores: dict[str, threading.Semaphore] = {}
_semaphores_lock = threading.Lock()


def _get_semaphore(file_path: str) -> threading.Semaphore:
    """Get or create a semaphore for the given file path."""
    with _semaphores_lock:
        if file_path not in _file_semaphores:
            _file_semaphores[file_path] = threading.Semaphore(1)
        return _file_semaphores[file_path]


def _save_json_sync(file_path: str, data: Any) -> None:
    """Save data as JSON synchronously with semaphore protection."""
    semaphore = _get_semaphore(file_path)
    if not semaphore.acquire(blocking=False):
        return  # Another save in progress, skip

    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.debug(f"Saved JSON to {file_path}")
    except OSError as e:
        logger.warning(f"Failed to save JSON to {file_path}: {e}")
    finally:
        semaphore.release()


def _save_pickle_sync(file_path: str, data: Any) -> None:
    """Save data as pickle synchronously with semaphore protection."""
    semaphore = _get_semaphore(file_path)
    if not semaphore.acquire(blocking=False):
        return  # Another save in progress, skip

    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(data, f)
        logger.debug(f"Saved pickle to {file_path}")
    except OSError as e:
        logger.warning(f"Failed to save pickle to {file_path}: {e}")
    finally:
        semaphore.release()


def save_json_async(file_path: str, data: Any) -> None:
    """Save data as JSON in a background thread, non-blocking.

    If a save is already in progress for this file, this call is skipped.
    The next mutation will persist the data anyway.
    """
    _executor.submit(_save_json_sync, file_path, data)


def save_pickle_async(file_path: str, data: Any) -> None:
    """Save data as pickle in a background thread, non-blocking.

    If a save is already in progress for this file, this call is skipped.
    The next mutation will persist the data anyway.
    """
    _executor.submit(_save_pickle_sync, file_path, data)


def load_json(file_path: str, default: Any = None) -> Any:
    """Load JSON from file, returning default if file doesn't exist or is invalid."""
    path = Path(file_path)
    if not path.exists():
        return default

    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to load JSON from {file_path}: {e}")
        return default


def load_pickle(file_path: str, default: Any = None) -> Any:
    """Load pickle from file, returning default if file doesn't exist or is invalid."""
    path = Path(file_path)
    if not path.exists():
        return default

    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except (pickle.PickleError, OSError) as e:
        logger.error(f"Failed to load pickle from {file_path}: {e}")
        return default
