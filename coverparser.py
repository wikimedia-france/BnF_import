# -*- coding: utf-8 -*-
"""
Creates the template page for Wikimedia Commons DjVu file (writes it to descriptionFileCommons).
Creates the template for the index page of the book (writes it to coverFileWikisource).

Takes into account the metadata file (metadatabook) and the xmlCoverFile from Alto.

"""
__authors__ =  'User:Seb35, User:Jean-Frédéric, User:Plyd for BNF partnership with Wikimedia France'

import xml.dom.minidom, codecs

# Create the covers for Wikisource and Wikimedia Commons
def generateFromCover(xmlCoverFile,metadatabook,coverFileWikisource,descriptionFileCommons):
    
    print u"* cover generated for wikisource"
    
    doc = xml.dom.minidom.parse(xmlCoverFile)
    editeur=u""
    djvuname = metadatabook[1]
    if doc.getElementsByTagName('genre').length > 0:
        genre = doc.getElementsByTagName('genre').item(0).firstChild.data#.encode('utf-8')
    titre = metadatabook[3]
    auteur = metadatabook[4]
    ark = metadatabook[2]
    pagelist = metadatabook[6]
    if doc.getElementsByTagName('dateEdition').length > 0:    
        dateEdition = doc.getElementsByTagName('dateEdition').item(0).firstChild.data#.encode('utf-8')
        annee = dateEdition[:4]
    else:
        dateEdition = u""
        annee = u""
    if doc.getElementsByTagName('nombrePages').length > 0:
        nombrePages = doc.getElementsByTagName('nombrePages').item(0).firstChild.data#.encode('utf-8')
    else:
        nombrePages = u""
    if doc.getElementsByTagName('editeur').length > 0:
    	editeur = editeur+doc.getElementsByTagName('editeur').item(0).firstChild.data#.encode('utf-8')
    else:
        editeur = u""

    auteurs=metadatabook[7]
    
    creators=u""
    wikisourceAuteurs=u""
    commonsCat=u""
    if auteur==u"Collectif":
        creators=u"{{Collective}}"
        wikisourceAuteurs=u"Collectif"
        commonsCat=u"[[Category:Collective books]]"
    elif auteurs==u"Anonyme":
        creators=u"{{Anonymous}}"
        wikisourceAuteurs=u"Anonyme"
        commonsCat=u"[[Category:Anonymous books]]"
    else:
        listAuthor=auteurs.split(';');
        creators = u'\n'.join( [ u"""{{Creator:%s}}"""%(author)  for author in listAuthor ] )
        wikisourceAuteurs = u', '.join( [ u"""[[Auteur:%s|%s]]"""%(author,author)  for author in listAuthor ] )
        commonsCat = u'\n'.join( [ u"""[[Category:%s]]"""%(author) for author in listAuthor ] )
    
    typepubli=u""
    if genre == u"MONOGRAPHIE":
        typepubli=u"book"
    elif genre == u"PERIODIQUE":
        typepubli=u"journal"
    
    wikisourceTpl=u"""{{:MediaWiki:Proofreadpage_index_template
|Type=%s
|Series=
|Titre=%s
|Volume=
|Auteur=%s
|Traducteur=
|Éditeur scientifique=
|Éditeur=%s
|School=
|Lieu=
|Annee=%s
|Clé=
|Source=djvu
|Image=
|Avancement=C
|Pages=%s
|Tomes=
|Sommaire=
}}"""%(typepubli,titre,wikisourceAuteurs,editeur,annee,pagelist)
    
    codecs.open( coverFileWikisource, 'w', 'utf-8' ).write(wikisourceTpl)

    commonsTpl = u"""== {{int:filedesc}} ==
{{Book
|Author       =%s
|Translator   =
|Editor       =%s
|Title        ={{lang|fr|%s}}
|Subtitle     =
|Series title =
|Volume       =
|Edition      =
|Publisher    =
|Printer      =
|Date         =%s
|City         =
|Language     ={{language|fr}}
|Description  ={{fr|1=[[:s:fr:Livre:%s]]}}
|Source       ={{ARK-BNF|%s}}
|License      =PD-scan
|Image        =
}}
{{BNF cooperation project}}

[[Category:Scanned French books in DjVu]]
[[Category:%s books]]
%s
"""%(creators,editeur,titre,dateEdition,djvuname,ark,annee,commonsCat)

    codecs.open( descriptionFileCommons, 'w', 'utf-8' ).write(commonsTpl)
