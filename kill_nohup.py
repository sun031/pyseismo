#!/usr/bin/env python

import commands
import os
from time import sleep

pidname = "fm3d"
usrname = "weijias"


while True:
    lst = commands.getoutput("ps aux | grep %s" % (pidname))    
    row = lst.split()
    
    for i in range(len(row)):
        if row[i]==usrname:
            try:
                pid = int(row[i+1])
                print pid
                os.system("kill -9 %d" % pid)
            except:
                pass
    
    sleep(3)        
    
    
