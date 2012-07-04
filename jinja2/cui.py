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


 Requirements: python-jinja2, python-simplejson (python < 2.6) and PyYAML
 References: http://jinja.pocoo.org
"""
import codecs
import jinja2
import locale
import logging
import optparse
import os.path
import sys


# Data loaders: Key=file_extension, Value=load_func
LOADERS = {}

_ENCODING = locale.getdefaultlocale()[1]

sys.stdout = codecs.getwriter(_ENCODING)(sys.stdout)
sys.stderr = codecs.getwriter(_ENCODING)(sys.stderr)

EXIT_ON_WARNS = False


# Override the default implementation:
def open(path, flag='r', enc=_ENCODING):
    return codecs.open(path, flag, enc)


try:
    import json
    LOADERS["json"] = LOADERS["jsn"] = json.loads
except ImportError:
    try:
        import simplejson as json
        LOADERS["json"] = LOADERS["jsn"] = json.loads
    except ImportError:
        sys.stderr.write(u"JSON support is disabled as module not found.\n")

try:
    import yaml
    LOADERS["yaml"] = LOADERS["yml"] = yaml.load
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


def get_loader(filepath=None, filetype=None, loaders=LOADERS):
    if filepath is None and filetype is None:
        logging.error("Could not determine loader type")
        return None

    if filepath is None or filetype is not None:
        ext = filetype
    else:
        ext = get_fileext(filepath)

    logging.info("type=" + ext)
    return loaders.get(ext, None)


def load_context(filepath, filetype=None, enc=_ENCODING):
    """Load context data from given file.

    :param filepath: Context data file path :: str
    """
    loader = get_loader(filepath, filetype)
    if loader is None:
        m = "Couldn't get loader: path=%s, type=%s" % (filepath, filetype)
        if EXIT_ON_WARNS:
            logging.warn(m)
        else:
            raise RuntimeError(m)
        return {}

    logging.info("Loader found: path=%s, type=%s" % (filepath, filetype))
    data = open(filepath, enc=enc).read()
    try:
        return loader(data)
    except Exception, e:
        if EXIT_ON_WARNS:
            logging.warn(str(e))
        else:
            raise RuntimeError(str(e))
        return {}


def load_contexts(pathspecs, enc):
    """Load context data from given files.

    :param paths: Context data file path list :: [str]
    """
    d = {}
    for path, filetype in pathspecs:
        diff = load_context(path, filetype, enc)
        if diff:
            d.update(diff)

    return d


def render(filepath, context, template_paths=[]):
    """
    Compile and render template, and returns the result.

    see also: http://jinja.pocoo.org/docs/api/#basics

    :param filepath: (Base) filepath of template file
    :param context: Context dict needed to instantiate templates
    :param template_paths: Template search paths
    """
    topdir = os.path.abspath(os.path.dirname(filepath))
    filename = os.path.basename(filepath)

    paths = [topdir, os.curdir]

    if template_paths:
        paths += template_paths

    paths = list(set(paths))  # uniq
    logging.debug("Template search paths: " + str(paths))

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(paths))

    return env.get_template(filename).render(**context)


def parse_filespec(filespec, sep=":"):
    """
    >>> parse_filespec("base.json")
    ('json', 'base.json')
    >>> parse_filespec("yaml:foo.yaml")
    ('yaml', 'foo.yaml')
    >>> parse_filespec("yaml:foo.dat")
    ('yaml', 'foo.dat')
    """
    if sep in filespec:
        return tuple(filespec.split(sep))
    else:
        return (get_fileext(filespec), filespec)


def flip(xy):
    (x, y) = xy
    return (y, x)


def parse_filespecs(filespecs, sep=","):
    """
    >>> parse_filespecs("")
    []
    >>> parse_filespecs("base.json")
    [('base.json', 'json')]
    >>> parse_filespecs("base.json,foo.yaml")
    [('base.json', 'json'), ('foo.yaml', 'yaml')]
    >>> parse_filespecs("base.json,yaml:foo.dat")
    [('base.json', 'json'), ('foo.dat', 'yaml')]
    """
    return [flip(parse_filespec(fs)) for fs in filespecs.split(sep) if fs]


def option_parser():
    defaults = dict(
        template_paths=None,
        output=None,
        contexts=[],
        debug=False,
        encoding=_ENCODING,
    )

    p = optparse.OptionParser("%prog [OPTION ...] TEMPLATE_FILE")
    p.set_defaults(**defaults)

    p.add_option("-T", "--template-paths",
        help="Colon ':' separated template search paths [.]")
    p.add_option("-C", "--contexts",
        help="Specify file[s] (and its file type optionally) to provides "
            " context data to instantiate templates. "
            " The option argument's format is "
            " [type:]<filename_or_path>[,[type:]<filename_or_path>,...], "
            " ex. json:common.json,./specific.yaml,yaml:test.dat"
    )
    p.add_option("-o", "--output", help="Output filename [stdout]")
    p.add_option("-E", "--encoding",
        help="Input and output encoding [%default]"
    )
    p.add_option("-D", "--debug", action="store_true", help="Debug mode")
    p.add_option("-W", "--warn", action="store_true",
        help="Exit on warnings if True such like -Werror optoin for gcc"
    )

    return p


def main(argv):
    global EXIT_ON_WARNS  # FIXME.

    logging.getLogger().setLevel(logging.INFO)

    p = option_parser()
    (options, args) = p.parse_args(argv[1:])

    if not args:
        p.print_help()
        sys.exit(0)

    if options.warn:
        EXIT_ON_WARNS = True

    if options.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if options.contexts:
        ctx = load_contexts(
            parse_filespecs(options.contexts), options.encoding
        )
    else:
        ctx = {}

    if options.template_paths:
        try:
            paths = options.template_paths.split(":")
        except:
            sys.stderr.write(
                u"Ignored as invalid form: '%s'\n" % options.template_paths
            )
            paths = []
    else:
        paths = []

    tmpl = args[0]
    result = render(tmpl, ctx, paths)

    if options.output:
        open(options.output, "w", options.encoding).write(result)
    else:
        codecs.getwriter(options.encoding)(sys.stdout).write(result)


if __name__ == '__main__':
    main(sys.argv)


# vim:sw=4:ts=4:et:
