#!/usr/bin/env python3

###############################################################################
# VAST 2015 Mini-Challenge 1 parser
#
# This file creates two tensors, a 3D and a 5D version of the dataset. The
# modes are:
#
#   time x person x action x x-location x y-location
#
# and the values are always 1.0.
# 
# File format:
#   Timestamp,id,type,X,Y
###############################################################################

import sys
import csv
from dateutil import parser

###############################################################################
#
# FILES - EDIT THESE
#

fout3 = open('vast-2015-mc1-3d.tns', 'w')
fout5 = open('vast-2015-mc1-5d.tns', 'w')
###############################################################################


if len(sys.argv) == 1:
  print('usage: {} <CSV files>'.format(sys.argv[0]))
  sys.exit(1)


def write_map(map_dic, fname):
  # invert map_dic so we can print keys in order
  lookup = [None] * len(map_dic)
  for x in map_dic.keys():
    lookup[map_dic[x] - 1] = x

  with open(fname, 'w') as fout:
    for x in lookup:
      print(x, file=fout)


def get_map_id(map_dic, key):
  if key not in map_dic:
    map_dic[key] = len(map_dic) + 1
  return map_dic[key]


def read_csv(fname):
  with open(fname, 'r') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    next(csvreader) # grab header
    for row in csvreader:
      yield row


times = dict()
ids   = dict()
types = dict()
xs    = dict()
ys    = dict()


# file is in the format: date, userID, itemID, tag
for csv_file in sys.argv[1:]:
  for row in read_csv(csv_file):

    time      = get_map_id(times, row[0])
    person_id = get_map_id(ids, row[1])
    action    = get_map_id(types, row[2])
    x         = get_map_id(xs, row[3])
    y         = get_map_id(ys, row[4])
    
    print('{} {} {} 1.0'.format(time, person_id, action), file=fout3)
    print('{} {} {} {} {} 1.0'.format(time, person_id, action, x, y), file=fout5)

fout3.close()
fout5.close()

print('#times: {}'.format(len(times)))
print('#persons: {}'.format(len(ids)))
print('#types: {}'.format(len(types)))
print('#xs: {}'.format(len(xs)))
print('#ys: {}'.format(len(ys)))

write_map(times, 'mode-1-times.map')
write_map(ids,   'mode-2-persons.map')
write_map(types, 'mode-3-types.map')
write_map(xs,    'mode-4-xlocs.map')
write_map(ys,    'mode-5-ylocs.map')

