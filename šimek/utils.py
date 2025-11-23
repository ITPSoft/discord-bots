import asyncio
import random
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Iterable, Any

import aiohttp
from disnake import Message
from ufal.morphodita import Tagger, Forms, TaggedLemmas, TokenRanges, Morpho, TaggedLemmasForms


def truncate_emojis(text):
    # emojis are sometimes analyzed as noun
    emoji_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"  # emoticons
        "\U0001f300-\U0001f5ff"  # symbols & pictographs
        "\U0001f680-\U0001f6ff"  # transport & map symbols
        "\U0001f1e0-\U0001f1ff"  # flags (iOS)
        "\U00002702-\U000027b0"  # other symbols
        "\U000024c2-\U0001f251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r"", text)


print("Loading tagger: ")
tagger_path = "./czech-morfflex2.0-pdtc1.0-220710/czech-morfflex2.0-pdtc1.0-220710.tagger"
tagger = Tagger.load(tagger_path)
dict_path = "./czech-morfflex2.0-pdtc1.0-220710/czech-morfflex2.0-220710.dict"
morpho = Morpho.load(dict_path)

if not tagger:
    print(f"Cannot load tagger from file {tagger_path}")
    sys.exit(1)

print("Tagger loaded.")

tokenizer = tagger.newTokenizer()
if tokenizer is None:
    print("No tokenizer is defined for the supplied model!")
    sys.exit(1)


@dataclass
class Token:
    text_before: str
    lemma: str
    lemma_tag: str
    text: str

    def tag_matches(self, tag: str) -> bool:
        # * means anything
        for i, char in enumerate(tag):
            if char != "*" and char != self.lemma_tag[i]:
                return False
        return True


# CPU-heavy věci budeme dělat v separátním threadu
executor = ThreadPoolExecutor(max_workers=1)


async def run_async(func: callable, *args: Any) -> tuple[bool, str, int]:
    return await asyncio.get_running_loop().run_in_executor(executor, func, *args)


def find_self_reference(text: str, keyword: str, use_vocative: bool) -> tuple[bool, str, int]:
    lemmas_forms = TaggedLemmasForms()
    toks, word_count = parse_sentence_with_keyword(text, keyword, True)
    # kontroluje, zda je tam nějaké podstatné jméno jednotného čísla v prvním pádu
    singular_noun = any([tok.tag_matches("NN*S1") for tok in toks])
    # pokud je tam další sloveso, je to špatně
    any_verb = any([tok.tag_matches("VB") for tok in toks])
    valid_me = singular_noun and not any_verb
    # správné skloňování
    if use_vocative:
        nouns2vocative(lemmas_forms, toks)
    result = "".join([tok.text if i == 0 else tok.text_before + tok.text for i, tok in enumerate(toks)])
    return valid_me, result, word_count


def nouns2vocative(lemmas_forms: TaggedLemmasForms, toks: list[Token]):
    try:
        for tok in toks:
            if not tok.tag_matches("NN*S1"):
                continue
            tok_tags = tok.lemma_tag
            tok_tags = tok_tags[:4] + "5" + tok_tags[5:]
            morpho.generate(tok.lemma, tok_tags, morpho.GUESSER, lemmas_forms)
            tok.text = next(form.form for lemma_forms in lemmas_forms for form in lemma_forms.forms)
    except:
        print("Selhalo skloňování")


def needs_help(text: str) -> bool:
    toks, word_count = parse_sentence_with_keyword(text, "pomoc", False)
    if any(tok.tag_matches("NN*S") and tok.lemma == "pomoc" for tok in toks) or any(tok.tag_matches("Vf") and tok.lemma == "pomoci" for tok in toks):
        if len(toks) == 1:
            return True
        if any(tok.tag_matches("VB-S***1P*A")
               # and tok.lemma in ["potřebovat", "chtít"]
        for tok in toks) and not any(tok.tag_matches("V*******R") for tok in toks):   # jen přítomný čas a žádný záporný
            return True
    return False


def parse_sentence_with_keyword(text: str, keyword: str, after_keyword: bool) -> tuple[list[Token], int]:
    text = truncate_emojis(text.lower())
    word_count = 0
    forms = Forms()
    lemmas = TaggedLemmas()
    tokens = TokenRanges()
    # Tag
    tokenizer.setText(text)
    toks = []
    t_iter = 0
    while tokenizer.nextSentence(forms, tokens):
        has_word = False
        sentence_end = False
        toks = []
        tagger.tag(forms, lemmas)

        for i in range(len(lemmas)):
            word_count += 1
            if sentence_end:
                has_word = False
                sentence_end = False
                toks = []

            lemma = lemmas[i]
            token = tokens[i]

            tok = Token(
                text[t_iter: token.start], lemma.lemma, lemma.tag, text[token.start: token.start + token.length]
            )
            t_iter = token.start + token.length

            # interpunkce
            if tok.lemma_tag[0] == "Z":
                sentence_end = True
                if len(toks) > 0:
                    break
            # pokud je after keyword true, přidáváme až po keywordu, ale keyword samotný vynecháváme
            if (has_word and not sentence_end) or (not after_keyword):
                toks.append(tok)
            # jsem
            if tok.text == keyword:
                has_word = True
        if has_word and sentence_end:
            break
    return toks, word_count


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
