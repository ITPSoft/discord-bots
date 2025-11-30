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

### [Grossmann](src/grossmann)

Spiritual successor of [DecimBOT](https://github.com/Skavenlord58/DecimBot2).

### [Krampol](src/krampol)

An automation bot for Discord.

This bot will be used to automate Šimek&Grossmann's tasks in order to reduce overhead in the messy script I wrote for him.


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

Make .env file following [.env.sample](.env.sample) and fill there the required variables.

## Deployment

### Docker

Docker images are automatically built and pushed to GitHub Container Registry (GHCR) on every push to main and on version tags.

**Pull and run a bot:**

```shell
# Pull the latest image
docker pull ghcr.io/itpsoft/discord-bots:latest

# Run Grossmann (default)
docker run -d --name grossmann --env-file .env ghcr.io/itpsoft/discord-bots:latest

# Run Šimek
docker run -d --name simek --env-file .env -e BOT_NAME=šimek ghcr.io/itpsoft/discord-bots:latest

# Run Krampol
docker run -d --name krampol --env-file .env -e BOT_NAME=krampol ghcr.io/itpsoft/discord-bots:latest
```

**Build and run locally:**

Using Docker Compose (recommended):
```shell
# Build the image
docker compose build

# Run specific bot(s)
docker compose up grossmann  # or simek, or krampol
docker compose up -d grossmann  # run in background

# Run all bots
docker compose --profile all up -d

# Stop bots
docker compose down
```

Using Docker directly:
```shell
docker build -t discord-bots .
docker run --env-file .env discord-bots
```

### Bare Metal

Currently deployed on bare metal (see historical deployment in `src/krampol/systemd files/`).

## Development

### Checks

Run linting and formatting:
```shell
uv run poe format-code
```
or if you activated the `.venv`
```shell
poe format-code
```

### Tests

run
```shell
uv run pytest
```
or if you activated the `.venv`, just
```shell
pytest
```

See [development.md](development.md) for more information.

### Adding packages

See the [documentation](https://docs.astral.sh/uv/concepts/projects/dependencies/#adding-dependencies).

- Environment locking after updating dependencies
  - ```shell
    uv lock
    ```

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for more information.