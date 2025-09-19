import json
import os
import random
import datetime as dt
import disnake
from disnake import Message
from disnake.ext import commands
import requests
from collections import defaultdict, Counter

import decimdictionary as decdi 
import schizodict as schdic

from dotenv import load_dotenv
import pickle


# preload all useful stuff
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TEXT_SYNTH_TOKEN = os.getenv('TEXT_SYNTH_TOKEN')
PREFIX = os.getenv('BOT_PREFIX')

MOT_HLASKY = decdi.MOT_HLASKY
LINUX_COPYPASTA = decdi.LINUX_COPYPASTA
CESKA_LINUX_COPYPASTA = schdic.CESKA_LINUX_COPYPASTA
RECENZE = schdic.RECENZE
REPLIES = ("Ano.", "Ne.", "Perhaps.")
SADPENIS_ID = 786624092706046042;
ALLOW_CHANNELS = [1000800481397973052, 324970596360257548, 932301697836003358,959137743412269187,996357109727891456,1370041352846573630,276720867344646144,438037897023848448,979875595896901682,786625189038915625,786643519430459423,990724186550972477,998556012086829126] 

# add intents for bot and command prefix for classic command support
intents = disnake.Intents.all()
client = disnake.ext.commands.Bot(command_prefix=PREFIX, intents=intents)

MARKOV_FILE = "markov_twogram.pkl"

def build_trigram_counts(messages):
    words = " ".join(messages).split()
    if len(words) < 3:
        return {}
    markov = defaultdict(list)
    for i in range(len(words) - 2):
        key = (words[i], words[i + 1])
        next_word = words[i + 2]
        markov[key].append(next_word)
    markov_counts = {k: Counter(v) for k, v in markov.items()}
    return markov_counts

def save_trigram_counts(markov_counts, filename=MARKOV_FILE):
    with open(filename, "wb") as f:
        pickle.dump(markov_counts, f)

def load_trigram_counts(filename=MARKOV_FILE):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except Exception:
        return {}

def markov_chain(messages, max_words=20):
    # Build and save trigram counts
    markov_counts = build_trigram_counts(messages)
    save_trigram_counts(markov_counts)

    # Load trigram counts
    markov_counts = load_trigram_counts()

    if not markov_counts:
        return "Not enough data for trigram Markov chain."

    start_key = random.choice(list(markov_counts.keys()))
    sentence = [start_key[0], start_key[1]]

    for _ in range(max_words - 2):
        if start_key in markov_counts:
            next_words, weights = zip(*markov_counts[start_key].items())
            next_word = random.choices(next_words, weights=weights)[0]
            sentence.append(next_word)
            if next_word.endswith(('.', '!', '?' ':D', ':)', '😂', '🤣')):
                break
            start_key = (start_key[1], next_word)
        else:
            break

    return " ".join(sentence)

# on_ready event - happens when bot connects to Discord API
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.command()
async def say(ctx, *args):
    if str(ctx.message.author) == 'skavenlord58':
        await ctx.message.delete()
        await ctx.send(f'{" ".join(args)}')
    else:
        print(f'{ctx.message.author} tried to use "say" command.')

