# Discord bots

Spiritual successors to [DecimBOT](https://github.com/Skavenlord58/DecimBot2) and [BasedSchizoBOT](https://github.com/Skavenlord58/BasedSchizoBOT),
this time developed as a community project in a monorepo.

- [Šimek](https://cs.wikipedia.org/wiki/Miloslav_%C5%A0imek) is the successor to BasedSchizoBOT (Šimek -> Schizo) (easy to remember by the S)
- [Grossmann](https://cs.wikipedia.org/wiki/Ji%C5%99%C3%AD_Grossmann) is the successor to DecimBOT
- [Krampol](https://cs.wikipedia.org/wiki/Ji%C5%99%C3%AD_Krampol) is the successor to [DecimAutomation](https://github.com/Skavenlord58/DecimAutomation)

## Individual bots

### [Šimek](src/šimek)

A schizo impersonation bot.

The funny one.


## Setup and Environment

We use [uv](https://docs.astral.sh/uv/) for package and Python version management.

- [uv installation](https://docs.astral.sh/uv/getting-started/installation/)
- Install dependencies
  - ```shell
    uv sync --frozen
    ```
  this installs everything needed into the `.venv` folder

- Local run
  - šimek
    - ```shell
      uv run src/šimek/main.py
      ```
  - grossmann
    - ```shell
      uv run src/grossmann/main.py
      ```

Make .env file following [.env.sample](.env.sample) in all directories:
- src/grossmann
- src/šimek

## Deployment

Currently no bot runs in Docker, but on bare metal.

## Development

### Checks

Run linting:
```shell
uv run ruff check --fix
```

Run formatting:
```shell
uv run ruff format
```

Check the formatting
```shell
uv run ruff check
```

Or run all linting and formatting at once
```
format-and-lint.ps1
```

### Tests

run
```shell
uv run pytest
```

or individual file
```bash
# Main bot functionality
uv run pytest tests/simek/test_main.py

# NetHack module tests
uv run pytest tests/grossmann/test_nethack.py

# Integration scenarios
uv run pytest tests/grossmann/test_integration.py
```

### Adding packages

See the [documentation](https://docs.astral.sh/uv/concepts/projects/dependencies/#adding-dependencies).

- Environment locking after updating dependencies
  - ```shell
    uv lock
    ```

## Troubleshooting

Check the Guild IDs when getting errors like
```
SyncWarning: Failed to overwrite commands in <Guild id=276720867344646144> due to 403 Forbidden (error code: 50001): Missing Access
```

that can be caused by using `guild_ids` of servers where the bot is not a member.