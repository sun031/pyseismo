#!/usr/bin/env python

"""
functions for FMTomo
"""

import os, sys
import glob
import shutil

# sys.path.append('/media/weijia/ANU/swsrc')
from swSeismo import *


from operator import itemgetter

def resamp_src(oatfile, threshold=1, grdsize=[1,1], tempdir="./temp"):
    """
    resample the cluster of earthquake
    if the number of earthquake in a regular grid exceed threshold, we only take the events
    with the first threshold maximum magnitude.
    evtfile: containing events information ,date, time, evla, evlo, evdp, mag
    threshold: number of events in regular grid
    grdsize: sampling interval in longitude and latitude
    tempdir: save data
    output oatfile with appended "_resamp"
    """
    
    threshold = abs(threshold)
        
    evtfile = "junk.event"
    evtoat(oatfile, evtfile)
    
    name, ext = os.path.splitext(oatfile)
    
    newoat = name+"_resamp.oat"
    
    with open(evtfile, "r") as fp:
        evtlst = fp.readlines()
        
        
    templst = []
    for line in evtlst:
        row = line.split()
        templst.append(row)
        
    aa = sorted(templst, key=itemgetter(3))
    xmin = float(aa[0][3])
    
    aa = sorted(templst, key=itemgetter(2))
    ymin = float(aa[0][2])
   
    dx = abs(grdsize[0])*1.0
    dy = abs(grdsize[1])*1.0
    
    try:
        shutil.rmtree(tempdir)
    except:
        pass
    
    if not os.path.exists(tempdir):
        os.makedirs(tempdir)
                
    for line in evtlst:
        row = line.split()
        evla = float(row[2])
        evlo = float(row[3])
        
        ix = round((evlo-xmin)/dx)
        iy = round((evla-ymin)/dy)
        
        filename = tempdir+"/%i_%i" % (ix, iy)
        
        fp = open(filename,"a")
        fp.write(line)
        fp.close()
        
    evtlst = []
    fp_disc = open("discard.event","w")
    for file in glob.glob(tempdir+"/*"):
        
        with open(file, "r") as fp:
            lst = fp.readlines()
            
        if len(lst)<=threshold:
            for line in lst:
                evtlst.append(line)
                
        else:
            templst = []
            for line in lst:
                
                row = line.split()
                templst.append(row)
                                
            bb = sorted(templst, key=itemgetter(5), reverse=1)
            for i in range(threshold):
                aa = bb[i]
                line = "%s\t%s\t%s\t%s\t%s\t%s\n" % (aa[0], aa[1], aa[2], aa[3], aa[4], aa[5])
                evtlst.append(line)
                        
            for i in range(threshold, len(templst)):
                aa = bb[i]
                line = "%s\t%s\t%s\t%s\t%s\t%s\n" % (aa[0], aa[1], aa[2], aa[3], aa[4], aa[5])
                fp_disc.write(line)

            
    fp_disc.close()
    
    fp = open("save.event", "w")
    for line in evtlst:
        fp.write(line)
    fp.close()
    
    ## open oatfile and resamp
    with open(oatfile, "r") as fp:
        oatlst = fp.readlines()
        
    fp = open(newoat, "w")
    
    oat = Oat()
    for line in oatlst:

        try:
            oat.read(line)
        except:
            continue

        evt = "%s\t%s\t%s\t%s\t%s\t%s\n" % (oat.date, oat.time, str("%.4f")%oat.evla, str("%.4f")%oat.evlo, str("%.3f")%oat.evdp, str("%.3f")%oat.mag)
        if evt in evtlst:
            fp.write(line)
            
    fp.close()
    
#     return evtlst


def evtcount(infile, ofile, num=5):
    """
    for each event must have at least num arrivals
    """
    
    oatfile = infile
    oatfile2 = ofile
    
    with open(oatfile, "r") as fp:
        oatlst = fp.readlines()
        
    fp = open(oatfile2, "w")

    oat = Oat()
    
    temp = []
    tempall = []
    temprm = []
    
    lst = []
    
    for line in oatlst:
        oat.read(line)
        
        key = oat.date+oat.time
        tempall.append(key)
        if key not in temp:
            temp.append(key)
            
    for line in temp:
        coun = tempall.count(line)
        if coun<num and line not in temprm:
            temprm.append(line)
    
    for line in oatlst:
        oat.read(line)
        
        key = oat.date+oat.time
        if key not in temprm:
            oat.write(fp)
            
#     return lst

def onlyfirst(oatfile, tempdir="./temp"):
    """
    remove multiple arrivals for each station eg P,Pn,Pg
    only first arrival for P and S allowed
    """
    
    with open(oatfile, "r") as fp:
        oatlst = fp.readlines()
         
    aa, bb = os.path.splitext(oatfile)
    newoat = aa + "_first.oat"
    newoatlst = []
    
    try:
        shutil.rmtree(tempdir)
    except:
        pass
         
    if not os.path.exists(tempdir):
        os.makedirs(tempdir)
         
