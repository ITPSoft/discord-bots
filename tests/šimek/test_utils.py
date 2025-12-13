import datetime as dt
from unittest.mock import patch

import pytest

from šimek import utils


async def test_run_async():
    res = await utils.run_async(lambda a: a + 1, 2)
    assert res == 3


def test_build_trigram_counts():
    """Test trigram counting function."""
    utils._markov_cache = {}
    messages = ["hello world test", "world test again"]
    result = utils.build_trigram_counts(messages)

    assert isinstance(result, dict)
    assert ("hello", "world") in result
    assert ("world", "test") in result


def test_markov_chain_insufficient_data():
    """Test markov chain with insufficient data."""
    utils._markov_cache = {}
    messages = ["hi"]
    result = utils.markov_chain(messages)

    assert "Not enough data" in result


# Test format_time_ago function
@pytest.mark.parametrize(
    "seconds_offset,expected",
    [
        # Past times
        (0, "0 seconds ago"),
        (1, "1 second ago"),
        (30, "30 seconds ago"),
        (60, "1 minute ago"),
        (90, "1 minute, 30 seconds ago"),
        (120, "2 minutes ago"),
        (3600, "1 hour ago"),
        (3661, "1 hour, 1 minute, 1 second ago"),
        (7200, "2 hours ago"),
        (7265, "2 hours, 1 minute, 5 seconds ago"),
        (86400, "1 day ago"),
        (90061, "1 day, 1 hour, 1 minute, 1 second ago"),
        (172800, "2 days ago"),
        (90000, "1 day, 1 hour ago"),
        (93784, "1 day, 2 hours, 3 minutes, 4 seconds ago"),
        (180122, "2 days, 2 hours, 2 minutes, 2 seconds ago"),
        # Future times (negative offset)
        (-1, "in 1 second"),
        (-60, "in 1 minute"),
        (-3600, "in 1 hour"),
        (-86400, "in 1 day"),
        (-90061, "in 1 day, 1 hour, 1 minute, 1 second"),
    ],
)
def test_format_time_ago(seconds_offset, expected):
    """Test format_time_ago with various past and future times."""
    now = dt.datetime(2024, 6, 15, 12, 0, 0)
    target_time = now - dt.timedelta(seconds=seconds_offset)

    with patch("šimek.utils.dt.datetime") as mock_dt:
        mock_dt.now.return_value = now
        result = utils.format_time_ago(target_time)

    assert result == expected
