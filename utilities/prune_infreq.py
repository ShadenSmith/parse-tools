#!/usr/bin/env python3

import sys
import argparse
from collections import Counter

parser = argparse.ArgumentParser(description='Prune infrequent slices from a tensor.')

parser.add_argument('tensor', type=str, help='tensor to prune')
parser.add_argument('output', type=str, help='output tensor')
parser.add_argument('--mode', metavar='MODE,MIN-FREQ', action='append',
    help='min. frequency for a mode (default: 1)')

args = parser.parse_args()

# First get the number of modes
nmodes = 0
with open(args.tensor, 'r') as fin:
  line = fin.readline()
  nmodes = len(line.split()[:-1]) # skip the val at the end


# Get user-specified minimum frequencies
mode_mins = [1] * nmodes
if args.mode:
  for mode_tup in args.mode:
    mode_tup = mode_tup.split(',')
    m = int(mode_tup[0]) - 1
    freq = int(mode_tup[1])
    mode_mins[m] = freq

print('minimum frequencies: {}'.format(mode_mins))

def read_tensor(fname):
  '''
    Read each line of the tensor and return a list of indices and the value.
    This function skips comments and blank lines.
  '''
  with open(fname, 'r') as fin:
    for line in fin:
      # skip comments and blank lines
      if line[0] == '#' or line is '':
        continue

      # convert to integers and return list
      line = line.strip().split()
      yield [int(x) for x in line[:-1]], line[-1]
    


# Count appearances in each mode.
ind_counts = [Counter() for x in range(nmodes)]
for inds, val in read_tensor(args.tensor):
  for m in range(nmodes):
    ind_counts[m][inds[m]] += 1


# indmaps[m][i] gives the NEW index for original slice i
ind_maps = [dict() for m in range(nmodes)]

# Go over counts and prune infrequent slices
gapped_modes = []
for m in range(nmodes):
  for index in ind_counts[m].keys():
    if ind_counts[m][index] < mode_mins[m]:
      ind_counts[m][index] = 0

  # prune
  keep = [x for x in sorted(ind_counts[m]) if ind_counts[m][x] >= mode_mins[m]]

  gaplen = max(ind_counts[m]) - len(keep)
  # Have we pruned any slices?
  if gaplen > 0:
    gapped_modes.append(m)
    print('mode-{}: {} empty slices'.format(m+1, gaplen))

    # assign new IDs and write map file
    with open('mode-{}-gaps.map'.format(m+1), 'w') as mapfile:
      for i in keep:
        ind_maps[m][i] = len(ind_maps[m]) + 1
        # invert map and write to file
        print('{}'.format(i), file=mapfile)



if len(gapped_modes) == 0:
  print('no empty slices')
  sys.exit(0)


# Go back over the tensor and map indices
nnz = 0
pruned_nnz = 0
with open(args.output, 'w') as fout:
  for inds, val in read_tensor(args.tensor):
    pruned = False

    # map indices and check for pruned nnz
    for m in gapped_modes:
      if inds[m] in ind_maps[m]:
        inds[m] = ind_maps[m][inds[m]]
      else:
        pruned = True
        pruned_nnz += 1

    # write non-zero
    if not pruned:
      print('{} {}'.format(' '.join(map(str, inds)), val), file=fout)
      nnz += 1

print('pruned nnz: {:,d} new nnz: {:,d}'.format(pruned_nnz, nnz))

