#! /bin/bash
set -ex
testsdir=${0%/*}
cd ${testsdir}
python ../jinja2_cui/cui.py -T . -C x.yaml -C yaml:y_yaml -o /tmp/test.out -D b.template
