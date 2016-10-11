#!/usr/bin/env python

import os,sys
import math
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy import interpolate

# infile = 'interfaces.in'
# vgfile = 'vgrids.in'
# ofile  = 'ausinvert_vp.txt'
# ifile  = 'ausinvert.igrd'
# 
# dxout = 1.0
# dyout = 1.0
# dzout = 10.0
# 
# xmin = 110.0
# xmax = 156.0
# ymin = -45.0
# ymax = -10.0
# zmin = 0.0
# zmax = 180.0
# 
# earth_radius = 6371.0

## body of code

# zmin = earth_radius - zmin
# zmax = earth_radius - zmax
## convert interface and vgrid in FMTOMO format to xyz or xyzv format
def fmtomo2xyz(infile="interfaces.in", vgfile="vgrids.in", vxyzfile="vgrids.xyzv",ixyzfile="interfaces.xyz",
               dxout = 1.0, dyout=1.0, dzout=5.0, xmin=110., xmax=156., ymin=-45., ymax=-10., zmin=0., zmax=180.,
               earth_radius = 6371.0):
    
    ofile = vxyzfile
    ifile = ixyzfile
    
    with open(infile, 'r') as fp:
        inflst = fp.readlines()
        
    ninf = int(inflst[0].strip())
    nlat = int(inflst[1].split()[0])
    nlon = int(inflst[1].split()[1])
    dlat = float(inflst[2].split()[0])*180.0/math.pi
    dlon = float(inflst[2].split()[1])*180.0/math.pi
    olat = float(inflst[3].split()[0])*180.0/math.pi
    olon = float(inflst[3].split()[1])*180.0/math.pi
    elat = olat + (nlat-1)*dlat
    elon = olon + (nlon-1)*dlon
    
    print ninf
    print nlat, nlon
    print dlat, dlon
    print olat, olon
    print elat, elon
    
    # arraging the interface
    ainf = []
    for i in range(4,len(inflst)):
        ainf.append(float(inflst[i].split()[0]))
        
    ainf = np.array(ainf).reshape(ninf, nlat, nlon)
    x = np.arange(olon, elon+dlon, dlon)
    y = np.arange(olat, elat+dlat, dlat)
    print len(x), len(y)
    
    # construct interpolation
    xi = np.arange(xmin, xmax+dxout, dxout)
    yi = np.arange(ymin, ymax+dxout, dyout)
    
    print 'ainf:', ainf.shape, ainf.size
    print ainf[:,0,0]
    
    # output interface
    test = ainf[1,:,:]
    interp2sp = interpolate.RectBivariateSpline(y, x, test, s=0)
    interp2ln = RegularGridInterpolator((y, x), test)
    
    fp = open(ifile, 'w')
    for xx in xi:
        for yy in yi:
            val  = interp2sp(yy,xx)
            valn = interp2ln((yy,xx))
            fp.write("%f\t%f\t%f\n" % (xx, yy, earth_radius - val))
    #         fp.write("%f\t%f\t%f\n" % (xx, yy, earth_radius - valn))
    fp.close()
    
#     os._exit(0)
    
    # velocity model
    with open(vgfile, 'r') as fp:
        inflst = fp.readlines()
        
    nv = int(inflst[0].split()[0].strip())
    nty= int(inflst[0].split()[1].strip())
    
    if ninf-nv!=1:
        print "ERROR: regions and interfaces of %s and %s are not consistent" % (infile, vgfile)
        os._exit(0)
        
    if nty!=1:
        print "ERROR: Treat one type of velocities currently. Exit."
        os._exit(0)
    
    ndep  = int(inflst[1].split()[0])
    nlatv = int(inflst[1].split()[1])
    nlonv = int(inflst[1].split()[2])
    
    if nlatv!=nlat or nlonv!=nlon:
        print "ERROR: sampling numbers of %s and %s are not consistent" % (infile, vgfile)
        os._exit(0)
    
    ddep  = float(inflst[2].split()[0])
    dlatv = float(inflst[2].split()[1])*180.0/math.pi
    dlonv = float(inflst[2].split()[2])*180.0/math.pi
    
    if abs(dlatv-dlat)>1e-3 or abs(dlonv-dlon)>1e-3:
        print "ERROR: sampling intervals of %s and %s are not consistent" % (infile, vgfile)
        os._exit(0)
    
    odep  = float(inflst[3].split()[0])
    olatv = float(inflst[3].split()[1])*180.0/math.pi
    olonv = float(inflst[3].split()[2])*180.0/math.pi
    
    if abs(olatv-olat)>1e-3 or abs(olonv-olon)>1e-3:
        print "ERROR: sampling numbers of %s and %s are not consistent" % (infile, vgfile)
        os._exit(0)
    
    edep  = odep + (ndep-1)*ddep
    elatv = olat + (nlat-1)*dlat
    elonv = olon + (nlon-1)*dlon
    
     
    print ninf, nv
    print nlat, nlon, ndep
    print dlatv, dlonv, ddep
    print olatv, olonv, odep
    print elatv, elonv, edep
    
    str1 = inflst[0]
    str2 = inflst[1]
    str3 = inflst[2]
    str4 = inflst[3]
    
    vglst = []
    for i in range(len(inflst)):
        line = inflst[i]
        if line not in [str1, str2, str3, str4]:
            vglst.append(float(inflst[i].split()[0]))
            
    avgi = np.array(vglst[0:nv*ndep*nlat*nlon]).reshape(nv,ndep, nlat, nlon)
    
    
    print "----"
    print (len(vglst))
    print avgi.shape
    print ainf.shape
    
