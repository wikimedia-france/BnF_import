# -*- coding: utf-8 -*-
"""
Reads the alto XML page and generates two files, one at the DjVu format (with parenthesis), one at WikiSource format.
It also read position of the text blocks and sets it in the DjVu file.
"""
__authors__ =  'User:Seb35, User:Jean-Frédéric, User:Plyd for BNF partnership with Wikimedia France'
import xml.dom.minidom, gzip, codecs, re

def generateFromAltoGz(cmdAddTxt,filebase,xmlAltoFilename,wikisourceFilename,djvuTextFilename,xminPage,yminPage,tailleX,tailleY):
    generateFromAlto(cmdAddTxt,filebase,gzip.open(xmlAltoFilename,'r'),wikisourceFilename,djvuTextFilename,xminPage,yminPage,tailleX,tailleY)

def generateFromAlto(cmdAddTxt,filebase,xmlAltoFilename,wikisourceFilename,djvuTextFilename,xminPage,yminPage,tailleX,tailleY):
    
    altoFileiso88591 = codecs.EncodedFile( xmlAltoFilename, 'iso8859-1' ) #this works!
    #altoiso88591 = '\n'.join(xmlAltoFilename.readlines()).decode('iso8859-1')
    #print type(altoiso88591)
    #print type('\n'.join(xmlAltoFilename.readlines()))
    
    #for i in range(0,40):
    #    print altoutf8.readline()
    #print altoiso88591.encode('utf-8')
    
    doc = xml.dom.minidom.parse(altoFileiso88591)
    #doc = xml.dom.minidom.parse(xmlAltoFilename)
    #doc = xml.dom.minidom.parseString(altoiso88591)
    #doc = xml.dom.minidom.parseString(altoiso88591.encode('utf-8'))
    pg = doc.getElementsByTagName('Page')
    altoHeight = int(pg.item(0).getAttribute('HEIGHT'))
    altoWidth  = int(pg.item(0).getAttribute('WIDTH'))
    
    wikisource = codecs.open(wikisourceFilename,'w','utf-8')
    djvuText = codecs.open(djvuTextFilename,'w','utf-8')
    #wikisource = sys.stdout
    #djvuText = sys.stdout
    
    djvuText.write('(page 0 0 '+str(int(tailleX))+' '+str(int(tailleY)))
    
    empty = True
    for alto in doc.childNodes:
        if alto.localName == 'alto':
            for layout in alto.childNodes:
                if layout.localName == 'Layout':
                    for textblock in layout.childNodes:
                        if textblock.localName == 'Page':
                            for page in textblock.childNodes:
                                if page.localName == 'TopMargin':
                                    wikisource.write("""<noinclude><div class="pagetext">""")
                                    for tb in page.childNodes:
                                        if tb.localName == 'TextBlock':
                                            parseTextBlock(tb,wikisource,djvuText,xminPage,yminPage,tailleY)
                                            empty = False
                                    wikisource.write(chr(10))
                                    wikisource.write("""</noinclude>""")
                                else: # (si bottomMargin) if page.localName == 'PrintSpace':
                                    for tb in page.childNodes:
                                        if tb.localName == 'TextBlock':
                                            parseTextBlock(tb,wikisource,djvuText,xminPage,yminPage,tailleY)
                                            empty = False
    
    if empty:
        djvuText.write(' ""')
    djvuText.write(')') #close page
    
    if not empty:
        cmdAddTxt.write( 'select %d; set-txt %s.djvu.txt\n'%(int(filebase[2:]),filebase) )

