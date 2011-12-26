import os
from operator import itemgetter
from subprocess import Popen, PIPE

from django.db import settings

from utils import parse
from words.models import Entry, Item


MAX_N_WORDSETS = 1000
MIN_N_WORDSETS = 100
MINIMUM_WORDSET_SIZE = 3
MAXIMUM_WORDSET_SIZE = 3
INFILE = '/tmp/in'


def get_new_wordsets(start_time):
    entry_pub_times = sorted(Entry.objects.values_list('pub_time', flat=True))
    earliest, latest = entry_pub_times[0], entry_pub_times[-1]
    old_items, old_wordsets = get_frequent_wordsets(earliest, start_time)
    new_items, new_wordsets = get_frequent_wordsets(start_time, latest)

    old_set = set(wordset[0] for wordset in old_wordsets)
    for wordset, freq in new_wordsets:
        if wordset in old_set:
            new_wordsets.remove((wordset, freq))

    return new_items, new_wordsets


def get_frequent_wordsets(start_time, end_time):
    with open(INFILE, 'w') as fp:
        items = dump_wordsets(fp,
                              entry__pub_time__range=(start_time, end_time))

    for support in range(8, 0, -1):
        print 'Trying support=%d' % support
        with open(INFILE) as stdin:
            wordsets = _get_frequent_wordsets(stdin, support, start_time, end_time)
        print 'Got %d wordsets' % len(wordsets)
        if len(wordsets) > MIN_N_WORDSETS:
            return items, wordsets

    print 'Warning: Failed to find any frequent wordsets'
    return items, []


def _get_frequent_wordsets(stdin, support, start_time, end_time):
    executable = os.path.join(settings.SITE_DIRECTORY,
                              '../bin/apriori')

    cmd = [executable,
           '-s%s' % support,
           '-m%s' % MINIMUM_WORDSET_SIZE,
           '-n%s' % MAXIMUM_WORDSET_SIZE,
           '-v %S',
           '-', '-']
    print ' '.join(cmd)

    finder = Popen(cmd, stdin=PIPE, stdout=PIPE)
    finder.stdin.write(stdin.read())
    finder.stdin.close()

    wordsets = []
    for line_num, line in enumerate(finder.stdout):
        if line_num > MAX_N_WORDSETS:
            print 'Warning: more than %d wordsets' % MAX_N_WORDSETS
            break
        words = line.strip().split()
        freq = float(words[-1].strip())
        words = set(words[0:(len(words) - 1)])
        if include(words):
            wordsets.append((tuple(sorted(words)), freq))

    return sorted(wordsets, key=itemgetter(1), reverse=True)


def include(words):
    for similar_wordset in settings.SIMILAR_WORDSETS:
        if len(words & similar_wordset) > 1:
            return False
    return True


def dump_wordsets(fp, **filter_kwargs):
    """
    Format suitable as input to Christian Borgelt's frequent
    pattern mining programs.
    http://borgelt.net/fpm.html
    """
    print 'Searching for items matching:'
    for kwarg in filter_kwargs.items():
        print '\t%s: %s' % kwarg

    items = Item.objects.filter(**filter_kwargs).distinct()
    print 'Got %d items' % items.count()
    for item in items:
        words = set(parse(item.value)) - settings.COMMON_WORDS
        # TODO: the file object that is passed in should know how
        # to do the necessary encoding
        fp.write((' '.join(words) + '\n').encode('utf-8'))

    return items
