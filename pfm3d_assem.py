#!/usr/bin/env python


import os
import sys, getopt
import numpy as np

def Usage():
    print "Usage:"
    print "python pfm3d_assem.py -n 12"
    print "-n the number of CPUs or CPU cores"


if __name__=="__main__":

    try:
        opts, args = getopt.getopt(sys.argv[1:], "n:", ["ncpu="])
    except getopt.GetoptError, err:
        print str(err)
        Usage()   
        sys.exit(2) 
    
    ncpu=0
    print opts,args
    
    for op, value in opts:
        if op in ["-n", "--ncpu"]:
            ncpu = int(value)
        else:
            Usage()
            sys.exit(0)
    
    with open("cpu", "r") as fp:
        lst = fp.readlines()
        
    psrc1 = np.zeros(len(lst), dtype=np.int)
    for i in range(len(lst)):
        row = lst[i].split()
        psrc1[i] = int(row[0])
        
    print psrc1
        
    fparr = open("arrivals.dat", "w")
    
    counter = 0
    for i in range(ncpu):
        
        i2s = str(i).zfill(2)
        with open(i2s+"/arrivals.dat") as fp:
            lst = fp.readlines()
            
        for line in lst:
            counter += 1
            row = line.split()
            
            isrc = int(row[1])+psrc1[i]-1
            
            fparr.write("%6d%6d%6s%6s%15s%5s%5s\n" %(counter, isrc, row[2], row[3], row[4], row[5], row[6]))
            
        
    fparr.close()