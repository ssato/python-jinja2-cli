"""
    Dump vars in Jinja2-based template files.

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
 References: http://jinja.pocoo.org
"""
import jinja2_cui.render as R
import jinja2.meta
import logging
import optparse
import sys

from functools import reduce as foldl
from logging import DEBUG, INFO
from operator import concat as listplus


def find_vars_0(filepath, paths):
    """
    Find and return variables in given template.

    see also: http://jinja.pocoo.org/docs/api/#the-meta-api

    :param filepath: (Base) filepath of template file
    :param paths: Template search paths

    :return:  [(template_abs_path, [var])]
    """
    filepath = R.template_path(filepath, paths)
    ast = R.get_ast(filepath, paths)

    def find_undecls_0(fpath, paths=paths):
        ast_ = R.get_ast(fpath, paths)
        if ast_:
            return list(jinja2.meta.find_undeclared_variables(ast_))
        else:
            return []

    return [(f, find_undecls_0(f)) for f in R.find_templates(filepath, paths)]


def find_vars(filepath, paths):
    return R.uniq(
        foldl(listplus, (vs[1] for vs in find_vars_0(filepath, paths)), [])
    )


def option_parser(argv=sys.argv, defaults=None):
    if defaults is None:
        defaults = dict(
            template_paths=None, output=None, debug=False,
            encoding=R._ENCODING,
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

    p.add_option("-o", "--output", help="Output filename [stdout]")
    p.add_option("-E", "--encoding", help="I/O encoding [%default]")
    p.add_option("-D", "--debug", action="store_true", help="Debug mode")

    return p


def main(argv):
    p = option_parser(argv)
    (options, args) = p.parse_args(argv[1:])

    if not args:
        p.print_help()
        sys.exit(0)

    logging.getLogger().setLevel(DEBUG if options.debug else INFO)

    tmpl = args[0]
    paths = R.parse_template_paths(tmpl, options.template_paths)

    vars = '\n'.join(find_vars(tmpl, paths)) + '\n'
    R.write_to_output(options.output, options.encoding, vars)


if __name__ == '__main__':
    main(sys.argv)

# vim:sw=4:ts=4:et:
