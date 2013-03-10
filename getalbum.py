# -*- coding: utf-8 -*-

from pbapi import PbApi
from xml.etree import ElementTree
import getopt
import sys
import os
import urllib
import codecs

import pbkey # module containing your PhotoBucket key and secret

def album2lj(album_name, outfile, super, alib, pcol, col):
	api = PbApi(pbkey.api_key, pbkey.api_secret)
	api.pb_request.connection.cache = None

	result = api.album(album_name, {'sortorder':'alpha'}).get().response_string
	ET = ElementTree.fromstring(result)
	images = ET.findall('content/album/media')

	if len(images) == 0:
		print "no images found"
		return

	f = codecs.open(outfile, encoding='utf-8', mode='w')

	if not alib:
		if super:
			f.write(u'Уайльд, Оскар. Мальчик-звезда. Перевод с  и послесловие А. Аникста. Художник Ника Гольц. М.: Детская литература. 1972 г.\r\n')
		else:
			f.write(u'Александрова, Т. Кузька в новой квартире. Художник Е. Чайко, М. Гран. М.: Детская литература. 1977 г.\r\n')
		f.write("<table>\r\n")
		cnt = 0
		for image in images:
			if cnt % pcol == 0: f.write("<tr>\r\n")
			f.write('<td><img src="%s" border="0" alt="Photobucket"></td>\r\n' % (image.findtext('thumb')))
			cnt += 1 
			if cnt % pcol == 0: f.write("</tr>\r\n")
		if cnt % pcol != 0: f.write("</tr>\r\n")
		f.write("</table>\r\n")

		if super:
			f.write(u"<b>Уайльд, Оскар. Мальчик-звезда. Перевод с английского и послесловие А. Аникста. Художник Ника Гольц. </b>М.: Детская литература. 1972 г.  Переплет: ледериновый + суперобложка; 112 страниц; формат: энциклопедический\r\n")
		else:
			f.write(u"<b>Александрова, Т. Кузька в новой квартире. Художник Е. Чайко, М. Гран. </b> М.: Детская литература. 1977 г.   Переплет: мягкий; 48 страниц;  формат: энциклопедический\r\n")
		
		f.write(u'<lj-cut text="Посмотреть еще и в большем разрешении">\r\n')

	idx = 0	
	if not super:
		idx = 1
		f.write("<center><table><tr>\r\n")
		f.write('<td><img src="%s" border="0" alt="Photobucket"></td>\r\n' % (images[0].findtext('url')))
		f.write("</tr></table></center>\r\n")

	f.write("<center><table>\r\n")
	cnt = 0
	for image in images[idx:]:
		if cnt %col == 0: f.write( "<tr>\r\n")
		f.write('<td><img src="%s" border="0" alt="Photobucket"></td>\r\n' % (image.findtext('url')))
		cnt += 1
		if cnt %col == 0: f.write( "</tr>\r\n")
	if cnt %col != 0: f.write( "</tr>\r\n")
	f.write("</table></center>\r\n")
	
	if not alib:
		f.write(u'</lj-cut><a href="http://www.libex.ru/detail/book187623.html?saleid=1060421">Купить</a>\r\n')
	f.close()

def album_download(album_name):
	api = PbApi(api_key, api_secret)
	api.pb_request.connection.cache = None

	result = api.album(album_name, {'sortorder':'alpha', 'recurse':True, 'paginated':False}).get().response_string
	print result
	ET = ElementTree.fromstring(result)	
	album = ET.find('content/album')
	do_download_album(album)

def do_download_album(album):
	albums = album.findall('album')
	images = album.findall('media')
	name = album.get('name')
	if not os.path.exists(name): os.makedirs(name)
	
	print "%s: # of images: %d, # of subalbums: %d" % (name, len(images), len(albums))
	count = 0
	for image in images:
		(filename, headers) = urllib.urlretrieve(image.findtext('url'))
		newfilename = os.path.join(name, image.get('name'))
		if os.path.exists(newfilename): os.unlink(newfilename)
		os.rename(filename, newfilename)
		#print filename, '->', os.path.join(name, image.get('name'))
		count += 1
		print "\rDownloaded %.2f%% (%d/%d) of %s" % (float(count)/len(images)*100.0, count, len(images), name), 
		#if count > 10: break
	print
	for subalbum in albums:
		do_download_album(subalbum)
	

def usage():
	print "\r\ngetalbum -c [lj|download] -a albumname [-s] -o filename"
	print
	print "\t-c command (lj or download)"
	print "\t-a name of the album (e.g. bukvoed/27266/Bukvar_1955)"
	print "\t-o output file name"
	print "\t-s with a cover (only for 'lj' commasnd)"
	print "\t--alib alib mode ('lj' commasnd)"
	print "\t--pcol=6 number of preview columns ('lj' command)"
	print "\t--col=2 number of regular columns ('lj' command)"
	print "\t-h this help"
	print "\r\nExample:"
	print "\tgetalbum -c lj -a bukvoed/27266/Bukvar_1955"

def main():
    if len(sys.argv) < 2:
    	usage()
    	sys.exit(1)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:c:a:s", ["help", "output=", "command=", "album=", "super", "pcol=", "col=", "alib"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    album = None
    output = None
    command = None
    super = False
    alib = False
    pcol = 6
    col = 2
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-o", "--output"):
            output = a
        elif o in ("-c", "--command"):
        	command = a
        elif o in ("-a", "--album"):
        	album = a
        elif o in ("-s", "super"):
        	super = True
        elif o == "--pcol":
        	pcol = int(a)
        elif o == "--col":
        	col = int(a)
        elif o == "--alib":
        	alib = True
        else:
            print "unhandled option: %s" % o

    if command is None: 
    	print "command not specified"
    	usage()
    	sys.exit()

    if album is None: 
    	print "album not specified"
     	usage()
    	sys.exit()

    if command == "lj":
    	if output is None:
    		print "output file not specified"
    		usage()
    		sys.exit()
    	album2lj(album, output, super, alib, pcol, col)
    elif command == "download":
    	album_download(album)

if __name__ == "__main__":
    main()