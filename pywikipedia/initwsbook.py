# -*- coding: utf-8 -*-
import wikipedia,os,codecs,re

""" Init the pywikipedia bot, to initiate the index pages of Wikisource books and the pages pages. """
__authors__ =  'User:Seb35, User:Plyd for BNF partnership with Wikimedia France'
#
# Parameters
#

# Folder containing the books
workfolder = u"/home/projetbnf/out.ter.cjb2/ok"

# File containing the ID of the books to process
dobookname = u"/home/projetbnf/prog.ter/bnfbotwsbooks.txt"

# Log file
logname = u"/home/projetbnf/prog.ter/bnfbotwsbookslog.txt"

# Init Wikisource cover ?
initWSCover = False
commentWSCover = u"Robot : initialisation de l’index"

# Init Wikisource pages ?
initWSPages = True
commentWSPages = u"Robot : initialisation de la page à partir de l’OCR BnF"


#
# Code
#
# TODO: mettre en pause, ou reprendre au bon endroit si ça a planté

booklist = os.listdir( workfolder )
booklist.sort()

dobookfile = codecs.open( dobookname, 'r', 'utf-8' )
dobooklist = [ word[:-1] for word in dobookfile.readlines() ]

logfile = codecs.open( logname, 'w', 'utf-8' )

site = wikipedia.getSite()

for book in booklist:
    
    bookfolder = workfolder+'/'+book
    logfile.write( u'** book '+book+' ** ' )
    if not os.path.isdir(bookfolder) or book not in dobooklist:
        logfile.write( u'skiped\n' )
        continue
    
    # Checks if the book was fully and correctly generated
    os.chdir(bookfolder)
    retry = False
    try:
        f = codecs.open( 'generation.status.txt', 'r', 'utf-8' )
        goon = (f.read().strip() == "success")
        f.close()
        if not goon: print "Erreur %s" % book
    except:
        os.chdir("retry")
        f = codecs.open( 'generation.status.txt', 'r', 'utf-8' )
        goon = (f.read().strip() == "success")
        f.close()
        if not goon: print "Erreur %s" % book
    
    # Get DjVu filename
    f = codecs.open( 'djvufilename.txt', 'r', 'utf-8' )
    djvuname = f.read().strip()
    f.close()
    print book
    
    # Init the Wikisource cover
    if initWSCover:
        coverPageName = u"Livre:%s" % djvuname
        f = codecs.open( 'cover.wikisource.txt', 'r', 'utf-8' )
        coverContent = f.read()
        coverPageName = re.sub( r' +', ' ', coverPageName )
        f.close()
        
        coverpage = wikipedia.Page( site, coverPageName )
        if not coverpage.exists():
            coverpage.put( coverContent, comment = commentWSCove )
            logfile.write( u'cover initialized\n' )
        else:
            logfile.write( u'cover already exists\n' )
    
    # Init the Wikisource pages
    if initWSPages:
        
        # Get Wikisource folder
        wikisourcepagesFolder = u"%s/wikisourcepages" % bookfolder
        filelist = os.listdir( wikisourcepagesFolder )
        filelist.sort()
        
        for wikisourceFile in filelist:
            pageNumber = int(wikisourceFile[1:8])
            pageContent = codecs.open(wikisourcepagesFolder+'/'+wikisourceFile, 'r', 'utf-8' ).read()
            if pageContent[0:11] == u'<noinclude>':
                pageContent = '<noinclude><pagequality level="1" user="BnFBoT" />' + pageContent[11:] + u'<noinclude>\n<references/></div></noinclude>'
            pageName = "Page:%s/%d" % (djvuname,pageNumber)
            
            page = wikipedia.Page( site, pageName )
            if not page.exists():
                page.put( pageContent, comment = commentWSPages )
                logfile.write( u'page %s initialized\n' % pageName )
            else:
                logfile.write( u'page %s already exists\n' % pageName )
    
    logfile.write( u'\n' )
    

