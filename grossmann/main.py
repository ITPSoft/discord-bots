import os
import random

from disnake import Message, Intents
from disnake.ext.commands import Bot
from dotenv import load_dotenv

import decimdictionary as decdi
import schizodict as schdic
from utils import *

# preload all useful stuff
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
TEXT_SYNTH_TOKEN = os.getenv("TEXT_SYNTH_TOKEN")
PREFIX = os.getenv("BOT_PREFIX")

MOT_HLASKY = decdi.MOT_HLASKY
LINUX_COPYPASTA = decdi.LINUX_COPYPASTA
CESKA_LINUX_COPYPASTA = schdic.CESKA_LINUX_COPYPASTA
RECENZE = schdic.RECENZE
REPLIES = ("Ano.", "Ne.", "Perhaps.")
SADPENIS_ID = 786624092706046042
IGNORE_CH = [
    SADPENIS_ID,
    1042052161338626128,
    1276805111506796605,
    324465236209958922,
    276789712318889984,
    1150244662133653534,
    1034927837263704074,
    1034513061182197810,
]

# add intents for bot and command prefix for classic command support
intents = Intents.all()
client = Bot(command_prefix=PREFIX, intents=intents)

# on_ready event - happens when bot connects to Discord API
@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")


@client.command()
async def say(ctx, *args):
    message = ctx.message
    if str(message.author) == "skavenlord58":
        await message.delete()
        await ctx.send(f"{' '.join(args)}")
    else:
        print(f'{message.author} tried to use "say" command.')


@client.event
async def on_message(m: Message):
    if not m.content:
        return

    if m.content[0] == PREFIX:
        # nutnost aby jely commandy
        await client.process_commands(m)
        return

    if str(m.author) == "BasedSchizo#7762":
        return

    if m.channel.id in IGNORE_CH:
        return

    await maybe_react(m)


