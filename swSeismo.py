## \package Seismology module
# \author Weijia Sun <swj@mail.iggcas.ac.cn>
# \date 2015-08-11
# \version $Id$

import css_types
import os
from obspy.core import UTCDateTime
import commands
from obspy.taup.tau import TauPyModel
# from obspy.iris.client import Client
from obspy.clients.iris.client import Client

from obspy.taup import getTravelTimes
import DistAz
import simplekml

def swVersion(val=1):
    print 'SW Seismology Pack'
    if val==1:
        print 'Version 0.1'
        print 'June 17, 2015'
    else:
        print 'Version 0.1'
        print 'June 17, 2015'
    
    print 'Author: Weijia Sun'
    print 'Copyright reserved'

##
def swCSS3Temp(sta, iphase, time, deltim, evInfo, fp):
    """
    Generate a peseudo CSS3.0 arrival file to fool comptuter
    This is for relocation program by Dr de Kool.
    """        
    arr = css_types.arrival30()
    arr.sta = sta
    arr.time = time
    arr.iphase = iphase
    arr.deltim = deltim
    
    arr.ema = evInfo[0]
    arr.rect = evInfo[1]
    arr.amp = evInfo[2]
    arr.per = evInfo[3]
    
    arr.write_record(fp)

##    
def swBasename(file):
    '''
    file = /usr/local/test.txt
    returns /usr/local, test, .txt
    '''
    (path, name) = os.path.split(file)
    (basename, extension) = os.path.splitext(name)
    return [path, basename, extension]

##
def swCleanupLoc():
    
    try:
        os.remove("fort.18")
    except:
        pass
    
    try:
        os.remove("fort.20")
    except:
        pass
    
#     try:
#         os.remove("arrival_list")
#     except:
#         pass
    
    try:
        os.remove("arrival_list.original")
    except:
        pass
    
    try:
        os.remove("latlon.log")
    except:
           pass
    
    try:
        os.remove("log")
    except:
        pass
    
#     try:
#         os.remove("na.in")
#     except:
#         pass
    
    try:
        os.remove("na.nad")
    except:
        pass
    
    try:
        os.remove("na.sum")
    except:
        pass
    
#     try:
#         os.remove("ranges.in")
#     except:
#         pass
    
    try:
        os.remove("sobol.coeff")
    except:
        pass
    
    try:
        os.remove("seismic_parameters.in")
    except:
        pass
    
    try:
        os.remove("grid")
    except:
        pass
       
def swGetSacOriginTime(kzdate, kztime, o):
    date = kzdate.replace('/', '-')
    eventtime = UTCDateTime(date+'T'+kztime)
    eventtime += o  # 0.1 for error
#    eventtime.microsecond = 0
    
    return eventtime

# def swGetSacOriginTimeAccurate(kzdate, kztime, o):
#     date = kzdate.replace('/', '-')
#     eventtime = UTCDateTime(date+'T'+kztime)
#     eventtime += o  # 0.1 for error
# #    eventtime.microsecond = 0
#     
#     return eventtime

def swGetSacReferTime(kzdate, kztime):
    date = kzdate.replace('/', '-')
    eventtime = UTCDateTime(date+'T'+kztime)
    
    return eventtime


def swAicClean():
    os.system('rm ?.sac araic.in')
    
def swSacHeader2miniArrival(sacfile, fp, mode='P'):
    '''
    get event header and station header, pick, from sac fiel
    '''
    output = commands.getoutput('saclst kzdate kztime o evla evlo evdp mag f '+sacfile)
    line = output.split()
    kzdate = line[1]
    kztime = line[2]
    o = float(line[3])
    evla = float(line[4])
    evlo = float(line[5])
    evdp = float(line[6])
    mag = float(line[7])
    origin = swGetSacOriginTime(kzdate, kztime, o)
#    originAccurate = swGetSacOriginTimeAccurate(kzdate, kztime, o)
    date = origin.date
    time = origin.time
    
    reftime = swGetSacReferTime(kzdate, kztime)
    if mode=='P' or mode=='p':
        output = commands.getoutput('saclst t5 a f '+sacfile)
    elif mode=='S' or mode=='s':
        output = commands.getoutput('saclst t6 t0 f '+sacfile)
    line = output.split()
    if float(line[2])==-12345:
        return
    tak135 = reftime + float(line[1]) - origin
    tpick = reftime + float(line[2]) - origin
    

    output = commands.getoutput('saclst knetwk kstnm stla stlo stel dist gcarc az baz kcmpnm f '+sacfile)
    line = output.split()
    knetwk = line[1].rstrip()
    kstnm = line[2].rstrip()
    stla = float(line[3])    
    stlo = float(line[4])    
    stel = float(line[5])    
    dist = float(line[6])    
    gcarc = float(line[7])    
    az = float(line[8])   
    baz = float(line[9]) 
    kcmpnm = line[10]
    
    fp.write('%s %s %f %f %f %f %s %s %s %f %f %f %f %f %f %f %s %f %f\n'%(date, time, evla, evlo, evdp, mag, knetwk, kstnm, kcmpnm, stla, stlo, stel, dist, gcarc, az, baz, mode.upper(), tak135, tpick))

