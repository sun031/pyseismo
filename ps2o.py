#!/usr/bin/env python

import os

os.system("find . -name '*.ps' > psfile.txt")

with open("psfile.txt", "r") as fp:
    lst = fp.readlines()
    
for line in lst:
    row = line.split()
    fn, ext = os.path.splitext(row[0])
    
    print row[0]
    
    os.system("ps2pdf %s %s.pdf"%(row[0], fn))