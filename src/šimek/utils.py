import asyncio
import datetime as dt
import os.path as osp
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Callable

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

cur_dir = osp.dirname(__file__)
tagger_path = "czech-morfflex2.0-pdtc1.0-220710/czech-morfflex2.0-pdtc1.0-220710.tagger"
tagger = Tagger.load(osp.join(cur_dir, tagger_path))
dict_path = "./czech-morfflex2.0-pdtc1.0-220710/czech-morfflex2.0-220710.dict"
morpho = Morpho.load(osp.join(cur_dir, dict_path))
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


async def run_async(func: Callable[..., Any], *args: Any) -> tuple[bool, str, int]:
    return await asyncio.get_running_loop().run_in_executor(executor, func, *args)


async def find_self_reference_a(text: str, keyword: str, use_vocative: bool) -> tuple[bool, str, int]:
    return await run_async(find_self_reference, text, keyword, use_vocative)


def find_self_reference(text: str, keyword: str, use_vocative: bool) -> tuple[bool, str, int]:
    lemmas_forms = TaggedLemmasForms()
    # toks, word_count, keyword_idx = parse_sentence_with_keyword(text, keyword, False)
    toks, word_count, keyword_idx = parse_sentence_with_keyword(text, keyword, True)
    # kontroluje, zda je tam nějaké podstatné jméno jednotného čísla v prvním pádu
    singular_noun = any([tok.tag_matches("NN*S1") for tok in toks])
    # pokud je tam další sloveso, je to špatně
    any_verb = any([tok.tag_matches("VB") for tok in toks])
    valid_me = singular_noun and not any_verb
    # správné skloňování
    if use_vocative:
        nouns2vocative(lemmas_forms, toks)
    # result = "".join([tok.text if i == 0 else tok.text_before + tok.text for i, tok in enumerate(toks[keyword_idx:])])
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
    toks, word_count, _ = parse_sentence_with_keyword(text, "pomoc", False)
    if any(tok.tag_matches("NN*S") and tok.lemma == "pomoc" for tok in toks) or any(
        tok.tag_matches("Vf") and tok.lemma == "pomoci" for tok in toks
    ):
        if len(toks) == 1:
            return True
        if any(
            tok.tag_matches("VB-S***1P*A")
            # and tok.lemma in ["potřebovat", "chtít"]
            for tok in toks
        ) and not any(tok.tag_matches("V*******R") for tok in toks):  # jen přítomný čas a žádný záporný
            return True
    return False


def parse_sentence_with_keyword(text: str, keyword: str, after_keyword: bool) -> tuple[list[Token], int, int]:
    text = truncate_emojis(text.lower())
    word_count = 0
    keyword_idx = 0
    forms = Forms()
    lemmas = TaggedLemmas()
    tokens = TokenRanges()
    # Tag
    tokenizer.setText(text)
    toks: list[Token] = []
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
                text[t_iter : token.start], lemma.lemma, lemma.tag, text[token.start : token.start + token.length]
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
                keyword_idx = len(toks)
        if has_word and sentence_end:
            break
    return toks, word_count, keyword_idx


def format_time_ago(time: dt.datetime) -> str:
    """Format a datetime as a relative time string (e.g., '2 hours, 15 minutes ago')."""
    now = dt.datetime.now()
    delta = now - time
    total_seconds = int(delta.total_seconds())
    is_future = total_seconds < 0
    total_seconds = abs(total_seconds)

    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0 or not parts:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

    time_ago = ", ".join(parts)
    if is_future:
        return f"in {time_ago}"
    else:
        return f"{time_ago} ago"