#     x = np.arange(olon, elon+dlon, dlon)
#     y = np.arange(olat, elat+dlat, dlat)
#     z = np.arange(odep, edep+ddep, ddep)
    
    x = np.zeros(nlon)
    y = np.zeros(nlat)
    z = np.zeros(ndep)
    
    for i in range(nlon):
        x[i] = olon + i*dlon
    for i in range(nlat):
        y[i] = olat + i*dlat
    for i in range(ndep):
        z[i] = odep + i*ddep
    
    print "ppppppp"
    print len(x), len(y), len(z)
    print min(x), min(y), min(z)
    print max(x), max(y), max(z)
    print np.min(ainf), np.max(ainf)
    print np.min(avgi), np.max(avgi)
    
    # construct interpolation
    xi = np.arange(xmin, xmax+dxout, dxout)
    yi = np.arange(ymin, ymax+dyout, dyout)
    zi = earth_radius - np.arange(zmin, zmax+dzout, dzout)
    
    s = (ndep, nlat, nlon)
    av = np.zeros(s)
    
    # incorporate velocity grids
    for iiv in range(0,nv):
        iift = iiv
        iifb = iiv+1
        
        print "iiv=", iiv
        
        for ilat in range(0, nlat):
            for ilon in range(0, nlon):
    #     for ilat in range(0, 1):
    #         for ilon in range(0, 1):
                
                depth_inft = ainf[iift, ilat, ilon]
                depth_infb = ainf[iifb, ilat, ilon]
                
    #             print "depth:", iiv, depth_inft, depth_infb
                
                for idep in range(0, ndep):
                    dd = idep*ddep + odep
                    if dd <= depth_inft and dd >= depth_infb:
                        av[idep, ilat, ilon] = avgi[iiv, idep, ilat, ilon]
                        
                    if iiv==0 and dd >=depth_inft:
                        av[idep, ilat, ilon] = avgi[0, idep, ilat, ilon]
                        
                    if iiv==nv-1 and dd<=depth_infb:
                        av[idep, ilat, ilon] = avgi[nv-1, idep, ilat, ilon]
                        
    fp = open(ofile, 'w')
    
    # construct interpolator
    interp3d = RegularGridInterpolator((z, y, x), av)
    
    # for line in vglst:
    #     fp.write("%s\n" % line)
        
    
    # for ilon in range(0, nlon):
    #     lon = ilon*dlon + olon
    #     for ilat in range(0, nlat):
    #         lat = ilat*dlat + olat
    #         for idep in range(0, ndep):
    #             dep = idep*ddep + odep
    #             fp.write("%f\t%f\t%f\t%f\t%f\t%f\n" % (lon, lat, dep, avgi[0,idep, ilat, ilon],avgi[1,idep, ilat, ilon],av[idep, ilat, ilon]))
                
    for zz in zi:
        for xx in xi:
            for yy in yi:
                pt = np.array([[zz,yy,xx]])
                val= interp3d(pt)
                fp.write("%f\t%f\t%f\t%f\n" % (xx, yy, earth_radius-zz, val))
    
    fp.close()
                        
    
    print np.min(av), np.max(av)
                
## handle multi-velocity type in vgrids.in    
# x-longitude, y-latitude, z-depth
def fmtomo2xyzv(infile="interfaces.in", vgfile="vgrids.in", vxyzfile="vgrids.xyzv",ixyzfile="interfaces.xyz",
               dxout = 1.0, dyout=1.0, dzout=5.0, xmin=110., xmax=156., ymin=-45., ymax=-10., zmin=0., zmax=180.,
               earth_radius = 6371.0):

    # velocity model
    with open(vgfile, 'r') as fp:
        inflst = fp.readlines()
        
    nv = int(inflst[0].split()[0].strip())  # number of velocity region
    nty= int(inflst[0].split()[1].strip())  # number of velocity type, e.g., nty=1 for only P or S, nty=2 for P and S
    
    print "nv=",nv
    print "nty",nty
    print "length", len(inflst)
    
    ndep  = int(inflst[1].split()[0])
    nlatv = int(inflst[1].split()[1])
    nlonv = int(inflst[1].split()[2])
        
    if nty==1:
        fmtomo2xyz(infile, vgfile, vxyzfile, ixyzfile, dxout, dyout, dzout, xmin, xmax, ymin, ymax, zmin, zmax, earth_radius)
        
    elif nty==2: # separate vgfile into several vgrids.in.[?] and use fmtomo2xyz

        for i in range(nty):
            file2 = vxyzfile+"."+str(i+1)
#             file1 = vgfile+"."+str(i+1)
            print file2
            
            slino = i*(ndep*nlatv*nlonv+3)*nv+1
            elino = (i+1)*(ndep*nlatv*nlonv+3)*nv+1
            print "line no:", slino, elino
            
            newlst = inflst[slino:elino]
            
            fp = open("temp.in", "w")
            fp.write("\t%d\t%d\n"%(nv, 1))
            fp.writelines(newlst)
            fp.close()
            
            fmtomo2xyz(infile, "temp.in", file2, ixyzfile, dxout, dyout, dzout, xmin, xmax, ymin, ymax, zmin, zmax, earth_radius)
            
            os.system("rm temp.in")
            
#         mystr = "" 
#         for i in range(nty):
#             print (i+1)*4  
#             mystr += ",$"+str((i+1)*4)
#             
#         print mystr
        file1 = vxyzfile+"."+str(1)
        file2 = vxyzfile+"."+str(2)
        os.system("paste %s %s > junk" % (file1, file2))
        os.system("cat junk | awk '{print $1,$2,$3,$4,$8,$4/$8}' > %s" % (vxyzfile))
        os.system("rm junk %s %s" % (file1, file2))

    else:
        print "ERROR: type of velocities should equal 1 or 2. Exit."
        os._exit(0)
        
if __name__=='__main__':
    pass





















