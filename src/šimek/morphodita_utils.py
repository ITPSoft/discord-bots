import logging
import os.path as osp
from dataclasses import dataclass

from ufal.morphodita import Tagger, Forms, TaggedLemmas, TokenRanges, Morpho, TaggedLemmasForms
from šimek.utils import run_async, truncate_emojis

logger = logging.getLogger(__name__)

logger.info("Preparing to load tagger.")
# we can not optimize the loading time, because the C code blocks GIL, so we can not postpone it.
cur_dir = osp.dirname(__file__)
tagger_path = "czech-morfflex2.0-pdtc1.0-220710/czech-morfflex2.0-pdtc1.0-220710.tagger"
tagger = Tagger.load(osp.join(cur_dir, tagger_path))
dict_path = "./czech-morfflex2.0-pdtc1.0-220710/czech-morfflex2.0-220710.dict"
morpho = Morpho.load(osp.join(cur_dir, dict_path))
if not tagger:
    raise Exception(f"Cannot load tagger from file {tagger_path}")
tokenizer = tagger.newTokenizer()
if tokenizer is None:
    raise Exception("No tokenizer is defined for the supplied model!")
logger.info("Tagger loaded.")


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


async def find_self_reference_a(text: str, keyword: str, use_vocative: bool) -> tuple[bool, str, int]:
    return await run_async(find_self_reference, text, keyword, use_vocative)


def find_self_reference(text: str, keyword: str, use_vocative: bool) -> tuple[bool, str, int]:
    lemmas_forms = TaggedLemmasForms()
    toks, word_count, keyword_idx, _ = parse_sentence_with_keyword(text, [keyword], False)
    if word_count == 0:  # keyword is not separate work, but substring in a word
        return False, "", 0
    # toks, word_count, keyword_idx = parse_sentence_with_keyword(text, keyword, True)
    # kontroluje, zda je tam nějaké podstatné jméno jednotného čísla v prvním pádu
    singular_noun = any([tok.tag_matches("NN*S1") for tok in toks])
    # pokud je tam další sloveso přítomního času, není to odkaz na sebe
    other_present_verb = any([tok.tag_matches("VB") and tok.text != keyword for tok in toks])
    # pokud je tam další sloveso minulého času, tak "jsem" patří k němu
    other_past_verb = any([tok.tag_matches("Vp******R") and tok.text != keyword for tok in toks])
    valid_me = singular_noun and not other_present_verb and not other_past_verb
    # správné skloňování
    if use_vocative:
        nouns2vocative(lemmas_forms, toks, text)
    result = "".join([tok.text if i == 0 else tok.text_before + tok.text for i, tok in enumerate(toks[keyword_idx:])])
    return valid_me, result, word_count


def nouns2vocative(lemmas_forms: TaggedLemmasForms, toks: list[Token], text: str):
    for tok in toks:
        try:
            if not tok.tag_matches("NN*S1"):
                continue
            tok_tags = tok.lemma_tag
            tok_tags = tok_tags[:4] + "5" + tok_tags[5:]
            morpho.generate(tok.lemma, tok_tags, morpho.GUESSER, lemmas_forms)
            if len(lemmas_forms) == 0:  # unknown word to morphodita, no variant generated
                return
            tok.text = next(form.form for lemma_forms in lemmas_forms for form in lemma_forms.forms)
        except Exception as e:
            logger.error(f"Selhalo skloňování v {text=}: {tok=}", exc_info=e)


async def needs_help_a(text: str) -> bool:
    return await run_async(needs_help, text)


def needs_help(text: str) -> bool:
    keywords = ["pomoc", "pomoci", "pomoct"]
    toks, word_count, _, nested = parse_sentence_with_keyword(text, keywords, after_keyword=False, match_lemma=True)
    if nested:
        return False
    if any(tok.tag_matches("NN*S4") and tok.lemma in keywords for tok in toks) or any(
        (tok.tag_matches("Vf") or tok.tag_matches("Vi")) and tok.lemma in keywords
        for tok in toks  # sloveslo v infinitivu nebo imperativu
    ):
        if len(toks) == 1:
            return True
        # volání o pomoc shortcut
        help_ask = any(
            tok.tag_matches("Vi-****2**A") and tok.lemma in keywords for tok in toks
        )  # sloveso přítomného času jednotného čísla, pozitivní a první osoba, jako chci pomoct apod.
        help_ask_me = any(tok.tag_matches("P***3") and tok.lemma in ["já"] for tok in toks)
        if help_ask and help_ask_me:
            return True
        verb_present = any(
            tok.tag_matches("VB-S***1P*A")
            and tok.lemma not in ["být"]  # být apod. je moc obecné a způsobuje false positivy
            for tok in toks
        )  # sloveso přítomného času jednotného čísla, pozitivní a první osoba, jako chci pomoct apod.
        verb_past = any(tok.tag_matches("V*******R") for tok in toks)  # sloveso minulého času
        verb_negated = any(tok.tag_matches("V*********N") for tok in toks)  # jen když u sloves není zápor
        if verb_past or verb_negated:
            return False
        if verb_present:
            return True
    return False


def parse_sentence_with_keyword(
    text: str, keywords: list[str], after_keyword: bool, match_lemma: bool = False
) -> tuple[list[Token], int, int, bool]:
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
    has_word = False
    nesting_char = '"'
    cur_nested = False  # assuming only 1 level of " nesting
    keyword_nested = False
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
                if tok.text == nesting_char:
                    cur_nested = not cur_nested
                sentence_end = True
                if len(toks) > 0 and has_word:
                    break
            # pokud je after keyword true, přidáváme až po keywordu, ale keyword samotný vynecháváme
            if (has_word and not sentence_end) or (not after_keyword):
                toks.append(tok)
            # jsem, pomoc apod.
            if (tok.text in keywords and not match_lemma) or (tok.lemma in keywords and match_lemma):
                keyword_nested = cur_nested
                has_word = True
                keyword_idx = len(toks)
        if has_word and sentence_end:
            break
    if has_word:
        return toks, word_count, keyword_idx, keyword_nested
    else:
        return [], 0, -1, keyword_nested
