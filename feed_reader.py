#!/usr/bin/env python

import sys
from collections import Counter
from argparse import ArgumentParser
import feedparser


def read_feeds(urls):
    feeds = []
    for url in urls:
        print url
        feeds.append(feedparser.parse(url))

    return feeds


def validate_urls(urls):
    suffixes = ['rss']

    urls = filter(None, urls)
    for num, url in enumerate(urls):
        suffix = url.split('.')[-1]
        if suffix not in suffixes:
            print >>sys.stderr, 'Bad URL on line %d: %s' % (num+1, url)
            urls.remove(url)

    dups = (url for url, count in Counter(urls).iteritems()
            if count > 1)
    for url in dups:
        print >>sys.stderr, 'Duplicated URL: %s' % url

    urls = sorted(set(urls))


    return urls



if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('feed_file', help='File containing feed URLS, one per line')
    args = parser.parse_args()

    with open(args.feed_file) as fp:
        urls = [line.strip() for line in fp.readlines()]

    urls = validate_urls(urls)

    feeds = read_feeds(urls)
    import ipdb ; ipdb.set_trace()
