import operator
from datetime import datetime

from django.shortcuts import render_to_response
from django.db.models import Q
from django import forms
from django.template import RequestContext

from utils.time_utils import get_datetime_from_date_and_time
from utils.time_utils import datetime_at_start_of
from words.models import Item, Entry, Feed
from wordsets import get_frequent_wordsets, get_new_wordsets


def home(request):
    today = datetime.today()
    start_of_today = datetime_at_start_of(today)
    now = datetime.now()
    new_wordsets_form = NewWordsetsForm(
        initial={'new_wordsets_start_date': today,
                 'new_wordsets_start_time': start_of_today})

    if request.method == 'POST':
        wordsets_form = WordsetsForm(request.POST)
        if wordsets_form.is_valid():
            start_time = get_datetime_from_date_and_time(
                wordsets_form.cleaned_data['start_date'],
                wordsets_form.cleaned_data['start_time'])
            end_time = get_datetime_from_date_and_time(
                wordsets_form.cleaned_data['end_date'],
                wordsets_form.cleaned_data['end_time'])
            return frequent_wordsets(start_time, end_time)
    else:
        wordsets_form = WordsetsForm(initial={'start_date': today,
                                              'start_time': start_of_today,
                                              'end_date': today,
                                              'end_time': now})

    entry_pub_times = sorted(Entry.objects.values_list('pub_time', flat=True))
    earliest, latest = entry_pub_times[0], entry_pub_times[-1]
    n_entries = len(entry_pub_times)

    title = 'Feed Reader'
    n_items = Item.objects.count()
    n_feeds = Feed.objects.count()

    return render_to_response('browse.html', locals(),
                              context_instance=RequestContext(request))


class NewWordsetsForm(forms.Form):
    new_wordsets_start_date = forms.DateField(
        label='Start date',
        required=True,
        widget=forms.DateInput(
            attrs={
                'class': 'required, datepicker'}))
    new_wordsets_start_time = forms.TimeField(
        label='Start time',
        required=True,
        widget=forms.TimeInput(
            attrs={'class': 'required, timepicker'}))


class WordsetsForm(forms.Form):
    start_date = forms.DateField(
        label='Start date',
        required=True,
        widget=forms.DateInput(
            attrs={
                'class': 'required, datepicker'}))
    start_time = forms.TimeField(
        label='Start time',
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


def new_wordsets(request):
    if request.method == 'POST':
        form = NewWordsetsForm(request.POST)
        if form.is_valid():
            start_time = get_datetime_from_date_and_time(
                form.cleaned_data['new_wordsets_start_date'],
                form.cleaned_data['new_wordsets_start_time'])
    else:
        raise Exception('Should not happen')

    items, wordsets = get_new_wordsets(start_time)
    n_items = Item.objects.count()

    return render_to_response('wordsets.html', locals())


def frequent_wordsets(start_time, end_time):
    items, wordsets = get_frequent_wordsets(start_time, end_time)
    n_items = Item.objects.count()

    return render_to_response('wordsets.html', locals())


def matching_items(request):
    wordset = request.GET['wordset'].split(',')

    item_Q = reduce(operator.and_,
                    (Q(value__contains=word) for word in wordset))
    items = Item.objects.filter(item_Q). \
            select_related('entry__feed'). \
            order_by('-entry__pub_time')

    return render_to_response('items.html', locals())