@client.event
async def on_message(m: Message):
    # Track last reaction time per channel
    if not hasattr(client, "last_reaction_time"):
        client.last_reaction_time = {}

    if not m.content:
        pass

    # Check if bot reacted in the last minute in this channel
    now = dt.datetime.utcnow()
    last_time = client.last_reaction_time.get(m.channel.id)
    if last_time and (now - last_time).total_seconds() < 60:
        return

    if "@grok" in m.content.lower() or "@schizo" in m.content.lower():
        # Fetch previous 50 messages (excluding the current one)
        messages = []
        async for msg in m.channel.history(limit=50, before=m):
            if msg.content:
                messages.append(msg.content)
        response = f'{random.choice(REPLIES)} Protože '
        response += markov_chain(messages)
        await m.reply(response)
        client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
    elif m.channel.id not in ALLOW_CHANNELS:
        return
    elif m.content[0] == PREFIX:
        # nutnost aby jely commandy    
        await client.process_commands(m)
    elif str(m.author) != "BasedSchizo#7762":
        if  m.content.lower().startswith("hodný bot"):
            await m.add_reaction("🙂")
            client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "windows" in m.content.lower():
            if random.randint(0, 4) == 2:
                await m.add_reaction("😔")
                client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "debian" in m.content.lower():
            if random.randint(0, 4) == 2:
                await m.add_reaction("💜")
                client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "všechno nejlepší" in m.content.lower():
            await m.add_reaction("🥳")
            await m.add_reaction("🎉")
            client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "kdo je negr?" in m.content.lower():
            await m.channel.send("Decim je negr.")
            client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "kdo je based schizo?" in m.content.lower():
            await m.channel.send("To jsem já!")
            client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "linux" in m.content.lower() and not "gnu/linux" in m.content.lower():
            if random.randint(0, 64) == 4:
                if bool(random.getrandbits(1)):
                    await m.reply(LINUX_COPYPASTA)
                else:
                    await m.reply(CESKA_LINUX_COPYPASTA)
                client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "hilfe" in m.content.lower() or "pomoc" in m.content.lower() and "pomocí" not in m.content.lower():
            if random.randint(0, 3) == 1:
                await m.reply(f'''
            „{MOT_HLASKY[random.randint(0, len(MOT_HLASKY) - 1)]}“
                                                                                - Mistr Oogway, {random.randint(470,480)} př. n. l.
            ''')
                client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "novinky.cz" in m.content.lower():
            if random.randint(0, 32) == 4:
                await m.reply("Přestaň postovat cringe, bro.")
                client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "drž hubu" in m.content.lower() and m.mentions:
            print(m.mentions)
            await m.reply("Ne, ty. 😃")
            client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "free primos" in m.content.lower() or "príma džemy" in m.content.lower():
            await m.reply(
                "Neklikejte na odkazy s názvem FREE PRIMOS. Obvykle toto bývá phishing scam. https://www.avast.com/cs-cz/c-phishing")
            client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "jsem" in m.content.lower():
            if random.randint(0, 36) == 4:
                kdo = " ".join(m.content.split("jsem")[1].split(".")[0].split(",")[0].split(" ")[1:])
                await m.reply(f'Ahoj, {kdo}. Já jsem táta.')
                client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if m.content.lower() == "kdo":
            await m.channel.send(f'kdo se ptal?')
            client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "zhongli" in m.content.lower():
            await m.reply(f'haha žongli :clown:')
            client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "aneurysm" in m.content.lower():
            await m.reply(f'https://www.youtube.com/watch?v=kyg1uxOsAUY')
            client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "schizo" in m.content.lower():
            if random.randint(0, 4) == 2: 
                await m.reply(f'doslova já')
                client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "?" in m.content.lower():
            if random.randint(0, 32) == 4:
                await m.reply(f'{random.choice(REPLIES)}')
                client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "proč " in m.content.lower() or "proc " in m.content.lower():
            if random.randint(0, 8) == 4:
                await m.reply(f'skill issue')
                client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "kiryu" in m.content.lower() or "kyriu" in m.content.lower():
            if random.randint(0, 4) == 4:
                await m.reply(f'Kiryu-chaaaaan!')
                client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "jsi" in m.content.lower():
            if random.randint(0, 16) == 4:
                kdo = " ".join(m.content.split("jsi")[1].split(" ")[1:])
                await m.reply(f'Tvoje máma je {kdo}.')
                client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "negr" in m.content.lower():
            if random.randint(0, 6969):
                await m.reply(f':+1:')
                client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "žid" in m.content.lower() and not "židle" in m.content.lower():
            if random.randint(0, 4) == 4:
                await m.reply(f'taky nesnáším židy :+1:')
                client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "židle" in m.content.lower():
            if random.randint(0, 2) == 2:
                await m.reply(f'židle jsou ok, krom monoblocu, mrdat monobloc')
                client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "buzna" in m.content.lower():
            if random.randint(0, 4) == 4:
                await m.reply(f':+1:')
                client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "israel" in m.content.lower() or "izrael" in m.content.lower():
            if random.randint(0, 4) == 4:
                await m.reply(f':pensive:')
                client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if random.randint(0, 6969) == 1:
            await m.reply(f'mňau')
            client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if random.randint(0, 500000) == 1:
            await m.reply(f'pipík')
            client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if random.randint(0, 6969) == 1:
            if m.channel.id != SADPENIS_ID:
                await m.reply(f'víš co? raději drž hubu, protože z tohohle jsem chytil rakovinu varlat')
            else:
                await m.reply(f'dissnul bych tě, ale budu hodnej, takže uhhh to bude dobrý, wishing the best for you :slight_smile: :+1:')
            client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "mama" in m.content.lower() or \
            "máma" in m.content.lower() or \
            "mami" in m.content.lower() or \
            "mommy" in m.content.lower() or \
            "mamka" in m.content.lower() or \
            "mamko" in m.content.lower():
            if random.randint(0, 64) == 1:
                try:
                    apiCall = requests.get("https://www.yomama-jokes.com/api/v1/jokes/random/")
                    if apiCall.status_code == 200:
                        await m.reply(f'{apiCall.json()["joke"]}')
                        client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
                except Exception as exc:
                    print(f"Caught exception:\n {exc}")
        if "lagtrain" in m.content.lower():
            await m.reply(f"https://www.youtube.com/watch?v=UnIhRpIT7nc")
            client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "cum zone" in m.content.lower():
            await m.reply(f"https://www.youtube.com/watch?v=j0lN0w5HVT8")
            client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "crab rave" in m.content.lower():
            await m.reply(f"https://youtu.be/LDU_Txk06tM?t=75")
            client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "já jo" in m.content.lower():
            if random.randint(0, 16) == 1:   
                await m.reply(f"já ne")
                client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "já ne" in m.content.lower():
            if random.randint(0, 16) == 1:   
                await m.reply(f"já jo")
                client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "chci se zabít" in m.content.lower() or "suicidal" in m.content.lower():
            await m.reply(f"omg don't kill yourself, ur too sexy, haha <:catcry:1158475025473622167>")
            client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "v píči" in m.content.lower():
            await m.reply(f"stejně tak moc v píči jako já včera večer v tvojí mámě loool <:kekWR:1063089161587933204>")
            client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "buisness" in m.content.lower() \
            or "bussines" in m.content.lower() \
            or "bussiness" in m.content.lower() \
            or "buissnes" in m.content.lower() \
            or "buisnes" in m.content.lower():
            await m.reply(f"KÁMO lmao ukažte si na toho blbečka, co neumí napsat 'business' XDDDD :index_pointing_at_the_viewer: příště raději napiš 'byznys' dík :)")
            client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "reminder" in m.content.lower():
            if random.randint(0, 4) == 1:
                await m.reply(f"kind reminder: ur a bitch :)")
                client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "youtu.be" in m.content.lower() or "youtube.com" in m.content.lower():
            if random.randint(0, 5) == 1:
                await m.reply(RECENZE[random.randint(0,len(RECENZE)-1)])
                client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if m.content.__len__() >= 625:
            await m.reply(f"i ain't reading all of that. im happy for you tho, or sorry that happened. depends on you")
            client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "špatný bot" in m.content.lower() or "spatny bot" in m.content.lower():
            await m.reply(f"i'm trying my best :pensive:")
            client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
        if "podle mě" in m.content.lower() or "myslím si" in m.content.lower():
            if bool(random.getrandbits(1)):
                await m.reply(f"Souhlasím.")
            else:
                await m.reply(f"Rozhodně nesouhlasím.")
            client.last_reaction_time[m.channel.id] = dt.datetime.utcnow()
client.run(TOKEN)
