import os
import operator
from operator import itemgetter
from subprocess import Popen, PIPE
from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.db import settings
from django.db.models import Q
from django import forms
from django.template import RequestContext

from utils.time_utils import get_datetime_from_date_and_time, datetime_at_start_of
from words.models import Item, Entry, Feed


MAX_N_WORDSETS = 1000


def home(request):
    today = datetime.today()
    start_of_today = datetime_at_start_of(today)
    now = datetime.now()

    if request.method == 'POST':
        form = BrowseForm(request.POST)
        if form.is_valid():
            start_time = get_datetime_from_date_and_time(
                form.cleaned_data['start_date'],
                form.cleaned_data['start_time'])
            end_time = get_datetime_from_date_and_time(
                form.cleaned_data['end_date'],
                form.cleaned_data['end_time'])
            return frequent_wordsets(start_time, end_time)
    else:
        form = BrowseForm(initial={'start_date': today,
                                   'start_time': start_of_today, 
                                   'end_date': today,
                                   'end_time': now})

    entry_pub_times = sorted(Entry.objects.values_list('pub_time', flat=True))
    earliest, latest = entry_pub_times[0], entry_pub_times[-1]
    n_entries = len(entry_pub_times)

    return render_to_response('browse.html', {
        'title': 'Feed Reader',
        'n_items': Item.objects.count(),
        'n_entries': n_entries,
        'n_feeds': Feed.objects.count(),        
        'earliest': earliest,
        'latest': latest,
        'now': now,
        'form': form,
    }, context_instance=RequestContext(request))


class BrowseForm(forms.Form):
    start_date = forms.DateField(
        label='Start date',
        required=True,
        widget=forms.DateInput(
            attrs={
                'class': 'required, datepicker'}))
    start_time = forms.TimeField(
        label = 'Start time',
        required=True,
        widget=forms.TimeInput(
            attrs={'class': 'required, timepicker'}))
    end_date = forms.DateField(
        label='End date',
        required=True,
        widget=forms.DateInput(
            attrs={
                'class': 'required, datepicker'}))
    end_time = forms.TimeField(
        required=True,
        widget=forms.TimeInput(
            attrs={'class': 'required, timepicker'}))


def frequent_wordsets(start_time, end_time):
    executable = os.path.join(settings.SITE_DIRECTORY,
                              '../bin/apriori')
    finder = Popen([executable, '-s3', '-m3','-v %S', '-', '-'],
                   stdin=PIPE, stdout=PIPE)
    Item.objects.dump_wordsets(finder.stdin,
                               entry__pub_time__range=(start_time, end_time))
    finder.stdin.close()
    wordsets = []
    for line in finder.stdout.readlines()[0:MAX_N_WORDSETS]:
        words = line.strip().split()
        freq = float(words[-1].strip())
        words = set(words[0:(len(words) - 1)])
        if include(words):
            wordsets.append((sorted(words), freq))

    finder.stdout.close()

    wordsets = sorted(wordsets, key=itemgetter(1), reverse=True)

    return render_to_response('wordsets.html',
                              {'start_time': start_time,
                               'end_time': end_time,
                               'wordsets': wordsets})


def include(words):
    for similar_wordset in settings.SIMILAR_WORDSETS:
        if len(words & similar_wordset) > 1:
            return False
    return True


def matching_items(request):
    wordset = request.GET['wordset'].split(',')

    item_Q = reduce(operator.and_,
                    (Q(value__contains=word) for word in wordset))
    items = Item.objects.filter(item_Q). \
            select_related('entry__feed'). \
            order_by('-entry__pub_time')

    return render_to_response('items.html',
                              {'items': items})
