#
# Copyright (C) 2015 Satoru SATOH <ssato at redhat.com>
#
import os.path
import os
import subprocess
import unittest

import jinja2_cli.cli as TT
import jinja2_cli.tests.common as C


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


def run_and_check_exit_code(args=[], code=0):
    try:
        TT.main(["dummy"] + args)
    except SystemExit as e:
        return e.code == code

    return True


class Test_00(unittest.TestCase):

    def run_and_check_exit_code(self, args=[], code=0, _not=False):
        if _not:
            self.assertFalse(run_and_check_exit_code(args, code))
        else:
            self.assertTrue(run_and_check_exit_code(args, code))

    def test_10_parse_template_paths__wo_paths(self):
        self.assertEquals(TT.parse_template_paths("/a/b/c.yml"),
                          [os.curdir, "/a/b"])

    def test_12_parse_template_paths__w_paths(self):
        self.assertEquals(TT.parse_template_paths("/a/b/c.yml", "/a/d:/a/e"),
                          ["/a/d", "/a/e", "/a/b"])

    def test_50_main__wo_args(self):
        self.run_and_check_exit_code()

    def test_10__show_usage(self):
        self.run_and_check_exit_code(["--help"])

    def test_12__wrong_option(self):
        self.run_and_check_exit_code(["--wrong-option-xyz"], _not=True)


class Test_10_with_workdir(unittest.TestCase):

    def setUp(self):
        self.workdir = C.setup_workdir()

    def tearDown(self):
        C.cleanup_workdir(self.workdir)

    def run_and_check_exit_code(self, args=[], code=0, _not=False):
        if _not:
            self.assertFalse(run_and_check_exit_code(args, code))
        else:
            self.assertTrue(run_and_check_exit_code(args, code))

    def test_10_main_dumpvars(self):
        tmpl = os.path.join(self.workdir, "test.j2")
        output = os.path.join(self.workdir, "output.txt")
        open(tmpl, 'w').write("{{ hello }}\n")

        self.run_and_check_exit_code(["--dumpvars", "-o", output, tmpl])
        self.assertEquals(open(output).read(), "hello\n")

    def test_20_main_render(self):
        tmpl = os.path.join(self.workdir, "test.j2")
        output = os.path.join(self.workdir, "output.txt")
        open(tmpl, 'w').write("{{ hello|default('hello') }}")

        self.run_and_check_exit_code(["-o", output, tmpl])
        self.assertEquals(open(output).read(), "hello")

# vim:sw=4:ts=4:et:
