#!/usr/bin/env python

import os, sys
import glob
from obspy.core import UTCDateTime
sys.path.append('/media/weijia/ANU/swsrc')
from swSeismo import *
import gmt as gmt5
import shutil

"""
plot raypath for each station 
"""

def rayp_station(oatfile, gmtproj="B120/36/17/55/10c", gmtrange="100/140/17/60", tempdir="./temp", phase="P", threshold=10):
    
    Jh = gmtproj
    Rh = gmtrange
    
    try:
        shutil.rmtree(tempdir)
    except:
        pass
    if not os.path.exists(tempdir):
        os.makedirs(tempdir)
        
    try:
        shutil.rmtree("./fig")
    except:
        pass
    if not os.path.exists("./fig"):
        os.makedirs("./fig")
        
    with open(oatfile, "r") as fp:
        oatlst = fp.readlines()
     
    oat = Oat()   
    for line in oatlst:
        oat.read(line)
        
        filen = tempdir+"/"+oat.knetwk+oat.kstnm+".oat"
        fp = open(filen, "a")
        fp.write(line)
        fp.close()
        
    for file in glob.glob(tempdir+"/*.oat"):
        
        psfile = "./fig/"+os.path.basename(file).split(".")[0]+".ps"
        
        print psfile
        
        with open(file, 'r') as fp:
            lst = fp.readlines()
            
        if len(lst)<threshold:
            continue
        
        gmt = gmt5.Gmt()
        gmt.comment("basemap")
        gmt.cmd("psbasemap", "-J%s -R%s -BWSNE -Bxa10+l'Latitude [\\260]' -Bya10+l'Depth [km]' -K > %s" % (Jh, Rh, psfile))
        
        gmt.comment("coast")
        gmt.cmd("pscoast", "-J%s -R%s -W1/0.25p -N1 -N2 -K -O >> %s" % (Jh, Rh, psfile) )
        
        fp_ray = open("junk.raypath", "w")
        for line in lst:
            oat.read(line)
            os.system("gmt project -C%f/%f -E%f/%f -G10 -Q > great_circle.xyp" % (oat.evlo, oat.evla, oat.stlo, oat.stla))
            
            with open("great_circle.xyp", "r") as fp:
                raylst = fp.readlines()
                
            for rayline in raylst:
                row = rayline.split()
                fp_ray.write("%s\t%s\t%f\n" % (row[0], row[1], oat.tobs-oat.tak135));
                
        fp_ray.close()
            
        gmt.comment("plot raypath")  
        gmt.cmd("makecpt", "-Ccpt-city/cb/div/RdYlGn_10 -T-10/10/0.05 -I > colors.cpt")
        gmt.cmd("psxy", "junk.raypath -J%s -R%s  -K -O -Sc0.5p -Ccolors.cpt -W+0.5p >> %s" % (Jh, Rh, psfile))
        gmt.cmd("psscale", "-Ccolors.cpt -D5c/-0.7c/7.5c/0.5ch -K -O -Ba2+l'%s residuals [s]' >> %s" %(phase, psfile))

        gmt.comment("end")
        gmt.cmd("psxy", "-J -R -O -T >> %s" % psfile)
        gmt.cmd("ps2raster", "-A -P %s" % psfile)
        gmt.execute()



if __name__=="__main__":
    
    oatfile = "../cmb_cedc_isc_p.oat"
    oatfile = "../cmb_cedc_isc_s.oat"
    
    rayp_station(oatfile)

