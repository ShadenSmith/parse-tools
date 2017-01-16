#!/usr/bin/env python3


import os, sys, email

if len(sys.argv) != 3:
  print('usage: {} <emails.csv> <output.tns>'.format(sys.argv[0]))
  sys.exit(1)

import numpy as np
import pandas as pd

sys.path.append('../')
import text_parser


##############################################################################
#
# PARSE DATASET
#
# Modified from Kaggle:
# https://www.kaggle.com/zichen/d/wcukierski/enron-email-dataset/explore-enron
##############################################################################

def get_text_from_email(msg):
  parts = []
  for part in msg.walk():
    if part.get_content_type() == 'text/plain':
      parts.append( part.get_payload() )
  return ''.join(parts)

def split_email_addresses(line):
  if line:
    addrs = line.split(',')
    addrs = frozenset(map(lambda x: x.strip(), addrs))
  else:
    addrs = None
  return addrs


# read emails dataframe
emails_df = pd.read_csv(sys.argv[1])

# Parse the emails into a list email objects
messages = list(map(email.message_from_string, emails_df['message']))
emails_df.drop('message', axis=1, inplace=True)
# Get fields from parsed email objects
keys = messages[0].keys()
for key in keys:
    emails_df[key] = [doc[key] for doc in messages]
# Parse content from emails
emails_df['content'] = list(map(get_text_from_email, messages))
# Split multiple email addresses
emails_df['From'] = emails_df['From'].map(split_email_addresses)
emails_df['To'] = emails_df['To'].map(split_email_addresses)

# Extract the root of 'file' as 'user'
emails_df['user'] = emails_df['file'].map(lambda x:x.split('/')[0])
del messages

# Set index and drop columns with two few values
emails_df = emails_df.set_index('Message-ID')\
    .drop(['file', 'Mime-Version', 'Content-Type', 'Content-Transfer-Encoding'], axis=1)
# Parse datetime
emails_df['Date'] = pd.to_datetime(emails_df['Date'], infer_datetime_format=True)
emails_df.dtypes





##############################################################################
#
# CONSTRUCT TENSOR
#
##############################################################################

def assign_id(dic, item):
  if item not in dic:
    dic[item] = len(dic) + 1

people = dict()
dates = dict()
words = dict()


# dictionary of people -- we only want people that sent an email
for fset in emails_df['From']:
  for curr_user in fset:
    if '@enron.com' in curr_user:
      assign_id(people, curr_user)

# dictionary of sorted dates
for timestamp in emails_df['Date']:
  assign_id(dates, timestamp.date())
# reassign date IDs to be sorted
date_ids = dict()
for d in sorted(dates):
  # skip some invalid dates
  if d.year < 1995 or d.year > 2002:
    continue
  assign_id(date_ids, d)
dates = date_ids


skip_words = set(['>', 'Subject:'])

nnz = 0

# Parse words and generate non-zeros
fout = open(sys.argv[2], 'w')
for idx in range(len(emails_df['From'])):
  s = list(emails_df['From'][idx])[0]
  if '@enron.com' not in s:
    continue

  # list because it's a frozenset
  sender = people[s]

  # get receivers -- only select from people which have sent an email in the
  # dataset, too.
  recvs = []
  if emails_df['To'][idx]:
    for rec in emails_df['To'][idx]:
      if rec in people:
        recvs.append(people[rec])
  
  # skip some invalid dates
  d = emails_df['Date'][idx]
  if d.year < 1995 or d.year > 2002:
    continue

  # get date
  date = dates[emails_df['Date'][idx].date()]

  for word in text_parser.parse_text(emails_df['content'][idx]):
    # quoted original message is at the bottom and starts with this
    if '-----Origin' in word or 'http' in word:
      break
    assign_id(words, word)
    word_id = words[word]

    for r in recvs:
      print('{} {} {} {} 1'.format(sender, r, word_id, date), file=fout)
      nnz += 1
fout.close()


print('{:,d} people'.format(len(people)))
print('{:,d} dates'.format(len(dates)))
print('{:,d} words'.format(len(words)))
print('{:,d} nnz'.format(nnz))


def write_ids(fname, dic):
  # invert dictionary first
  inv = {}
  for x in dic.keys():
    inv[dic[x]] = x

  with open(fname, 'w') as f:
    for i in range(1, len(dic)+1):
      f.write('{}\n'.format(inv[i]))

# Write keys
write_ids('mode-1-senders.map', people)
write_ids('mode-2-receivers.map', people)
write_ids('mode-3-words.map', words)
write_ids('mode-4-dates.map', dates)

