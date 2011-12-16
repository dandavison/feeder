#!/usr/bin/env python

import sys
from collections import Counter
from itertools import combinations
from argparse import ArgumentParser
from datetime import datetime, timedelta
import time
import socket

import feedparser
import BeautifulSoup

from common_words import Word
from lib import utils


LOG_FP = open('feeder.log', 'w')
COMMON_WORD_RANK = 500

socket.setdefaulttimeout(5.0)


def digest_feeds(feeds, k, common_words):
    counts = Counter()
    for url, contents in feeds:
        for content in contents:
            words = set(parse(content)) - common_words
            counts.update(combinations(words, k))

    return counts


def write_output(counts, write_header=False):
    outfile = 'wordcount.html'
    fp = open(outfile, 'w')

    if write_header:
        header = '''
          <thead>
            <tr>
              <th> Word Set </th>
              <th> Count </th>
            </tr>
          </thead>
        '''
    else:
        header = ''

    fp.write('''
    <html>
      <body>
        <table>
             %s
             <tbody>
    ''' % header)

    for words, count in counts.most_common()[0:100]:
        fp.write('<tr><td>%s</td><td>%d</td></tr>' % (' '.join(words), count))

    fp.write('</tbody>')
    fp.write('</table>')
    fp.write('</body>')
    fp.write('</html>')

    print '\nTop 100 word sets written to %s' % outfile


def get_common_words():
    words = Word.file_reader('common_words/words.txt')
    with open('common_words/extra_words.txt') as fp:
        extra_words = set(line.strip()
                          for line in fp.readlines())

    common_words =  set(word.wordform for word in words
                         if word.rank <= COMMON_WORD_RANK)

    return common_words | extra_words


def parse(string):
    return filter(None,
                  map(utils.clean, utils.html_to_txt(string).split()))


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
            try:
                pub_time = datetime.fromtimestamp(time.mktime(entry.date_parsed))
            except AttributeError:
                log('No date_parsed attribute on entry')
                continue
            except:
                log('Error reading entry date')
                continue

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
                log('discarding: %s' % citem.value[0:100])

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
            log('Bad URL on line %d: %s' % (num+1, url))
            continue
        urls.append(url)

    dups = (url for url, count in Counter(urls).iteritems()
            if count > 1)
    for url in dups:
        log('Duplicated URL: %s' % url)

    urls = sorted(set(urls))


    return urls


def log(string, indent=1):
    try:
        LOG_FP.write(
            ('\t' * indent) + string + '\n')
    except UnicodeEncodeError:
        LOG_FP.write('<UnicodeEncodeError> during logging...')


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('feed_file', help='File containing feed URLS, one per line')
    args = parser.parse_args()

    with open(args.feed_file) as fp:
        urls = [line.strip() for line in fp.readlines()]

    urls = validate_urls(urls)
    feeds = read_feeds(urls)
    common_words = set(get_common_words())
    for k in [2]:
        counts = digest_feeds(feeds, k, common_words)
        write_output(counts)
