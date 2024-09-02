import random
import os
from string import ascii_lowercase as lowercase

with open(os.path.join(os.path.dirname(__file__), "common-words-982.txt"), "r", encoding="utf-8") as f:
    WORD_DICT = f.read().split("\n")


def genname_letters():
    return "".join([random.choice(lowercase) for _ in range(4)])


def genname_words():
    return "".join([random.choice(WORD_DICT) for _ in range(2)])


if __name__ == "__main__":
    print(genname_letters())
    print(genname_words())
