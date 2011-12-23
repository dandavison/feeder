import os
from operator import itemgetter
from subprocess import Popen, PIPE
from datetime import timedelta

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.db import settings
from django import forms

from words.models import Item


MAX_N_WORDSETS = 1000


def frequent_wordsets(request):
    executable = os.path.join(settings.SITE_DIRECTORY,
                              '../bin/apriori')
    finder = Popen([executable, '-s3', '-m3','-v %S', '-', '-'],
                   stdin=PIPE, stdout=PIPE)
    Item.objects.dump_wordsets(finder.stdin)
    finder.stdin.close()
    wordsets = []
    for line in finder.stdout.readlines()[0:MAX_N_WORDSETS]:
        words = line.strip().split()
        freq = float(words[-1].strip())
        words = set(words[0:(len(words) - 1)])
        if include(words):
            wordsets.append((' '.join(sorted(words)), freq))

    finder.stdout.close()

    wordsets = sorted(wordsets, key=itemgetter(1), reverse=True)

    return render_to_response('wordsets.html',
                              {'wordsets': wordsets})

def include(words):
    for similar_wordset in settings.SIMILAR_WORDSETS:
        if len(words & similar_wordset) > 1:
            return False
    return True


class BrowseForm(forms.Form):
    start_date = forms.DateField(
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'required, datepicker'}))
    start_time = forms.TimeField(
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'required, timepicker'}))


def home(request):
    if request.method == 'POST': # If the form has been submitted...
        form = BrowseForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            return HttpResponseRedirect('') # Redirect after POST
    else:
        form = BrowseForm() # An unbound form

    return render_to_response('browse.html', {
        'form': form,
    })
