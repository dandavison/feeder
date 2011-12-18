import sys

from lib import utils


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


def parse(string):
    return filter(None,
                  map(utils.clean, utils.html_to_txt(string).split()))


def log(string, indent=1, fp=sys.stderr):
    try:
        fp.write(
            ('\t' * indent) + string + '\n')
    except UnicodeEncodeError:
        fp.write('<UnicodeEncodeError> during logging...')
