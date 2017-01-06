#!/usr/bin/env python3


#
# NOTE: due to some duplicated tagging, this script will emit duplicate
# non-zeros. We merge them with a `max()` reduction, so the tensor remains
# binary.
#
# To fully replicate the tensor used in FROSTT:
#   $ ./parse_flickr.py
#   $ splatt check flickr4d.tns --fix=fixed.tns
#   $ awk '{print($1,$2,$3,$4,"1.0")}' fixed.tns > flickr4d.tns
#
# Generating the order-3 flickr tensor can be achieved by removing the
# fourth mode (`awk` works well for this). More duplicate non-zeros will
# appear, so perform the above process again.
#



import sys
from dateutil import parser


if len(sys.argv) == 1:
  print('usage: {} <data>'.format(sys.argv[0]))
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

users = dict()
items = dict()
tags  = dict()
times = dict()

# file is in the format: date, userID, itemID, tag
fout4 = open('flickr4d.tns', 'w')
fout3 = open('flickr3d.tns', 'w')

with open(sys.argv[1], 'r') as fin:
  for line in fin:
    l = line.split()

    if len(l) >= 5:
      # just parse the day
      time = parser.parse(l[0])
      user = l[2]
      item = l[3]
      tag = ''.join(l[4:])

      time_id = get_map_id(times, time)
      user_id = get_map_id(users, user)
      item_id = get_map_id(items, item)
      tag_id = get_map_id(tags, tag)

      print('{} {} {} {} 1.0'.format(user_id, item_id, tag_id, time_id), file=fout4)
      print('{} {} {} 1.0'.format(user_id, item_id, tag_id), file=fout3)

fout4.close()
fout3.close()

print('#users: {}'.format(len(users)))
print('#items: {}'.format(len(items)))
print('#tags: {}'.format(len(tags)))
print('#times: {}'.format(len(times)))

write_map(users, 'mode-1-users.map')
write_map(items, 'mode-2-items.map')
write_map(tags,  'mode-3-tags.map')
write_map(times, 'mode-4-days.map')

