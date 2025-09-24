import json
import os
import random
import datetime as dt
import disnake
from disnake import Message
from disnake.ext import commands
import requests
from collections import defaultdict, Counter

import schizodict as schdic

from dotenv import load_dotenv
import pickle


# preload all useful stuff
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TEXT_SYNTH_TOKEN = os.getenv('TEXT_SYNTH_TOKEN')
PREFIX = os.getenv('BOT_PREFIX')
REPLIES = ("Ano.", "Ne.", "Perhaps.")

MOT_HLASKY = schdic.MOT_HLASKY
LINUX_COPYPASTA = schdic.LINUX_COPYPASTA
RECENZE = schdic.RECENZE
ALLOW_CHANNELS = [1000800481397973052, 324970596360257548, 932301697836003358,959137743412269187,996357109727891456,1370041352846573630,276720867344646144,438037897023848448,979875595896901682,786625189038915625,786643519430459423,990724186550972477,998556012086829126] 
MARKOV_FILE = "markov_twogram.pkl"

# add intents for bot and command prefix for classic command support
intents = disnake.Intents.all()
client = disnake.ext.commands.Bot(command_prefix=PREFIX, intents=intents)

# Trigram Markov chain functions

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

def markov_chain(messages, max_words=30):
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
            if next_word.endswith(('.', '!', '?' ':', '😂', '🤣')):
                break
            start_key = (start_key[1], next_word)
        else:
            break

    return " ".join(sentence)

# trigram Markov chain functions end


async def do_response(reply: str, m: Message, chance=10, reaction=False):
    '''
    reply: str - text or emoji to reply with
    m: Message - message object to reply to
    chance: int - 1 in `chance` probability to reply
    reaction: bool - if True, add reaction instead of reply
    '''
    if random.randint(1, chance) == 1:
        if reaction:
            await m.add_reaction(reply)
        else:
            await m.reply(reply)

# on_ready event - happens when bot connects to Discord API
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(m: Message):
    if not m.content:
        return
    if str(m.author) == "BasedSchizo#7762":
        return
    if not hasattr(client, "last_reaction_time"):
        client.last_reaction_time = {}    
    now = dt.datetime.utcnow()
    last_time = client.last_reaction_time.get(m.channel.id)
    if last_time and (now - last_time).total_seconds() < 60:
        return            
    
    # TODO change discord user id after new name
    if "@grok" in m.content.lower() or "@schizo" in m.content.lower():
        # Fetch previous 50 messages (excluding the current one)
        messages = []
        async for msg in m.channel.history(limit=50, before=m):
            if msg.content:
                messages.append(msg.content)
        response = f'{random.choice(REPLIES)} Protože '
        response += markov_chain(messages)
        await m.reply(response)

    if m.channel.id not in ALLOW_CHANNELS:
        return
    
    match m.content.lower():
        case "hodný bot":
            do_response("🙂", m, chance=1, reaction=True)
        case "windows":
            do_response("😔", m, chance=2, reaction=True)
        case "debian":
            do_response("💜", m, chance=2, reaction=True)
        case "všechno nejlepší":
            do_response("🥳", m, chance=1, reaction=True)
        case "kdo je negr?":
            do_response("Decim je negr.", m, chance=1)
        case "kdo je based?":
            do_response("To jsem já!", m, chance=1)
        case "linux" | "gnu/linux":
            do_response("🐧", m, chance=10, reaction=True)
            do_response(LINUX_COPYPASTA, m, chance=10)
        case "hilfe" | "pomoc" | "pomocí" | "help":
            do_response(f'''„{MOT_HLASKY[random.randint(0, len(MOT_HLASKY) - 1)]}“
                                                                                - Mistr Oogway, {random.randint(470,480)} př. n. l.''', m, chance=3)        
        case "novinky":
            do_response("😖", m, chance=3, reaction=True)
            do_response("Přestaň postovat cringe, bro.", m, chance=10)
        case "drž hubu":
            do_response("Ne, ty. 😃", m, chance=1)
        case "jsem":
            do_response(f'Ahoj, {" ".join(m.content.split("jsem")[1].split(".")[0].split(",")[0].split(" ")[1:])}. Já jsem táta.', m, chance=4)    
        case "kdo":
            do_response('kdo se ptal?', m, chance=3)
        case "anureysm" | "aneuerysm" | "brain damage" | "brian damage":
            do_response('https://www.youtube.com/watch?v=kyg1uxOsAUY', m, chance=1)
        case "schizo":
            do_response('never forgeti', m, chance=4)    
        case "?":
            do_response(f'{random.choice(REPLIES)}', m, chance=6)        
        case "proč" | "proc":
            do_response("skill issue", m, chance=8)
        case "jsi":
            do_response(f'Tvoje máma je {" ".join(m.content.split("jsi")[1].split(" ")[1:])}.', m, chance=8)
        case "negr":
            do_response(':sad:', m, chance=10)
            do_response(':+1:', m, chance=30)
        case "israel" | "izrael":
            do_response(':pensive:', m, chance=5)
        case "mama" | "mamá" | "mami" | "mommy" | "mamka" | "mamko":
            apiCall = requests.get("https://www.yomama-jokes.com/api/v1/jokes/random/")
            if apiCall.status_code == 200:
                do_response(f'{apiCall.json()["joke"]}', m, chance=4)
        case "lagtrain":
            do_response("https://www.youtube.com/watch?v=UnIhRpIT7nc", m, chance=1)
        case "cum zone":
            do_response("https://www.youtube.com/watch?v=j0lN0w5HVT8", m, chance=1)
        case "crab rave":
            do_response("https://youtu.be/LDU_Txk06tM?t=75", m, chance=1)
        case "já jo":
            do_response("já ne", m, chance=2)
        case "já ne":
            do_response("já jo", m, chance=2)
        case "chci se zabít" | "suicidal":
            do_response("omg don't kill yourself, ur too sexy, haha",m, chance=1)
        case "v píči" | "v pici":
            do_response("stejně tak moc v píči jako já včera večer v tvojí mámě loool",m,chance=10)
        case "buisness" | "buisnes" | "buissnes" | "bussiness" | "bussines":
            do_response("KÁMO lmao ukažte si na toho blbečka, co neumí napsat 'business' XDDDD :index_pointing_at_the_viewer: příště raději napiš 'byznys' dík :)",m,chance=1)´
        case "reminder":
            do_response("kind reminder: ur a bitch :)", m, chance=4)
        case "youtu.be" | "youtube.com":
            do_response(RECENZE[random.randint(0,len(RECENZE)-1)],m,chance=1)
        case "špatný bot" | "spatny bot":
            do_response("i'm trying my best :pensive:",m,chance=1)
        case "podle mě" | "myslím si" | "myslim si":
            do_response(f'{random.choice(["souhlasím","nesouhlasím",""])}')      
        case _:
            do_response("Mňau", m, chance=10000)
            do_response("Pipík", m, chance=500000)
            do_response("víš co? raději drž hubu, protože z tohohle jsem chytil rakovinu varlat", m, chance=500000)
            do_response("dissnul bych tě, ale budu hodnej, takže uhhh to bude dobrý :+1:", m, chance=1000000)
            do_response('https://www.youtube.com/watch?v=kyg1uxOsAUY', m, chance=1000000)
                       
   client.last_reaction_time[m.channel.id] = dt.datetime.utcnow() 
client.run(TOKEN)
