#!/usr/bin/env python3

import os, sys

from collections import defaultdict

# paper x author x word x year = count

WORDS='words.txt'
AUTHORS='author_names.txt'
DOC_NAMES='doc_names.txt'

COUNTS='counts.ijv'
DOC_AUTHORS='doc_authors.ijv'


def assign_id(dic, item):
  if item not in dic:
    dic[item] = len(dic) + 1



word_ids   = {}
author_ids = {}
year_ids   = {}
doc_ids    = {}


doc_years = {}


# parse word ids
with open(WORDS, 'r') as fin:
  for line in fin:
    assign_id(word_ids, line.strip())

print('words: {:,d}'.format(len(word_ids)))


# parse author ids
with open(AUTHORS, 'r') as fin:
  for line in fin:
    assign_id(author_ids, line.strip())
print('authors: {:,d}'.format(len(author_ids)))


# parse paper names and years
with open(DOC_NAMES, 'r') as fin:
  for line in fin:
    line = line.strip()
    year = line.split('/')[0]
    assign_id(year_ids, year)
    assign_id(doc_ids, line)

    doc_years[doc_ids[line]] = year_ids[year]

print('papers: {:,d}'.format(len(doc_ids)))
print('years: {:,d}'.format(len(year_ids)))


# for each paper, make a list of authors
author_list = defaultdict(list)

with open(DOC_AUTHORS, 'r') as fin:
  for line in fin:
    # doc author 1
    line = line.strip().split()
    doc = int(line[0])
    auth = int(line[1])

    # DOC_AUTHORS has an author 2865 which does not appear in the name list
    if auth > len(author_ids):
      continue

    author_list[doc].append(auth)


# generate nnz
nnz = 1
fout = open('nips.tns', 'w')
with open(COUNTS, 'r') as fin:
  for line in fin:
    line = line.strip().split()
    word = int(line[0])
    doc = int(line[1])
    count = int(line[2])

    # there is a doc # 2484 which does not appear in doc_names
    if doc > len(doc_ids):
      continue

    year = doc_years[doc]

    for auth in author_list[doc]:
      print('{} {} {} {} {}'.format(doc, auth, word, year, count), file=fout)
      nnz += 1
fout.close()
print('nnz: {:,d}'.format(nnz))



