#!/usr/bin/env python3

import os
import sys
import csv

from collections import defaultdict

###############################################################################
# UTILITY FUNCTIONS
###############################################################################

# convert UTC to monthly resolution
def convert_utc(utc_int):
  return int(utc_int / (60 * 60 * 24 * 30))


def write_ids(fname, dic):
  # invert dictionary first
  inv = {}
  for x in dic.keys():
    inv[dic[x]] = x

  with open(fname, 'w') as f:
    for i in range(1, len(dic)+1):
      f.write('{}\n'.format(inv[i]))


def assign_id(dic, item):
  if item not in dic:
    dic[item] = 1 + len(dic)
  return dic[item]


def get_id(dic, item):
  if item not in dic:
    return None
  return dic[item]


# globals

user_ids = {}
tag_ids = {}
movie_ids = {}
dates = {} # temporary; we later sort to have sequential date ids
date_ids = {}

# some movies only appear in tags, so mark those
rated_movies = set()


def read_csv(fname):
  with open(fname, 'r') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')

    # grab header
    next(csvreader)

    for row in csvreader:
      yield row


def get_rated_movies(fname):
  for row in read_csv(fname):
    rated_movies.add(int(row[1]))


def assign_tag_ids(fname):
  for row in read_csv(fname):
    m = int(row[1])
    if m in rated_movies:
      assign_id(user_ids, int(row[0]))
      assign_id(movie_ids, m)
      assign_id(tag_ids, row[2].lower())
      assign_id(dates, convert_utc(int(row[3])))


def write_tags(fname, ofname):
  tag_file = open(ofname, 'w')
  for row in read_csv(fname):
    m_orig = int(row[1])
    if m_orig in rated_movies:
      u = get_id(user_ids, int(row[0]))
      m = get_id(movie_ids, m_orig)
      t = get_id(tag_ids, row[2].lower())
      d = get_id(date_ids, convert_utc(int(row[3])))

      print('{} {} {} {} 1'.format(u, m, t, d), file=tag_file)


  tag_file.close()


def assign_rating_ids(fname):
  for row in read_csv(fname):
    assign_id(user_ids, int(row[0]))
    assign_id(movie_ids, int(row[1]))
    assign_id(dates, convert_utc(int(row[3])))


def write_ratings(fname, ofname):
  rating_file = open(ofname, 'w')
  for row in read_csv(fname):
    u = get_id(user_ids, int(row[0]))
    m = get_id(movie_ids, int(row[1]))
    r = row[2]
    d = get_id(date_ids, convert_utc(int(row[3])))

    print('{} {} {} {}'.format(u, m, d, r), file=rating_file)



###############################################################################
# GO GO GO
###############################################################################

if len(sys.argv) != 3:
  print('usage: {} <ratings.csv> <tags.csv>'.format(sys.argv[0]))
  sys.exit(1)


rating_name = sys.argv[1]
tag_name = sys.argv[2]

get_rated_movies(rating_name)

print('{:,d} rated movies'.format(len(rated_movies)))
assign_tag_ids(tag_name)
print('{:,d} tagged movies'.format(len(movie_ids)))
assign_rating_ids(rating_name)


print('{:,d} users'.format(len(user_ids)))
print('{:,d} movies'.format(len(movie_ids)))
print('{:,d} tags'.format(len(tag_ids)))
print('{:,d} dates'.format(len(dates)))



# assign time IDs so they are sorted
uniques = sorted(dates.keys())
for i in range(len(uniques)):
  date_ids[uniques[i]] = i + 1
del uniques
del dates

# write ids
write_ids('users.txt', user_ids)
write_ids('movies.txt', movie_ids)
write_ids('tags.txt', tag_ids)
write_ids('dates.txt', date_ids)


# go back over data and write tensor
write_ratings(rating_name, 'ml20m_ratings.tns')
write_tags(tag_name, 'ml20m_tags.tns')


