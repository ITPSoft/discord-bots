import time

from ufal.morphodita import *

from utils import truncate_emojis, find_self_reference

# load from file
with open("sentences.txt", "r", encoding="utf-8") as f:
    texts = f.readlines()
texts = [truncate_emojis(x.strip().lower()) for x in texts]

# measure time
start = time.monotonic()
word_count = 0

keyword = "jsem"

for text in texts:
    ok, sentence, word_count_add = find_self_reference(text, keyword, True)
    word_count += word_count_add
    print(f"{"správná" if ok else "špatná"}: "  + sentence)

end = time.monotonic()
print("Time in seconds: ", end - start)
print("Word count: ", word_count)
print("Words per second: ", word_count / (end - start))
