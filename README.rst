About
======

A CLI frontend for python-jinja2 based on:

* https://github.com/ssato/misc/blob/master/jinja2_template_render.py

Also imported some ideas in:

* https://github.com/mitsuhiko/jinja2/pull/129
  (https://github.com/mattrobenolt/jinja2/blob/cli/jinja2/cli.py)

Author: Satoru SATOH <ssato@redhat.com>
License: Same as python-jinja2, that is, BSD3.


Features
============

Multiple configuration files support
-------------------------------------

It supports multiple configuration files in YAML or JSON to set parameters w/
-C|--contexts option, ex. -C a.yaml -C b.yaml -C c.json.

Composition of config files are handled by external python-anyconfig module.

* anyconfig on PyPI: http://pypi.python.org/pypi/anyconfig/
* python-anyconfig github site: https://github.com/ssato/python-anyconfig

Template search paths
------------------------------

It supports setting template search paths w/ -T|--template-paths. This is
useful when using 'include' directive in templates; ex. -T .:templates/.

NOTE: The default search path will be [., templatedir] where templatedir is the
directory in which the given template file exists if -T option is not given.
And even if -T option is used, templatedir will be appended to that search
paths at the end.

Examples
==============================

please try `make -C examples` and  see the results:
"/tmp/jinja2-cli.examples.d/*.out"
