from sheets import Row
from sheets import StringColumn
from sheets import FloatColumn
from sheets import IntegerColumn
from sheets import Dialect


class Word(Row):
    Dialect = Dialect(use_header_row=True, delimiter="\t")

    rank = IntegerColumn()
    wordform = StringColumn()
    abs	= IntegerColumn()
    r = IntegerColumn()
    mod = FloatColumn()
