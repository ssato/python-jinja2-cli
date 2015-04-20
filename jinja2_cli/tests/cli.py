#
# Copyright (C) 2015 Satoru SATOH <ssato at redhat.com>
#
import os.path
import os
import subprocess
import unittest

import jinja2_cli.cli as TT
import jinja2_cli.tests.common as C


class Test_00_pure_functions(unittest.TestCase):

    def test_10_parse_template_paths__wo_paths(self):
        self.assertEquals(TT.parse_template_paths("/a/b/c.yml"),
                          [os.curdir, "/a/b"])

    def test_12_parse_template_paths__w_paths(self):
        self.assertEquals(TT.parse_template_paths("/a/b/c.yml", "/a/d:/a/e"),
                          ["/a/d", "/a/e", "/a/b"])


CLI_SCRIPT = os.path.join(C.selfdir(), "..", "cli.py")


def run(args=[]):
    """
    :throw: subprocess.CalledProcessError if something goes wrong
    """
    args = ["python", CLI_SCRIPT] + args
    devnull = open("/dev/null", 'w')

    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.join(C.selfdir(), "..")

    subprocess.check_call(args, stdout=devnull, stderr=devnull, env=env)


class Test_10_effectful_functions(unittest.TestCase):

    def setUp(self):
        self.workdir = C.setup_workdir()

    def tearDown(self):
        C.cleanup_workdir(self.workdir)

    def run_and_check_exit_code(self, args=[], code=0, _not=False):
        try:
            TT.main(["dummy"] + args)
        except SystemExit as e:
            if _not:
                self.assertNotEquals(e.code, code)
            else:
                self.assertEquals(e.code, code)

    def test_10__show_usage(self):
        run(["--help"])

    def test_12__wrong_option(self):
        self.run_and_check_exit_code(["--wrong-option-xyz"], _not=True)

# vim:sw=4:ts=4:et:
