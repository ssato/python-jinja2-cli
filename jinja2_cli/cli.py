"""
CLI frontend for jinja2, one of most popular template engines.

:copyright: (c) 2012 - 2015 Red Hat, Inc.
:copyright: (c) 2012 by Satoru SATOH <ssato@redhat.com>
:license: BSD-3
"""
from __future__ import absolute_import

import logging
import optparse
import sys

from . import utils, render


def parse_template_paths(tmpl, paths=None, sep=":"):
    """
    Parse template_paths option string and return [template_path].

    :param tmpl: Template file to render
    :param paths: str to specify template path list separated by `sep`
    :param sep: template path list separator
    """
    if paths:
        try:
            paths = render.mk_template_paths(tmpl, paths.split(sep))
            assert paths
        except:
            logging.warn("Ignored as invalid form: %s", paths)
            paths = render.mk_template_paths(tmpl, [])
    else:
        paths = render.mk_template_paths(tmpl, [])

    logging.debug("Template search paths: %s", str(paths))
    return paths


def option_parser(argv=sys.argv):
    defaults = dict(template_paths=None, output=None, contexts=[], debug=False,
                    werror=False, ask=False)

    p = optparse.OptionParser("%prog [OPTION ...] TEMPLATE_FILE", prog=argv[0])
    p.set_defaults(**defaults)

    p.add_option("-T", "--template-paths",
                 help="Colon ':' separated template search paths. "
                      "Please note that dir in which given template exists "
                      "is always included in the search paths (at the end of "
                      "the path list) regardless of this option. "
                      "[., dir in which given template file exists]")
    p.add_option("-C", "--contexts", action="append",
                 help="Specify file path and optionally its filetype, to "
                      "provides context data to instantiate templates. "
                      " The option argument's format is "
                      " [type:]<file_name_or_path_or_glob_pattern>"
                      " ex. -C json:common.json -C ./specific.yaml -C "
                      "yaml:test.dat, -C yaml:/etc/foo.d/*.conf")
    p.add_option("-o", "--output", help="Output filename [stdout]")
    p.add_option("-D", "--debug", action="store_true", help="Debug mode")
    p.add_option("-W", "--werror", action="store_true",
                 help="Exit on warnings if True such as -Werror optoin "
                      "in gcc")
    return p


def main(argv):
    p = option_parser(argv)
    (options, args) = p.parse_args(argv[1:])

    if not args:
        p.print_help()
        sys.exit(0)

    logging.basicConfig(format="[%(levelname)s] %(message)s",
                        level=(logging.DEBUG if options.debug else
                               logging.INFO))

    tmpl = args[0]
    ctx = utils.parse_and_load_contexts(options.contexts, options.werror)
    paths = parse_template_paths(tmpl, options.template_paths)
    render.renderto(tmpl, ctx, paths, options.output)


if __name__ == '__main__':
    main(sys.argv)

# vim:sw=4:ts=4:et:
