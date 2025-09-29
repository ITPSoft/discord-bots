# Discord bots

Spiritual successors to [DecimBOT](https://github.com/Skavenlord58/DecimBot2) and [BasedSchizoBOT](https://github.com/Skavenlord58/BasedSchizoBOT),
this time developed as a community project in a monorepo.

- [Šimek](https://cs.wikipedia.org/wiki/Miloslav_%C5%A0imek) is the successor to BasedSchizoBOT (Šimek -> Schizo) (easy to remember by the S)
- [Grossmann](https://cs.wikipedia.org/wiki/Ji%C5%99%C3%AD_Grossmann) is the successor to DecimBOT
- [Krampol](https://cs.wikipedia.org/wiki/Ji%C5%99%C3%AD_Krampol) is the successor to [DecimAutomation](https://github.com/Skavenlord58/DecimAutomation)

## Setup and Environment

We use [uv](https://docs.astral.sh/uv/) for package and Python version management.

- [uv installation](https://docs.astral.sh/uv/getting-started/installation/)
- Enter the bot folder
  - ```shell
    cd grossmann
    ```
  - ```shell
    cd šimek
    ```
  - ```shell
    cd krampol
    ```
- Install dependencies
  - ```shell
    uv sync --frozen
    ```
  this installs everything needed into the `.venv` folder for the given bot

- Local execution
  - ```shell
    uv run main.py
    ```

- Environment locking after updating dependencies
  - ```shell
    uv lock
    ```

See the 
## Deployment

Currently no bot runs in Docker, but on bare metal.

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

Run tests:
```shell
uv run pytest
```

Or run all linting and formatting at once
```
format-and-lint.ps1
```

### Tests

inside the given folder, run
```shell
uv run pytest
```

or individual file
```bash
# Main bot functionality
uv run pytest tests/test_main.py -v

# NetHack module tests
uv run pytest tests/test_nethack.py -v

# Integration scenarios
uv run pytest tests/test_integration.py -v
```

### Adding packages

See the [documentation](https://docs.astral.sh/uv/concepts/projects/dependencies/#adding-dependencies).

## Troubleshooting

Check the Guild IDs when getting errors like
```
SyncWarning: Failed to overwrite commands in <Guild id=276720867344646144> due to 403 Forbidden (error code: 50001): Missing Access
```

that can be caused by using `guild_ids` of servers where the bot is not a member.