class Oat:
    """
    Definition of OAT format
    
    
    """
    def __init__(self):
        """The constructor."""
        ## event date
        self.date = "1970-01-01"    
        ## event time
        self.time = "00:00:00.000"
        ## event latitude
        self.evla = -1.0
        self.evlo = -1.0
        self.evdp = -1.0
        self.mag = -1.0
        self.knetwk = "???"
        self.kstnm = "???"
        self.kcmpnm = "???"
        self.stla = -1.0
        self.stlo = -1.0
        self.stel = -1.0
        self.dist = -1.0
        self.gcarc = -1.0
        self.az = -1.0
        self.baz = -1.0
        self.phase = "???"
        self.tak135 = -1.0
        self.tobs = -1.0
        
        self.o = 0.0
        
    ## read line of a oat file
    #  \param line input
    #  \param date event date
    #  \param time event time
    def read(self, line):
        row = line.split()
        self.date = row[0].strip()
        self.time = row[1].strip()
        self.evla = float(row[2])
        self.evlo = float(row[3])
        self.evdp = float(row[4])
        self.mag = float(row[5])    ## \param mag magnitude
        self.knetwk = row[6].strip()
        self.kstnm = row[7].strip()
        self.kcmpnm = row[8].strip()
        self.stla = float(row[9])
        self.stlo = float(row[10])
        self.stel = float(row[11])
        self.dist = float(row[12])
        self.gcarc = float(row[13])
        self.az = float(row[14])
        self.baz = float(row[15])
        self.phase = row[16].strip()
        self.tak135 = float(row[17])
        self.tobs = float(row[18])
       
    ## write oat file
    # \param fp file pointer 
    def write(self, fp):
        fp.write('%12s %14s %12.4f %12.4f %8.3f %8.3f %-8s %-8s %-8s %12.4f %12.4f %12.4f %12.4f %12.4f %12.4f %12.4f %-8s %12.4f %12.4f\n'%(self.date, self.time, self.evla, self.evlo, self.evdp, self.mag, self.knetwk, self.kstnm, self.kcmpnm, self.stla, self.stlo, self.stel, self.dist, self.gcarc, self.az, self.baz, self.phase, self.tak135, self.tobs))
    
    ## write oat into a string
    #  return line
    def writeline(self):
        line = '%12s %14s %12.4f %12.4f %8.3f %8.3f %-8s %-8s %-8s %12.4f %12.4f %12.4f %12.4f %12.4f %12.4f %12.4f %-8s %12.4f %12.4f\n'%(self.date, self.time, self.evla, self.evlo, self.evdp, self.mag, self.knetwk, self.kstnm, self.kcmpnm, self.stla, self.stlo, self.stel, self.dist, self.gcarc, self.az, self.baz, self.phase, self.tak135, self.tobs)
        return line
    
    ## calculation of P first arrival
    #  \param phase_list a list containing possible P first arrival    
    def ttak135pf(self, phase_list=['P','Pn','Pg','p']):    # travel time of first P arrivals with AK135 model
        model = TauPyModel(model="ak135")
        
        if self.evdp>0 and self.evdp<1.4:
            self.evdp = 0
        
        arrivals = model.get_travel_times(self.evdp, self.gcarc, phase_list=phase_list)
        arr = arrivals[0]
#         self.phase = arr.name
        self.tak135 = arr.time

    ## calculation of S first arrival
    #  \param phase_list a list containing possible S first arrival    
    def ttak135sf(self, phase_list=['S','Sn','Sg','s']):    # travel time of first S arrivals with AK135 model
        model = TauPyModel(model="ak135")
        
        if self.evdp>0 and self.evdp<1.4:
            self.evdp = 0
        
        arrivals = model.get_travel_times(self.evdp, self.gcarc, phase_list=phase_list)
#         print len(arrivals), self.date, self.time, self.stla, self.stlo, self.evla, self.evlo
        arr = arrivals[0]
#         self.phase = arr.name
        self.tak135 = arr.time
#         for i in range(len(arrivals)):
#             arr = arrivals[i]
#             phase = arr.phase
#             print phase
#             if phase[0] == 'S':
#                 self.phase = arr.name
#                 self.tak135 = arr.time

