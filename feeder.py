#!/usr/bin/env python
import os
import sys
from collections import Counter
from collections import defaultdict
from itertools import combinations
from operator import itemgetter
import argparse
from datetime import datetime, timedelta
import time
import socket

import feedparser
import BeautifulSoup
from concurrent import futures

from common_words import Word
from lib import utils


OUTDIR = 'output'
LOG_FP = open(os.path.join(OUTDIR, 'feeder.log'), 'w')
COMMON_WORD_RANK = 500
N_MOST_COMMON = 100
START_TIME = None
END_TIME = None
socket.setdefaulttimeout(10.0)


HTML_TABLE_PAGE_TEMPLATE = '''
<html>
  <body>
    %s
    <br>
    <br>
    <table>
       %s
       <tbody>
         %s
       </tbody>
    </table>
  </body>
<html>
'''

def read_feeds(urls, start, end):
    feeds = []

    print 'Fetching feeds...'
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(feedparser.parse, url): url
                         for url in urls}

    for future in futures.as_completed(future_to_url):
        url = future_to_url[future]
        if future.exception() is not None:
            log('Error reading %r: %s' % (url, future.exception()))
            continue

        feed = future.result()
        content = []
        for entry in feed.entries:
            try:
                pub_time = get_datetime(entry.date_parsed)
            except AttributeError:
                log('No date_parsed attribute on entry')
                continue
            except:
                log('Error reading entry date')
                continue

            assert pub_time < now
            if start < pub_time < end:
                content.extend(get_content(entry))
            else:
                log('Entry time outside window: %s' % pub_time)

        feeds.append((url, content))

    return feeds


def digest_feeds(feeds, k, common_words):
    occur = defaultdict(list)
    for url, contents in feeds:
        for content in contents:
            words = set(parse(content)) - common_words
            for combn in combinations(words, k):
                occur[combn].append(url)

    return occur


def write_output(occur, outfile, write_header=False):
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

    counts = sorted(((words, len(urls)) for words, urls in occur.iteritems()),
                    key=itemgetter(1), reverse=True)
    rows = []
    for words, count in counts[0:N_MOST_COMMON]:
        urlfile = 'urls/%s.html' % '-'.join(words)
        rows.append(make_html_table_row(
            ' '.join(words), make_link(urlfile , '%d' % count)))

        url_rows = '\n'.join(make_html_table_row(make_link(url), '%d' % count)
                             for url, count in Counter(occur[words]).most_common())
        write_table(url_rows, os.path.join(OUTDIR, urlfile))

    write_table('\n'.join(rows), outfile, header=header)

    print 'Top %d word sets written to %s' % (N_MOST_COMMON, outfile)


# Utils -------------------------------------------------

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


def make_html_table_row(*args):
    make_cell = lambda cell: '<td>%s</td>' % cell
    return '<tr>' + ''.join(map(make_cell, args)) + '</tr>'


def make_link(target, display=None):
    if display is None:
        display = target
    return '<a href=%s>%s</a>' % (target, display)


def write_urls(urls, urlfile):
    rows = '\n'.join(make_html_table_row(make_link(url)) for url in urls)

    write_table(rows, urlfile)


def write_table(rows, path, header=''):
    with open(path, 'w') as fp:
        fp.write(HTML_TABLE_PAGE_TEMPLATE % (
            '%s - %s' % (as_local_time(START_TIME), as_local_time(END_TIME)),
            header, rows))


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


def get_datetime(struct_time):
    return datetime.fromtimestamp(time.mktime(struct_time))


def as_local_time(datetime):
    return datetime - timedelta(seconds=time.timezone)


def log(string, indent=1):
    try:
        LOG_FP.write(
            ('\t' * indent) + string + '\n')
    except UnicodeEncodeError:
        LOG_FP.write('<UnicodeEncodeError> during logging...')


def validate_args(args):
    def die(last_words):
        print >>sys.stderr, last_words
        sys.exit(1)

    try:
        assert args.end < args.start
    except AssertionError:
        die('--end value must be less than --start value.'
            ' (I got --start=%d and --end=%d)' % (args.start, args.end))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        epilog='''examples:
    ./feeder.py --start 12 my_feeds.txt
    Summarize feeds published within the last 12 hours.

    ./feeder.py --start 12 --end 6 my_feeds.txt
    Summarize feeds published within the last 12 hours, but not more recently than 6 hours ago.
''',
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('feed_file', help='file containing feed URLS, one per line')
    parser.add_argument('--start', type=int, default=24,
                        help='maximum age of feeds in hours (default: 24)')
    parser.add_argument('--end', type=int, default=0,
                        help='minimum age of feeds in hours (default: 0)')

    args = parser.parse_args()
    validate_args(args)

    os.system('find %s -type f -delete' % OUTDIR)

    with open(args.feed_file) as fp:
        urls = [line.strip() for line in fp.readlines()]

    urls = validate_urls(urls)

    now = get_datetime(time.gmtime())
    START_TIME = now - timedelta(hours=args.start)
    END_TIME = now - timedelta(hours=args.end)

    feeds = read_feeds(urls, START_TIME, END_TIME)
    common_words = set(get_common_words())
    words_files = []
    for k in [1, 2]:
        print '\n%d-word analysis...' % k
        words_file = '%d-word.html' % k
        words_files.append(words_file)
        occur = digest_feeds(feeds, k, common_words)
        write_output(occur, os.path.join(OUTDIR, words_file))

    write_urls(words_files,
               os.path.join(OUTDIR, 'index.html'))
