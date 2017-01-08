#!/usr/bin/env python3

##############################################################################
# This script takes a tensor and discovers gaps in the modes. Gaps are defined
# as slices which do not have any non-zeros. This performs the same operation
# as splatt-fix, but does so without needing to load the complete tensor into
# memory. This uses O(sum(dims[:])) memory instead of O(nnz) memory.
#
# Note that unlike splatt-fix, it does not merge duplicate non-zeros.
##############################################################################

import sys

if len(sys.argv) < 3:
  print('usage: {} <tensor.tns> <newtensor.tns>'.format(sys.argv[0]))
  sys.exit(1)

nmodes = 0

# get the number of modes
with open(sys.argv[1], 'r') as fin:
  line = fin.readline()
  nmodes = len(line.split()[:-1]) # skip the val at the end

seen_inds = [set() for x in range(nmodes)]

# Get list of indices that appear in tensor. Converting to integers is a little
# more expensive, but uses less memory.
with open(sys.argv[1], 'r') as fin:
  for line in fin:
    if line[0] == '#' or line is '':
      continue

    inds = [int(x) for x in line.split()[:-1]]
    for m in range(nmodes):
      seen_inds[m].add(inds[m])


gapped_modes = set()
for m in range(nmodes):
  gaplen = max(seen_inds[m]) - len(seen_inds[m])
  if gaplen > 0:
    gapped_modes.add(m)
    print('mode-{}: {} empty slices'.format(m+1,
        max(seen_inds[m]) - len(seen_inds[m])))


if len(gapped_modes) == 0:
  print('no empty slices')
  sys.exit(0)

# indmaps[m][i] gives the NEW index for original slice i
ind_maps = [dict() for m in range(nmodes)]
for m in range(nmodes):
  if m not in gapped_modes:
    continue
  with open('mode-{}-gaps.map'.format(m+1), 'w') as mapfile:
    for i in sorted(seen_inds[m]):
      ind_maps[m][i] = len(ind_maps[m]) + 1

      # now invert map and write to file
      print('{}'.format(i), file=mapfile)


# Go back over tensor data and map indices
fout = open(sys.argv[2], 'w')
with open(sys.argv[1], 'r') as fin:
  for line in fin:
    if line[0] == '#' or line is '':
      continue

    line = line.split()
    inds = [int(x) for x in line[:-1]]
    for m in range(nmodes):
      if m in gapped_modes:
        inds[m] = ind_maps[m][inds[m]]

    print('{} {}'.format(' '.join(map(str, inds)), line[-1]), file=fout)

fout.close()


