#!/bin/sh
"""
Packs the files needed by the wikibot to init wikisource pages.
(used to save only a part of the folders to be exported easily, with few megabytes)
"""
cd /home/projetbnf/out.ter.cjb2/ok

touch empty
tar -cf ocr.tar empty

for folder in *
do
	tar -rf ocr.tar $folder
done

tar -f ocr.tar --delete */add_txt */cover.wikisource.txt */log.err.txt */log.out.txt

