About
======

.. image:: https://api.travis-ci.org/ssato/python-jinja2-cli.png?branch=master
   :target: https://travis-ci.org/ssato/python-jinja2-cli
   :alt: Test status

A CLI frontend for python-jinja2 based on:

* https://github.com/ssato/misc/blob/master/jinja2_template_render.py

Also imported some ideas in:

* https://github.com/mitsuhiko/jinja2/pull/129
  (https://github.com/mattrobenolt/jinja2/blob/cli/jinja2/cli.py)

Author: Satoru SATOH <ssato@redhat.com>
License: Same as python-jinja2, that is, BSD3.

Features
=========

Multiple configuration files support
-------------------------------------

It supports multiple configuration files in YAML or JSON or others to set
parameters w/ -C|--contexts option, ex. -C a.yaml -C b.yaml -C c.json.

Composition of config files are handled by external python-anyconfig module if
available.

- anyconfig on PyPI: http://pypi.python.org/pypi/anyconfig/
- python-anyconfig github site: https://github.com/ssato/python-anyconfig

Template search paths
-----------------------

It supports setting template search paths w/ -T|--template-paths. This is
useful when using 'include' directive in templates; ex. -T .:templates/.

NOTE: The default search path will be [., templatedir] where templatedir is the
directory in which the given template file exists if -T option is not given.
And even if -T option is used, templatedir will be appended to that search
paths at the end.

Usage
=======

Help
-------

.. code-block:: console

  ssato@localhost% PYTHONPATH=. python tools/jinja2-cli -h
  Usage: tools/jinja2-cli [OPTION ...] TEMPLATE_FILE

  Options:
    -h, --help            show this help message and exit
    -T TEMPLATE_PATHS, --template-paths=TEMPLATE_PATHS
                          Colon ':' separated template search paths. Please note
                          that dir in which given template exists is always
                          included in the search paths (at the end of the path
                          list) regardless of this option. [., dir in which
                          given template file exists]
    -C CONTEXTS, --contexts=CONTEXTS
                          Specify file path and optionally its filetype, to
                          provides context data to instantiate templates.  The
                          option argument's format is
                          [type:]<file_name_or_path_or_glob_pattern> ex. -C
                          json:common.json -C ./specific.yaml -C yaml:test.dat,
                          -C yaml:/etc/foo.d/*.conf
    -o OUTPUT, --output=OUTPUT
                          Output filename [stdout]
    --dumpvars            Dump template variables instead of compile it
    -D, --debug           Debug mode
    -W, --werror          Exit on warnings if True such as -Werror optoin in gcc
  ssato@localhost%

Examples
---------

please try `make -C examples` and  see the results:
"/tmp/jinja2-cli.examples.d/\*.out".

Build & Install
================

If you're Fedora or Red Hat Enterprise Linux user, you can build and install
[s]rpm by yourself:

.. code-block:: console

   $ python setup.py srpm && mock dist/python-jinja2-cli-<ver_dist>.src.rpm

or:

.. code-block:: console

   $ python setup.py rpm

Otherwise, try usual ways to build and/or install python modules such like 'pip
install git+https://github.com/ssato/python-jinja2-cli' and 'python setup.py
bdist', etc.

Hacks
=======

How to test
-------------

Try to run '[WITH_COVERAGE=1] ./pkg/runtest.sh [path_to_python_code]'.

Other alternatives
=======================

The followings look having similar to this module, that is, these can processs
YAML/JSON/... context files and render (compile) jinja2-based templates, I
guess.

- https://github.com/mattrobenolt/jinja2-cli
- https://github.com/kolypto/j2cli
- https://bitbucket.org/luisfernando/jinjaconfig

This module (python-jinja2-cli) might demonstrate a few advantages over them in
the following respect:

- It can process multiple configuration file formats with python-anyconfig's help.
- It can process multiple cascading configuration files with python-anyconfig's help.
- It can process UTF-8 configuration (context) files and templates properly.

.. vim:sw=2:ts=2:et:
