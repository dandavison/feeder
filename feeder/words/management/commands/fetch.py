import sys
from datetime import timedelta

import feedparser
from concurrent import futures
import BeautifulSoup
from fish import ProgressFish

from words.models import Feed, Entry, Item

from feeder_cli import get_datetime, gmtime, log


TIME_EPSILON = timedelta(minutes=1)


def fetch(urls):
    now = get_datetime(gmtime())
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(feedparser.parse, url): url
                         for url in urls}

    fish = ProgressFish(total=len(urls))
    i = 0
    for future in futures.as_completed(future_to_url):
        url = future_to_url[future]
        if future.exception() is not None:
            log('Error reading %r: %s' % (url, future.exception()))
            continue

        feed = future.result()
        _feed, created = Feed.objects.get_or_create(url=url)
        for entry in feed.entries:
            try:
                pub_time = get_datetime(entry.date_parsed)
            except AttributeError:
                log('No date_parsed attribute on entry')
                continue
            except:
                log('Error reading entry date')
                continue

            try:
                assert pub_time - now < TIME_EPSILON
            except AssertionError:
                print >>sys.stderr, 'Entry is from future? %s %s' % (pub_time, url)

            _entry, created = Entry.objects.get_or_create(feed=_feed, pub_time=pub_time)
            for item in get_items(entry):
                Item.objects.get_or_create(value=item, entry=_entry)

        fish.animate(amount=i)
        i += 1

def get_items(entry):

    def get_value(citem):
        if citem.type == 'text/html':
            value = BeautifulSoup.BeautifulSoup(citem.value).text
        else:
            value = citem.value

        if value.startswith('http://'):
            return None

        return value

    values = []
    try:
        try:
            content = entry.content
        except AttributeError:
            content = entry.summary_detail

        for citem in content:
            log('%s\t%s' % (citem.type, citem.value[0:100]))

            value = get_value(citem)
            if value:
                values.append(value)
            else:
                log('discarding: %s' % citem.value[0:100])

        return values

    except AttributeError:
        log('AttributeError: %s' % content.keys())
        return []


def report_db_contents():
    print '%d Feeds, %d Entries, %d Items' % (
        Feed.objects.count(),
        Entry.objects.count(),
        Item.objects.count())


if __name__ == '__main__':

    with open(sys.argv[1]) as fp:
        urls = [line.strip() for line in fp.readlines()]

    print 'Was: ',
    report_db_contents()
    fetch(urls)
    print 'Now: ',
    report_db_contents()
