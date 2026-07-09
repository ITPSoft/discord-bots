"""Tests for hall of fame forwarded-message persistence."""

import json
from unittest.mock import patch

import pytest

from grossmann import fame_persistence as fame


@pytest.fixture
def temp_fame_file(tmp_path):
    """Create a temporary fame file and isolate the cache for testing."""
    fame_file = tmp_path / "forwarded_fames.json"
    with patch.object(fame, "_get_fame_file_path", return_value=fame_file):
        fame._reset_cache()
        fame._init_cache()
        yield fame_file
        fame._reset_cache()


def test_empty_file_has_nothing_forwarded(temp_fame_file):
    assert fame.get_forwarded() == {}
    assert not fame.is_forwarded(123)


def test_mark_and_check_forwarded(temp_fame_file):
    fame.mark_forwarded(123, 1700000000.0)

    assert fame.is_forwarded(123)
    assert fame.get_forwarded()[123] == 1700000000.0


def test_mark_trims_to_max_tracked(temp_fame_file):
    for i in range(fame.MAX_TRACKED + 10):
        fame.mark_forwarded(i, float(i))

    forwarded = fame.get_forwarded()
    assert len(forwarded) == fame.MAX_TRACKED
    # Oldest (lowest timestamps) are dropped, newest are kept.
    assert not fame.is_forwarded(0)
    assert fame.is_forwarded(fame.MAX_TRACKED + 9)


def test_survives_restart(temp_fame_file):
    """Forwarded IDs saved by a previous session are reloaded on startup."""
    # Simulate a file written by a previous run (JSON keys are strings).
    temp_fame_file.write_text(json.dumps({"555": 1700000000.0}), encoding="utf-8")

    # Simulate a restart: drop the in-memory cache and reload from file.
    fame._reset_cache()
    fame._init_cache()

    assert fame.is_forwarded(555)
    assert fame.get_forwarded()[555] == 1700000000.0
