import sys
from itertools import combinations, chain
from collections import defaultdict

from fish import ProgressFish

from words.models import Item, Combination

from feeder_cli import get_common_words, parse, log



def analyze(kmax):
    common_words = set(get_common_words())

    for k in range(2, kmax + 1):
        print '\n%d-word analysis...' % k
        digest_feeds(k, common_words)


def digest_feeds(k, common_words):
    items = Item.objects.all()

    print len(items)

    words = set(chain(*(parse(value) for value in set(item.value for item in items))))
    print len(words)
    print len(words) * (len(words) - 1) / 2
    import codecs
    with codecs.open('words.txt', 'w', 'utf-8') as fp:
        fp.write('\n'.join(words) + '\n')
    0/0

    item_id2wordsets = defaultdict(set)
    n_comb = 0
    for item in items:
        for wordset in combinations(set(parse(item.value)) - common_words, k):
            item_id2wordsets[item.id].add(wordset)
            n_comb += 1

    print n_comb



    wordsets = set(wordset
                   for value in set(item.value for item in items)
                   for wordset in combinations(set(parse(value)) - common_words, k))
    print len(wordsets)

    # combns = []
    # fish = ProgressFish(total=len(wordsets))
    # for i, wordset in enumerate(wordsets):
    #     text = ' '.join(wordset)
    #     combns.append(Combination.objects.create(length=k, text=text))
    #     fish.animate(amount=i)


    # fish = ProgressFish(total=len(items))
    # for i, item in enumerate(items):
    #     words = set(parse(item.value)) - common_words
    #     combns = []
    #     for wordset in set(combinations(words, k)):
    #         text = ' '.join(wordset)
    #         kwargs = {'length': k, 'text': text}
    #         combn = Combination.objects.get(**kwargs)
    #         item.combinations.add(combn)

    #     fish.animate(amount=i)

    #     item.save()


if __name__ == '__main__':
    Combination.objects.all().delete()
    analyze(kmax=2)
