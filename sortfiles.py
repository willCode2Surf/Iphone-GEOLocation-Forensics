import os
import sys
import subprocess
import types
import hashlib
import sqlite3
import time
from PIL import Image
from PIL.ExifTags import TAGS
import fnmatch

import json
'''
with open('my_dict.json', 'w') as f:
    json.dump(my_dict, f)

# elsewhere...

with open('my_dict.json') as f:
    my_dict = json.load(f)
'''
'''
files:
	Binary file ./CoreDataStore.sqlite matches
	Binary file ./master.db matches
Binary file ./GoogleScout.sqlite matches 	->  zscnotification no time
Binary file ./CardCase.sqlite matches		-> 	zmerchant		no time
Binary file ./business.sqlite matches		-> 	zbusiness		+date
Binary file ./results.sqlite matches		-> results			+date
	Binary file ./storedata.sqlite matches	->EMPTY
	Binary file ./ShazamDataModel.sqlite matches ->EMPTY
	Binary file ./DataUsage.sqlite matches -> eMPTY
Binary file ./passes23.sqlite matches		-> location 		no time
	Binary file ./Photos.sqlite matches
	Binary file ./consolidated.db matches



'''



hash_dic = {}
mbdx = {}

json = 1
Manifest_mbdb = 1



if len(sys.argv) > 1:
	dir_name = sys.argv[1]

else:
	print "No direcoroty give"
	exit()

if len(sys.argv) > 2:
	hash_dic_name = sys.argv[2]
else:
	hash_dic_name = 'hash_dic.json'

try:
	with open(hash_dic_name) as f:
   		hash_dic = json.load(f)
except:
	print "Couldn't load hash_dictionary"
	json = 0
 


try:
	import manifestParse
	try:
		print "Processing Manifest.mbdb ..."
		mbdx, hash_dic = manifestParse.manifestParse(dir_name + '/')
	except:
		print "Couldn't process Manifest.mbdb"
		Manifest_mbdb = 0 
		#do import of dictionary from json file

except:
	print "Couldn't locate manifestParse.py"
	Manifest_mbdb = 0

if(not(Manifest_mbdb + json)):
	print "Couldn't craete Hash dictionary, exiting"
	exit()

types = []
counter = 0
percent = 0
print "Sorting",
for dirname, dirnames, filenames in os.walk(dir_name):
	nFiles = len(filenames)
	if(not(counter)):
		print  nFiles, "files",
	for fn in filenames:
		counter += 1

		ffn = dirname  + '/' + fn
		try:
			typ = subprocess.check_output(["file",ffn])
			typ = typ.split(":")[1]
			typ1 = typ.split()[0]
			typ = typ1 + "_folder"
			typ1 = typ1.lower()
			if typ1 == "sqlite":
				typ1 = ''
			if (not( typ in types)):
				types +=[typ]
				try:
					 message = subprocess.check_output(["mkdir", dirname+ '/'  +typ])
					 #print message
				except:
					pass
			#print typ
			try:
				if (fn in hash_dic ):
					new_fn = hash_dic[fn].split('/')[-1]
				else:
					new_fn = fn
				subprocess.check_output(["cp",ffn, dirname + '/' + typ + '/' + new_fn])
				subprocess.check_output(["rm", ffn  ])
			except Exception, e:
				print e
				exit()

		except Exception, e:
			print e
			exit()

		if(nFiles*.90 < counter and percent < 90 ):
			print "90%",
			percent = 90
		elif (nFiles*.80 < counter and percent < 80 ):
			print "80%",
			percent = 80
		elif (nFiles*.70 < counter and percent < 70 ):
			print "70%",
			percent = 70
		elif (nFiles*.60 < counter and percent < 60 ):
			print "60%",
			percent = 60
		elif (nFiles*.50 < counter and percent < 50 ):
			print "50%",
			percent = 50
		elif (nFiles*.40 < counter and percent < 40 ):
			print "40%",
			percent = 40
		elif (nFiles*.30 < counter and percent < 30 ):
			print "30%",
			percent = 30
		elif (nFiles*.20 < counter and percent < 20 ):
			print "20%",
			percent = 20
		elif (nFiles*.10 < counter and percent < 10 ):
			print "10%",
			percent = 10

print "[Done]"

def imageData(ffn):
    try:
        img = Image.open(ffn)
        info = img._getexif()
        exif_data = {}
        for tag, value in info.items():
            decoded_tag = TAGS.get(tag, tag)
            exif_data[decoded_tag] = value
            # from the exif data, extract gps
            #print  exif_data
        exifGPS = exif_data['GPSInfo']
        exifTime = exif_data['DateTimeOriginal']
        latData = exifGPS[2]
        lonData = exifGPS[4]
            # calculate the lat / long
        latDeg = latData[0][0] / float(latData[0][1])
        latMin = latData[1][0] / float(latData[1][1])
        latSec = latData[2][0] / float(latData[2][1])
        lonDeg = lonData[0][0] / float(lonData[0][1])
        lonMin = lonData[1][0] / float(lonData[1][1])
        lonSec = lonData[2][0] / float(lonData[2][1])
            # correct the lat/lon based on N/E/W/S
        lat= (latDeg + (latMin + latSec/60.0)/60.0)
        if exifGPS[1] == 'S': 
            lat = lat * - 1
        lon = (lonDeg + (lonMin + lonSec / 60.0)/60.0)
        if exifGPS[3] == 'W': 
            lon = lon* -1
            #print exifTime
        e_timeTemp = exifTime.split()[0].split(":")
        e_time = str(e_timeTemp[1]) + "/" + str(e_timeTemp[2]) + "/" + str(e_timeTemp[0][2:]) + " " + str(exifTime.split()[1]) 
        print "latitude:", 
        print "longtitude:",
        print "Time:", e_time 
    except Exception,e:
            #print e
        pass     