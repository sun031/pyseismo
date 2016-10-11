#!/usr/bin/env python


import numpy as np
import os
from operator import itemgetter


def foldaz(oatfile, range="0/180/-90/90", binsize=0.5, fast=False):
    """
    :param oatfile:
    :param range: "lonmin/lonmax/latmin/latmax"
    :param binsize: size of bin in degree unit
    :param fast: if True, then calculate the (lat1+lat2)/2 and (lon1+lon2)/2;
                 if False, the midpoint along great circle path
    :return:
    """

    # infile = '../oat/au_tomo_p_dist.oat'
    # ofile  = 'foldaz_tomo_p_dist'+str(d)+'.xyzal'

    d = float(binsize)

    infile = oatfile
    ofile = os.path.splitext(infile)[0]+"_"+str(d)+".xyzal"

    # range
    tt = range.split("/")


    lonmin = float(tt[0])
    lonmax = float(tt[1])
    latmin = float(tt[2])
    latmax = float(tt[3])
    dlat = float(d)
    dlon = float(d)

    nlat = int(round((latmax-latmin)/dlat))
    nlon = int(round((lonmax-lonmin)/dlon))

    fold = np.zeros((nlat, nlon))

    print nlat, nlon

    fp = open(infile, 'r')
    lst = fp.readlines()
    fp.close()

    fp = open(ofile, 'w')

    azlst = []

    # print len(lst)

    # for i in range(len(lst)):
    for line in lst:
    #     print i, len(lst)

        # line = lst[i]
        row = line.split()

        gcarc = float(row[13])   # in degree
        baz = float(row[15])

        g = gcarc*0.5 #    midpoint

        evla = float(row[2])
        evlo = float(row[3])
        stla = float(row[9])
        stlo = float(row[10])

        if not fast:

            cmd = "gmt project -C%f/%f -E%f/%f -G%f > junk" % (evlo, evla, stlo, stla, g)
            os.system(cmd)

            fptemp = open('junk', 'r')
            lsttemp = fptemp.readlines()
            fptemp.close()
            aa = lsttemp[1].split()

            x = float(aa[0])
            y = float(aa[1])
            z = 0
            a = baz
            l = gcarc
        else:
            x = (evlo+stlo)*0.5
            y = (evla+stla)*0.5
            z = 0
            a = baz
            l = gcarc

    #     fp.write("%f\t%f\t%f\t%f\t%f\n" % (x, y, z, a, l))
        azlst.append([x, y, z, a, l])

        x -= lonmin
        y -= latmin
        ilon = int((x/dlon))
        ilat = int((y/dlat))

        fold[ilat, ilon] += 1

    azlst.sort(cmp=None, key=itemgetter(0,1), reverse=False)

    print "number of bin ", len(azlst)

    foldmin = 100000.0
    foldmax = 0.0

    # for i in range(len(azlst)):
    for line in azlst:

        # row = azlst[i]
        row = line
        x = row[0] - lonmin
        y = row[1] - latmin
        a = row[3]
        l = row[4]
        ilon = int((x/dlon))
        ilat = int((y/dlat))
        lat = (ilat+0.5)*dlat + latmin
        lon = (ilon+0.5)*dlon + lonmin
        fp.write("%f\t%f\t%f\t%f\t%f\n" % (lon, lat, fold[ilat, ilon], a, l))

        if fold[ilat, ilon]>foldmax:
            foldmax = fold[ilat, ilon]
        elif fold[ilat, ilon]<foldmin:
            foldmin = fold[ilat, ilon]

    print 'minimum fold is ', foldmin
    print 'maximum fold is ', foldmax

    # for ilat in range(nlat):
    #     for ilon in range(nlon):
    #         lat = (ilat+0.5)*dlat + latmin
    #         lon = (ilon+0.5)*dlon + lonmin
    #         fp2.write("%f\t%f\t%f\n" % (lon, lat, fold[ilat, ilon]))


    fp.close()

    pass

if __name__=="__main__":
    foldaz(oatfile="crude_p.oat", range="112/123/26/36", binsize=0.5, fast=True)
    foldaz(oatfile="crude_s.oat", range="112/123/26/36", binsize=0.5, fast=True)

    foldaz(oatfile="crude_p.oat", range="112/123/26/36", binsize=0.25, fast=True)
    foldaz(oatfile="crude_s.oat", range="112/123/26/36", binsize=0.25, fast=True)

    foldaz(oatfile="crude_p.oat", range="112/123/26/36", binsize=1.0, fast=True)
    foldaz(oatfile="crude_s.oat", range="112/123/26/36", binsize=1.0, fast=True)

    foldaz(oatfile="crude_p.oat", range="112/123/26/36", binsize=0.75, fast=True)
    foldaz(oatfile="crude_s.oat", range="112/123/26/36", binsize=0.75, fast=True)