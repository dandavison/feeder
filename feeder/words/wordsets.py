import os
from operator import itemgetter
# from subprocess import Popen, PIPE

from django.db import settings

from utils import parse
from words.models import Item


MAX_N_WORDSETS = 1000
MIN_N_WORDSETS = 100
MINIMUM_WORDSET_SIZE = 3
MAXIMUM_WORDSET_SIZE = 3
INFILE = '/tmp/in'
OUTFILE = '/tmp/out'


def get_frequent_wordsets(start_time, end_time):
    with open(INFILE, 'w') as fp:
        items = dump_wordsets(fp,
                              entry__pub_time__range=(start_time, end_time))

    for support in range(8, 0, -1):
        print 'Trying support=%d' % support
        wordsets = _get_frequent_wordsets(support, start_time, end_time)
        print 'Got %d wordsets' % len(wordsets)
        if len(wordsets) > MIN_N_WORDSETS:
            return items, wordsets

    print 'Warning: Failed to find any frequent wordsets'
    return items, []


def _get_frequent_wordsets(support, start_time, end_time):
    executable = os.path.join(settings.SITE_DIRECTORY,
                              '../bin/apriori')
    with open(INFILE) as fp:
        print 'input num lines: %d' % len(fp.readlines())
    os.system('%s -s%s -m%s -n%s -v" %%S" %s - |head -n %d >%s' % (
        executable, support, MINIMUM_WORDSET_SIZE, MAXIMUM_WORDSET_SIZE,
        INFILE, MAX_N_WORDSETS, OUTFILE))

    # print 'counting output lines'
    # with open(OUTFILE) as fp:
    #     print 'output num lines: %d' % len(fp.readlines())

    stdout = open(OUTFILE)
    wordsets = []
    for line_num, line in enumerate(stdout):
        if line_num > MAX_N_WORDSETS:
            raise Exception('Should not happen')
            break
        words = line.strip().split()
        freq = float(words[-1].strip())
        words = set(words[0:(len(words) - 1)])
        if include(words):
            wordsets.append((sorted(words), freq))

    stdout.close()

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
