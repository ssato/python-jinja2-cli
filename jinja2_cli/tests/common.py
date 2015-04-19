#
# Copyright (C) 2011 - 2015 Satoru SATOH <ssato at redhat.com>
# License: MIT
#
import os.path
import subprocess
import tempfile


def selfdir(filename=__file__):
    return os.path.dirname(filename)


def setup_workdir():
    return tempfile.mkdtemp(dir="/tmp", prefix="python-jinja2-cli-tests-")


def cleanup_workdir(workdir):
    """
    FIXME: Danger!
    """
    return subprocess.check_call(["/bin/rm", "-rf", workdir])

# vim:sw=4:ts=4:et:
