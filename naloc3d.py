## \package naloc3d Relocation with NA algorithm
# \brief Relocation with NA algorithm
# \author Weijia Sun 
# \email swj@mail.iggcas.ac.cn
# \date 2015-08-11
# \version $Id$

import os,glob,subprocess
from swSeismo import *
from obspy.core import UTCDateTime
from obspy.core.util import locations2degrees
import simplekml
from posix import lstat
import shutil


## convert oat file to css arrival format for naloc3d
#  \param oatfile filename of oat
#  \param csspath path of css arrival, no '/'   
#  \param ntwksta if True use network and station together as the station name, or else use the station name
#  \param phase if True, keep the original phase name, else change phasename to 'Pf' for Pg or Pn and 'Sf' for Sg or Sn
def oat2css(oatfile, csspath, ntwksta=False, phase=True):
    
    if not os.path.exists(csspath):
        os.makedirs(csspath)
    
    fp = open(oatfile, 'r')
    oatlst = fp.readlines()
    fp.close()
    
    evtlst = []
    
    oat = Oat()
    
    for line in oatlst:
        oat.read(line)
        oat.roundOrigin()    
        evt = [oat.date, oat.time]
        
        if evt not in evtlst:
            evtlst.append(evt)
           
    for i in range(len(evtlst)):
        date = evtlst[i][0]
        time = evtlst[i][1]
        ofile = csspath+'/'+date+'_'+time+'.arrival'
        ofile = ofile.replace(':', '_')
        ofile = ofile.replace('-', '_')

        print ofile
        
        fp = open(ofile, 'w')    
        
        for line in oatlst:
            oat.read(line)
            oat.roundOrigin()
    
            if oat.date!=date or oat.time!=time:
                continue
            
            oat.origin()
            evtInfo = [oat.o, oat.evla, oat.evlo, oat.evdp]
            
            tobs = oat.o + oat.tobs
            if not phase:
                if oat.phase[0]=='P':
                    oat.phase = 'Pf'
                    deltim = 0.15*10
                elif oat.phase[0]=='S':
                    oat.phase = 'Sf'
                    deltim = 0.45*10
            else:
                if oat.phase[0]=='P':
                    # oat.phase = 'Pf'
                    deltim = 0.15*10
                elif oat.phase[0]=='S':
                    # oat.phase = 'Sf'
                    deltim = 0.45*10

            
            if ntwksta==True:
                kstnm=oat.knetwk+oat.kstnm
            elif ntwksta==False:
                kstnm = oat.kstnm
            swCSS3Temp(kstnm, oat.phase, tobs, deltim, evtInfo, fp)
                   
        fp.close()