#     os.system("rm -rf %s/*" % tempdir)
 
    oat = Oat()
    templst = []
    for line in oatlst:
        oat.read(line)
         
        date = oat.date.replace("-", "")
        time = oat.time.replace(":", "")
        net  = oat.knetwk.replace("?", "")
        sta  = oat.kstnm
        phas = oat.phase[0]
         
        key= date+time+net+sta+phas
                 
        filename = tempdir+"/"+key
        fp = open(filename, "a")
        fp.write(line)
        fp.close()
        
    for file in glob.glob(tempdir+"/*"):
        with open(file, "r") as fp:
            lst = fp.readlines()
            
        tobs0=9999999999;
        if len(lst)>1:  ## multiple phase for this station
            for line in lst:
                row = line.split()
                tobs = float(row[18])
                if tobs<tobs0:
                    tobs0=tobs
                    line0=line
                
            newoatlst.append(line)
                    
        else:
            line = lst[0]
            newoatlst.append(line)
                        
    fp = open(newoat, "w")
    fp.writelines(newoatlst)
    fp.close()    
        
def seprt_ps(oatfile):
    """
    separate the P and S arrivals
    """
    
    with open(oatfile, "r") as fp:
        oatlst = fp.readlines()
        
    fn, ext = os.path.splitext(oatfile)
    pfile = fn+"_p.oat"
    sfile = fn+"_s.oat"
    
    fp_p = open(pfile, "w")
    fp_s = open(sfile, "w")
        
    oat = Oat()
    for line in oatlst:
        
        try:
            oat.read(line)
        except:
            continue
        
        phase = oat.phase
        if phase[0].upper() == "P":
            oat.write(fp_p)
        elif phase[0].upper() == "S":
            oat.write(fp_s)
        
    fp_p.close()
    fp_s.close()
            
            
    
def arrival2otime(arrfile="arrivals.dat", otimefile="otimes.dat"):
    """
    convert arrival.dat by fm3d to otimes.dat by fmtomo
    this function is normally used for resoltuion test.
    """
        
    infile = arrfile
    ofile  = otimefile
    
    fp = open(infile, 'r')
    lst = fp.readlines()
    fp.close()
    
    fp = open(ofile, 'w')
    fp.write('\t%d\n' % len(lst))
    
    for line in lst:
        row = line.split()
        fp.write('\t%s\t%s\t%s\t%s\t%s\t%f\n' % (row[0], row[1], row[2], row[3], row[4], 0.15))
    
    fp.close()   
    
    
## convert ISC arrival to oat file
#  \param infile ISC arrival file
#  \param oatfile oatfile
#  \param distaz bool, calculate distaz or not, default False
#  \param tt bool, calculate travel time based on the ak135 model or not, defulat False
def isc2oat(infile, oatfile, distaz=False, tt=False):
    
    with open(infile, "r") as fp:
        lst = fp.readlines()
    
    fp = open(oatfile, "w")
    oat = Oat()
    
    for line in lst:
        row = line.split(',')
        
        try:
            evid = int(row[0].strip())
        except:
            continue
        
        oat.__init__()
        oat.kstnm = row[2].strip()
        oat.stla = float(row[3].strip())
        oat.stlo = float(row[4].strip())
        oat.stel = float(row[5].strip())
        oat.kcmpnm = row[6].strip()
        oat.gcarc = float(row[7].strip())
        oat.baz = float(row[8].strip())
        oat.phase = row[10].strip()
        if oat.phase == "":
            continue
        
        date = row[11].strip()
        time = row[12].strip()
        tobs = UTCDateTime(date+"T"+time)
        
        res = float(row[13].strip())
    
        date = row[18].strip()
        time = row[19].strip()
        orgi = UTCDateTime(date+"T"+time)
        
        oat.tobs = tobs - orgi
        oat.tak135 = oat.tobs - res
        
        oat.date = date
        oat.time = time
        oat.originfmt()
        
        oat.evla = float(row[20].strip())
        oat.evlo = float(row[21].strip())
        
        oat.dist = oat.gcarc*111.195
        
        try:
            oat.evdp = float(row[22].strip())
        except:
            pass
        
        try:
            oat.mag = float(row[25].strip())
        except:
            continue
        
        if distaz:
            oat.DistAz()
            
        if tt:
            if oat.phase[0] == 'P' or oat.phase[0] == 'p':
                oat.ttak135pf(phase_list=['P','Pn','Pg', 'p'])
            elif oat.phase[0] == 'S' or oat.phase[0] == 's':
                oat.ttak135sf(phase_list=['S','Sn','Sg', 's'])

        
        oat.write(fp)

    fp.close()

## convert cedc arrivals to crude oat
# filelst: containing the cedc arrivals
# oatfile: output oatfile name
# phaselst: arrivals containing the phases would be taken, or excluded.
# CB: containing the earthquake outside China, True include, False exclude
# SH: include SH(NEZ) component or not     
    
