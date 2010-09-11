# -*- coding: utf-8 -*-

"""
Technical main of all tasks to generate the DjVu and the Wiki templates for a single book.
"""
__authors__ =  'User:Seb35, User:Jean-Frédéric, User:Plyd for BNF partnership with Wikimedia France'
import os,sys,xml.dom.minidom, gzip, codecs, tarfile
from altoparser import generateFromAltoGz
from subprocess import check_call,Popen,PIPE
from coverparser import generateFromCover

# Create the ultimate Commons tar file
def serveCommonsFolder(djvuname, commonsDescFile, commonsFolder):
    """ Generates a tar file with the djvu file and the commons template, to be uploaded to commons. """
    tar = tarfile.open("%s/%star"%(commonsFolder,djvuname[:-4]),'w')
    tar.add(commonsDescFile)
    tar.add(djvuname)
    tar.close()
    #check_call( ['tar','-cf',"%s/%star"%(commonsFolder,djvuname[:-4]),commonsDescFile,djvuname], stdout=sys.stdout, stderr=sys.stderr )


#### CROP SIZING ####

def determineCropMaskGz(xmlAltoFilename):
    """ Wrapper for the gz extension """
    return determineCropMask(gzip.open(xmlAltoFilename))

def determineCropMask(xmlAltoFilename):
    """ Browse the blocks to search the dimensions of the cropping for this file """
    doc = xml.dom.minidom.parse(xmlAltoFilename)
    
    xmin = []
    ymin = []
    xmax = []
    ymax = []
    
    searchedTags = [ 'TextBlock', 'GraphicalElement', 'Illustration' ]
    tagList = []
    for tag in searchedTags:
        tagList += doc.getElementsByTagName(tag)
    
    for textBlock in tagList :
        xmin.append(int(textBlock.getAttribute('HPOS')))
        ymin.append(int(textBlock.getAttribute('VPOS')))
        xmax.append(int(textBlock.getAttribute('HPOS'))+int(textBlock.getAttribute('WIDTH')))
        ymax.append(int(textBlock.getAttribute('VPOS'))+int(textBlock.getAttribute('HEIGHT')))
    
    if len(xmin) == 0 | len(ymin) == 0 | len(xmax) == 0 | len(ymax) == 0 :
        return (400000,400000,0,0)
    
    thexmin = min(xmin)
    theymin = min(ymin)
    thexmax = max(xmax)
    theymax = max(ymax)
    return (thexmin,theymin,thexmax,theymax)


def bookProcess(folder, origfolder, commonsFolder, metadatabook):
    """ Process for the creation of a book """
    print u'* Creation the book %s'%folder
    
    # Metadata needed for the creation of the book
    shortname = metadatabook[0]
    djvuname = metadatabook[1]
    resolution = metadatabook[5]
    print u'* resolution=%s shortname=%s djvuname=%s'%(resolution,shortname,djvuname)
    
    # Save the title of the book for future use
    f = codecs.open('djvufilename.txt','w','utf-8')
    f.write(djvuname)
    f.close()
	
    xmin = 0
    xmax = 0
    ymin = 0
    ymax = 0
    isX = False
    
    
    ### Split tif images ###
    print u'* Split tif images'
    os.mkdir('images')
    os.chdir('images')
    if os.path.exists( "%sD%s.tif"%(origfolder,folder) ):
        check_call( ['tiffsplit', "%sD%s.tif"%(origfolder,folder), "img"], stdout=sys.stdout, stderr=sys.stderr )
        print u'* file with .tif'
    elif os.path.exists( "%sD%s.TIF"%(origfolder,folder) ):
        check_call( ['tiffsplit', "%sD%s.TIF"%(origfolder,folder), "img"], stdout=sys.stdout, stderr=sys.stderr )
        print u'* file with .TIF'
    else:
        print u'* no tif file'
        return
    
    # Rename tif images with integer instead of letters
    listtif = os.listdir( '.' )
    listtif.sort()
    imagecounter = 1
    
    for imagetif in listtif:
        os.rename(imagetif,"imgint%d.tif"%imagecounter)
        imagecounter+=1
    listimages = [ "images/imgint%d"%(i+1) for i in range(0,len(listtif))]
    os.chdir('..')
    
    
    ### Create the text files for the XML Alto
    ### and the command file to add these file into the DjVu
    ### and determine the cropping size
    if os.path.exists( origfolder+'X' ) :
        
        print u'* Search the cropping size'
        isX = True
        os.mkdir('wikisourcepages')
        
        # The command file used later
        cmdAddTxt = codecs.open( 'add_txt', 'w', 'utf-8' )
        listxmlgz = os.listdir( origfolder+'X' )
        listxmlgz.sort()
        
        
        ### Size of the crop of each page ###
        cropMasks= []
        for filexmlgz in listxmlgz :
            filebase = filexmlgz[:-7]
            print filexmlgz
            cropMasks.append(determineCropMaskGz(origfolder+'X/'+filexmlgz))
        
        # Read the size of a image
        doc = xml.dom.minidom.parse(gzip.open(origfolder+'X/'+listxmlgz[0]))
        pg = doc.getElementsByTagName('Page')
        altoHeight = int(pg.item(0).getAttribute('HEIGHT'))
        altoWidth  = int(pg.item(0).getAttribute('WIDTH'))
        
        # Déterminer le crop mask optimal - we crop the files later
        xmin = max(min([xmini for (xmini,b,c,d) in cropMasks])-60,0)
        ymin = max(min([ymini for (a,ymini,c,d) in cropMasks])-60,0)
        xmax = min(max([xmaxi for (a,b,xmaxi,d) in cropMasks])+60,altoWidth)
        ymax = min(max([ymaxi for (a,b,c,ymaxi) in cropMasks])+60,altoHeight)
        print u'* Cropping size: xmin=%d ymin=%d xmax=%d ymax=%d'%(xmin,ymin,xmax,ymax)
        
        
        ### Generate the text layers ###
        print u'* Creation of the text layers'
        for filexmlgz in listxmlgz :
            filebase = filexmlgz[:-7]
            print filexmlgz
            generateFromAltoGz( cmdAddTxt, filebase, origfolder+'X/'+filexmlgz, 'wikisourcepages/'+filebase+'.ws.txt', filebase+'.djvu.txt', xmin, ymin, xmax-xmin, ymax-ymin )
        
        print u'* End of the creation of the text files'
    
    
    ### Create the .ppm images then the .djvu files ###
    
    # Convert the images into .ppm
    # On my computer (Seb) if I convert all images in once time IM loads all images in memory (3,6Go) then uses the swap... bad!
    # Very better to use the batch feature of IM: gain of about 50 seconds on a 500-page-book (~2'10'' instead of 3')
    if isX:
        
        # Cropping
        width = xmax-xmin
        height = ymax-ymin
        cropCmd = "%dx%d+%d+%d"%(width,height,xmin,ymin)
        
        # Add watermarking to the first page
        print u'* Add watermarking to the first page'
        check_call( ['convert', '-crop', cropCmd, '+repage', "images/imgint1.tif", '-pointsize', '20', '-gravity', 'South', '-annotate', '+0+30', u"Source : Gallica - Bibliothèque nationale de France", "imgint1.tif"], stdout=sys.stdout, stderr=sys.stderr )
        #(ter)check_call( ['convert', "imgint1.tif", "imgint1.ppm"], stdout=sys.stdout, stderr=sys.stderr )
        
        # Start with 1 for the rest of the pages
        print u'* Conversion of the png - Cropping'
        for i in range( 1, len(listimages), 10 ) :
            check_call( ['convert', '-scene', str(i+1), '-crop', cropCmd, "images/imgint%%d.tif[%d-%d]"%(i+1,min([i+10,len(listimages)])), "imgint%d.tif"], stdout=sys.stdout, stderr=sys.stderr )
        
    else:
        
        # Trimming
        
        # Add watermarking to the first page
        print u'* Add watermarking to the first page'
        check_call( ['convert', '-trim', '+repage', "images/imgint1.tif", '-pointsize', '20', '-gravity', 'South', '-annotate', '+0+30', u"Source : Gallica - Bibliothèque nationale de France", "imgint1.tif"], stdout=sys.stdout, stderr=sys.stderr )
        #(ter)check_call( ['convert', "imgint1.tif", "imgint1.ppm"], stdout=sys.stdout, stderr=sys.stderr )
        
        # Start with 1 for the rest of the pages
        print u'* Conversion of the png - Trimming'
        for i in range( 1, len(listimages), 15 ) :
            check_call( ['convert', '-scene', str(i+1), '-trim', "images/imgint%%d.tif[%d-%d]"%(i+1,min([i+15,len(listimages)])), "imgint%d.tif"], stdout=sys.stdout, stderr=sys.stderr )
        
        ## Search the larger and widther sizes
        print u'* Search the larger and widther sizes'
        width = 0
        height = 0
        for i in range( 0, len(listimages) ) :
            sizes = Popen( ['identify', '-format', '%w %h', 'imgint%d.tif'%(i+1)], stdout=PIPE ).communicate()[0].split()
            if int(sizes[0]) > width  : width  = int(sizes[0])
            if int(sizes[1]) > height : height = int(sizes[1])
        print '  %dx%d'%(width,height)
        
        # Resize all images of the book to an identical size
        print u'* Resize the images'
        trimCmd = "%dx%d"%(width,height)
        for i in range( 0, len(listimages), 15 ) :
            check_call( ['convert', '-scene', str(i+1), '-extent', trimCmd, '-gravity', 'Center', 'imgint%%d.tif[%d-%d]'%(i+1,min(i+15,len(listimages))), 'imgint%d.tif'], stdout=sys.stdout, stderr=sys.stderr )
    
    
    # Create the single-page DjVuS
    print u'* Creation of the single-page DjVuS'
    listdjvu = [ 'djvm', '-c', folder+'.djvu' ]
    for fileppm in listimages :
        djvufilename =  shortname + str(int(fileppm[len('images/imgint'):])) + '.djvu' 
        listdjvu.append(djvufilename)
        check_call( ['cjb2', '-dpi', resolution, fileppm[len('images/'):]+'.tif', djvufilename], stdout=sys.stdout, stderr=sys.stderr )
    
    # Create the multi-page DjVu
    print u'* Creation of the multi-page DjVu '
    check_call( listdjvu, stdout=sys.stdout, stderr=sys.stderr )
    
    # Add the text layer
    if isX :
        print u'* Add the text layer'
        #print os.getcwd()
        check_call( ['djvused', '-s', '-f', 'add_txt', folder+'.djvu'], stdout=sys.stdout, stderr=sys.stderr )
    
    # Rename the djvu with the final name
    os.rename( folder+'.djvu', djvuname)
    
    # Names of the metadata files
    commonsDescFile = djvuname[:-4]+"txt"
    wikisourceCoverFile = "cover.wikisource.txt"
    
    # Generate templates for commons description and wikisource cover page
    generateFromCover(origfolder+"X"+folder+".XML", metadatabook, wikisourceCoverFile, commonsDescFile)
    
    # Create the tar for commons
    serveCommonsFolder(djvuname, commonsDescFile, commonsFolder)
    
    # set status to "success" for the wiki bot
    f = open('generation.status.txt','w')
    f.write("success")
    f.close()
    
    # Finished for this book
    print u'* '+djvuname+' finished'
    
