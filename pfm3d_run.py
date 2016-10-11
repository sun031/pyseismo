#!/usr/bin/env python

import os
import sys, getopt

def Usage():
    print "Usage:"
    print "python pfm3d_run.py -n 12"
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
            
            
    for i in range(ncpu):
        i2s = str(i).zfill(2)
        

        os.chdir("./"+i2s)
        print os.getcwd()
        os.system("nohup fm3d &")
        os.chdir("../")
        print os.getcwd()
        