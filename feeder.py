#!/usr/bin/env python
import os
import sys
from collections import Counter
from collections import defaultdict
from itertools import combinations
from itertools import chain
from operator import itemgetter
import argparse
import socket
from time import gmtime
from datetime import timedelta

import feedparser
import BeautifulSoup
from concurrent import futures

from common_words import Word
from utils import parse, make_link
from utils.time_utils import get_datetime, as_local_time


OUTDIR = 'output'
LOG_FP = open(os.path.join(OUTDIR, 'feeder.log'), 'w')
COMMON_WORD_RANK = 500
N_MOST_COMMON = 100
START_TIME = None
END_TIME = None
socket.setdefaulttimeout(10.0)


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


def _process_content(args):
    url, content, k = args
    occur = defaultdict(list)
    words = set(parse(content)) - common_words
    for combn in combinations(words, k):
        occur[combn].append(url)

    return occur


def digest_feeds(feeds, k, common_words):

    with futures.ProcessPoolExecutor() as executor:
        occurs = executor.map(_process_content,
                              [(url, content, k)
                               for url, contents in feeds
                               for content in contents])

        occur = defaultdict(list)
        for combn, urls in chain(*(o.items() for o in occurs)):
            occur[combn].extend(urls)

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
        rows.append((' '.join(words),
                     make_link(urlfile, '%d' % count)))

        url_rows = [(make_link(url), '%d' % count)
                    for url, count in Counter(occur[words]).most_common()]
        with open(os.path.join(OUTDIR, urlfile), 'w') as fp:
            fp.write(format_table_page(url_rows))

    with open(outfile, 'w') as fp:
        fp.write(format_table_page(rows, header=header))

    print 'Top %d word sets written to %s' % (N_MOST_COMMON, outfile)


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


def get_common_words():
    words = Word.file_reader('common_words/words.txt')
    with open('common_words/extra_words.txt') as fp:
        extra_words = set(line.strip()
                          for line in fp.readlines())

    common_words = set(word.wordform for word in words
                       if word.rank <= COMMON_WORD_RANK)

    return common_words | extra_words


def format_table_page(*args, **kwargs):
    import utils
    preamble = utils.format_table([('Start:', as_local_time(START_TIME)),
                                   ('End:', as_local_time(END_TIME))])
    return utils.format_table_page(preamble, *args, **kwargs)


def validate_urls(raw_urls):
    urls = []
    for num, url in enumerate(raw_urls):
        if not url:
            continue
        if not (url.startswith('www.') or url.startswith('http://')):
            log('Bad URL on line %d: %s' % (num + 1, url))
            continue
        urls.append(url)

    dups = (url for url, count in Counter(urls).iteritems()
            if count > 1)
    for url in dups:
        log('Duplicated URL: %s' % url)

    urls = sorted(set(urls))

    return urls


def validate_args(args):
    def die(last_words):
        print >>sys.stderr, last_words
        sys.exit(1)

    try:
        assert args.end < args.start
    except AssertionError:
        die('--end value must be less than --start value.'
            ' (I got --start=%d and --end=%d)' % (args.start, args.end))


def log(*args, **kwargs):
    import utils
    utils.log(*args, fp=LOG_FP, **kwargs)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        epilog='''examples:
    ./feeder.py --start 12 my_feeds.txt
    Summarize feeds published within the last 12 hours.

    ./feeder.py --start 12 --end 6 my_feeds.txt
    Summarize feeds published within the last 12 hours, but not more recently than 6 hours ago.

    ./feeder.py --kmax 3 my_feeds.txt
    Do 3-word analysis, in addition to 1 and 2. (This command will use the default --start value of 24)
''',
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('feed_file',
                        help='file containing feed URLS, one per line')
    parser.add_argument('--start', type=int, default=24,
                        help='maximum age of feeds in hours (default: 24)')
    parser.add_argument('--end', type=int, default=0,
                        help='minimum age of feeds in hours (default: 0)')
    parser.add_argument('--kmax', type=int, default=2,
                        help='maximum number of words in a combination (default: 2)')


    args = parser.parse_args()
    validate_args(args)

    os.system('find %s -type f -delete' % OUTDIR)

    with open(args.feed_file) as fp:
        urls = [line.strip() for line in fp.readlines()]

    urls = validate_urls(urls)

    now = get_datetime(gmtime())
    START_TIME = now - timedelta(hours=args.start)
    END_TIME = now - timedelta(hours=args.end)

    feeds = read_feeds(urls, START_TIME, END_TIME)
    common_words = set(get_common_words())
    link_rows = []
    for k in range(1, args.kmax + 1):
        print '\n%d-word analysis...' % k
        words_file = '%d-word.html' % k
        link_rows.append((make_link(words_file),))
        occur = digest_feeds(feeds, k, common_words)
        write_output(occur, os.path.join(OUTDIR, words_file))

    with open(os.path.join(OUTDIR, 'index.html'), 'w') as fp:
        fp.write(format_table_page(link_rows))
