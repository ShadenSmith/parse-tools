#!/usr/bin/env python3

import sys
import gzip

DB_URL = 'http://www-users.cs.umn.edu/~shaden/frostt_data'

if len(sys.argv) == 1:
  print('usage: {} <tensor.tns.gz> [outfile.md]'.format(sys.argv[0]))
  sys.exit(1)

tensor_file = sys.argv[1]


nnz = 0
order = 0
dims = []


def process_dims(new_string, dims, order):
  for m in range(order):
    dims[m] = max(dims[m], int(new_string[m]))

# Determine the number of modes
with gzip.open(tensor_file, 'rb') as fin:        

  # Skip to first nnz
  line = fin.readline().decode('utf-8').split()
  while line[0] == '#':
    line = fin.readline().decode('utf-8').split()

  order = len(line) - 1
  dims = [0] * order
  nnz = 1

  # process the first line
  process_dims(line, dims, order)

  # Now go over the rest of the non-zeros.
  for line in fin:
    line = line.decode('utf-8')

    # skip comments
    if line[0] == '#':
      continue

    line = line.split()
    if line:
      process_dims(line, dims, order)
      nnz += 1


outfile = tensor_file.replace('.tns.gz', '.md')
if len(sys.argv) == 3:
  outfile = sys.argv[2]


with open(outfile, 'w') as fout:
  print('---', file=fout)
  print('title: {}\n'.format(outfile.replace('.md', '')), file=fout)
  print('description: >', file=fout)
  print('\n', file=fout)
  print("order: '{}'".format(order), file=fout)
  print("nnz: '{:,d}'".format(nnz), file=fout)

  dims = ['{:,d}'.format(d) for d in dims]
  print('dims: {}'.format(dims), file=fout)

  print('files:', file=fout)
  basename = tensor_file[tensor_file.rfind('/')+1 :]
  print(' - [Tensor, "{}/{}"]'.format(DB_URL, basename), file=fout)

  print('\n', file=fout)
  print('citation: >', file=fout)


  print('\n', file=fout)
  print('tags: []', file=fout)
  print('---', file=fout)


