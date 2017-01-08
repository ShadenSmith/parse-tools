#!/usr/bin/env python3


import os
import bz2


##############################################################################
# CONSTANTS - EDIT THESE FOR YOUR OWN SETUP

TMP_FILE = "tmp"

##############################################################################


def get_id(dic, item):
  if item not in dic:
    return None
  return dic[item]


def read_ids(fname, fn):
  nbr = 1
  ids = dict()
  with open(fname, 'r') as infile:
    for line in infile:
      ids[fn(line.strip())] = nbr
      nbr += 1
  return ids


# read ids
user_ids = read_ids('users.txt', str)
sub_ids  = read_ids('subreddits.txt', str)
word_ids = read_ids('words.txt', str)
dates    = read_ids('dates.txt', int)

print('users: {:,d}'.format(len(user_ids)))
print('subreddits: {:,d}'.format(len(sub_ids)))
print('words: {:,d}'.format(len(word_ids)))
print('dates: {:,d}'.format(len(dates)))


#
# Finally, go back over original input and write tensor nonzeros
#
t3file = open('reddit3.tns', 'w')
t4file = open('reddit4.tns', 'w')
nnz = 0
pruned = 0

with bz2.open(TMP_FILE + '.bz2', 'rt') as bfile:

  for line in bfile:
    comment = line.split()

    uid = get_id(user_ids, comment[0])
    sid = get_id(sub_ids, comment[1])
    wid = get_id(word_ids, comment[2])
    tid = get_id(dates, int(comment[3]))

    if uid is None or sid is None or tid is None or wid is None:
      pruned += 1
      continue

    print('{} {} {} 1'.format(uid, sid, wid), file=t3file)
    print('{} {} {} {} 1'.format(uid, sid, wid, tid), file=t4file)
    nnz += 1

t3file.close()
t4file.close()
os.remove(TMP_FILE + '.bz2')

print('nnz: {:,d}'.format(nnz))
print('pruned: {:,d}'.format(pruned))

