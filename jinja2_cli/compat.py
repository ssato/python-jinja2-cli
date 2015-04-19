#
# Author: Satoru SATOH <ssato redhat.com>
# License: MIT
#
import codecs
import itertools
import locale
import sys

try:
    from logging import NullHandler
except ImportError:  # python < 2.7 doesn't have it.
    import logging

    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


IS_PYTHON_3 = sys.version_info[0] == 3
ENCODING = locale.getdefaultlocale()[1]


# Borrowed from library doc, 9.7.1 Itertools functions:
def _from_iterable(iterables):
    """
    itertools.chain.from_iterable alternative.

    >>> list(_from_iterable([[1, 2], [3, 4]]))
    [1, 2, 3, 4]
    """
    for it in iterables:
        for element in it:
            yield element


def copen(filepath, flag='r', encoding=ENCODING):
    """
    FIXME: How to test this ?

    >>> c = copen(__file__)
    >>> c is not None
    True
    """
    return codecs.open(filepath, flag, encoding)


if IS_PYTHON_3:
    from_iterable = itertools.chain.from_iterable
    raw_input = input
else:
    try:
        from_iterable = itertools.chain.from_iterable
    except AttributeError:
        from_iterable = _from_iterable

    raw_input = raw_input

# vim:sw=4:ts=4:et:
