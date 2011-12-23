import sys

from lib import utils


def format_table_page(preamble, *args, **kwargs):
    HTML_TABLE_PAGE_TEMPLATE = '''
<html>
  <body>
    %s
    <br>
    <br>
    %s
  </body>
</html>'''
    return HTML_TABLE_PAGE_TEMPLATE % (
        preamble, format_table(*args, **kwargs))


def format_table(rows, header=''):
    HTML_TABLE_TEMPLATE = '''
    <table>
       %s
       <tbody>
         %s
       </tbody>
    </table>'''
    return HTML_TABLE_TEMPLATE % (
        header,
        '\n'.join(make_html_table_row(*row) for row in rows))


def make_html_table_row(*args):
    make_cell = lambda cell: '<td>%s</td>' % cell
    return '<tr>' + ''.join(map(make_cell, args)) + '</tr>'


def make_link(target, display=None):
    if display is None:
        display = target
    return '<a href=%s>%s</a>' % (target, display)


def parse(string):
    return filter(None,
                  map(utils.clean, utils.html_to_txt(string).split()))


def log(string, indent=1, fp=sys.stderr):
    try:
        fp.write(
            ('\t' * indent) + string + '\n')
    except UnicodeEncodeError:
        fp.write('<UnicodeEncodeError> during logging...')
