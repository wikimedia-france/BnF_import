# Copyright (c) 2010 by User:Seb35, User:Jean-Frédéric, User:Plyd, User:VIGNERON from Wikimédia France
#
# See main page :
# http://meta.wikimedia.org/wiki/BnF_%E2%88%92_Wikim%C3%A9dia_France_cooperation_project
#
# GNU General Public Licence (GPL)
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#

Main process, called with mainBnF.py:
- mainBnF.py, to be called to loop over all books in parallel or on a single book
- bookprocess.py, Calls all the scripts and commands needed for a single book
- altoparser.py, Reads the alto XML page and generates a text at DjVu format (with parenthesis), and a text at WikiSource format.
- coverparser.py, Parse the refnum file and the metadata to generate index page of the book (Wikisource and Commons templates).

Independent tools:
- createPagelist.py generates the <pagelist /> tags for metadata
- readResol.py generates the metadata resolution (dpi) to resolution.txt, that will be injected in metadatabooks.txt, to finally be included in DjVu.
- treat_list.php merges the metadata inputs into a single metadatabooks.txt, to be used for by mainBnF process to add data to DjVu &co.
- packOCR.sh packs the files needed by the wikibot to init wikisource pages.
- imageExtractor.py extract the images from TIFF files given the position in the XML ALTO.

pywikipedia:
- initwsbook.py, initiate the index pages and the pages of the Wikisource books. To be launched after mainBnF.py.
