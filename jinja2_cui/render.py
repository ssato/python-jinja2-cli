"""
    Jinja2 based template renderer.
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Compiles and render Jinja2-based template files.

    :copyright: (c) 2012 by Satoru SATOH <ssato@redhat.com>
    :license: BSD-3

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions are met:

   * Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.
   * Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.
   * Neither the name of the author nor the names of its contributors may
     be used to endorse or promote products derived from this software
     without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
 DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

 Requirements: python-jinja2, python-simplejson (if python < 2.6) and PyYAML
 References: http://jinja.pocoo.org,
    especially http://jinja.pocoo.org/docs/api/#basics
"""
from jinja2.exceptions import TemplateNotFound

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

from logging import DEBUG, INFO

try:
    chain_from_iterable = itertools.chain.from_iterable
except AttributeError:
    # Borrowed from library doc, 9.7.1 Itertools functions:
    def _from_iterable(iterables):
        for it in iterables:
            for element in it:
                yield element

    chain_from_iterable = _from_iterable


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


def is_dict(x):
    return isinstance(x, (MyDict, dict))


def is_iterable(x):
    return isinstance(x, (list, tuple)) or getattr(x, "next", False)


class MyDict(dict):

    @classmethod
    def createFromDict(cls, dic={}):
        md = MyDict()

        for k, v in dic.iteritems():
            md[k] = cls.createFromDict(v) if is_dict(v) else v

        return md

    def update(self, other, merge_lists=False):
        """Merge `self` and `other` recursively.

        :param merge_lists: Merge not only dicts but also lists,
            e.g. [1, 2], [3, 4] ==> [1, 2, 3, 4]
        """
        if is_dict(other):
            for k, v in other.iteritems():
                if k in self and is_dict(v) and is_dict(self[k]):
                    self[k].update(v, merge_lists)  # update recursively.
                else:
                    if merge_lists and is_iterable(v):
                        self[k] = self[k] + list(v)  # append v :: list
                    else:
                        self[k] = v  # replace self[k] w/ v or set.


def get_fileext(filepath):
    """
    >>> get_fileext("a.json")
    'json'
    >>> get_fileext("abc")
    ''
    """
    return os.path.splitext(filepath)[1][1:]


def get_loader(filepath=None, filetype=None, loaders=_LOADERS):
    if filepath is None and filetype is None:
        logging.error("Could not determine loader type")
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
    default = MyDict.createFromDict()

    loader = get_loader(filepath, filetype)
    if loader is None:
        m = "Couldn't get loader: path=%s, type=%s" % (filepath, filetype)
        if werror:
            raise RuntimeError(m)

        logging.warn(m)
        return default

    logging.debug("Loader found: path=%s, type=%s" % (filepath, filetype))
    data = open(filepath, enc=enc).read()
    try:
        x = loader(data)
        if not is_dict(x):
            logging.warn("Top-level object is not a dict: " + filepath)
            return default

        return MyDict.createFromDict(x)

    except Exception, e:
        if werror:
            raise RuntimeError(str(e))

        logging.warn(str(e))
        return default


def load_contexts(pathspecs, enc=_ENCODING, werror=False):
    """Load context data from given files.

    :param paths: Context data file path list :: [str]
    """
    d = MyDict.createFromDict()
    for path, filetype in pathspecs:
        diff = load_context(path, filetype, enc, werror)
        if diff:
            d.update(diff)

    return d


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


def mk_template_paths(filepath, template_paths=[]):
    """
    :param filepath: (Base) filepath of template file
    :param template_paths: Template search paths
    """
    tmpldir = os.path.abspath(os.path.dirname(filepath))
    if template_paths:
        return uniq(template_paths + [tmpldir])
    else:
        # default:
        return [os.curdir, tmpldir]


def tmpl_env(paths):
    """
    :param paths: Template search paths
    """
    return jinja2.Environment(loader=jinja2.FileSystemLoader(paths))


def render_s(tmpl_s, ctx, paths=[os.curdir]):
    """
    Compile and render given template string `tmpl_s` with context `context`.

    :param tmpl_s: Template string
    :param ctx: Context dict needed to instantiate templates
    :param paths: Template search paths

    >>> render_s('a = {{ a }}, b = "{{ b }}"', {'a': 1, 'b': 'bbb'})
    u'a = 1, b = "bbb"'
    """
    return tmpl_env(paths).from_string(tmpl_s).render(**ctx)


def render_impl(filepath, ctx, paths):
    """
    :param filepath: (Base) filepath of template file or '-' (stdin)
    :param ctx: Context dict needed to instantiate templates
    :param paths: Template search paths
    """
    env = tmpl_env(paths)
    return env.get_template(os.path.basename(filepath)).render(**ctx)


def chaincalls(callables, x):
    """
    :param callables: callable objects to apply to x in this order
    :param x: Object to apply callables
    """
    for c in callables:
        assert callable(c), "%s is not callable object!" % str(c)
        x = c(x)

    return x


