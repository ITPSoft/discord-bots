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
