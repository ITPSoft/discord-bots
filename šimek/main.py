import json
import os
import random
import datetime as dt
import disnake
from disnake import Message
import requests
from collections import defaultdict, Counter

import schizodict as schdic

from dotenv import load_dotenv
import pickle


# preload all useful stuff
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TEXT_SYNTH_TOKEN = os.getenv('TEXT_SYNTH_TOKEN')
REPLIES = ("Ano.", "Ne.","Ano.", "Ne.", "Perhaps.", "Ano.", "Ne.", "Perhaps." ,"Možná.", "Pravděpodobně.", "bruh", "nemám tušení") #repeat ano/ne/perhaps to give it more common occurence

MOT_HLASKY = schdic.MOT_HLASKY
LINUX_COPYPASTA = schdic.LINUX_COPYPASTA
RECENZE = schdic.RECENZE
ALLOW_CHANNELS = [1420168841501216873, 1000800481397973052, 324970596360257548, 932301697836003358,959137743412269187,996357109727891456,1370041352846573630,276720867344646144,438037897023848448,979875595896901682,786625189038915625,786643519430459423,990724186550972477,998556012086829126] 
MARKOV_FILE = "markov_twogram.pkl"

# add intents for bot and command prefix for classic command support
intents = disnake.Intents.all()
client = disnake.Client(intents=intents)

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

# we use a evil class magic to hack match case to check for substrings istead of exact matches
# https://stackoverflow.com/a/78046484
class Substring(str):
    def __eq__(self, other):
            return self.__contains__(other)
# evil hack end

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
    if str(m.author) == "šimek#3885":
        return
    if not hasattr(client, "last_reaction_time"):
        client.last_reaction_time = {}    
    now = dt.datetime.now()
    last_time = client.last_reaction_time.get(m.channel.id)
    if last_time and (now - last_time).total_seconds() < 10:
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

    # we are matching whole substrings now, not exact matches, only one case will be executed, if none match, default case will be executed 
    match Substring(m.content.lower()):
        case "hodný bot":
            await do_response("🙂", m, chance=1, reaction=True)
        case "windows":
            await do_response("😔", m, chance=4, reaction=True)
        case "debian":
            await do_response("💜", m, chance=4, reaction=True)
        case "všechno nejlepší":
            await do_response("🥳", m, chance=1, reaction=True)
        case "linux" | "gnu/linux":
            await do_response("🐧", m, chance=10, reaction=True)
            await do_response(LINUX_COPYPASTA, m, chance=10)
        case "hilfe" | "pomoc" | "pomocí" | "help":
            await do_response(f'''„{MOT_HLASKY[random.randint(0, len(MOT_HLASKY) - 1)]}“
                                                                                - Mistr Oogway, {random.randint(470,480)} př. n. l.''', m, chance=3)        
        case "novinky":
            await do_response("😖", m, chance=3, reaction=True)
            await do_response("Přestaň postovat cringe, bro.", m, chance=10)
        case "drž hubu":
            await do_response("ok", m, chance=1)
            client.last_reaction_time[m.channel.id] = dt.datetime.now() + dt.timedelta(minutes=5) # 5 minute timeout after being told to shut up
            return # skip setting the time again at the end of the function    
        case "jsem":
            await do_response(f'Ahoj, {" ".join(m.content.split("jsem")[1].split(".")[0].split(",")[0].split(" ")[1:])}. Já jsem táta.', m, chance=4)    
        case "kdo":
            await do_response('kdo se ptal?', m, chance=3)
        case "anureysm" | "aneuerysm" | "brain damage" | "brian damage":
            await do_response('https://www.youtube.com/watch?v=kyg1uxOsAUY', m, chance=2)
        case "schizo":
            await do_response('never forgeti', m, chance=4)    
        case "?":
            await do_response(f'{random.choice(REPLIES)}', m, chance=6)        
        case "proč" | "proc":
            await do_response("skill issue", m, chance=8)
        case "jsi":
            await do_response(f'Tvoje máma je {" ".join(m.content.split("jsi")[1].split(" ")[1:])}.', m, chance=8)
        case "negr":
            await do_response(':sad:', m, chance=10)
            await do_response(':+1:', m, chance=30)
        case "israel" | "izrael":
            await do_response(':pensive:', m, chance=5)
        case "mama" | "mamá" | "mami" | "mommy" | "mamka" | "mamko":
            apiCall = requests.get("https://www.yomama-jokes.com/api/v1/jokes/random/")
            if apiCall.status_code == 200:
                await do_response(f'{apiCall.json()["joke"]}', m, chance=4)
        case "lagtrain":
            await do_response("https://www.youtube.com/watch?v=UnIhRpIT7nc", m, chance=1)
        case "cum zone":
            await do_response("https://www.youtube.com/watch?v=j0lN0w5HVT8", m, chance=1)
        case "crab rave":
            await do_response("https://youtu.be/LDU_Txk06tM?t=75", m, chance=1)
        case "já jo":
            await do_response("já ne", m, chance=2)
        case "já ne":
            await do_response("já jo", m, chance=2)
        case "chci se zabít" | "suicidal":
            await do_response("omg don't kill yourself, ur too sexy, haha",m, chance=1)
        case "v píči" | "v pici":
            await do_response("stejně tak moc v píči jako já včera večer v tvojí mámě loool",m,chance=10)
        case "buisness" | "buisnes" | "buissnes" | "bussiness" | "bussines":
            await do_response("KÁMO lmao ukažte si na toho blbečka, co neumí napsat 'business' XDDDD :index_pointing_at_the_viewer: příště raději napiš 'byznys' dík :)",m,chance=1)
        case "reminder":
            await do_response("kind reminder: ur a bitch :)", m, chance=4)
        case "youtu.be" | "youtube.com":
            await do_response(RECENZE[random.randint(0,len(RECENZE)-1)],m,chance=1)
        case "špatný bot" | "spatny bot":
            await do_response("i'm trying my best :pensive:",m,chance=1)
        case "twitter" | "twiter":
            await do_response("preferuji #twitter-péro",m,chance=1)
        case "podle mě" | "myslím si" | "myslim si":
            await do_response(f'{random.choice(["souhlasím","nesouhlasím",""])}')      
        case _:
            if random.randint(1, 5000) == 1:
                messages = []
                async for msg in m.channel.history(limit=50, before=m):
                    if msg.content:
                        messages.append(msg.content)
                response += markov_chain(messages)
                await m.reply(response)

            await do_response(f'{random.choice(
                ["Mňau",
                 "víš co? raději drž hubu, protože z tohohle jsem chytil rakovinu varlat",
                 "dissnul bych tě, ale budu hodnej, takže uhhh to bude dobrý :+1:",
                 "https://www.youtube.com/watch?v=kyg1uxOsAUY",
                 ])}', m, chance=500000)     
            await do_response(f'{random.choice([":kekWR:",":kekW:",":heart:",":5head:",":adampat:",":catworry:",":maregg:",":pepela:",":pog:",":333:"])}', m,reaction=True, chance=1000)                 
    client.last_reaction_time[m.channel.id] = dt.datetime.now() 
client.run(TOKEN)