def normpath(path):
    """Normalize given path.

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


def render(filepath, ctx, paths, ask=False):
    """
    Compile and render template, and return the result.

    Similar to the above but template is given as a file path `filepath` or
    sys.stdin if `filepath` is '-'.

    :param filepath: (Base) filepath of template file or '-' (stdin)
    :param ctx: Context dict needed to instantiate templates
    :param paths: Template search paths
    :param ask: Ask user for missing template location if True
    """
    if filepath == '-':
        return render_s(sys.stdin.read(), ctx, paths)
    else:
        try:
            return render_impl(filepath, ctx, paths)
        except TemplateNotFound, mtmpl:
            if not ask:
                raise RuntimeError("Template Not found: " + str(mtmpl))

            usr_tmpl = raw_input(
                "\n*** Missing template '%s'. "
                "Please enter its location (path): " % mtmpl
            )
            usr_tmpl = normpath(usr_tmpl.strip())
            usr_tmpldir = os.path.dirname(usr_tmpl)

            return render_impl(usr_tmpl, ctx, paths + [usr_tmpldir])


def template_path(filepath, paths):
    """
    Return resolved path of given template file

    :param filepath: (Base) filepath of template file
    :param paths: Template search paths
    """
    for p in paths:
        candidate = os.path.join(p, filepath)
        if os.path.exists(candidate):
            return candidate

    logging.warn("Could not find template=%s in paths=%s" % (filepath, paths))
    return None


def get_ast(filepath, paths):
    """Parse template (`filepath`) and return an abstract syntax tree.

    see also: http://jinja.pocoo.org/docs/api/#the-meta-api

    :param filepath: (Base) filepath of template file
    :param paths: Template search paths
    """
    try:
        return tmpl_env(paths).parse(open(filepath).read())
    except:
        return None


def flip(xy):
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
    return list(chain_from_iterable(xs for xs in xss))


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
        if gpat in fspec else [flip(tp)]


def parse_and_load_contexts(contexts, enc=_ENCODING, werr=False):
    """
    :param contexts: list of context file specs
    :param enc: Input encoding of context files
    :param werr: Exit immediately if True and any errors occurrs
        while loading context files
    """
    if contexts:
        ctx = load_contexts(
            concat(parse_filespec(f) for f in contexts), enc, werr
        )
    else:
        ctx = MyDict.createFromDict()

    return ctx


def parse_template_paths(tmpl, paths, sep=":"):
    """
    Parse template_paths option string and return [template_path].

    :param tmpl: Template file to render
    :param paths: str to specify template path list separated by `sep`
    :param sep: template path list separator
    """
    if paths:
        try:
            paths = mk_template_paths(tmpl, paths.split(sep))
            assert paths
        except:
            sys.stderr.write(u"Ignored as invalid form: '%s'\n" % paths)
            paths = mk_template_paths(tmpl, [])
    else:
        paths = mk_template_paths(tmpl, [])

    logging.debug("Template search paths: " + str(paths))
    return paths


def option_parser(argv=sys.argv):
    defaults = dict(
        template_paths=None, output=None, contexts=[], debug=False,
        encoding=_ENCODING, werror=False, ask=False,
    )

    p = optparse.OptionParser(
        "%prog [OPTION ...] TEMPLATE_FILE", prog=argv[0],
    )
    p.set_defaults(**defaults)

    p.add_option("-T", "--template-paths",
        help="Colon ':' separated template search paths. " + \
            "Please note that dir in which given template exists " + \
            "is always included in the search paths (at the end of " + \
            "the path list) regardless of this option. " + \
            "[., dir in which given template file exists]")
    p.add_option("-C", "--contexts", action="append",
        help="Specify file path and optionally its filetype, to provides "
            " context data to instantiate templates. "
            " The option argument's format is "
            " [type:]<file_name_or_path_or_glob_pattern>"
            " ex. -C json:common.json -C ./specific.yaml -C yaml:test.dat, "
            "     -C yaml:/etc/foo.d/*.conf"
    )
    p.add_option("-o", "--output", help="Output filename [stdout]")
    p.add_option("-E", "--encoding", help="I/O encoding [%default]")
    p.add_option("-D", "--debug", action="store_true", help="Debug mode")
    p.add_option("-W", "--werror", action="store_true",
        help="Exit on warnings if True such like -Werror optoin for gcc"
    )

    return p


def write_to_output(output=None, encoding="utf-8", content=""):
    if output and not output == '-':
        outdir = os.path.dirname(output)
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        open(output, "w", encoding).write(content)
    else:
        codecs.getwriter(encoding)(sys.stdout).write(content)


def renderto(tmpl, ctx, paths, output=None, encoding=_ENCODING, ask=True):
    write_to_output(output, encoding, render(tmpl, ctx, paths, ask))


def main(argv):
    p = option_parser(argv)
    (options, args) = p.parse_args(argv[1:])

    if not args:
        p.print_help()
        sys.exit(0)

    logging.getLogger().setLevel(DEBUG if options.debug else INFO)

    tmpl = args[0]
    ctx = parse_and_load_contexts(
        options.contexts, options.encoding, options.werror
    )
    paths = parse_template_paths(tmpl, options.template_paths)
    renderto(tmpl, ctx, paths, options.output, options.encoding)


if __name__ == '__main__':
    main(sys.argv)

# vim:sw=4:ts=4:et:
