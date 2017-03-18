#!/usr/bin/env python3


import os
import sys
sys.path.append('../')

import text_parser

import bz2
import json


import datetime

from collections import defaultdict, Counter


##############################################################################
# CONSTANTS - EDIT THESE FOR YOUR OWN SETUP

USER_MIN = 1
SUB_MIN  = 1
WORD_MIN = 5
WORD_MAX = -1

TMP_FILE = "tmp"
##############################################################################


'''
Sample comment (in JSON):
{
  "gilded":0,
  "author_flair_text":"Male",
  "author_flair_css_class":"male",
  "retrieved_on":1425124228,
  "ups":3,
  "subreddit_id":"t5_2s30g",
  "edited":false,
  "controversiality":0,
  "parent_id":"t1_cnapn0k",
  "subreddit":"AskMen",
  "body":"I can't agree with passing the blame, but I'm glad to hear it's at least helping you with the anxiety. I went the other direction and started taking responsibility for everything. I had to realize that people make mistakes including myself and it's gonna be alright. I don't have to be shackled to my mistakes and I don't have to be afraid of making them. ",
  "created_utc":"1420070668",
  "downs":0,
  "score":3,
  "author":"TheDukeofEtown",
  "archived":false,
  "distinguished":null,
  "id":"cnasd6x",
  "score_hidden":false,
  "name":"t1_cnasd6x",
  "link_id":"t3_2qyhmp"
}
'''

def get_id(dic, item):
  if item not in dic:
    dic[item] = 1 + len(dic)
  return dic[item]


def write_ids(fname, dic):
  # invert dictionary first
  inv = {}
  for x in dic.keys():
    inv[dic[x]] = x

  with open(fname, 'w') as f:
    for i in range(1, len(dic)+1):
      f.write('{}\n'.format(inv[i]))


# convert UTC to day resolution
def convert_utc(utc_str):
  return str(datetime.date.fromtimestamp(int(utc_str)))

user_counts = Counter()
sub_counts  = Counter()
word_counts = Counter()

dates = {}

if len(sys.argv) == 1:
  print('usage: {} <comment bz2 files>'.format(sys.argv[0]))
  sys.exit(1)

decoder = json.JSONDecoder()

ncomments = 0
nwords = 0

outfile = bz2.open(TMP_FILE + '.bz2', 'wt')

for infile in sys.argv[1:]:
  print('parsing {}'.format(infile))
  bfile = bz2.open(infile, 'rt')

  # decode each comment into a JSON object
  for line in bfile:
    comment = decoder.decode(line)

    # parse user, skipping deleted comments
    user = comment['author']
    if user == '[deleted]':
      continue

    sub = comment['subreddit']
    timestamp = convert_utc(int(comment['created_utc']))

    # increment counters
    user_counts[user] += 1
    sub_counts[sub] += 1
    dates[timestamp] = 1

    text = comment['body']
    for word in text_parser.parse_text(text):
      word_counts[word] += 1
      nwords += 1

      outfile.write('{} {} {} {}\n'.format(user, sub, word, timestamp))

    ncomments += 1

  bfile.close()

  # WARNING - delete input file
  # s.remove(infile)

outfile.close()

print(user_counts.most_common(10))
print(sub_counts.most_common(10))
print(word_counts.most_common(10))

user_ids = {}
sub_ids  = {}
word_ids = {}

#
# write counts and assign unique IDs (after pruning infrequent/frequent)
#

# assign time IDs so they are sorted
uniques = sorted(dates.keys())
dates = {}
for i in range(len(uniques)):
  dates[uniques[i]] = i + 1
del uniques

with open('users.counts', 'w') as user_file:
  for u in user_counts:
    if user_counts[u] >= USER_MIN:
      user_file.write('{} {}\n'.format(user_counts[u], u))
      get_id(user_ids, u)
del user_counts


with open('subreddits.counts', 'w') as sub_file:
  for u in sub_counts:
    if sub_counts[u] >= SUB_MIN:
      sub_file.write('{} {}\n'.format(sub_counts[u], u))
      get_id(sub_ids, u)
del sub_counts


with open('words.counts', 'w') as word_file:
  for u in word_counts:
    if word_counts[u] >= WORD_MIN and (WORD_MAX == -1 or word_counts[u] <= WORD_MAX):
      word_file.write('{} {}\n'.format(word_counts[u], u))
      get_id(word_ids, u)
del word_counts

write_ids('mode-1-dates.map', dates)
write_ids('mode-2-users.map', user_ids)
write_ids('mode-3-subreddits.map', sub_ids)
write_ids('mode-4-words.map', word_ids)

print('comments: {:,d} (avg length: {:0.2f})'.format(ncomments, float(nwords) / float(ncomments)))
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
    tid = get_id(dates, comment[3])

    if uid is None or sid is None or tid is None or wid is None:
      pruned += 1
      continue

    print('{} {} {} 1'.format(uid, sid, wid), file=t3file)
    print('{} {} {} {} 1'.format(tid, uid, sid, wid), file=t4file)
    nnz += 1

t3file.close()
t4file.close()
os.remove(TMP_FILE + '.bz2')

print('nnz: {:,d}'.format(nnz))
print('pruned: {:,d}'.format(pruned))