async def maybe_react(m: Message):
    content = m.content.lower()
    if "negr" in content:
        await m.add_reaction("🇳")
        # await m.add_reaction("🇪")
        # await m.add_reaction("🇬")
        # await m.add_reaction("🇷")
    if "based" in content:
        await m.add_reaction("👌")
    if content.startswith("hodný bot"):
        await m.add_reaction("🙂")
    if "drip" in m.content.lower():
        await m.add_reaction("🥶")
        await m.add_reaction("💦")
    if "windows" in content:
        if random.randint(0, 4) == 2:
            await m.add_reaction("😔")
    if "debian" in content:
        if random.randint(0, 4) == 2:
            await m.add_reaction("💜")
    if "všechno nejlepší" in content:
        await m.add_reaction("🥳")
        await m.add_reaction("🎉")
    if "atpro" in m.content.lower():
        await m.add_reaction("😥")
        await m.reply("To mě mrzí.")
    if "in a nutshell" in m.content.lower():
        await m.add_reaction("🌰")
    if "kdo je negr?" in content:
        await m.channel.send("Decim je negr.")
    if "kdo je based schizo?" in content:
        await m.channel.send("To jsem já!")
    if "linux" in content and "gnu/linux" not in content:
        if random.randint(0, 64) == 4:
            if bool(random.getrandbits(1)):
                await m.reply(LINUX_COPYPASTA)
            else:
                await m.reply(CESKA_LINUX_COPYPASTA)
    if has_any(content, ["hilfe", "pomoc"]) and "pomocí" not in content:
        if random.randint(0, 3) == 1:
            await m.reply(f"""
            „{MOT_HLASKY[random.randint(0, len(MOT_HLASKY) - 1)]}“
                                                                                - Mistr Oogway, {random.randint(470, 480)} př. n. l.
            """)
    if "novinky.cz" in content:
        if random.randint(0, 32) == 4:
            await m.reply("Přestaň postovat cringe, bro.")
    if "drž hubu" in content and m.mentions:
        print(m.mentions)
        await m.reply("Ne, ty. 😃")
    if has_any(content, ["free primos", "príma džemy"]):
        await m.reply(
            "Neklikejte na odkazy s názvem FREE PRIMOS. Obvykle toto bývá phishing scam. https://www.avast.com/cs-cz/c-phishing"
        )
    if "jsem" in content:
        if random.randint(0, 36) == 4:
            kdo = find_who(content, "jsem")
            await m.reply(f"Ahoj, {kdo}. Já jsem táta.")
    if content == "kdo":
        await m.channel.send("kdo se ptal?")
    if "zhongli" in content:
        await m.reply("haha žongli :clown:")
    if "aneurysm" in content:
        await m.reply("https://www.youtube.com/watch?v=kyg1uxOsAUY")
    if "schizo" in content:
        if random.randint(0, 4) == 2:
            await m.reply("doslova já")
    if "?" in content:
        if random.randint(0, 32) == 4:
            await m.reply(f"{random.choice(REPLIES)}")
    if has_any(content, ["proč ", "proc "]):
        if random.randint(0, 8) == 4:
            await m.reply("skill issue")
    if has_any(content, ["kiryu", "kyriu"]):
        if random.randint(0, 4) == 4:
            await m.reply("Kiryu-chaaaaan!")
    if "jsi" in content:
        if random.randint(0, 16) == 4:
            kdo = find_who(content, "jsi")
            await m.reply(f"Tvoje máma je {kdo}.")
    await hate_comment(content, m)
    if has_any(content, ["israel", "izrael"]):
        if random.randint(0, 8000):
            await m.reply("další důkaz, že rakouský malíř umřel moc brzo :pensive:")
    if random.randint(0, 6969) == 1:
        await m.reply("mňau")
    if random.randint(0, 500000) == 1:
        await m.reply("pipík")
    if random.randint(0, 6969) == 1:
        # sadpenis is skipped everywhere
        await m.reply("víš co? raději drž hubu, protože z tohohle jsem chytil rakovinu varlat")
    if has_any(content, ["mama", "máma", "mami", "mommy", "mamka", "mamko"]):
        if random.randint(0, 64) == 1:
            await random_joke(m)
    if "lagtrain" in content:
        await m.reply("https://www.youtube.com/watch?v=UnIhRpIT7nc")
    if "cum zone" in content:
        await m.reply("https://www.youtube.com/watch?v=j0lN0w5HVT8")
    if "crab rave" in content:
        await m.reply("https://youtu.be/LDU_Txk06tM?t=75")
    if "já jo" in content:
        if random.randint(0, 16) == 1:
            await m.reply("já ne")
    if "já ne" in content:
        if random.randint(0, 16) == 1:
            await m.reply("já jo")
    if has_any(content, ["chci se zabít", "suicidal"]):
        await m.reply("omg don't kill yourself, ur too sexy, haha <:catcry:1158475025473622167>")
    if "v píči" in content:
        await m.reply("stejně tak moc v píči jako já včera večer v tvojí mámě loool <:kekWR:1063089161587933204>")
    if has_any(content, ["buisness", "bussines", "bussiness", "buissnes", "buisnes"]):
        await m.reply(
            "KÁMO lmao ukažte si na toho blbečka, co neumí napsat 'business' XDDDD :index_pointing_at_the_viewer: příště raději napiš 'byznys' dík :)"
        )
    if "reminder" in content:
        if random.randint(0, 4) == 1:
            await m.reply("kind reminder: ur a bitch :)")
    if has_any(content, ["youtu.be", "youtube.com"]):
        if random.randint(0, 5) == 1:
            await m.reply(RECENZE[random.randint(0, len(RECENZE) - 1)])
    if content.__len__() >= 625:
        await m.reply("i ain't reading all of that. im happy for you tho, or sorry that happened. depends on you")
    if has_any(content, ["špatný bot", "spatny bot"]):
        await m.reply("i'm trying my best :pensive:")
    if has_any(content, ["podle mě", "myslím si"]):
        if bool(random.getrandbits(1)):
            await m.reply("Souhlasím.")
        else:
            await m.reply("Rozhodně nesouhlasím.")


client.run(TOKEN)
