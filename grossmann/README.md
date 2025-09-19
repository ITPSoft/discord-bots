# DecimBOT 2
## A custom discord bot, that does everything I tell him to do

### Introduction
The OG DecimBOT was my school project in the junior year. But it was poorly written in
node.js, so I decided to go back to it, after I migrated to Discord as my main comms
platform. And now it's time to rewrite it in python and dockerise it.

### Some technical stuff
WIP

### Discordeno is trash, dont use it

### Running it

Run as
```bash
docker build -t decimbot2 .
docker run -it decimbot2
```

Create an .env file and add this stuff to it:
```cfg
DISCORD_TOKEN={DISCORD_API_TOKEN} # cuz we won't push ours to the repo XD
BOT_PREFIX=$
NETHACK_PATH=/usr/games/nethack -u kouzelnik
```