def parseTextBlock(textblock,wikisource,djvuText,xminPage,yminPage,tailleY):
    
    para = u'\n   (para '+changeCoords(textblock,xminPage,yminPage,tailleY)
    emptypara = True
    
    i = 0
    nbchildren = len(textblock.getElementsByTagName('String'))
    for textblocktag in textblock.childNodes:
        if textblocktag.localName == 'TextLine':
            closedword = True
            emptyLine = True
            para = para + u'\n    (line '+changeCoords(textblocktag,xminPage,yminPage,tailleY)
            for textline in textblocktag.childNodes:
                if textline.localName == 'String':
                    emptypara = False
                    i = i+1
                    if not closedword:
                        para = para + u'")'
                        closedword = True
                    if textline.getAttribute('SUBS_TYPE') == 'HypPart1':
                        attrContent = textline.getAttribute("SUBS_CONTENT").replace("'",u'’')
                        wikisource.write(attrContent)
                        para = para + u'\n     (word '+changeCoords(textline,xminPage,yminPage,tailleY)+' "'
                        closedword = False
                        emptyLine = False
                        attrContent = attrContent.replace('\\','\\\\')
                        attrContent = attrContent.replace('"','\\"')
                        para = para + unicode(attrContent)
                        if i<nbchildren:
                            wikisource.write(' ')
                    elif textline.getAttribute('SUBS_TYPE') == 'HypPart2':
                        pass
                    else:
                        attrContent = textline.getAttribute("CONTENT").replace("'",u'’')
                        wikisource.write(attrContent)
                        para = para + u'\n     (word '+changeCoords(textline,xminPage,yminPage,tailleY)+' "'
                        closedword = False
                        emptyLine = False
                        attrContent = attrContent.replace('\\','\\\\')
                        attrContent = attrContent.replace('"','\\"')
                        para = para + unicode(attrContent)
                        if i<nbchildren:
                            wikisource.write(' ')
                elif textline.localName == 'SP':
                    para = para + u' '
            if not closedword:
                para = para + u'")' #close word
            if emptyLine:
                para = para + u' ""'
            para = para + u')' #close line
    para = para + u')' #close paragraph
    wikisource.write(chr(10))
    wikisource.write(chr(10))
    
    if emptypara == False:
        djvuText.write(para)


#  Change of the coordinates Alto -> DjVU
#                                         
#          xminPage  WIDTH                
#             <-->  <--->                 
#              HPOS                       
#             <---->                      
# -   -  -    +-----------------          
# |   |  |    |                |          
# | - |  -    |   ---------    |          
# | | |  y    |   |       |    |          
# | | -  m -  |   | ***** |    |  -    -  
# | | V  i |  |   | ***** |    |  |    |  
# | | P  n -  |   | ***** |    |  | -  |  
# | | O  P H  |   |       |    |  | |  |  
# | | S  a E  |   |       |    |  | |  |  
# | |    g I  |   |       |    |  | |  |  
# | -    e G  |   @--------    |  - -  | -
# | t      H  |                |  y y  | |
# | a      T  |                |  m m  | |
# - i         ------------------  a i  - -
# y l             <>              x n  1 2
# m l             xminNode        N N  s n
# a e             <----->         o o  t d
# x Y             xmaxNode        d d  ( (
# P                               e e  ) )
# a           
# g           xminNode = HPOS-xminPage
# e           xmaxNode = xminNode + WIDTH
#             ymaxNode = (ymaxPage-VPOS) - (ymaxPage-tailleY-yminPage) = tailleY+yminPage-VPOS
#             yminNode = ymaxNode - HEIGHT
# 
# + : ref Alto
# @ : ref DjVu
# 
def changeCoords(node,xminPage,yminPage,tailleY):
    """ Change referentiel from top-left to bottom-left """
    xminNode = int(node.getAttribute("HPOS")) - xminPage
    xmaxNode = xminNode + int(node.getAttribute("WIDTH"))
    ymaxNode = tailleY + yminPage - int(node.getAttribute("VPOS"))
    yminNode = ymaxNode - int(node.getAttribute("HEIGHT"))
    return '%d %d %d %d'%(int(xminNode),int(yminNode),int(xmaxNode),int(ymaxNode))

def main():
    # Test main
    xmlAltoFilename = "0001222/X/X0000213.XML";
    wikisourceFilename = "X0000213.wikisource.txt";
    djvuTextFilename = "X0000213.djvu.txt";
    generateFromAlto(xmlAltoFilename,wikisourceFilename,djvuTextFilename)

if __name__ == "__main__":
    main()
