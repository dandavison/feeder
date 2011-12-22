class Dialect:
    def __init__(self, has_header_row=False, use_header_row=False,
            reader_func=None, allow_missing=False, all_columns=True, **kwargs):
        self.has_header_row = has_header_row or use_header_row
        self.use_header_row = use_header_row
        self.reader_func = reader_func
        self.allow_missing = allow_missing
        self.all_columns = all_columns

        kwargs.setdefault("lineterminator", "\n")
        self.csv_dialect = kwargs
        self.columns = []

    def add_column(self, column):
        self.columns.append(column)

    def finalize(self):
        self.columns.sort(key=lambda column: column.counter)
