#!/usr/bin/env python3

import sys
import re

if len(sys.argv) == 1:
  print('usage: {} <parsed TCPDUMP files>'.format(sys.argv[0]))
  print('run `tcpdump -tt -n -r <.anon> > out.txt` to parse.')
  sys.exit(0)

def get_id(dic, item):
  if item not in dic:
    dic[item] = 1 + len(dic)
  return dic[item]

def write_ids(dic, fname):
  with open(fname, 'w') as ofile:
    inv = {}
    for i in dic:
      inv[dic[i]] = i
    for i in range(1, 1+len(inv)):
      print(inv[i], file=ofile)


def sort_ids(dic):
# write times (and make IDs sorted)
  newids = {}
  for t in sorted(dic.keys()):
    get_id(newids, t)
  return newids

def parse_time(s):
  # truncate last 4 digits
  return float(s[:-4])


address_re = re.compile('([\d+\.]+)\.(\d+):?$')
length_re = re.compile('length (\d+)\[\|SMB\]')

times = {}
send_ips = {}
send_ports = {}
dest_ips = {}
dest_ports = {}

nnz = 0

for rawfile in sys.argv[1:]:
  with open(rawfile, 'r') as infile:

    for line in infile:

      length = None
      # get packet length, easier before splitting
      m = length_re.search(line)
      if m:
        length = int(m.group(1))
      else:
        continue

      line = line.split()
      if len(line) < 5:
        continue
      if line[1] != 'IP':
        continue

      # truncate time to seconds
      secs = parse_time(line[0])
      times[secs] = 1

      send_add = line[2]
      m = address_re.match(send_add)
      if m:
        get_id(send_ips, m.group(1))
        get_id(send_ports, int(m.group(2)))
      else:
        print('ERROR: {}'.format(send_add))


      dest_add = line[4]
      m = address_re.match(dest_add)
      if m:
        get_id(dest_ips, m.group(1))
        get_id(dest_ports, int(m.group(2)))
      else:
        print('ERROR: {}'.format(dest_add))

      nnz += 1

print('nnz: {}'.format(nnz))
print('senders: {}'.format(len(send_ips)))
print('sender ports: {}'.format(len(send_ports)))
print('destinations: {}'.format(len(dest_ips)))
print('dest ports: {}'.format(len(dest_ports)))
print('times: {}'.format(len(times)))

# sort ids
times = sort_ids(times)
send_ports = sort_ids(send_ports)
dest_ports = sort_ids(dest_ports)

write_ids(send_ips, 'send_ips.txt')
write_ids(send_ports, 'send_ports.txt')
write_ids(dest_ips, 'dest_ips.txt')
write_ids(dest_ports, 'dest_ports.txt')
write_ids(times, 'times.txt')


# go back over data and write nonzeros!
tensor = open('lbnl.tns', 'w')
for rawfile in sys.argv[1:]:
  with open(rawfile, 'r') as infile:

    for line in infile:

      length = None
      # get packet length, easier before splitting
      m = length_re.search(line)
      if m:
        length = int(m.group(1))
      else:
        continue

      # split the line and move on if it is not the correct type
      line = line.split()
      if len(line) < 5:
        continue
      if line[1] != 'IP':
        continue

      # truncate time to seconds
      secs = times[parse_time(line[0])]

      send_ip = None
      dest_ip = None
      send_port = None
      dest_port = None

      send_add = line[2]
      m = address_re.match(send_add)
      if m:
        send_ip = send_ips[m.group(1)]
        send_port = send_ports[int(m.group(2))]
      else:
        print('ERROR: {}'.format(send_add))


      dest_add = line[4]
      m = address_re.match(dest_add)
      if m:
        dest_ip = dest_ips[m.group(1)]
        dest_port = dest_ports[int(m.group(2))]
      else:
        print('ERROR: {}'.format(dest_add))


      # now write nonzero!
      print('{} {} {} {} {} {}'.format(send_ip, send_port, dest_ip, dest_port,
          secs, length), file=tensor)

tensor.close()
