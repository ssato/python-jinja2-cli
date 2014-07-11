#! /usr/bin/python -tt
import sys
import json
import yaml

try:
    inp = sys.argv[1]
    out = sys.argv[2]

    assert inp != out, "Input and output is same file!"

    data = yaml.load(open(inp))
    json.dump(data, open(out, "w"), indent=2)

except IndexError:
    sys.stderr.write("Usage: %s INPUT OUTPUT\n" % sys.argv[0])
    sys.exit(1)
