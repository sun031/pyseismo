## \package A simple GMT wrapper
#  

import os
import commands

## Class Gmt
# 
class Gmt:
    
    ## initial constructor
    def __init__(self, scr='./rungmt.sh'):
        """
        initial constructor
        """

        self.scr = scr
        fp = open(self.scr,'w')
        fp.write('#!/bin/sh\n\n')
        fp.close()
        self.set('FONT_ANNOT_PRIMARY','10p,Helvetica,black')
        self.set('FONT_ANNOT_SECONDARY', '10p,Helvetica,black')
        self.set('FONT_LABEL', '10p,Helvetica,black')
        self.set('FONT_LOGO', '10p,Helvetica,black')
        self.set('FONT_TITLE', '10p,Helvetica,black')
    
    def set(self, arg, val):
        """
        set gmtdefaults
        """
        fp = open(self.scr, 'a')
        fp.write('gmtset '+arg+'='+val+'\n')
        fp.close()
        
    def cmd(self, cmd, arg):
        """
        gmt commands
        """
        arg = arg.replace('\n', ' \ \n\t')
        fp = open(self.scr, 'a')
        fp.write('gmt '+cmd+' '+arg+'\n')
        fp.close()

    def execute(self):
        """
        execute the generated shell script
        """
        out = commands.getoutput("sh "+self.scr)
        if out.strip()!="":
            print out
    
    def comment(self,str):
        """
        comment here in the script
        """
        fp = open(self.scr, 'a')
        fp.write('\n# '+str+'\n')
        fp.close()

    def shell(self, cmd):
        """
        shell command, e.g, "cat file.xy | awk '{print $1, $2}' "
        """
        cmd = cmd.replace('\n', ' \ \n\t')
        fp = open(self.scr, 'a')
        fp.write(cmd+'\n')
        fp.close()        

    def saveas(self, newfilename):
        """
        save 'rungmt.sh' as ...
        """
        os.system("cp %s %s" % (self.scr, newfilename) )