## location using NA
#  \param csspath path of css arrival, no '/'
#  \param nalocfile file containing source paramters before and after relocation
#  \param locmd path and name of naloc3, default is './loc3d_aug'
#  \param ttgridpath path containing travel-time grid, no '/'
#  \param filter used to debug the parameters, default='*'
def naloc3(csspath, nalocfile, locmd='./loc3d_aug', ttgridpath='../ttgrid',filter='*'):
    
    # if ttgridpath != "../austtg":
    #     os.system('ln -s %s ../austtg' % (ttgridpath) )

    if ttgridpath != "../ttgrid":
        os.system('ln -s %s ../ttgrid' % (ttgridpath) )

    # get CSS3 arrival file
    cssfilelst = glob.glob(csspath+"/"+filter+"*.arrival")
    cssfilelst.sort()
    
    logFile = open('naloc.log','w')
    locfp = open(nalocfile, 'a+')
    
    
    evid = 0
    
    for cssfile in cssfilelst:
        print cssfile 
        
        os.system('cp ' + cssfile + ' arrival_list')
        
        fp = open('arrival_list','r')
        lineTemp = fp.readlines()
        fp.close()
        numberPhase = len(lineTemp)
        
        if numberPhase < 3:
            continue    
        
        row = lineTemp[0].split()
        originOld = UTCDateTime(float(row[14]))
        evlaOld = float(row[15])
        evloOld = float(row[16])
        evdpOld = float(row[17])
            
        p = subprocess.Popen([locmd],stdout = logFile).communicate()[0]
    #     os.system('./loc3d_aug')
        
        if not os.path.exists('fort.13'):
            logFile.write('Location failed.')
    #         print 'Loc fail'
        else:
            fp = open('fort.13', 'r')
            line = fp.readline()
            fp.close()
            row = line.split()
            evla = float(row[1])
            evlo = float(row[2])
            evdp = float(row[3])
            origin = UTCDateTime(float(row[10]))+float(row[4])
                    
            eorigin = origin - originOld        
            edist = locations2degrees(evla, evlo, evlaOld, evloOld)
            edepth = evdp - evdpOld
            
            [date, time] = datetimefmt(origin)
            [dateold, timeold] = datetimefmt(originOld)
            
    #         sstring = '%s %12.4f %12.4f %8.3f %s %12.4f %12.4f %8.3f %8.3f %8.3f %8.3f %4d \n' % (str(origin), evla, evlo, evdp, str(originOld), evlaOld, evloOld, evdpOld, eorigin, edist, edepth, numberPhase)
    #         locfp.write(sstring)
    #         evid += 1
            sstring = '%12s %14s %12.4f %12.4f %8.3f %12s %14s %12.4f %12.4f %8.3f %8.3f %8.3f %8.3f %4d \n' % (date, time, evla, evlo, evdp, dateold, timeold, evlaOld, evloOld, evdpOld, eorigin, edist, edepth, numberPhase)
            locfp.write(sstring)
            
            try:
                #os.remove('fort.13')
                pass
            except:
                pass
            
            swCleanupLoc()
            
    locfp.close()
    logFile.close()
    
    if ttgridpath != "../austtg":
        os.system('rm -rf ../austtg')
    
## update oatfile after relocation
#  \param oatfile filename of oat
#  \param nalocfile file containing source paramters before and after relocation
#  \param ophase1 if True, keep the original phase name and calculate its arrival time, else calculate the first arrival for P or S
def updateoat(oatfile, nalocfile, ophase=True):
    a = os.path.splitext(oatfile)
    naloc_oat_file = a[0]+'_naloc'+a[1]
    
    oatfp = open(oatfile, 'r')
    oatlst = oatfp.readlines()
    oatfp.close()
    
    fp = open(nalocfile, 'r')
    naloclst = fp.readlines()
    fp.close()
    
    fp = open(naloc_oat_file, 'w')
    
    oldevt = []
    newevt = []
    
    oat = Oat()
    
    print 'total number of arrivals:', len(oatlst)
    
    count = 0
    for line in naloclst:
        row = line.split()
        newdate = row[0].strip()
        newtime = row[1].strip()
        newlat  = float(row[2].strip())
        newlon  = float(row[3].strip())
        newdep  = float(row[4].strip())
    
        olddate = row[5].strip()
        oldtime = row[6].strip()
        oldlat  = float(row[7].strip())
        oldlon  = float(row[8].strip())
        olddep  = float(row[9].strip())
        
        oldorigin = round(UTCDateTime(olddate+'T'+oldtime))
        
        for oatline in oatlst:
            oat.read(oatline)
            
            origin = round(UTCDateTime(oat.date+'T'+oat.time))
            if origin!=oldorigin:
                continue
            
            tobs = origin + oat.tobs        
    #         count += 1
            
            oat.date = newdate
            oat.time = newtime
            oat.evla = newlat
            oat.evlo = newlon
            oat.evdp = newdep
            
            oat.origin()
            oat.tobs = tobs - oat.o
            
            oat.DistAz()
                
#             if oat.evdp<0.6:    # due to the bug of obspy
#                 oat.evdp = 0.0
#             elif oat.evdp>=0.6 and oat.evdp <1.3:
#                 oat.evdp = 1.3
                
    #         print oat.evdp, newdep, oat.gcarc
             
            phase = oat.phase
            try:
                if ophase:
                    if phase[0]=='P':
                        oat.ttak135pf(phase_list=[phase])
                    elif phase[0]=='S':
                        oat.ttak135sf(phase_list=[phase])
                    else:
                        continue
                else:
                    if phase[0]=='P':
                        oat.ttak135pf(phase_list=['P','Pn','Pg', 'p'])
                    elif phase[0]=='S':
                        oat.ttak135sf(phase_list=['S','Sn','Sg', 's'])
                    else:
                        continue
            except:
                count += 1
                continue

            count += 1
            
            print count, len(oatlst)
            
            oat.evdp = newdep
                
            oat.write(fp)
    
    fp.close()
    
    print oatfile
    print 'total number of arrivals:', len(oatlst)
    print naloc_oat_file
    print 'number of arrivals updated: ', count
    
## convert naloc to KML, this function depends on the package simplekml
#  please see https://pypi.python.org/pypi/simplekml/1.2.8
#    \param oatfile oat filename
#    \param kmlfile kml filename

def naloc2kml(nalocfile, kmlfile):

    with open(nalocfile, 'r') as fp:
        lst = fp.readlines()
    
    evtlst = []
    for line in lst:
        row = line.split()
        
        date=row[0].strip()
        time=row[1].strip()
        evla = float(row[2].strip())
        evlo = float(row[3].strip())
        evdp = float(row[4].strip())
                
        evt= [date+' '+time, evla, evlo, evdp]
        if evt not in evtlst:
            evtlst.append(evt)
            
    evttup = tuple(evtlst)
    
    kml = simplekml.Kml(open=1) # the folder will be open in the table of contents
    
    folevt = kml.newfolder(name='Relocated Earthquakes')
    # folevt.lookat.tilt = 0
    for date, evla, evlo, evdp in evttup:
        pnt = folevt.newpoint()
        pnt.name = date
        pnt.description = "Date:%s\nLat:%12.4f\nLon:%12.4f\nDep:%8.3f" % (date, evla, evlo, evdp)
        pnt.style.iconstyle.scale = 1.5  # Icon thrice as big
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/earthquake.png'
        pnt.coords = [(evlo, evla)]    
        
    kml.save(kmlfile)

class naloc3d:
    def __init__(self):
        self.date = "1970-01-01"    
    
    def read(self, line):
        row = line.split()
        self.date = row[0].strip()
        self.time = row[1].strip()
        self.evla = float(row[2].strip())    
        self.evlo = float(row[3].strip())    
        self.evdp = float(row[4].strip()) 
           
        self.date0 = row[5].strip()
        self.time0 = row[6].strip()
        self.evla0 = float(row[7].strip())    
        self.evlo0 = float(row[8].strip())    
        self.evdp0 = float(row[9].strip())  
          
        self.eorigin  = float(row[10].strip())
        self.edist = float(row[11].strip())
        self.edepth  = float(row[12].strip())
        self.narr    = float(row[13].strip())
    
    def write(self, fp):
        sstring = '%12s %14s %12.4f %12.4f %8.3f %12s %14s %12.4f %12.4f %8.3f %8.3f %8.3f %8.3f %4d \n' % (self.date, self.time, self.evla, self.evlo, self.evdp, self.date0, self.time0, self.evla0, self.evlo0, self.evdp0, self.eorigin, self.edist, self.edepth, self.narr)
        fp.write(sstring)

## read fort.14 from NA relocation
# \param file filename, default is fort.14 in current directory
# \return  chisq, wchisq, misfit
# \param chisq error estimates   
# \param wchisq weight error estimates
# \misfit misfit
def namisfit(file="fort.14"):
    with open(file, "r") as fp:
        lst = fp.readlines()
    
    chisq = -12345.0
    wchisq = -12345.0
    misfit = -12345.0
        
    for line in lst:
        try:
            row = line.split()
            if row[0] == "opt":
                chisq = float(row[2])
#                 print chisq
            elif row[2] =="solutionchisq":
                wchisq = float(row[4])
                misfit = float(row[6])
#                 print wchisq, misfit
        except:
            pass
        
    return chisq, wchisq, misfit


# chisq, wchisq, misfit = readfort14("../fort.14")
# print chisq, wchisq, misfit
    
## location using NA
#  \param csspath path of css arrival, no '/'
#  \param nalocfile file containing source paramters before and after relocation
#  \param locmd path and name of naloc3, default is './loc3d_aug'
#  \param ttgridpath path containing travel-time grid, no '/'
#  \param filter used to debug the parameters, default='*'
def naloc3v2(csspath, nalocfile, locmd='./loc3d_aug', ttgridpath='../austtg',filter='*'):
    
    if ttgridpath != "../austtg":
        os.system('ln -s %s ../austtg' % (ttgridpath) )
    
    # get CSS3 arrival file
    cssfilelst = glob.glob(csspath+"/"+filter+"*.arrival")
    cssfilelst.sort()
    
    logFile = open('naloc.log','w')
    locfp = open(nalocfile, 'w')
    
    
    evid = 0
    
    for cssfile in cssfilelst:
        print cssfile 
        
        os.system('cp ' + cssfile + ' arrival_list')
        
        fp = open('arrival_list','r')
        lineTemp = fp.readlines()
        fp.close()
        numberPhase = len(lineTemp)
        
        if numberPhase < 3:
            continue    
        
        row = lineTemp[0].split()
        originOld = UTCDateTime(float(row[14]))
        evlaOld = float(row[15])
        evloOld = float(row[16])
        evdpOld = float(row[17])
            
        p = subprocess.Popen([locmd],stdout = logFile).communicate()[0]
    #     os.system('./loc3d_aug')
        
        if not os.path.exists('fort.13'):
            logFile.write('Location failed.')
    #         print 'Loc fail'
        else:
            fp = open('fort.13', 'r')
            line = fp.readline()
            fp.close()
            row = line.split()
            evla = float(row[1])
            evlo = float(row[2])
            evdp = float(row[3])
            origin = UTCDateTime(float(row[10]))+float(row[4])
                    
            eorigin = origin - originOld        
            edist = locations2degrees(evla, evlo, evlaOld, evloOld)
            edepth = evdp - evdpOld
            
            [date, time] = datetimefmt(origin)
            [dateold, timeold] = datetimefmt(originOld)
            
            chisq, wchisq, misfit = namisfit()
            
    #         sstring = '%s %12.4f %12.4f %8.3f %s %12.4f %12.4f %8.3f %8.3f %8.3f %8.3f %4d \n' % (str(origin), evla, evlo, evdp, str(originOld), evlaOld, evloOld, evdpOld, eorigin, edist, edepth, numberPhase)
    #         locfp.write(sstring)
    #         evid += 1
            sstring = '%f\t %f\t %f %12s %14s %12.4f %12.4f %8.3f %12s %14s %12.4f %12.4f %8.3f %8.3f %8.3f %8.3f %4d \n' % (chisq, wchisq, misfit, date, time, evla, evlo, evdp, dateold, timeold, evlaOld, evloOld, evdpOld, eorigin, edist, edepth, numberPhase)
            locfp.write(sstring)
            
            try:
                #os.remove('fort.13')
                pass
            except:
                pass
            
            #swCleanupLoc()
            
    locfp.close()
    logFile.close()
    
    if ttgridpath != "../austtg":
        os.system('rm -rf ../austtg')
    
    
    
## location using NA version 2
#  in this version we save residuals and write the P and S residuals appended to the last two column in naloc file
#  \param csspath path of css arrival, no '/'
#  \param nalocfile file containing source paramters before and after relocation
#  \param locmd path and name of naloc3, default is './loc3d_aug'
#  \param ttgridpath path containing travel-time grid, no '/'
#  \param filter used to debug the parameters, default='*'
def naloc3v2(csspath, nalocfile, locmd='./loc3d_aug', ttgridpath='../austtg',filter='*'):
    
    if ttgridpath != "../austtg":
        os.system('ln -s %s ../austtg' % (ttgridpath) )
        
    resdir = "./residuals"
    if not os.path.exists(resdir):
        os.makedirs(resdir)
    
    # get CSS3 arrival file
    cssfilelst = glob.glob(csspath+"/"+filter+"*.arrival")
    cssfilelst.sort()
    
    logFile = open('naloc.log','w')
    locfp = open(nalocfile, 'w')
    
    
    evid = 0
    
    for cssfile in cssfilelst:
        print cssfile 
        
        os.system('cp ' + cssfile + ' arrival_list')
        
