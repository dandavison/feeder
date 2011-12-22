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

    wordsets = set(wordset
                   for value in set(item.value for item in items)
                   for wordset in combinations(set(parse(value)) - common_words, k))

    combns = []
    fish = ProgressFish(total=len(wordsets))
    for i, wordset in enumerate(wordsets):
        text = ' '.join(wordset)
        combns.append(Combination.objects.create(length=k, text=text))
        fish.animate(amount=i)


    fish = ProgressFish(total=len(items))
    for i, item in enumerate(items):
        words = set(parse(item.value)) - common_words
        combns = []
        for wordset in set(combinations(words, k)):
            text = ' '.join(wordset)
            kwargs = {'length': k, 'text': text}
            combn = Combination.objects.get(**kwargs)
            item.combinations.add(combn)

        fish.animate(amount=i)

        item.save()


if __name__ == '__main__':
    Combination.objects.all().delete()
    analyze(kmax=2)
