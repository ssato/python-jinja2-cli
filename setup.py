from setuptools import setup, Command, find_packages

import glob
import os
import subprocess
import sys

curdir = os.getcwd()
sys.path.append(curdir)

PACKAGE = "python-jinja2-cli"
VERSION = "0.0.4.6"

# For daily snapshot versioning mode:
if os.environ.get("_SNAPSHOT_BUILD", None) is not None:
    import datetime
    VERSION = VERSION + datetime.datetime.now().strftime(".%Y%m%d")

data_files = []


class SrpmCommand(Command):

    user_options = []
    build_stage = "s"

    curdir = os.path.abspath(os.curdir)
    rpmspec = os.path.join(curdir, "package.spec")

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.pre_sdist()
        self.run_command('sdist')
        self.build_rpm()

    def pre_sdist(self):
        c = open(self.rpmspec + ".in").read()
        open(self.rpmspec, "w").write(c.replace("@VERSION@", VERSION))

    def build_rpm(self):
        rpmbuild = os.path.join(self.curdir, "pkg/rpmbuild-wrapper.sh")
        workdir = os.path.join(self.curdir, "dist")

        cmd_s = "%s -w %s -s %s %s" % (rpmbuild, workdir, self.build_stage,
                                       self.rpmspec)
        subprocess.check_call(cmd_s, shell=True)


class RpmCommand(SrpmCommand):

    build_stage = "b"


setup(name=PACKAGE,
      version=VERSION,
      description="A CUI frontend for Jinja2 template engine.",
      author="Satoru SATOH",
      author_email="ssato@redhat.com",
      license="BSD",
      url="https://github.com/ssato/python-jinja2-cli",
      packages=find_packages(),
      scripts=glob.glob("tools/*"),
      data_files=data_files,
      cmdclass={
          "srpm": SrpmCommand,
          "rpm":  RpmCommand,
      },)

# vim:sw=4:ts=4:et:
