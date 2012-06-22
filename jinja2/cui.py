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
import logging
import optparse
import os.path
import sys


# Borrowed from https://github.com/mattrobenolt/jinja2/blob/cli/jinja2/cli.py:
class InvalidDataFormat(Exception): pass
class InvalidInputData(Exception): pass
class MalformedJSON(InvalidInputData): pass
class MalformedINI(InvalidInputData): pass
class MalformedYAML(InvalidInputData): pass
class MalformedQuerystring(InvalidInputData): pass


# Data loaders.
#   Key: file extension
#   Value: (load_func, possible_exception, exception_on_error)
LOADERS = {}


try:
    import json
    LOADERS["json"] = LOADERS["jsn"] = (json.loads, ValueError, MalformedJSON)
except ImportError:
    try:
        import simplejson as json
        LOADERS["json"] = LOADERS["jsn"] = (
            json.loads, json.JSONDecodeError, MalformedJSON
        )
    except ImportError:
        sys.stderr.write("JSON support is disabled as module not found.\n")

try:
    import yaml
    LOADERS["yaml"] = LOADERS["yml"] = (
        yaml.load, yaml.YAMLError, MalformedYAML
    )
except ImportError:
    sys.stderr.write("YAML support is disabled as module not found.\n")


sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
sys.stderr = codecs.getwriter('utf_8')(sys.stderr)


def get_loader(filepath, loaders=LOADERS):
    file_and_ext = os.path.splitext(filepath)

    if file_and_ext[1]: # ext, e.g. ".yaml"
        ldr = loaders.get(file_and_ext[1][1:], False)
        if ldr:
            return ldr

    return None 


def load_context(filepath):
    """Load context data from given file.

    :param filepath: Context data file path :: str
    """
    loader = get_loader(filepath)
    if loader is None:
        logging.warn("Could not get appropriate loader for " + loader)
        return {}

    (load_fun, possible_exception, exception_on_error) = loader
    data = open(filepath).read()
    try:
        return load_fun(data)

    except possible_exception:
        logging.warn(u"%s ..." % data[:50])
        # or:
        # raise exception_on_error(u"%s ..." % data[:50])
        return {}


def load_contexts(paths):
    """Load context data from given files.

    :param paths: Context data file path list :: [str]
    """
    d = {}
    for path in paths:
        diff = load_context(path)
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


def option_parser():
    defaults = dict(
        template_paths=None,
        output=None,
        contexts=[],
        debug=False,
    )

    p = optparse.OptionParser("%prog [OPTION ...] TEMPLATE_FILE")
    p.set_defaults(**defaults)

    p.add_option("-T", "--template-paths",
        help="Coron ':' separated template search paths [.]")
    p.add_option("-o", "--output", help="Output filename [stdout]")
    p.add_option("-C", "--contexts",
        help="Coron ':' separated context data file[s] to instantiate templates"
    )
    p.add_option("-D", "--debug", action="store_true", help="Debug mode")

    return p


def main(argv):
    logging.getLogger().setLevel(logging.INFO)

    p = option_parser()
    (options, args) = p.parse_args(argv[1:])

    if not args:
        p.print_help()
        sys.exit(0)

    if options.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    sep = ":"

    if options.contexts:
        ctx = load_contexts(options.contexts.split(sep))
    else:
        ctx = {}

    if options.template_paths:
        try:
            paths = options.template_paths.split(sep)
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
        open(options.output, "w").write(result)
    else:
        sys.stdout.write(result)


# vim:sw=4:ts=4:et:
