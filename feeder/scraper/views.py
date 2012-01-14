import os
import json
from subprocess import Popen, PIPE

from django.db import settings
from django.shortcuts import render_to_response


def scraper(request):
    return render_to_response('scraper.html',
                              {'data': get_scrape_data()})


def get_scrape_data():
    scrape = os.path.join(settings.SITE_DIRECTORY,
                          'scraper/js/scrape.coffee')

    scraper = Popen(['coffee', scrape], stdin=PIPE, stdout=PIPE)
    scraper.stdin.close()

    return json.loads(scraper.stdout.read())
