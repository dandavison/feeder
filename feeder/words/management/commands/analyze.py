import sys
from itertools import combinations

from fish import ProgressFish

from words.models import Item, Combination

from feeder_cli import get_common_words, parse, log



def analyze(kmax):
    common_words = set(get_common_words())

    for k in range(1, kmax + 1):
        print '\n%d-word analysis...' % k
        digest_feeds(k, common_words)


def digest_feeds(k, common_words):
    items = Item.objects.all()
    fish = ProgressFish(total=len(items))
    texts = set()
    for i, item in enumerate(items):
        words = set(parse(item.value)) - common_words
        combns = []
        for wordset in combinations(words, k):
            text = ' '.join(wordset)
            texts.add(text)
            combn, created = Combination.objects.get_or_create(length=k, text=text)
            combn.items.add(item)
            combn.save()

        fish.animate(amount=i)


if __name__ == '__main__':
    analyze(kmax=2)
