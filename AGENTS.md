## Dev environment tips
- See the [README](README.md) for development instructions.

## Testing instructions
- See the [README](README.md) for instructions on running tests.
- Do not add `@pytest.mark.asyncio`, it's not needed and it's handled automatically.
- Never replicate the "business logic" inside the code, the `conftest.py` must contain only mocking, 
fixtures and other test-related code, including dpytest and other code related to simulating the Discord API.
- The testing code must exercise actual bot commands, using the bot commands, not copy-pasting the logic to tests.
- No `if __name__ == "__main__":` is used in tests, pytest handles this automatically.
- Never run tests using unittest, use pytest instead.

## Coding 
- Always follow the best engineering practices, especially KISS and DRY. Skip overly verbose comments, UIs, etc. When importing a package, don't `try` if it's installed but import directly.
- Avoid overly defensive checks. Rely on type hints and use these. 
- Always cover new logic with tests.
- Always follow the current logic and structure of the code as in the rest of the repository, including style of testing and handling mocks and fixtures.
