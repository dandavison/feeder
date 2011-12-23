import os

from sheets import Row
from sheets import StringColumn
from sheets import FloatColumn
from sheets import IntegerColumn
from sheets import Dialect


COMMON_WORDS_FILE = os.path.join(os.path.dirname(__file__),
                                 'common_words.txt')
EXTRA_WORDS_FILE = os.path.join(os.path.dirname(__file__),
                                 'extra_words.txt')
SIMILAR_WORDSETS_FILE = os.path.join(os.path.dirname(__file__),
                                     'similar_wordsets.txt')

COMMON_WORD_RANK = 500


class Word(Row):
    Dialect = Dialect(use_header_row=True, delimiter="\t")

    rank = IntegerColumn()
    wordform = StringColumn()
    abs	= IntegerColumn()
    r = IntegerColumn()
    mod = FloatColumn()


def get_common_words():
    words = Word.file_reader(COMMON_WORDS_FILE)
    common_words = set(word.wordform for word in words
                       if word.rank <= COMMON_WORD_RANK)

    if os.path.exists(EXTRA_WORDS_FILE):
        with open(EXTRA_WORDS_FILE) as fp:
            common_words |= set(line.strip()
                                for line in fp.readlines())

    return common_words


def get_similar_wordsets():
    # if not os.path.exists(SIMILAR_WORDSETS_FILE):
    #     return []
    with open(SIMILAR_WORDSETS_FILE) as fp:
        return [set(line.strip().split())
                for line in fp.readlines()]
