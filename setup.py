from setuptools import setup, Command, find_packages

import glob
import os
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
    cmd_fmt = """rpmbuild -b%(build_stage)s \
        --define \"_topdir %(rpmdir)s\" \
        --define \"_sourcedir %(rpmdir)s\" \
        --define \"_buildroot %(BUILDROOT)s\" \
        %(rpmspec)s
    """

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.run_command('sdist')
        self.build_rpm()

    def build_rpm(self):
        params = dict()

        params["build_stage"] = self.build_stage
        rpmdir = params["rpmdir"] = os.path.join(
            os.path.abspath(os.curdir), "dist"
        )
        rpmspec = params["rpmspec"] = os.path.join(
            rpmdir, "../%s.spec" % PACKAGE
        )

        for subdir in ("SRPMS", "RPMS", "BUILD", "BUILDROOT"):
            sdir = params[subdir] = os.path.join(rpmdir, subdir)

            if not os.path.exists(sdir):
                os.makedirs(sdir, 493)  # 493 = 0o755 (py3) or 0755 (py2)

        c = open(rpmspec + ".in").read()
        open(rpmspec, "w").write(c.replace("@VERSION@", VERSION))

        os.system(self.cmd_fmt % params)


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
