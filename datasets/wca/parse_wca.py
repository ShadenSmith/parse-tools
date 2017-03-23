#!/usr/bin/env python2

import csv
import urllib
import zipfile
import numpy

urllib.urlretrieve('https://www.worldcubeassociation.org/results/misc/WCA_export.tsv.zip', 'WCA_export.tsv.zip')
zip_ref = zipfile.ZipFile('WCA_export.tsv.zip', 'r')
zip_ref.extract('WCA_export_Results.tsv')
zip_ref.close()

with open('WCA_export_Results.tsv', 'r') as f:
    reader = csv.reader(f, delimiter="\t")
    data = list(reader)

data = data[1:] # First line is a header

# dicts
Competitions = dict()
Events = dict()
Rounds = dict()
Persons = dict()

# Tensor
Results = []

def getOrSetDictVal( _key, _dict ):
    if _key in _dict :
        return _dict[_key]
    else:
        _dict[_key] = len(_dict) + 1
        return _dict[_key]

for entry in data :
    _time = 0

    if int(entry[5]) > 0 :  # use average if average > 0
        _time = int(entry[5])
    elif int(entry[4]) > 0 : # use best if best > 0
        _time = int(entry[4])

    if _time > 0:
        # A few WCA IDs have no times associated with them, so make sure that
        # they are not added to the tensor.
        _competition = getOrSetDictVal(entry[0], Competitions)
        _event = getOrSetDictVal(entry[1], Events)
        _round = getOrSetDictVal(entry[2], Rounds)
        _person = getOrSetDictVal(entry[7], Persons)

        _result = (_competition, _event, _round, _person, _time);
        Results.append(_result)

# Save tensor file
numpy.savetxt("WCA_Results.tns", Results, delimiter=" ", fmt='%i')

def writeMap(_dict, _file) :
    with open(_file, 'w') as f:
        for _key in sorted(_dict, key=_dict.get) :
            f.write('%s\n' % (_key))

writeMap(Competitions, 'mode-1-competitions.map')
writeMap(Events,       'mode-2-events.map')
writeMap(Rounds,       'mode-3-rounds.map')
writeMap(Persons,      'mode-4-persons.map')


