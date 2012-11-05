"""

 :copyright: (c) 2012 by Satoru SATOH <ssato@redhat.com>
 :license: BSD-3
"""
import jinja2_cui.utils as U

import codecs
import glob
import itertools
import jinja2
import jinja2.meta
import locale
import logging
import optparse
import os.path
import os
import sys

# Data loaders: Key=file_extension, Value=load_func
_LOADERS = {}
_ENCODING = locale.getdefaultlocale()[1] or "utf-8"

sys.stderr = codecs.getwriter(_ENCODING)(sys.stderr)


# Override the default implementation:
def open(path, flag='r', enc=_ENCODING):
    return codecs.open(path, flag, enc)


try:
    import json
    _LOADERS["json"] = _LOADERS["jsn"] = json.loads
except ImportError:
    try:
        import simplejson as json
        _LOADERS["json"] = _LOADERS["jsn"] = json.loads
    except ImportError:
        sys.stderr.write(u"JSON support is disabled as module not found.\n")

try:
    import yaml
    _LOADERS["yaml"] = _LOADERS["yml"] = yaml.load
except ImportError:
    sys.stderr.write(u"YAML support is disabled as module not found.\n")


def get_fileext(filepath):
    """
    >>> get_fileext("a.json")
    'json'
    >>> get_fileext("abc")
    ''
    """
    return os.path.splitext(filepath)[1][1:]


def find_loader(filepath=None, filetype=None, loaders=_LOADERS):
    if filepath is None and filetype is None:
        return None

    if filepath is None or filetype is not None:
        ext = filetype
    else:
        ext = get_fileext(filepath)

    return loaders.get(ext, None)


def load_context(filepath, filetype=None, enc=_ENCODING, werror=False):
    """Load context data from given file at `filepath`.

    :param filepath: Context data file path :: str
    :param filetype: Forced context file type
    :param enc: Character encoding of context file
    :param werror: raise exception if any error occured like gcc's -Werr
    """
    default = U.MyDict.createFromDict()

    loader = find_loader(filepath, filetype)
    if loader is None:
        m = "Couldn't find loader: path=%s, type=%s" % (filepath, filetype)
        if werror:
            raise RuntimeError(m)

        logging.warn(m)
        return default  # Return empty dict.

    logging.debug("Loader found: path=%s, type=%s" % (filepath, filetype))
    data = open(filepath, enc=enc).read()
    try:
        x = loader(data)
        if not U.is_dict(x):
            logging.warn("Top-level object is not a dict: " + filepath)
            return default

        return U.MyDict.createFromDict(x)

    except Exception, e:
        if werror:
            raise RuntimeError(str(e))

        logging.warn(str(e))
        return default


def load_contexts(pathspecs, enc=_ENCODING, werror=False):
    """Load context data from given files.

    :param paths: Context data file path list :: [str]
    """
    d = U.MyDict.createFromDict()
    for path, filetype in pathspecs:
        diff = load_context(path, filetype, enc, werror)
        if diff:
            d.update(diff)

    return d


# TODO:
#def __is_glob(s, gpat='*'):
#    return gpat in s and ...


def parse_filespec(fspec, sep=':', gpat='*'):
    """
    Parse given filespec `fspec` and return [(filetype, filepath)].

    :param fspec: filespec
    :param sep: a char separating filetype and filepath in filespec
    :param gpat: a char for glob pattern

    >>> parse_filespec("base.json")
    [('base.json', 'json')]
    >>> parse_filespec("yaml:foo.yaml")
    [('foo.yaml', 'yaml')]
    >>> parse_filespec("yaml:foo.dat")
    [('foo.dat', 'yaml')]

    # FIXME: How to test it?
    # >>> parse_filespec("yaml:bar/*.conf")
    # [('bar/a.conf', 'yaml'), ('bar/b.conf', 'yaml')]

    TODO: Allow '*' (glob pattern) in filepath when escaped with '\\', etc.
    """
    tp = (ft, fp) = tuple(fspec.split(sep)) if sep in fspec else \
        (get_fileext(fspec), fspec)

    return [(fs, ft) for fs in sorted(glob.glob(fp))] \
        if gpat in fspec else [U.flip(tp)]


def parse_and_load_contexts(contexts, enc=_ENCODING, werr=False):
    """
    :param contexts: list of context file specs
    :param enc: Input encoding of context files
    :param werr: Exit immediately if True and any errors occurrs
        while loading context files
    """
    if contexts:
        ctx = load_contexts(
            U.concat(parse_filespec(f) for f in contexts), enc, werr
        )
    else:
        ctx = MyDict.createFromDict()

    return ctx


# vim:sw=4:ts=4:et:
