#!/usr/bin/env python3

##############################################################################
# This script takes a gap file produced by fix_gaps.py or SPLATT and a map file
# of keys, and merges them into a new map file with gapped keys removed.
##############################################################################

import sys

if len(sys.argv) != 4:
  print('usage: {} <mode-X-gaps.map> <mode-X-keys.map> <new.map>'.format(sys.argv[0]))
  sys.exit(1)


gap_fname = sys.argv[1]
key_fname = sys.argv[2]
new_fname = sys.argv[3]

# read keys
keys = []
with open(key_fname, 'r') as fin:
  for line in fin:
    keys.append(line.strip())


fout = open(new_fname, 'w')
with open(gap_fname, 'r') as gap_file:
  for line in gap_file:
    # new ID
    key_id = int(line.strip())
    key = keys[key_id - 1]

    print(key, file=fout)
fout.close()