#         try:
#             os.system("rm fort.13")
#         except:
#             pass
        
        fp = open('arrival_list','r')
        lineTemp = fp.readlines()
        fp.close()
        numberPhase = len(lineTemp)
        
        if numberPhase < 3:
            continue    
        
        row = lineTemp[0].split()
        originOld = UTCDateTime(float(row[14]))
        evlaOld = float(row[15])
        evloOld = float(row[16])
        evdpOld = float(row[17])
            
        p = subprocess.Popen([locmd],stdout = logFile).communicate()[0]
    #     os.system('./loc3d_aug')
        
        if not os.path.exists('fort.13'):
            logFile.write('Location failed.')
    #         print 'Loc fail'
        else:
            fp = open('fort.13', 'r')
            line = fp.readline()
            fp.close()
            row = line.split()
            evla = float(row[1])
            evlo = float(row[2])
            evdp = float(row[3])
            origin = UTCDateTime(float(row[10]))+float(row[4])
                    
            eorigin = origin - originOld        
            edist = locations2degrees(evla, evlo, evlaOld, evloOld)
            edepth = evdp - evdpOld
            
            [date, time] = datetimefmt(origin)
            [dateold, timeold] = datetimefmt(originOld)
            
            # open residuals.dat
            with open("residuals.dat", "r") as fp:
                lst = fp.readlines()
                
            pfres = 0.0
            sfres = 0.0
            
            
            pfres = float(lst[-2].split()[-1])
            sfres = float(lst[-1].split()[-1])
            
    #         sstring = '%s %12.4f %12.4f %8.3f %s %12.4f %12.4f %8.3f %8.3f %8.3f %8.3f %4d \n' % (str(origin), evla, evlo, evdp, str(originOld), evlaOld, evloOld, evdpOld, eorigin, edist, edepth, numberPhase)
    #         locfp.write(sstring)
    #         evid += 1
            sstring = '%12s %14s %12.4f %12.4f %8.3f %12s %14s %12.4f %12.4f %8.3f %8.3f %8.3f %8.3f %4d %8.3f %8.3f\n' % (date, time, evla, evlo, evdp, dateold, timeold, evlaOld, evloOld, evdpOld, eorigin, edist, edepth, numberPhase, pfres, sfres)
            locfp.write(sstring)
            
            
            resfn = resdir+"/"+dateold.replace("-","")+timeold.replace(":", "")[0:6]+".res"
            os.system("cp residuals.dat %s" % resfn)
            
            swCleanupLoc()
            
    locfp.close()
    logFile.close()
    
    if ttgridpath != "../austtg":
        os.system('rm -rf ../austtg')
    
    
    
## convert oat file to css arrival format for naloc3d
#  \param oatfile filename of oat
#  \param csspath path of css arrival, no '/'   
#  \param ntwksta if True use network and station together as the station name, or else use the station name 
def oat2css_v2(oatfile, csspath, ntwksta=False):
    
    try:
        shutil.rmtree(csspath)
    except:
        pass
    
    if not os.path.exists(csspath):
        os.makedirs(csspath)
        
    
    fp = open(oatfile, 'r')
    oatlst = fp.readlines()
    fp.close()
        
    oat = Oat()
    
    for line in oatlst:
        oat.read(line)

        aa = oat.date
        ddate = aa.replace("-", "_")
        
        aa = oat.time
        ttime = aa.replace(":","_")[0:8]
        
        ofile = csspath+'/'+ddate+'_'+ttime+'.arrival'

        
        fp = open(ofile, 'a')
            
        oat.origin()
        evtInfo = [oat.o, oat.evla, oat.evlo, oat.evdp]           
        tobs = oat.o + oat.tobs
        
        if oat.phase[0]=='P':
            oat.phase = 'Pf'
            deltim = 0.15*10
        elif oat.phase[0]=='S':
            oat.phase = 'Sf'
            deltim = 0.45*10        
        
        if ntwksta==True:
            kstnm=oat.knetwk+oat.kstnm
        elif ntwksta==False:
            kstnm = oat.kstnm
    
        swCSS3Temp(kstnm, oat.phase, tobs, deltim, evtInfo, fp)
                   
        fp.close()
    
    
    
    
    
    
    
    
    
    
