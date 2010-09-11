# -*- coding: utf-8 -*-
"""
Reads the alto XML page and extracts the Illustration objects from the TIFF files.
"""
__authors__ =  'User:Seb35, User:Jean-Frédéric, User:Plyd for BNF partnership with Wikimedia France'

import xml.dom.minidom, gzip, shutil, os, sys,codecs,locale,re
from subprocess import check_call
from os.path import basename

# Save standard output and error (they will be replaced by log files for each book)
stdoutBak = sys.stdout
stderrBak = sys.stderr

bookFolder = u'/home/projetbnf/bouquins'
exeFolder     = os.getcwd()
#bookFolder    = u'./Bouquins'
workingFolder = exeFolder+'/work/'
outputFolder  = exeFolder+"/output/"
  
def bookProcessor(bookId):
  """Processes one book based on its id."""
  if bookId not in metadata.keys() :
    print u"Unable to do the book %s! no metadata"%folder 
    return
  metadatabook = metadata[bookId]
  bookName = re.sub(r' ','_',metadatabook[1][:-5])
  folderCreated=False
  print "Processing book %s - %s"%(bookId,bookName)
  manageTiff(bookFolder,bookId,workingFolder)
  generationFolder=outputFolder+bookId
  
  #Iteration over the pages
  xmlPagesPath='%s/%s/X'%(bookFolder,bookId)
  if(not os.path.exists(xmlPagesPath)):
    print "No XML ALTO file"
    return  0
  xmlPagesList = os.listdir(xmlPagesPath)
  xmlPagesList.sort()
  imageCounterOfBook=0
  for xmlPage in xmlPagesList:
    pageNumber=int(os.path.splitext(os.path.splitext(basename(xmlPage))[0])[0][1:])

    #Reading the XML
    doc = xml.dom.minidom.parse(gzip.open(xmlPagesPath+'/'+xmlPage))
    imageCounterOfPage=0
    if doc.getElementsByTagName('Illustration').length > 0:
      if(not folderCreated):
	if(os.path.exists(generationFolder)):
	  shutil.rmtree(generationFolder)
	os.mkdir(generationFolder)
	folderCreated=True
      imageBasename=u'%s_-_%s'%(bookName,pageNumber)
      illustrations = doc.getElementsByTagName('Illustration')
      moreThanOnePage=(illustrations.length > 1)
      for nodeIndex in range(0,illustrations.length):
	illustration = illustrations.item(nodeIndex)
	HPOS = illustration.getAttribute('HPOS')
	VPOS = illustration.getAttribute('VPOS')
	HEIGHT = illustration.getAttribute('HEIGHT')
	WIDTH = illustration.getAttribute('WIDTH')
	TYPE = illustration.getAttribute('TYPE')
	if(not moreThanOnePage):
	  imageName=imageBasename+'.tif'
	else:
	  #If there is more than one image per page, the naming convention is "bookname - page - 
	  imageName=imageBasename+str(letters[1+imageCounterOfPage])+'.tif'
	  
	extractImage(workingFolder,pageNumber,HPOS,VPOS,HEIGHT,WIDTH,generationFolder,imageName)
	imageCounterOfPage+=1
      imageCounterOfBook+=imageCounterOfPage
  return imageCounterOfBook

def manageTiff(inputFolder,bookId,outputFolder):
  """Processes the TIFF file: take it from the inputFolder based on its bookId, splits it and renames the resulting files."""
  tifPath1 = "%s/%s/D%s.tif"%(inputFolder,bookId,bookId)
  tifPath2 = "%s/%s/D%s.TIF"%(inputFolder,bookId,bookId)
  
  if os.path.exists(tifPath1):
    tifPath=tifPath1
  elif os.path.exists(tifPath2):
    tifPath=tifPath2
  else:
      print u'* no tif file'
      return
      
  newTiff="%s.tif"%(bookId)
  shutil.copyfile(tifPath, "%s/%s"%(workingFolder,newTiff))
  os.chdir(workingFolder)
  check_call( ['tiffsplit', newTiff, "img"], stdout=sys.stdout, stderr=sys.stderr )
  os.remove(newTiff)
  
  #Rename tif images with integer instead of letters
  listtif = os.listdir( '.' )
  listtif.sort()
  imagecounter = 1
  for imagetif in listtif:
      os.rename(imagetif,"%d.tif"%imagecounter)
      imagecounter+=1
  os.chdir(exeFolder)

def extractImage(tiffsFolder,pageNumber,HPOS,VPOS,HEIGHT,WIDTH,outputFolder,imageName):
  """Extracts an image from a TIFF file, using the given coordinates, and puts it in the given folder under the given name."""
  print "Extracting image %s from page %s in %s into %s)"%(imageName,pageNumber,tiffsFolder,outputFolder)
  cropCmd= WIDTH+'x'+HEIGHT+'+'+HPOS+'+'+VPOS
  #completeCmd= u'convert %s %s%s.tif %s/%s'%(cropCmd,tiffsFolder,str(pageNumber),outputFolder,imageName)
  #print u"Commande : %s"%(completeCmd)
  check_call( ['convert','-crop',cropCmd,'+repage','%s%s.tif'%(tiffsFolder,str(pageNumber)),'%s/%s'%(outputFolder,imageName)], stdout=sys.stdout,stderr=sys.stderr)

def main():
    if os.path.exists(workingFolder):
      shutil.rmtree(workingFolder)
    os.mkdir(workingFolder)
    
    global metadata
    metadata = getMetadata()
    imageCounter=0
    
    # Sets output in log files of the book
    logoutfile = codecs.open( u'log.out.txt', 'w', 'utf-8' )
    logerrfile = codecs.open( u'log.err.txt', 'w', 'utf-8' )
    sys.stdout = logoutfile
    sys.stderr = logerrfile
    
    if len(sys.argv) > 1:
        bookProcessor(sys.argv[1])
    else:
        #toreadfile = codecs.open( u'toRead.txt', 'r', 'utf-8' )
        #toread = [ word[:-1] for word in toreadfile.readlines() ]
        #toreadfile.close()
        for bookId in metadata.keys():
	  if os.path.exists(workingFolder):
	    shutil.rmtree(workingFolder)
	  os.mkdir(workingFolder)
	  #print bookId
	  imageCounter=imageCounter+bookProcessor(bookId)

	print "Done. %s images extracted"%(imageCounter)
	
    logoutfile.close()
    logerrfile.close()
    sys.stdout = stdoutBak
    sys.stderr = stderrBak

letters = {1:'a',2:'b',3:'c',4:'d',5:'e',6:'f',7:'g',8:'h',9:'i',10:'j',11:'k',12:'l',13:'m',14:'n',15:'o',16:'p',17:'q',18:'r',19:'s',20:'t',21:'u',22:'v',23:'w',24:'x',25:'y',26:'z' }

# format :
# ordre|titrecourt|titredjvu|ark|auteur|titre|resolution|pagelist|bonsauteurs
def getMetadata():
  """Retrieves the metadata from the text file"""
    metadatafile = codecs.open( 'metadatabooks.txt', 'r', 'utf-8' )
    metadatalist = [ line[:-1].split('|') for line in metadatafile.readlines() ]
    metadatafile.close()
    metadata = {}
    for book in metadatalist :
        metadata[book[0]] = book[1:]
    return metadata

if __name__ == "__main__":
    main()

