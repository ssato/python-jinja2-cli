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

NOTE: when multi-config files specified in -C option, parameters in these are
synthesized in a configuration, that is, if the content of a.yaml is::

   a:
     x: {'y': 1, 'z': 2}
     n: "aaa"

and the content of b.yaml is::

   a:
     x: {'y': 4, 'x': 0}
     m: "mmm"
     n: "bbb"

   b: "bbb"

then "-C a.yaml -C b.yaml" will provide a configuration such as

   a:
     x: {'x': 0, 'y': 4, 'z': 2}
     m: "mmm"
     n: "bbb"

   b: "bbb"


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
