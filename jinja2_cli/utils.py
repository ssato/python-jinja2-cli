"""
:copyright: (c) 2012 - 2015 by Satoru SATOH <ssato@redhat.com>
:license: BSD-3
"""
from __future__ import absolute_import
from __future__ import print_function

import codecs
import glob
import os.path
import os
import sys

import jinja2_cli.compat

try:
    from anyconfig.api import container, load
except ImportError:
    container = dict

    try:
        import json
    except ImportError:
        try:
            import simplejson as json
        except ImportError:
            raise ("Could not import any json module to load contexts!"
                   " Aborting...")

    def load(filepath, _ftype):
        return json.load(open(filepath))


def get_locale_sensitive_stdout(encoding=jinja2_cli.compat.ENCODING):
    """
    :param encoding: Chart sets encoding
    :return: sys.stdout can output encoded strings

    >>> _t = get_locale_sensitive_stdout("UTF-8")
    """
    return codecs.getwriter(encoding)(sys.stdout)


def get_locale_sensitive_stdin(encoding=jinja2_cli.compat.ENCODING):
    """
    :param encoding: Chart sets encoding
    :return: sys.stdout can output encoded strings

    >>> _t = get_locale_sensitive_stdin("UTF-8")
    """
    return codecs.getreader(encoding)(sys.stdin)


def uniq(xs):
    """Remove duplicates in given list with its order kept.

    >>> uniq([])
    []
    >>> uniq([1, 4, 5, 1, 2, 3, 5, 10])
    [1, 4, 5, 2, 3, 10]
    """
    acc = xs[:1]
    for x in xs[1:]:
        if x not in acc:
            acc += [x]

    return acc


def chaincalls(callables, x):
    """
    :param callables: callable objects to apply to x in this order
    :param x: Object to apply callables

    >>> chaincalls([lambda a: a + 1, lambda b: b + 2], 0)
    3
    """
    for c in callables:
        assert callable(c), "%s is not callable object!" % str(c)
        x = c(x)

    return x


def normpath(path):
    """Normalize given path in various different forms.

    >>> normpath("/tmp/../etc/hosts")
    '/etc/hosts'
    >>> normpath("~root/t")
    '/root/t'
    """
    if "~" in path:
        fs = [os.path.expanduser, os.path.normpath, os.path.abspath]
    else:
        fs = [os.path.normpath, os.path.abspath]

    return chaincalls(fs, path)


def flip(xy):
    """
    :param xy: A tuple of pair items

    >>> flip((1, 2))
    (2, 1)
    """
    (x, y) = xy
    return (y, x)


def concat(xss):
    """
    >>> concat([[]])
    []
    >>> concat((()))
    []
    >>> concat([[1,2,3],[4,5]])
    [1, 2, 3, 4, 5]
    >>> concat([[1,2,3],[4,5,[6,7]]])
    [1, 2, 3, 4, 5, [6, 7]]
    >>> concat(((1,2,3),(4,5,[6,7])))
    [1, 2, 3, 4, 5, [6, 7]]
    >>> concat(((1,2,3),(4,5,[6,7])))
    [1, 2, 3, 4, 5, [6, 7]]
    >>> concat((i, i*2) for i in range(3))
    [0, 0, 1, 2, 2, 4]
    """
    return list(jinja2_cli.compat.from_iterable(xs for xs in xss))


def parse_filespec(fspec, sep=':', gpat='*'):
    """
    Parse given filespec `fspec` and return [(filetype, filepath)].

    Because anyconfig.api.load should find correct file's type to load by the
    file extension, this function will not try guessing file's type if not file
    type is specified explicitly.

    :param fspec: filespec
    :param sep: a char separating filetype and filepath in filespec
    :param gpat: a char for glob pattern

    >>> parse_filespec("base.json")
    [('base.json', None)]
    >>> parse_filespec("json:base.json")
    [('base.json', 'json')]
    >>> parse_filespec("yaml:foo.yaml")
    [('foo.yaml', 'yaml')]
    >>> parse_filespec("yaml:foo.dat")
    [('foo.dat', 'yaml')]

    # FIXME: How to test this?
    # >>> parse_filespec("yaml:bar/*.conf")
    # [('bar/a.conf', 'yaml'), ('bar/b.conf', 'yaml')]

    TODO: Allow '*' (glob pattern) in filepath when escaped with '\\', etc.
    """
    tp = (ft, fp) = tuple(fspec.split(sep)) if sep in fspec else (None, fspec)

    return [(fs, ft) for fs in sorted(glob.glob(fp))] \
        if gpat in fspec else [flip(tp)]


def parse_and_load_contexts(contexts, werr=False,
                            enc=jinja2_cli.compat.ENCODING):
    """
    :param contexts: list of context file specs
    :param werr: Exit immediately if True and any errors occurrs
        while loading context files
    :param enc: Input encoding of context files (dummy param)
    """
    ctx = container()

    if contexts:
        for fpath, ftype in concat(parse_filespec(f) for f in contexts):
            diff = load(fpath, ftype)
            ctx.update(diff)

    return ctx


def write_to_output(content, output=None, encoding=jinja2_cli.compat.ENCODING):
    if output and not output == '-':
        outdir = os.path.dirname(output)
        if outdir and not os.path.exists(outdir):
            os.makedirs(outdir)

        jinja2_cli.compat.copen(output, 'w').write(content)
    else:
        print(content, get_locale_sensitive_stdout())

# vim:sw=4:ts=4:et:
