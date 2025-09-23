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

## Deployment

Currently no bot runs in Docker, but on bare metal.

### Checks and tests

Run formatting:
```shell
uv run ruff check --fix
```

Check the formatting
```shell
uv run ruff check
```

Run tests:
```shell
uv run pytest
```

## Development

### Adding packages

See the [documentation](https://docs.astral.sh/uv/concepts/projects/dependencies/#adding-dependencies).
