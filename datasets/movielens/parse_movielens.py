#!/usr/bin/env python3

###############################################################################
# Movielens20M parser
#
# This script transforms the raw ratings/tag data provided by Movielens into
# two tensors: a ratings tensor and a tagging tensor. The transformation that
# we perform permutations of the user and movie IDs such that
#
#     (1) IDs are contiguous
#     (2) IDs which occur in both datasets appear first
#     (3) Duplicate movies are combined (e.g., War of the Worlds (2005))
#
# In effect, the two tensors can be used as standalone datasets (without large
# gaps in numbering) but also as related datasets, possibly for joint
# factorization.
#
# To compute the permutations, we take the following steps:
#   1) Make a set of movies which appear in the ratings dataset. Any tagged
#      movies which have not been rated will be omitted (this is a small set).
#   2) Go over the tag dataset and assign user, movie, tag, and date IDs.
#   3) Go over the ratings dataset and assign user, movie, tag, and date IDs
#      while respecting the IDs from the previous step.
#
###############################################################################


import os
import sys
import csv
from collections import defaultdict


###############################################################################
# GLOBAL DICTIONARIES
#
# dic[orig_key] = new_id
###############################################################################
user_ids    = dict()
tag_ids     = dict()
date_ids    = dict()

# to be used with lookup_movie(orig_key)
movie_names = dict() # movie_names[orig_key] = 'Movie title'
movie_ids   = dict() # movie_ids['Movie title'] = my_id

# rated_movies['title'] present if rated
rated_movies = set()



###############################################################################
# UTILITY FUNCTIONS
###############################################################################

# convert UTC to weekly resolution
def convert_utc(utc_int):
  return int(utc_int / (60 * 60 * 24))


def write_ids(fname, dic):
  # invert dictionary first
  # (dic[key] = id) -> (inv[id] = key)
  inv = {}
  for x in dic.keys():
    inv[dic[x]] = x

  with open(fname, 'w') as fout:
    for i in range(1, len(dic)+1):
      print('{}'.format(inv[i]), file=fout)

def assign_id(dic, item):
  if item not in dic:
    dic[item] = 1 + len(dic)

def get_id(dic, item):
  return dic[item]


def read_csv(fname):
  with open(fname, 'r') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    next(csvreader) # grab header
    for row in csvreader:
      yield row



###############################################################################
# ML20M FUNCTIONS
###############################################################################

def read_movie_names(fname):
  # movie ID, title, genres
  for row in read_csv(fname):
    orig_id = int(row[0])
    title = row[1]
    movie_names[orig_id] = title


def get_rated_movies(fname):
  for row in read_csv(fname):
    movie_id = int(row[1])
    title = movie_names[movie_id]
    rated_movies.add(title)



def assign_tag_ids(fname):
  for row in read_csv(fname):
    orig_movie_id = int(row[1])
    title = movie_names[orig_movie_id]
    if title in rated_movies:
      assign_id(user_ids, int(row[0]))
      assign_id(movie_ids, title)
      assign_id(tag_ids, row[2].lower())
      assign_id(date_ids, convert_utc(int(row[3])))


def assign_rating_ids(fname):
  for row in read_csv(fname):
    assign_id(user_ids, int(row[0]))
    title = movie_names[int(row[1])]
    assign_id(movie_ids, title)
    assign_id(date_ids, convert_utc(int(row[3])))


def write_ratings(fname, ofname):
  with open(ofname, 'w') as rating_file:
    for row in read_csv(fname):
      u = get_id(user_ids, int(row[0]))
      m = get_id(movie_ids, movie_names[int(row[1])])
      r = row[2]
      d = get_id(date_ids, convert_utc(int(row[3])))

      print('{} {} {} {}'.format(u, m, d, r), file=rating_file)



def write_tags(fname, ofname):
  with open(ofname, 'w') as tag_file:
    for row in read_csv(fname):
      m_orig = int(row[1])
      title = movie_names[m_orig]
      if title in rated_movies:
        u = get_id(user_ids, int(row[0]))
        m = get_id(movie_ids, title)
        t = get_id(tag_ids, row[2].lower())
        d = get_id(date_ids, convert_utc(int(row[3])))
        print('{} {} {} {} 1'.format(u, m, t, d), file=tag_file)





###############################################################################
# MAIN CODE
###############################################################################

if len(sys.argv) != 4:
  print('usage: {} <ratings.csv> <tags.csv> <movies.csv>'.format(sys.argv[0]))
  sys.exit(1)
rating_fname = sys.argv[1]
tag_fname    = sys.argv[2]
movie_fname  = sys.argv[3]


read_movie_names(movie_fname)
get_rated_movies(rating_fname)
assign_tag_ids(tag_fname)
assign_rating_ids(rating_fname)


print('users: {:,d}'.format(len(user_ids)))
print('movies: {:,d}'.format(len(movie_ids)))
print('tags: {:,d}'.format(len(tag_ids)))
print('dates: {:,d}'.format(len(date_ids)))


# assign time IDs so they are sorted
uniques = sorted(date_ids.keys())
date_ids = dict()
for i in range(len(uniques)):
  date_ids[uniques[i]] = i + 1
del uniques


write_ids('mode-1-users.map',  user_ids)
write_ids('mode-2-movies.map', movie_ids)
write_ids('mode-3-tags.map',   tag_ids)
write_ids('mode-4-dates.map',  date_ids)

# go back over data and write tensor
write_ratings(rating_fname, 'movielens20m-ratings.tns')
write_tags(tag_fname, 'movielens20m-tags.tns')


