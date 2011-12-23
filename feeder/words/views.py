import os
from operator import itemgetter
from subprocess import Popen, PIPE
from datetime import timedelta

from django.shortcuts import render_to_response
from django.db import settings

from words.models import Item


MAX_N_WORDSETS = 1000


def get_frequent_wordsets(request):

    executable = os.path.join(settings.SITE_DIRECTORY,
                              '../bin/apriori')
    finder = Popen([executable, '-s', 3, '-m', 3, '-', '-'],
                   stdin=PIPE, stdout=PIPE)
    Item.objects.dump_wordsets(finder.stdin)
    finder.stdin.close()
    wordsets = []
    for line in finder.stdout.readlines()[0:MAX_N_WORDSETS]:
        words, freq = line.split('  ')
        wordsets.append((words.split(' '), float(freq)))

    finder.stdout.close()

    wordsets = sorted(wordsets, key=itemgetter(1))

    return render_to_response('wordsets.html',
                              {'wordsets': wordsets})
