#! /bin/bash
set -ex
testsdir=${0%/*}
cd ${testsdir}
PYTHONPATH=.. python ../src/jinja2-cui r -T . -C x.yaml -C yaml:y_yaml -C yaml:conf.d/*.conf -o /tmp/test.out -D b.template
