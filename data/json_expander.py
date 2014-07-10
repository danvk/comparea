#!/usr/bin/env python

import json
import sys

assert len(sys.argv) == 2
print json.dumps(json.load(file(sys.argv[1])), indent=2)
