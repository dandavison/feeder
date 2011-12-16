#!/usr/bin/env python

import sys
from collections import Counter
from argparse import ArgumentParser
from datetime import datetime, timedelta
import time

import feedparser
import BeautifulSoup


# log_fp = open('feeder.log', 'w')
log_fp = sys.stderr


def read_feeds(urls):
    feeds = []
    now = datetime.now()

    # Nobody can have a local time further forwards than this
    now += timedelta(days=1)

    time_window = timedelta(days=1.5)

    for url in urls:
        print url
        log(url, indent=0)
        feed = feedparser.parse(url)
        content = []
        for entry in feed.entries:
            pub_time = datetime.fromtimestamp(time.mktime(entry.date_parsed))
            assert pub_time < now
            if now - pub_time < time_window:
                content.extend(get_content(entry))
            else:
                log('entry too old')

        feeds.append((url, content))

    return feeds


def get_content(entry):

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
                print >>sys.stderr, 'Discarding: %s' % citem.value[0:100]

        return values

    except AttributeError:
        log('AttributeError: %s' % content.keys())
        return []


def validate_urls(raw_urls):
    urls = []
    for num, url in enumerate(raw_urls):
        if not url:
            continue
        if not (url.startswith('www.') or url.startswith('http://')):
            print >>sys.stderr, 'Bad URL on line %d: %s' % (num+1, url)
            continue
        urls.append(url)

    dups = (url for url, count in Counter(urls).iteritems()
            if count > 1)
    for url in dups:
        print >>sys.stderr, 'Duplicated URL: %s' % url

    urls = sorted(set(urls))


    return urls


def log(string, indent=1):
    log_fp.write(
        ('\t' * indent) + string + '\n')



if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('feed_file', help='File containing feed URLS, one per line')
    args = parser.parse_args()

    with open(args.feed_file) as fp:
        urls = [line.strip() for line in fp.readlines()]

    urls = validate_urls(urls)

    feeds = read_feeds(urls)

    import ipdb ; ipdb.set_trace()
    content = digest_feeds(feeds)

