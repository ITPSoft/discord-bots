from šimek.utils import run_async


async def test_run_async():
    res = await run_async(lambda a: a + 1, 2)
    assert res == 3
