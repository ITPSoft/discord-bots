import aiohttp

_http_session: aiohttp.ClientSession | None = None


def get_http_session() -> aiohttp.ClientSession:
    """Get the global HTTP session, creating it lazily if needed."""
    global _http_session
    if _http_session is None or _http_session.closed:
        _http_session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
    return _http_session


async def close_http_session() -> None:
    """Close the global HTTP session if it's open."""
    global _http_session
    if _http_session and not _http_session.closed:
        await _http_session.close()
        _http_session = None

