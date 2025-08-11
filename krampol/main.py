import disnake
import os
from disnake import Message
from disnake.ext.commands import Context
from dotenv import load_dotenv
from disnake.ext import tasks, commands
import requests
from automaton import Automaton

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('BOT_PREFIX')
PREFIXES = {
    "996439005405126787" : "$",
    "1044650088494010478" : "§"
}
CHANNELS = {
    "itpero": 786625189038915625
}

autoserv = Automaton()

# add intents for bot and command prefix for classic command support
intents = disnake.Intents.all()
client = disnake.ext.commands.Bot(command_prefix=PREFIX, intents=intents)

async def process_command(prefix, command: list):
    cc = command.split("-")
    try:
        if cc[1]:
            pass
    except Exception as exc:
        cc[1] = 932301697836003358
    
    channel = client.get_channel(CHANNELS[cc[1]])
    m = await channel.send(f"{prefix}{cc[0]}")
    await m.delete()

async def work_loop(jobs):
    if not jobs:
        pass
    else:
        for job in jobs:
            target, command = job.split(";")
            if target == "DecimAutomation#4633":
                eval(f"{command}()")
            else:
                await process_command(PREFIXES[target], command)
        pass

# running job check
@tasks.loop(seconds = 30)
async def check_jobs_loop():
    print("Running job checker!")
    await work_loop(autoserv.precheck_jobs())
    
@check_jobs_loop.before_loop
async def before_check_jobs():
    print('Waiting...')
    await client.wait_until_ready()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    autoserv.parse_cronjobs()
    if check_jobs_loop.start():
        print("Automaton running...")
    else:
        print("Automaton failed to run.")
    

## other DecimAutomation platform commands
@client.command()
async def ping(ctx: Context):
    m = await ctx.send(f'Ping?')
    ping = int(str(m.created_at - ctx.message.created_at).split(".")[1]) / 1000
    await m.edit(content=f'Pong! Latency is {ping}ms. API Latency is {round(client.latency * 1000)}ms.')
    pass

@client.command()
async def isdecimup(ctx: Context):
    m = await ctx.send("Checking... (if no change, he's down)")
    decim = await client.fetch_user("DecimBOT 2.0#8467")
    await decim.send("$autostat")

    def check(m):
        return "OK" in m.content.split(";")[0]

    msg = await client.wait_for("message", check=check)
    if msg:
        await m.edit(content="DecimBot is up.")
    else:
        pass


## parsing incoming messages
@client.event
async def on_message(m: Message):
    if not m.content:
        pass
    elif m.content[0] == PREFIX:
        # needed for commands to work    
        await client.process_commands(m)
    elif str(m.author) != "DecimAutomation#4633":
        # you can add your automatic reactions
        # check decimbot2 for inspiration
        pass

client.run(TOKEN)