def cedc_crude(filelst, oatfile, phaselst=['P', 'S', 'Pn', 'Sn', 'Sg', 'Pg'], CB=False, SH=False):
    
    files = filelst
    plst = phaselst
    
    a,b = os.path.splitext(oatfile)
    ofile = a+".evt"
    
    fp = open(ofile,'w')
    fpoat = open(oatfile, 'w')

    for file in files:
        fpevt = open(file,'r')
        lst = fpevt.readlines()
        fpevt.close()
    
        
        print "converting CEDC:", file
        
        oat = Oat()
        for line in lst:
            
            # event
            if line[0:3]=='DBO':
                    
                row = line.split()
                
                flag = 0
                if CB==False and row[1]=="CB":
                    flag = 1
                    continue
                                
                fp.write(line)

                oat.date = row[2].strip()
                oat.time = row[3].strip()
                oat.evla = float(row[4].strip())
                oat.evlo = float(row[5].strip())
                oat.evdp = float(row[6].strip())
                oat.mag  = float(row[8].strip())
            
            # station and arrival    
            elif line[0:3]=='DPB':
                if line[45:64].strip() == "" or flag==1:
                    continue
                oat.knetwk = line[5:9].strip()
                oat.kstnm  = line[9:14].strip()
                oat.kcmpnm = line[14:19].strip()
    #             oat.phase  = line[27:33].strip()
    #             
                
                if oat.knetwk=='CA':
                    continue
                            
                row = line.split()
                k = 0
                vbool = False
                for i in range(len(row)):
                    if row[i]=='V':
                        vbool = True
                        date = row[i+1]
                        time = row[i+2]
                        oat.phase = row[i-2]
                        if oat.phase[0:2]=='BH' or oat.phase[0:2]=='SH':
                            oat.phase=row[i-1]
    
    
                        try:
                            if oat.knetwk == 'CB':
                                oat.gcarc = float(row[i+4])
                                oat.dist = oat.gcarc*111.195
                            else:
                                oat.dist = float(row[i+4])
                                oat.gcarc = oat.dist/111.195
                        except:
                            oat.dist = -1
                            oat.gcarc = -1
                        break
    #             date = line[41:52].strip()
    #             time = line[52:65].strip()
                
                if vbool==False:
                    continue
                
                if oat.kcmpnm[0:2] == 'SH' and SH==False:
                    continue
                
                oat.tobs = UTCDateTime(date+"T"+time) - UTCDateTime(oat.date+"T"+oat.time) 
                if oat.phase in plst:
                    for str1 in ['', '+','-', 'e', '-e', 'i','+i']:
                        oat.phase = oat.phase.replace(str1,'')
                    oat.write(fpoat)
            else:
                continue
    
            
    fp.close()
    fpoat.close() 
    
    os.system("mv %s junk" % oatfile)
    fp = open("junk", "r")
    lst = fp.readlines()
    fp.close()
    lst.sort()
    fp = open(oatfile, "w")
    fp.writelines(lst)
    fp.close()
    
## update the coordinate in the crude oatfile
# infile: oatfile withouth coordinate of station
# outfile: oatfile with coordinate of station
# coorfile: station coordinate, knetwk, kstnm, stla, stlo, evla
def cedc_stacoor(infile, outfile, coorfile, tt=True):  
    """
    add the coordinate to oat file
    """ 
    
    with open(infile, "r") as fp:
        inlst = fp.readlines()
        
    with open(coorfile, "r") as fp:
        coorlst = fp.readlines()
        
    netstalst = []
    for line in coorlst:
        row = line.split()
        netstalst.append(row[0]+"."+row[1])
    
    oat = Oat()    
    fpoat = open(outfile, "w")
    for line in inlst:
        
        try:
            oat.read(line)
        except:
            continue

        key = oat.knetwk+"."+oat.kstnm
        if key not in netstalst:
            continue
        
        ind = netstalst.index(key)
        row = coorlst[ind].split()
        
        oat.stla = float(row[2])
        oat.stlo = float(row[3])
        oat.stel = float(row[4])
        
        oat.DistAz()        
        
        if tt==True:
            print "sta coor and tak135:", oat.date, oat.time

            if oat.phase[0] == 'P' or oat.phase[0] == 'p':
                oat.ttak135pf(phase_list=['P','Pn','Pg', 'p'])
            elif oat.phase[0] == 'S' or oat.phase[0] == 's':
                oat.ttak135sf(phase_list=['S','Sn','Sg', 's'])

      
        oat.write(fpoat)
        
    fpoat.close()
 
    
def update_distaztt(oatfile,distaz=True, tt=True):
    
    with open(oatfile, "r") as fp:
        oatlst = fp.readlines()
        
    fp = open(oatfile, "w")
        
    oat = Oat()    
    for line in oatlst:
        oat.read(line)
        
        if distaz == True:
            oat.DistAz()        
        
        if tt==True:
            print "tak135:", oat.date, oat.time

            if oat.phase[0] == 'P' or oat.phase[0] == 'p':
                oat.ttak135pf(phase_list=['P','Pn','Pg', 'p'])
            elif oat.phase[0] == 'S' or oat.phase[0] == 's':
                oat.ttak135sf(phase_list=['S','Sn','Sg', 's'])

        oat.write(fp)
        
    fp.close()

