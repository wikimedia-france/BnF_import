# -*- coding: utf-8 -*-
"""
Seb: program out of main chain.
Creation of <pagelist /> tag for wikisource index page template.

Generates a file like this from the refnum file (file format from the bnf for describing books).

0007315 <pagelist 1to4=- 5=1 />
0016131 <pagelist 1to7=- 8=1 40to41=- 42=33 301=- />
0076088 <pagelist 1=- 2=1 />
0066408 <pagelist 1to4=- 5=1 282to283=- />
0050130 <pagelist 1to6=- 7=2 7to61=roman 62=- 63=2 />
0061837 <pagelist 1to2=- 3=1 />
0066333 <pagelist 1to6=- 7=1 448=- />
0024343 <pagelist 1to5=- 6=2 153to154=- 155=149 165to166=- 167=159 205to206=- 207=197 />
0208503 <pagelist 1to4=- 5=1 576=- />
0036231 <pagelist 1to2=- 3=1 129=- 130=127 336=- 337=333 473=- 474=469 />
0004925 <pagelist 1to5=- 6=1 6to8=roman 9=- 10=1 502=- />
0065314 <pagelist 1to11=- 12=1 388to391=- />
0072826 <pagelist 1to3=- 4=1 4to41=roman 42=1 />
0094614 <pagelist 1to5=- 6=1 />
0206050 <pagelist 1to8=- 9=5 25=- 26=21 434=- 435=429 />
0206374 <pagelist 1to3=- 4=1 402=- />
0017158 <pagelist 1to4=- 5=1 />
0036409 <pagelist 1to3=- 4=1 430=- />
0009066 <pagelist 1to4=- 5=1 />
0069992 <pagelist 1=- 2=1 />
0005121 <pagelist 1to9=- 10=3 591=- />
0208047 <pagelist 1to3=- 4=1 />

"""
__author__ = 'User:Seb35, User:VIGNERON for BNF partnership with Wikimedia France'

import xml.dom.minidom, gzip, os

def createPagelistTag(wikisourceFilename):
    
    typeAvailablePagination = {'A':'1', 'N':'-', 'R':'roman', 'X':'?'}
    
    os.chdir( '/home/projetbnf/bouquins' )
    
    listbook = os.listdir('.')
    print listbook
    
    wikisource = open(wikisourceFilename,'w')
    erreurfile = open('/home/projetbnf/tests/erreur-pagelists.txt','w')
    
    for book in listbook:
        
        print book
        
        doc = xml.dom.minidom.parse(book+'/X'+book+'.XML')
        pagelist = '<pagelist '
        ancienTag = ''
        ancienPage = 1
        ancienNumeroPage = 1
        page = 0
        
        for vueobjet in doc.getElementsByTagName('vueObjet'):
            typePagination = vueobjet.getAttribute('typePagination')
            numeroPage = vueobjet.getAttribute('numeroPage')
            page += 1
            if ancienTag == typePagination:
                continue
            if ancienTag == '':
                ancienTag = typePagination
                continue
            if not typePagination in typeAvailablePagination.keys():
                print 'erreur (pas dans types dispo)'+book
                erreurfile.write('erreur (pas dans types dispo)'+book+'\n')
            if ancienPage+1 == page:
                if ancienTag == 'A':
                    pagelist += str(ancienPage)+'='+str(ancienNumeroPage)+' '
                elif ancienTag == 'R':
                    pagelist += str(ancienPage)+'='+str(ancienNumeroPage)+';roman '
                elif ancienTag == 'N':
                    pagelist += str(ancienPage)+'=- '
                elif ancienTag == 'X':
                    pagelist += str(ancienPage)+'=? '
                else:
                    print 'erreur (autre unique)'+book
                    erreurfile.write('erreur (autre unique)'+book+'\n')
            else:
                if ancienTag == 'A':
                    pagelist += str(ancienPage)+'='+str(ancienNumeroPage)+' '
                elif ancienTag == 'R':
                    pagelist += str(ancienPage)+'='+str(ancienNumeroPage)+' '+str(ancienPage)+'to'+str(page-1)+'=roman '
                elif ancienTag == 'N':
                    pagelist += str(ancienPage)+'to'+str(page-1)+'=- '
                elif ancienTag == 'X':
                    pagelist += str(ancienPage)+'=? '
                else:
                    print 'erreur (autre multi)'+book
                    erreurfile.write('erreur (autre multi)'+book+'\n')
            ancienTag = typePagination
            ancienPage = page
            ancienNumeroPage = numeroPage
        
        page += 1
        if ancienPage != 1:
            if ancienPage+1 == page:
                if ancienTag == 'A':
                    pagelist += str(ancienPage)+'='+str(ancienNumeroPage)+' '
                elif ancienTag == 'R':
                    pagelist += str(ancienPage)+'='+str(ancienNumeroPage)+';roman '
                elif ancienTag == 'N':
                    pagelist += str(ancienPage)+'=- '
                elif ancienTag == 'X':
                    pagelist += str(ancienPage)+'=? '
                else:
                    print 'erreur (fin autre unique)'+book
                    erreurfile.write('erreur (fin autre unique)'+book+'\n')
            else:
                if ancienTag == 'A':
                    pagelist += str(ancienPage)+'='+str(ancienNumeroPage)+' '
                elif ancienTag == 'R':
                    pagelist += str(ancienPage)+'='+str(ancienNumeroPage)+' '+str(ancienPage)+'to'+str(page-1)+'=roman '
                elif ancienTag == 'N':
                    pagelist += str(ancienPage)+'to'+str(page-1)+'=- '
                elif ancienTag == 'X':
                    pagelist += str(ancienPage)+'=? '
                else:
                    print 'erreur (fin autre multi)'+book
                    erreurfile.write('erreur (fin autre multi)'+book+'\n')
        
        pagelist += '/>\n'
        wikisource.write(book+' '+pagelist)

def main():
    """ Test main """
    wikisourceFilename = "/home/projetbnf/tests/pagelists.txt";
    createPagelistTag(wikisourceFilename)

if __name__ == "__main__":
    main()

