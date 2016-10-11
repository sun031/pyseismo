#!/usr/bin/env python

'''
convert arrivals.dat by fm3d to otimes.dat by tomo3d.py
'''

infile = 'arrivals.dat'
ofile  = 'otimes.dat'

fp = open(infile, 'r')
lst = fp.readlines()
fp.close()

fp = open(ofile, 'w')
fp.write('\t%d\n' % len(lst))

for line in lst:
    row = line.split()
    fp.write('\t%s\t%s\t%s\t%s\t%s\t%f\n' % (row[0], row[1], row[2], row[3], row[4], 0.15))

fp.close()   