#     def ttak135pf_taup(self):    # travel time of first P arrivals with AK135 model
#         tt = getTravelTimes(delta=self.gcarc, depth=self.evdp, model='ak135')
#         self.phase = tt[0]['phase_name']
#         self.tak135 = tt[0]['time']
    
    ## distance and azimuth
    #  To use this function, you must have an access to Internet.
    #  This use the IRIS interface to calculate the distance and azimuthal angles.
    def distaz(self):
        client = Client()
        result = client.distaz(self.stla, self.stlo, self.evla, self.evlo)
        self.gcarc = result['distance']
        self.dist = self.gcarc*111.195
        self.az = result['azimuth']
        self.baz = result['backazimuth']
    
    ## origin time of an event with timestamp    
    def origin(self):
        self.o = UTCDateTime(self.date+'T'+self.time).timestamp   
    
    ## round up the origin time to avoid a very small bias, e.g.,1970-02-09T00:12:34.999990Z and 1970-02-09T00:12:35.000000Z
    def roundOrigin(self):      # 1970-02-09T00:12:34.999990Z
        origin = UTCDateTime(self.date+'T'+self.time)
        origin = UTCDateTime(round(origin))
        self.date = origin.strftime("%Y-%m-%d")
        self.time = origin.strftime("%H:%M:%S")
        self.o = origin
        
    def DistAz(self):
        diz = DistAz.DistAz(self.evla, self.evlo, self.stla, self.stlo)
        self.gcarc = diz.getDelta()
        self.dist = self.gcarc*111.195
        self.az = diz.getAz()
        self.baz = diz.getBaz()
        
    def originfmt(self):
        o = UTCDateTime(self.date+"T"+self.time)
        o = UTCDateTime(round(o,3))
        self.date = o.strftime("%Y-%m-%d")
        self.time = o.strftime("%H:%M:%S.%f")[0:12]
       
# end of class oat

## format the time, e.g., 1999-01-31, 00:12:24.123   
#  \param origin a string e.g., "1999-01-31T00:12:24.123456Z"  
#  return [date, time]
def datetimefmt(origin):    # 1999-01-31, 00:12:24.123  
    o = UTCDateTime(origin)
    o = UTCDateTime(round(o,3))
    date = o.strftime("%Y-%m-%d")
    time = o.strftime("%H:%M:%S.%f")[0:12]
    
    return [date, time]

## extract event information from a oatfile
#  \param oatfile oatfile name
#  \param evtfile evtfile name
def evtoat(oatfile, evtfile):
    fp = open(oatfile,'r')
    lst = fp.readlines()
    fp.close()
    
    fp = open(evtfile,'w')
    evtlst = []
    for line in lst:
        row=line.split()
        tlst = [row[0], row[1], row[2], row[3], row[4], row[5]]
        if tlst not in evtlst:
            evtlst.append(tlst)
            fp.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (row[0], row[1], row[2], row[3], row[4], row[5]))
    fp.close()
    

## extract station information from a oatfile
#  \param oatfile oatfile name
#  \param stafile evtfile name
def staoat(oatfile, stafile):
    fp = open(oatfile,'r')
    lst = fp.readlines()
    fp.close()
    
    fp = open(stafile,'w')
    evtlst = []
    for line in lst:
        row=line.split()
        tlst = [row[6], row[7], row[9], row[10], row[11]]
        if tlst not in evtlst:
            evtlst.append(tlst)
            fp.write("%s\t%s\t%s\t%s\t%s\n" % (row[6], row[7], row[9], row[10], row[11]))
    fp.close()
    
