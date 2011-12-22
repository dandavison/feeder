import sys
from itertools import combinations

from words.models import Item, Combination

from feeder_cli import get_common_words, parse, log



def analyze(kmax):
    common_words = set(get_common_words())

    for k in range(1, kmax + 1):
        print '\n%d-word analysis...' % k
        digest_feeds(k, common_words)


def digest_feeds(k, common_words):
    for item in Item.objects.all():
        words = set(parse(item.value)) - common_words
        for wordset in combinations(words, k):
            combn, created = Combination.objects.get_or_create(length=k, text=' '.join(wordset))
            combn.items.add(item)
            combn.save()


if __name__ == '__main__':
    analyze(kmax=2)
