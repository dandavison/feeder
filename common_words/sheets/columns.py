import decimal
import datetime
import functools

from itertools import count


class Column(object):
    """
    An individual column within a CSV file.

    This serves as a base for attributes and methods that are common to all
    types of columns. Subclasses of Column will define behavior for more
    specific data types.
    """

    _count = count()  # global counter to maintain attr order this can be
                      # removed in python 3.0 with metaclass.__prepare__.

    def __init__(self, title=None, required=True, strict=True, isQCFlag=False):
        self.title = title
        self.required = required
        self.strict = strict
        self.isQCFlag = isQCFlag
        self._validators = [self._to_python]

        # Hack to maintain class attribute order in Python < 3.0
        self.counter = next(self.__class__._count)

    def attach_to_class(self, cls, name, dialect):
        self.cls = cls
        self.name = name
        self.dialect = dialect

        # Check for None so that an empty string will skip this behavior
        if self.title is None:
            self.title = name

        dialect.add_column(self)

    def _to_python(self, value, allow_missing=False):
        try:
            return self.to_python(value)
        except (ValueError, TypeError):
            if allow_missing:
                if value in (None, ''):
                    return None
            if self.strict:
                raise
            else:
                return value

    def to_python(self, value):
        """
        Convert the given string to a native Python object.
        """
        return value

    def to_string(self, value):
        """
        Convert the given Python object to a string.
        """
        return value

    def validator(self, func):
        self._validators.append(functools.partial(func, self))
        return func

    def validate(self, value):
        """
        Validate that the given value matches the column's requirements.

        Raise a ValueError only if the given value was invalid.
        """
        for validate in self._validators:
            validate(value)


class StringColumn(Column):
    pass


class IntegerColumn(Column):
    def to_python(self, value):
        return int(value)


class FloatColumn(Column):
    def to_python(self, value):
        return float(value)


class BooleanColumn(Column):
    _bool_map = {"true": True, "false": False}
    _bool_map_QC = {"y": True, "n": False}

    def to_python(self, value):
        bool_map = self._bool_map_QC if self.isQCFlag else self._bool_map
        str_value = str(value).lower()
        if str_value not in bool_map:
            raise ValueError("cannot map '%s' to boolean with map %s" \
                             % (value, bool_map))

        return bool_map[str_value]


class DecimalColumn(Column):
    """
    A column that contains data in the form of decimal values.

    Represented in Python by decimal.Decimal.
    """

    def to_python(self, value):
        try:
            return decimal.Decimal(value)
        except decimal.InvalidOperation as e:
            raise ValueError(str(e))


class DateColumn(Column):
    """
    A column that contains data in the form of dates.

    Represented in Python by datetime.date.

    format
        A strptime()-style format string.
        See http://docs.python.org/library/datetime.html for details
    """

    def __init__(self, format='%Y-%m-%d', format_list=None, *args, **kwargs):
        super(DateColumn, self).__init__(*args, **kwargs)
        self.format = format
        self.input_formats = set([format] + (format_list or []))

    def to_python(self, value):
        """
        Parse a string value according to self.format
        and return only the date portion.
        """
        if isinstance(value, datetime.date):
            return value

        for format in self.input_formats:
            try:
                return datetime.datetime.strptime(value, format).date()
            except ValueError:
                continue

        msg = ("time data %s does not match and of the formats: %s" %
                (value, ", ".join(map(repr, self.input_formats))))
        raise ValueError(msg)

    def to_string(self, value):
        """
        Format a date according to self.format and return that as a string.
        """
        return value.strftime(self.format)
