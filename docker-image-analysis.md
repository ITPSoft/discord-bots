# Analysis of https://github.com/ITPSoft/discord-bots/pull/64/ on layer cacheability

2 last build images:
- [ghcr.io/itpsoft/discord-bots:sha-6a9d502](https://github.com/ITPSoft/discord-bots/pkgs/container/discord-bots/659478941?tag=sha-6a9d502)
- [ghcr.io/itpsoft/discord-bots:sha-0e8127a](https://github.com/ITPSoft/discord-bots/pkgs/container/discord-bots/641725861?tag=sha-0e8127a)

2 consecutive builds before the PR
- [ghcr.io/itpsoft/discord-bots:sha-e03b524](https://github.com/ITPSoft/discord-bots/pkgs/container/discord-bots/604519036?tag=sha-e03b524)
- [ghcr.io/itpsoft/discord-bots:sha-1cfc7c7](https://github.com/ITPSoft/discord-bots/pkgs/container/discord-bots/604053736?tag=sha-1cfc7c7)

```
docker pull ghcr.io/itpsoft/discord-bots:sha-6a9d502
docker pull ghcr.io/itpsoft/discord-bots:sha-0e8127a
docker pull ghcr.io/itpsoft/discord-bots:sha-e03b524
docker pull ghcr.io/itpsoft/discord-bots:sha-1cfc7c7

chmod +x compare-docker-layers.sh
./compare-docker-layers.sh ghcr.io/itpsoft/discord-bots:sha-6a9d502 ghcr.io/itpsoft/discord-bots:sha-0e8127a
./compare-docker-layers.sh ghcr.io/itpsoft/discord-bots:sha-e03b524 ghcr.io/itpsoft/discord-bots:sha-1cfc7c7
```

```
img1=ghcr.io/itpsoft/discord-bots:sha-e03b524; img2=ghcr.io/itpsoft/discord-bots:sha-1cfc7c7
```
