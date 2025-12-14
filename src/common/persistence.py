"""Common persistence utilities for async file saving.

Provides thread-safe, non-blocking file persistence with one semaphore per file.
"""

import json
import logging
import pickle
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Shared executor for all background file operations
_executor = ThreadPoolExecutor(max_workers=1)

# One semaphore per file path to prevent concurrent writes to the same file
_file_semaphores: dict[str, threading.Semaphore] = {}
_semaphores_lock = threading.Lock()

PathLike = str | Path


def _get_semaphore(file_path: str) -> threading.Semaphore:
    with _semaphores_lock:
        if file_path not in _file_semaphores:
            _file_semaphores[file_path] = threading.Semaphore(1)
        return _file_semaphores[file_path]


@contextmanager
def _atomic_save(file_path: PathLike, format_name: str):
    path = Path(file_path)
    semaphore = _get_semaphore(str(path))
    if not semaphore.acquire(blocking=False):
        yield None  # Another save in progress, skip
        return

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        yield path
        logger.debug(f"Saved {format_name} to {path}")
    except OSError as e:
        logger.warning(f"Failed to save {format_name} to {path}: {e}")
    finally:
        semaphore.release()


@contextmanager
def _safe_load(file_path: PathLike, format_name: str, errors: tuple):
    path = Path(file_path)
    if not path.exists():
        yield None
        return

    try:
        yield path
    except errors as e:
        logger.error(f"Failed to load {format_name} from {path}: {e}")


def _save_json_sync(file_path: PathLike, data: Any) -> None:
    with _atomic_save(file_path, "JSON") as path:
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)


def _save_pickle_sync(file_path: PathLike, data: Any) -> None:
    with _atomic_save(file_path, "pickle") as path:
        if path:
            with open(path, "wb") as f:
                pickle.dump(data, f)


def save_json_async(file_path: PathLike, data: Any) -> None:
    """Save data as JSON in a background thread, non-blocking.

    If a save is already in progress for this file, this call is skipped.
    """
    _executor.submit(_save_json_sync, file_path, data)


def save_pickle_async(file_path: PathLike, data: Any) -> None:
    """Save data as pickle in a background thread, non-blocking.

    If a save is already in progress for this file, this call is skipped.
    """
    _executor.submit(_save_pickle_sync, file_path, data)


def load_json(file_path: PathLike, default: Any = None) -> Any:
    """Load JSON from file, returning default if file doesn't exist or is invalid."""
    with _safe_load(file_path, "JSON", (json.JSONDecodeError, OSError)) as path:
        if path:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    return default


def load_pickle(file_path: PathLike, default: Any = None) -> Any:
    """Load pickle from file, returning default if file doesn't exist or is invalid."""
    with _safe_load(file_path, "pickle", (pickle.PickleError, OSError)) as path:
        if path:
            with open(path, "rb") as f:
                return pickle.load(f)
    return default
