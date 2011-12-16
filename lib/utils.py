# http://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
class memoized(object):
   """Decorator that caches a function's return value each time it is called.
   If called later with the same arguments, the cached value is returned, and
   not re-evaluated.
   """
   def __init__(self, func):
      self.func = func
      self.cache = {}
   def __call__(self, *args):
      try:
         return self.cache[args]
      except KeyError:
         value = self.func(*args)
         self.cache[args] = value
         return value
      except TypeError:
         # uncachable -- for instance, passing a list as an argument.
         # Better to not cache than to blow up entirely.
         return self.func(*args)
   def __repr__(self):
      """Return the function's docstring."""
      return self.func.__doc__
   def __get__(self, obj, objtype):
      """Support instance methods."""
      return functools.partial(self.__call__, obj)

@memoized
def clean(word):
    internal_chars = set(["'", '-'])
    word = word.lower()

    if not any(char.isalpha() for char in word):
        return None

    if not (word.isalpha() or word.isdigit()):
        word = word.replace('--', '')

        while word[-1] in internal_chars:
            word = word[:-1]
        while word[0] in internal_chars:
            word = word[1:]

        word = ''.join(char for char in word
                       if char.isalpha() or char in internal_chars)

        # inclusion_regexp, exclusion_regexp

    return word
