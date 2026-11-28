import logging

from common.discord_logging import DiscordFormatter


def test_discord_formatter_preserves_traceback_edges_within_limit():
    rows = [f"trace row {index:03d} " + "x" * 32 for index in range(100)]
    record = logging.LogRecord("test", logging.ERROR, "test.py", 1, "failure", (), None)
    record.exc_text = "\n".join(rows)

    formatted = DiscordFormatter("%(message)s", max_size=1_900).format(record)

    assert len(formatted) <= 1_900
    assert all(row in formatted for row in rows[:5])
    assert all(row in formatted for row in rows[-10:])
    assert rows[5] not in formatted
    assert "\n...\n" in formatted


def test_discord_formatter_caps_records_with_long_prefixes():
    record = logging.LogRecord("x" * 2_000, logging.ERROR, "test.py", 1, "failure", (), None)
    record.exc_text = "Traceback"

    formatted = DiscordFormatter("%(name)s", max_size=1_900).format(record)

    assert len(formatted) == 1_900


def test_discord_formatter_selects_rows_even_when_trace_fits():
    rows = [f"trace row {index:02d}" for index in range(20)]
    record = logging.LogRecord("test", logging.ERROR, "test.py", 1, "failure", (), None)
    record.exc_text = "\n".join(rows)

    formatted = DiscordFormatter("%(message)s", max_size=1_900).format(record)

    assert all(row in formatted for row in rows[:5])
    assert all(row in formatted for row in rows[-10:])
    assert rows[5] not in formatted
