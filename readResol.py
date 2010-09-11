# -*- coding: utf-8 -*-
"""
Reads refnum XML page to know resolution in dpi of the scanned book (tiff files).
It generates a resolution.txt file that is used for the metadata file.

(refnum is a BNF specific file format for book description).
"""
__author__ =  'User:Seb35 for BNF partnership with Wikimedia France'
resolfile = open('/home/projetbnf/log/resolution.txt','w')

import os, re

listfolder = os.listdir( '/home/projetbnf/bouquins' )

for folder in listfolder :
    
    xfile = open( '/home/projetbnf/bouquins/'+folder+'/X'+folder+'.XML', 'r' )
    m = re.search('resolution="(\d*),', ' '.join(xfile.readlines()))
    #print xfile.readlines()
    #print m
    if m != None :
       resol = m.group(1)
       print resol
       resolfile.write( folder+' '+resol+'\n' )
    xfile.close()

