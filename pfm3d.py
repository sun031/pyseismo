#!/usr/bin/env python

import os
import sys, getopt
import numpy as np

def srclineno(isrc):
    return int(6*isrc-5), int(6*isrc+1)

def reclineno(irec):
    return int(4*irec-3), int(4*irec+1)

def Usage():
    print "Usage:"
    print "python pfm3d.py -n 12"
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
    
    print "number of CPUs or Cores:\t",ncpu

    with open("sources.in", "r") as fpsrc:
        srclst = fpsrc.readlines()
        
    with open("receivers.in", "r") as fprec:
        reclst = fprec.readlines()
        
    nsrc = int(srclst[0])
    print "number of sources:\t", nsrc
    
    pnsrc = nsrc/ncpu+1
    
    if nsrc-pnsrc*ncpu > ncpu/2:
        pnsrc = pnsrc+1
    
    print "number of sources for parallel:\t", pnsrc
    
    # start and end shot number for each CPU core
    psrc1 = np.zeros(ncpu)
    psrc2 = np.zeros(ncpu)
    for i in range(ncpu):
        psrc1[i] = i*pnsrc+1
        psrc2[i] = (i+1)*pnsrc
        
    psrc2[-1]=nsrc
    
    print "start and end shot number for each CPU core"
    print psrc1
    print psrc2
    
    prec1 = np.zeros(ncpu)
    prec2 = np.zeros(ncpu)
    for i in range(3,len(reclst),4):
#         print i,int(reclst[i]), i-2, i+2
        
        srcno = int(reclst[i])
        
        flag1 = True
        for icpu in range(ncpu):
            if srcno==psrc2[icpu]:
                prec2[icpu] = int(i+2)
                break
            
    

    prec1[0] = int(1)            
    for icpu in range(1,ncpu):
        prec1[icpu] = int(prec2[icpu-1])
    
#     print prec1
#     print prec2
                
        
#         if i>50:
#             os._exit(0)
        
    fpsave = open("cpu", "w")
    for i in range(ncpu):
        pnsrc = int(psrc2[i]-psrc1[i]+1)
        
        i2s = str(i).zfill(2)
        
        if not os.path.exists(i2s):
            os.system("mkdir %s" % i2s)
        
        index1, index2 = srclineno(psrc1[i])
        index3, index4 = srclineno(psrc2[i])

        srcstr = ""
        fpsrc = open(i2s+"/sources.in", "w")
        srcstr += str(pnsrc)+"\n"
        
        fpsrc.write("%s" % srcstr)
        fpsrc.writelines(srclst[index1:index4])
        
        fpsrc.close()
        
        fprec = open(i2s+"/receivers.in", "w")
        nrec = int((prec2[i]-prec1[i])/4)
        fprec.write(str(nrec)+"\n")
        
        index1 = int(prec1[i])
        index2 = int(prec2[i])
        #print index1, index2
        
        lst = reclst[index1:index2]
        for irec in range(2,len(lst),4):
            
            isrc = int(lst[irec])-psrc1[i]+1
            
            lst[irec] = "       "+str(int(isrc))+"\n"
        
        fprec.writelines(lst)
        
        fprec.close()
        
        fpsave.write("%d\t%d\t%d\t%d\n" % (psrc1[i],psrc2[i],prec1[i],prec2[i]))
        
        cpfiles = "propgrid.in interfaces.in vgrids.in mode_set.in frechet.in"
        
        os.system("cp %s %s" % (cpfiles, i2s))
        
        
    fpsave.close()   
    
    pass