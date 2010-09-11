# -*- coding: utf-8 -*-
"""
Convert all BnF books into DjVu

Run as : nohup python mainBnF.py 0</dev/null &
to release the terminal and close ssh connexion without killing the process.

WARNING: the environment variable LANG should be set to fr_FR.UTF8
         zsh: export LANG=fr_FR.UTF8
"""
__authors__ =  'User:Seb35, User:Jean-Frédéric, User:Plyd for BNF partnership with Wikimedia France'
import sys,os,traceback,codecs,locale
from multiprocessing import Pool
from bookprocess import bookProcess

# The directory where to take the books to parse
bookFolder = u'/home/projetbnf/bouquins'
# The directory to receive the temporary data and the wiki templates for Wikisource.
outFolder = u'/home/projetbnf/out'
# The directory to receive the .tar with wiki template and djvu file.
commonsFolder = u'/home/commons/uploadToCommons'

# Save standard output and error (they will be replaced by log files for each book)
stdoutBak = sys.stdout
stderrBak = sys.stderr

def cleanup():
    """ Cleans up temporary files to prevent the folder to get too big! """
    for file in os.listdir('./images'):
        os.remove('images/'+file)
    for file in os.listdir('.'):
        if file.endswith('.tif'): os.remove(file)
        if file.endswith('.djvu'): os.remove(file)
        if file.endswith('.djvu.txt'): os.remove(file)
    os.rmdir('images')

def doABook(folder):
    """ Work for a single book, referenced by its working folder.
        This function calls bookProcess which launches scripts and operation.
        It handles the restart of the call to bookProcess in case of exception (useful for memory failures from scripts).
        If the bookProcess fails twice, it is stopped and moved to the 'ko' folder.
        If the bookProcess sucess, it is moved to the 'ok' folder.
        
        The output is redirected into two log files, one for standard output, one for error output.
    """
    print folder
    # init errorlog for this process
    errorlog = ""
    
    # Create the working directory for this book
    origfolder = bookFolder+'/'+folder+'/'
    workfolder = outFolder+'/running/'+folder+'/'
    os.mkdir( workfolder )
    os.chdir( workfolder )
    
    # Sets output in log files of the book
    logoutfile = codecs.open( u'log.out.txt', 'w', 'utf-8' )
    logerrfile = codecs.open( u'log.err.txt', 'w', 'utf-8' )
    sys.stdout = logoutfile
    sys.stderr = logerrfile
    
    print u"Encoding: %s"%(logoutfile.encoding)
    
    # Read the metadata for this book
    if folder not in metadata.keys() :
        print u"Unable to do the book %s! no metadata"%folder 
        return
    
    metadatabook = metadata[folder]
    
    try:
        bookProcess(folder, origfolder, commonsFolder, metadatabook)
        os.rename(outFolder+'/running/'+folder,outFolder+'/ok/'+folder)
    except:
        try:
            # Failure!!
            
            trace = traceback.format_exc()
            print u"Ooooops! first failure!"
            print unicode(trace)
            print "\n\n"
            sys.stderr.write(u"End of first failed try!\n\n")
            sys.stderr.flush()
            sys.stdout.flush()
            
            # Cleanup and try again!
            cleanup()
            # TRY AGAIN!
            workfolder = outFolder+'/running/'+folder+'/retry/'
            os.mkdir( workfolder )
            os.chdir( workfolder )
            bookProcess(folder, origfolder, commonsFolder, metadatabook)
            os.rename(outFolder+'/running/'+folder,outFolder+'/ok/'+folder)
        except:
            os.rename(outFolder+'/running/'+folder,outFolder+'/ko/'+folder)
            trace = traceback.format_exc()
            print u"Ooooops! second failure! - see error log"
            #print unicode(trace)
            djvuname = metadatabook[1]
            #errorlog = u"** Book: %s\n%s\n%s\n\n"%(folder,djvuname,trace)
            errorlog = u"** Book: %s\n\n"%(folder)
    
    cleanup()
    
    logoutfile.close()
    logerrfile.close()
    sys.stdout = stdoutBak
    sys.stderr = stderrBak
    return errorlog

# format :
# ordre|titrecourt|titredjvu|ark|auteur|titre|resolution|pagelist|bonsauteurs
def getMetadata():
    """ Parse the metadata file into an associative array. It contains metadata for a book. """
    metadatafile = codecs.open( 'metadatabooks.txt', 'r', 'utf-8' )
    metadatalist = [ line[:-1].split('|') for line in metadatafile.readlines() ]
    metadatafile.close()
    metadata = {}
    for book in metadatalist :
        metadata[book[0]] = book[1:]
    return metadata


def main():
    """ Main process for books analysis, creation of DjVu and Wiki Templates.
    
    Puts in parallel the books
    """
    # put metadata in global because we can't give more than one parameter to doABook (because of 'map')
    global metadata
    metadata = getMetadata()
    
    try:
        os.mkdir( outFolder )
        try: os.mkdir( outFolder+'/running' )
        except: print u"unable to create running directory... already exist?"
        try: os.mkdir( outFolder+'/ok' )
        except: print u"unable to create ok directory... already exist?"
        try: os.mkdir( outFolder+'/ko' )
        except: print u"unable to create ko directory... already exist?"
        try: os.mkdir( commonsFolder )
        except: print u"unable to create commons directory... already exist?"
    except:
        print u"unable to create all directories... already exist?"

    
    if len(sys.argv) > 1:
        doABook(sys.argv[1])
    else:
        # Filter list, to prevent from making all books.
        toreadfile = codecs.open( u'toread.txt', 'r', 'utf-8' )
        toread = [ word[:-1] for word in toreadfile.readlines() ]
        toreadfile.close()
        globalErrors = u"".join(Pool(4).map(doABook,[folder for folder in toread]))
        globalErrorLogFile = codecs.open( unicode(outFolder+'/books.err.txt'), 'w', 'utf-8' )
        globalErrorLogFile.write(globalErrors)
        globalErrorLogFile.close()


if __name__ == "__main__":
    main()