## convert arrival from Geoscience Australia to oat
#    \param arrfile arrival filename of GA
#    \param oatfile output oat filename
#    \param stafile input filename containing all station name and its lat, lon, ele, format is knetwk kstnm stla stlo stel
#    
def ga2oat(arrfile, oatfile, stafile):
    with open(arrfile, 'r') as fp:
        lst = fp.readlines()
        
    with open(stafile, 'r') as fp:
        stlst = fp.readlines()
    
    stalst = []
    for line in stlst:
        row = line.split()
        nwnm = row[0].strip()
        stnm = row[1].strip()
        stla = float(row[2])
        stlo = float(row[3])
        stel = float(row[4])
        tmp = [nwnm, stnm, stla, stlo, stel]
        stalst.append(tmp)
    
    fp = open(oatfile,'w')
    
    oat = Oat()
    
    month = {'January':1, 'February':2, 'March':3, 'April':4, 'May':5, 'June':6, 'July':7, 'August':8, 'September':9, 'October':10, 'November':11, 'December':12}
    
    k=0
    for line in lst:
        k = k+1
        print k, len(lst)
        if line.strip() == "":
            continue
        
        row = line.split()
        try:
            oat.mag = float(row[0])
            day = row[1]
            mon = str(month[row[2]]).zfill(2)
            year = row[3]
            oat.time = row[5]
            oat.date = year+'-'+mon+'-'+day
            oat.evla = float(row[11])
            oat.evlo = float(row[12])
            oat.evdp = float(row[13])
    
        except:
            if row[0] != '-':
                oat.kstnm = row[0]
            for i in range(len(row)):
                if row[i]=='P' or row[i]=='S':
                    break
            
            oat.phase = row[i]
            
            date = row[i+1]
            time = row[i+2]
            
            tt = date.split('/')
            date = tt[2]+'-'+tt[1]+'-'+tt[0]
            oat.tobs = UTCDateTime(date+'T'+time) - UTCDateTime(oat.date+'T'+oat.time)
            
            for i in range(len(stalst)):
                if oat.kstnm == stalst[i][1]:
                    oat.stla = stalst[i][2]
                    oat.stlo = stalst[i][3]
                    oat.stel = stalst[i][4]
                    oat.knetwk = stalst[i][0]
                    break
            
            if oat.stla == -1.0:
                continue
            
            oat.DistAz()
            if oat.phase[0] == 'P' or oat.phase[0] == 'p':
                oat.ttak135pf(phase_list=['P','Pn','Pg', 'p'])
            elif oat.phase[0] == 'S' or oat.phase[0] == 's':
                oat.ttak135sf(phase_list=['S','Sn','Sg', 's'])
    
            oat.write(fp)
        
    fp.close()

## convert oat to KML, this function depends on the package simplekml
#  please see https://pypi.python.org/pypi/simplekml/1.2.8
#    \param oatfile oat filename
#    \param kmlfile kml filename

def oat2kml(oatfile, kmlfile):

    with open(oatfile, 'r') as fp:
        lst = fp.readlines()
    
    evtlst = []
    stalst = []
    oat = Oat()
    for line in lst:
        oat.read(line)
        evt= [oat.date+' '+oat.time, oat.evla, oat.evlo, oat.evdp, oat.mag]
        if evt not in evtlst:
            evtlst.append(evt)
            
        sta = [oat.knetwk+'.'+oat.kstnm, oat.stla, oat.stlo, oat.stel]
        if sta not in stalst:
            stalst.append(sta)
            
    
    evttup = tuple(evtlst)
    statup = tuple(stalst)
    
    kml = simplekml.Kml(open=1) # the folder will be open in the table of contents
    
    folevt = kml.newfolder(name='Earthquakes')
    # folevt.lookat.tilt = 0
    for date, evla, evlo, evdp,mag in evttup:
        pnt = folevt.newpoint()
        pnt.name = date
        pnt.description = "Date:%s\nLat:%12.4f\nLon:%12.4f\nDep:%8.3f\nMag:%8.3f" % (date, evla, evlo, evdp, mag)
        pnt.style.iconstyle.scale = 1.5  # Icon thrice as big
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/earthquake.png'
        pnt.coords = [(evlo, evla)]
    #     pnt.lookat.tilt = 0
    
    folsta = kml.newfolder(name='Stations')
    for name, stla, stlo, stel in statup:
        pnt = folsta.newpoint()
        pnt.name = name
        pnt.description = "Sta:%s\nLat:%12.4f\nLon:%12.4f\nEle:%8.3f[m]" % (name, stla, stlo, stel)
        pnt.style.iconstyle.scale = 2  # Icon thrice as big
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pal3/icon23.png'
        pnt.coords = [(stlo, stla)]
    #     pnt.lookat.tilt = 0
            
    kml.save(kmlfile)

## station file to kml
def sta2kml(stafile, kmlfile):
    with open(stafile, 'r') as fp:
        lst = fp.readlines()

    kml = simplekml.Kml(open=1) # the folder will be open in the table of contents
        
    netold = ""
    for line in lst:
        row = line.split()
        net = row[0]
        sta = row[1]
        stla = float(row[2])
        stlo = float(row[3])
        stel = float(row[4])
        
        if net!=netold:
            folsta = kml.newfolder(name=net)
            netold = net
            
        pnt = folsta.newpoint()
        pnt.name = net+"."+sta
        pnt.description = "Sta:%s\nLat:%12.4f\nLon:%12.4f\nEle:%8.3f[m]" % (pnt.name, stla, stlo, stel)
        pnt.style.iconstyle.scale = 2  # Icon thrice as big
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pal3/icon23.png'
        pnt.coords = [(stlo, stla)]
    kml.save(kmlfile)
       
    


    
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











        
