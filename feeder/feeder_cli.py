#!/usr/bin/env python
import os
import sys
from collections import Counter
from collections import defaultdict
from itertools import combinations
from operator import itemgetter
import argparse
import socket
from time import gmtime
from datetime import timedelta
import codecs

from common_words import Word
from utils import parse, make_link
from utils.time_utils import get_datetime, as_local_time


OUTDIR = 'output'
LOG_FP = open(os.path.join(OUTDIR, 'feeder.log'), 'w')
COMMON_WORD_RANK = 500
N_MOST_COMMON = 1000
NOW = None
START_TIME = None
END_TIME = None
socket.setdefaulttimeout(10.0)


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

    with codecs.open(outfile, 'w', 'utf-8') as fp:
        fp.write(format_table_page(rows, header=header))

    print 'Top %d word sets written to %s' % (N_MOST_COMMON, outfile)


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
    parser.add_argument('--start', type=float, default=24,
                        help='maximum age of feeds in hours (default: 24)')
    parser.add_argument('--end', type=float, default=0,
                        help='minimum age of feeds in hours (default: 0)')
    parser.add_argument('--kmax', type=int, default=2,
                        help='maximum number of words in a combination (default: 2)')

    args = parser.parse_args()
    validate_args(args)

    main(feed_file, args.start, args.end, args.kmax, OUTDIR)


def main(feed_file, start, end, kmax, outdir):

    os.system('find %s -type f -delete' % outdir)

    with open(feed_file) as fp:
        urls = [line.strip() for line in fp.readlines()]

    urls = validate_urls(urls)

    global NOW, START_TIME, END_TIME
    NOW = get_datetime(gmtime())
    START_TIME = NOW - timedelta(hours=start)
    END_TIME = NOW - timedelta(hours=end)

    print 'Fetching feeds between %s and %s...' % (
        as_local_time(START_TIME),
        as_local_time(END_TIME))
    feeds = read_feeds(urls, START_TIME, END_TIME)
    print 'Got %d entries from %d feeds' % (
        sum(len(feed[1]) for feed in feeds),
        len(feeds))

    analyze(feeds, kmax, common_words, outdir)
