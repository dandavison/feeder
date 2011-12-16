import csv

import options

__all__ = ['Row', 'Reader', 'Writer']


class RowMeta(type):
    def __init__(cls, name, bases, attrs):
        if 'Dialect' in attrs:
            dialect = attrs.pop('Dialect')
        else:
            dialect = options.Dialect()
        cls._dialect = dialect

        for key, attr in attrs.items():
            if hasattr(attr, 'attach_to_class'):
                attr.attach_to_class(cls, key, cls._dialect)
        dialect.finalize()  # sort columns

        super(RowMeta, cls).__init__(name, bases, attrs)


class Row(object):
    __metaclass__ = RowMeta

    def __init__(self, *args, **kwargs):
        from_title = kwargs.pop("from_title", False)
        attr = "title" if from_title else "name"
        column_names = [getattr(column, attr)
                for column in self._dialect.columns]

        # First, make sure the arguments make sense
        if len(args) > len(column_names):
            msg = "__init__() takes at most %d arguments (%d given)"
            raise TypeError(msg % (len(column_names), len(args)))

        if self._dialect.all_columns:
            for name in kwargs:
                if name not in column_names:
                    raise TypeError("Got unknown keyword argument %s" \
                                    % repr(name))

        for i, name in enumerate(column_names[:len(args)]):
            if name in kwargs:
                msg = "__init__() got multiple values for keyword argument %s"
                raise TypeError(msg % repr(name))
            kwargs[name] = args[i]

        # Now populate the actual values on the object
        for column in self._dialect.columns:
            try:
                value = column._to_python(kwargs[getattr(column, attr)],
                        allow_missing=self._dialect.allow_missing)
            except KeyError:
                # No value was provided
                value = None
            setattr(self, column.name, value)

    errors = ()

    def __repr__(self):
        class_name = self.__class__.__name__
        column_names = [column.name for column in self._dialect.columns]
        str_args = ", ".join("%s=%s" % (name, repr(getattr(self, name)))
                for name in column_names)
        return "%s(%s)" % (class_name, str_args)

    def is_valid(self):
        valid = True
        self.errors = []
        for column in self._dialect.columns:
            value = getattr(self, column.name)
            try:
                column.validate(value)
            except ValueError as e:
                self.errors.append(e)
                valid = False
        return valid

    @classmethod
    def reader(cls, fp):
        return Reader(cls, fp)

    @classmethod
    def file_reader(cls, file):
        with open(file) as fp:
            for row in cls.reader(fp):
                yield row

    @classmethod
    def writer(cls, fp):
        return Writer(cls, fp)

    @classmethod
    def file_writer(cls, file, rows):
        with open(file, "w") as fp:
            writer = cls.writer(fp)
            writer.writerows(rows)


class Reader(object):
    def __init__(self, row_cls, fp):
        self.row_cls = row_cls
        self.has_header_row = row_cls._dialect.has_header_row
        self.use_header_row = row_cls._dialect.use_header_row

        reader_func = row_cls._dialect.reader_func
        if reader_func:
            fp = reader_func(fp)

        if self.use_header_row:
            reader = csv.DictReader(fp, **row_cls._dialect.csv_dialect)
        else:
            reader = csv.reader(fp, **row_cls._dialect.csv_dialect)
            if self.has_header_row:  # skip header
                next(reader)

        self.csv_reader = reader

    def __iter__(self):
        return self

    def next(self):
        row = next(self.csv_reader)
        if self.use_header_row:
            row.pop(None, None)  # remove unnamed columns
            return self.row_cls(from_title=True, **row)
        else:
            return self.row_cls(*row)


class Writer(object):
    def __init__(self, row_cls, fp):
        self.columns = row_cls._dialect.columns
        self._writer = csv.writer(fp, **row_cls._dialect.csv_dialect)
        self.needs_header_row = row_cls._dialect.has_header_row

    def writerow(self, row):
        if self.needs_header_row:
            values = [column.title for column in self.columns]
            self._writer.writerow(values)
            self.needs_header_row = False
        values = [getattr(row, column.name) for column in self.columns]
        self._writer.writerow(values)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
