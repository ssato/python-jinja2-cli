"""
    Jinja2 based template renderer.
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Compiles and render Jinja2-based template files.

    :copyright: (c) 2012 - 2015 Red Hat, Inc.
    :copyright: (c) 2012 by Satoru SATOH <ssato@redhat.com>
    :license: BSD-3

 Requirements: python-jinja2, python-simplejson (if python < 2.6) and PyYAML
 References: http://jinja.pocoo.org,
    especially http://jinja.pocoo.org/docs/api/#basics
"""
from __future__ import absolute_import

import jinja2.exceptions
import jinja2
import logging
import os.path
import os

from . import compat, utils


def mk_template_paths(filepath, template_paths=[]):
    """
    :param filepath: (Base) filepath of template file
    :param template_paths: Template search paths
    """
    tmpldir = os.path.abspath(os.path.dirname(filepath))
    if template_paths:
        return utils.uniq(template_paths + [tmpldir])
    else:
        return [os.curdir, tmpldir]  # default:


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

    >>> s = render_s('a = {{ a }}, b = "{{ b }}"', {'a': 1, 'b': 'bbb'})
    >>> assert s == 'a = 1, b = "bbb"'
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
        return render_s(utils.get_locale_sensitive_stdin().read(),
                        ctx, paths)
    else:
        try:
            return render_impl(filepath, ctx, paths)
        except jinja2.exceptions.TemplateNotFound as mtmpl:
            if not ask:
                raise RuntimeError("Template '%s' Not found: %s" %
                                   (filepath, str(mtmpl)))

            usr_tmpl = compat.raw_input(
                "\n*** Missing template '%s'. "
                "Please enter absolute or relative path starting from "
                "'.' to the template file: " % mtmpl
            )
            usr_tmpl = utils.normpath(usr_tmpl.strip())
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

    logging.warn("Could not find template=%s in paths=%s", filepath, paths)
    return None


def renderto(tmpl, ctx, paths, output=None, ask=True):
    content = render(tmpl, ctx, paths, ask)
    utils.write_to_output(content, output)

# vim:sw=4:ts=4:et:
