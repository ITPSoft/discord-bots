import random
from typing import Iterable

import aiohttp
from disnake import Message


def find_who(content: str, verb: str) -> str:
    do_konce_vety = content.split(verb)[1]
    for interpunkce in [".", ",", "!", "?"]:
        do_konce_vety = do_konce_vety.split(interpunkce)[0]
    kdo = " ".join(do_konce_vety.split(" ")[1:])
    return kdo


def has_any(content: str, words: Iterable) -> bool:
    return any(word in content for word in words)


async def random_joke(m: Message):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        try:
            async with session.get("https://www.yomama-jokes.com/api/v1/jokes/random/") as response:
                if response.status == 200:
                    joke = await response.json()
                    await m.reply(f"{joke['joke']}")
        except Exception as exc:
            print(f"Caught exception:\n {exc}")


async def hate_comment(content: str, m: Message) -> None:
    terms = [
        ("negr", "negry", 6969),
        ("žid", "židy", 8000),
        ("buzna", "buzny", 3000),
    ]
    for singular, plural, chance in terms:
        if has_any(content, [singular, plural]):
            if random.randint(0, chance):
                await m.reply(f"taky nesnáším {plural} :+1:")


async def bot_validate(content: str, m: Message):
    if content.startswith("hodný bot") or "good bot" in content:
        await m.add_reaction("🙂")
    if content.startswith("zlý bot") or has_any(content, ["bad bot", "naser si bote", "si naser bote"]):
        await m.add_reaction("😢")
