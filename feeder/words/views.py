import os
from datetime import timedelta

from django.shortcuts import render_to_response
from django.db import settings

from feeder_cli import main


FEED_FILE = os.path.join(settings.SITE_DIRECTORY, 'feeds.txt')
OUTDIR = os.path.join(settings.SITE_DIRECTORY, 'output')


def fetch(request):

    main(FEED_FILE, start=3, end=0, kmax=2, outdir=OUTDIR)

    return render_to_response('output/index.html', {})
