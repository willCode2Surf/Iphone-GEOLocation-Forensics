"Coded by Alexander Ryzhko"
import os
import time
import datetime
import hashlib
import sys
import subprocess
import types
import hashlib
import json 

try:
    import pygeoip
    from PIL import Image
    from PIL.ExifTags import TAGS
    import simplekml
    import sqlite3
except Exception,e:
    print "Please install needed moduals"
    print e
    exit()

#import fnmatch

SORT = False
dir_name = ''
output_dir = 'IphoneGeolocOutput'
SAVE_JSON = ''

GEO_hit_files_folder = "Files_with_GEOlocations"
GEO_IP_folder = "GEO_from_IP/"
GEO_found_folder = "GEO_from_SQLs/"
save_KML_IMG_as = "Geolocation_from_JPEG_IMGs"
save_big_KML_as = "GeolocationsFound"

HIT = False
IP = True
wlocList = ["LATITUDE", "LONGITUDE"]
wdateList = ["TIMESTAMP", "DATE"]
wlist = wlocList + wdateList 
IP_discr = ["country_name", 'city', 'region_name']
gi = ''
IPGeoDB ='GeoLiteCity.dat'
KMZ = False
ROUND = True
MORE = False
BIG_KML = False
SORT_TYPE = False
SORT_ORIGINAL = False
RENAME = False


hash_dic = {}
mbdx = {}

#json = 1
#Manifest_mbdb = 1


'''
Check for images only for CamerasPhotoes???
'''

def makeOutputDir(out = output_dir):
    try:
        if(MORE):
            print "Creating Output Directories"
        message = subprocess.check_output(["mkdir", out])
        message = subprocess.check_output(["mkdir", out + '/'  + GEO_found_folder ])
        message = subprocess.check_output(["mkdir", out + '/'  + GEO_IP_folder  ])
        if(HIT):
            message = subprocess.check_output(["mkdir", out + '/'  + GEO_hit_files_folder ])
    except Exception, e:
        pass
        if(HIT):
            try:
                message = subprocess.check_output(["mkdir", out + '/'  + GEO_hit_files_folder ])
            except:
                pass
def kmlAll(imglist, Ips, SQls):

    if(MORE):
        print "Creating BIG KML"
    kml = simplekml.Kml()

    #IMAGES    
    #print "imglist[0]", imglist[0]
    for point in imglist[-1]:
        #print "name=", point, "description=", point, "coords=", [(point, point)] 
        kml.newpoint(name=point[2], description=point[-1], coords=[(point[1], point[0])] )

    #IPS
    for dataBaseIPList in Ips:
        save_to = output_dir + '/' + GEO_IP_folder
        db_name = dataBaseIPList[0]
        save_as = db_name.split('/')[-1] +"_IP_geo" + '.kml'
        save_as = save_to + save_as 
        

        for table in dataBaseIPList[1]:
            table_name = table[0]

            for row in table[1]:
                add_info = ''
                point_name = ''
                for i in row[1]:
                    add_info = add_info + str(i[0]) + ":" + str(i[1]) +'\n'
                    possibl_date = i[1]
                    if (type(possibl_date) == type("string")):
                        if(wlist[2] in i[0].upper()):
                            point_name = possibl_date.split('#')[0] + " IP:"
                        if(wlist[3] in i[0].upper()):
                            point_name = possibl_date.split('#')[0] + " IP:"
                for point in row[0]:

                    discr = ''
                    point_name = point_name  + str(point[1]["ip"]) 
                    for key in point[1]:
                        if(key in IP_discr ):
                            discr += str(key) +":" + str(point[1][key]) + '\n' 

                    discr += "Culum: " + point[0] + '\n' 
                    discr += "Table:" + table_name + '\n'
                    discr += add_info + db_name


                    kml.newpoint(name=point_name , description=discr, coords=[(point[1]['longitude'], point[1]['latitude'])] )
    #GEOLOCATIONS
    for dataBaseList in SQls:
        save_to = output_dir + '/' + GEO_found_folder
        db_name = dataBaseList[0]
        if(MORE):
            print "Crating SQL Location KML:", db_name.split('/')[-1]
        
        for table in dataBaseList[1]:
            table_name = table[0]
            for point in table[1]:
                discr = ""
                for i in point:
                    discr += str(i[0]) + ":" + str(i[1]) +'\n'
                discr += "table:" + table_name +'\n'
                discr += db_name 
                point_name = ''
                isTS =0;
                for i in point:
                    possibl_date = i[1]
                    if (type(possibl_date) == type("string")):
                        if(wlist[2] in i[0].upper()):
                            isTS =1
                            point_name = possibl_date.split('#')[0]
                            break 
                        if(wlist[3] in i[0].upper()):
                            isTS =1
                            point_name = possibl_date.split('#')[0]
                if(not(isTS)):
                    point_name =  hashlib.md5(str(point[0][1]) + str (point[1][1])).hexdigest()[:8]   
                kml.newpoint(name=point_name , description=discr, coords=[(point[1][1], point[0][1])] )
        save_as = db_name.split('/')[-1] + '.kml'
        save_as = save_to + save_as         

    if(KMZ):
        kml.savekmz(output_dir + '/' + save_big_KML_as + '.kmz', format=False)
    else:
        kml.save(output_dir + '/' + save_big_KML_as  + '.kml')


def IP_info_By_IP(given_IP):
    '''returns IP info dictionary including location based on the IP adres, if failed returns None'''
    global gi
    try:

        return gi.record_by_addr(given_IP)
    except Exception, e:

        return None


def converTS(TS, earliest_possible_date = '2001-01-01 00:00:00' ):
    
    unix_base_TS = int(time.mktime(time.strptime('2001-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')))
    before_iphone_time = int(time.mktime(time.strptime('2006-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')))
    trashold = before_iphone_time - unix_base_TS 
    # if (type(TS) == type("String")):
    #     return None
    try:
        if (ROUND):
            TS = int(TS)
        else:
            TS = float(TS)
    except:
        return None

    if(TS < trashold ):
        return None
   
    unix_base_TS = int(time.mktime(time.strptime('2001-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')))
    try:
        earliest = int(time.mktime(time.strptime(earliest_possible_date, '%Y-%m-%d %H:%M:%S')))
    except:
        earliest = unix_base_TS

    if(TS < earliest):
        #NSDATE
        return str(datetime.datetime.fromtimestamp(unix_base_TS + TS)) + " #(NSDate TS)"
    else:
        #unix 
        try:
            return str(datetime.datetime.fromtimestamp(TS)) + " #(UNIX TS)"
        except:
            return None
def imageData(ffn):
    "This function is modification of a class method written by Grisha Kumar"
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
        e_time = ('-'.join(exifTime.split()[0].split(":"))) + ' ' + exifTime.split()[1]
        return [lat, lon, e_time] 
    except Exception,e:
            #print e
        pass     

def extractImage(dir_name):
    '''
    Extracts geolocation iformation from JPGs, returns list containing Data Name and
    list of image informations. Image information is a list containing latitude, 
    longtitude, date and filename
    '''
    ImgaDatas = []
    for dirname, dirnames, filenames in os.walk(dir_name):
        for fn in filenames:
            ffn = dirname + '/' + fn
            point = imageData(ffn)
            if(point != None):
                ImgaDatas += [point]
                #print point
    return ["Geolocation_from_JPEG_IMGs", ImgaDatas]

def IMG_KML(imglist):

    if(MORE):
        print "Creating IMG KML"
    kml = simplekml.Kml()
    #print "imglist[0]", imglist[0]
    for point in imglist[-1]:
        kml.newpoint(name=point[2], description=point[-1], coords=[(point[1], point[0])] )
    if(KMZ):
        kml.savekmz(output_dir + '/' + imglist[0] + '.kmz', format=False)
    else:
        kml.save(output_dir + '/' + imglist[0] + '.kml')

def SQL_IP_KML(dataBaseIPList):
    save_to = output_dir + '/' + GEO_IP_folder
    db_name = dataBaseIPList[0]
    save_as = db_name.split()[0].split('/')[-1]  +"_IP_geo" 
    save_as = save_to + save_as 
    kml = simplekml.Kml()

    for table in dataBaseIPList[1]:
        table_name = table[0]

        for row in table[1]:
            add_info = ''
            point_name = ''
            for i in row[1]:
                add_info = add_info + str(i[0]) + ":" + str(i[1]) +'\n'
                possibl_date = i[1]
                if (type(possibl_date) == type("string")):
                    if(wlist[2] in i[0].upper()):
                        point_name = possibl_date.split('#')[0] + " IP:"
                    if(wlist[3] in i[0].upper()):
                        point_name = possibl_date.split('#')[0] + " IP:"
            for point in row[0]:

                discr = ''
                point_name = point_name  + str(point[1]["ip"]) 
                for key in point[1]:
                    if(key in IP_discr ):
                        discr += str(key) +":" + str(point[1][key]) + '\n' 

                discr += "Culum: " + point[0] + '\n' 
                discr += "Table:" + table_name + '\n'
                discr += add_info + db_name


                kml.newpoint(name=point_name , description=discr, coords=[(point[1]['longitude'], point[1]['latitude'])] )
    if(KMZ):
        kml.savekmz(save_as+ '.kmz',  format=False)#  + '.kmz')
    else:
        kml.save(save_as + '.kml')

def SQL_KML(dataBaseList): 
    save_to = output_dir + '/' + GEO_found_folder
    db_name = dataBaseList[0]
    if(MORE):
        print "Crating SQL Location KML:", db_name.split('/')[-1]
    kml = simplekml.Kml()
    for table in dataBaseList[1]:
        table_name = table[0]
        for point in table[1]:
            discr = ""
            for i in point:
                discr += str(i[0]) + ":" + str(i[1]) +'\n'
            discr += "table:" + table_name +'\n'
            discr += db_name 
            point_name = ''
            isTS =0;
            for i in point:
                possibl_date = i[1]
                if (type(possibl_date) == type("string")):
                    if(wlist[2] in i[0].upper()):
                        isTS =1
                        point_name = possibl_date.split('#')[0]
                        break 
                    if(wlist[3] in i[0].upper()):
                        isTS =1
                        point_name = possibl_date.split('#')[0]
            if(not(isTS)):
                point_name =  hashlib.md5(str(point[0][1]) + str (point[1][1])).hexdigest()[:8]   
            kml.newpoint(name=point_name , description=discr, coords=[(point[1][1], point[0][1])] )
    save_as = db_name.split()[0].split('/')[-1] 
    #print db_name.split()
    save_as = save_to + save_as 
    if(KMZ):
        kml.savekmz(save_as + '.kmz', format=False)#  + '.kmz')
    else:
        kml.save(save_as    + '.kml')


def sqlCrowle(fileName, dbName): 
    if(MORE):
        print "Crowling :", dbName.split('/')[-1]
    wlistStr = ' '.join(wlist)
    con = sqlite3.connect(fileName)
    cursor = con.cursor()
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    except Exception, e:
            if(MORE):
                print e
            return None, None
    tables = cursor.fetchall()
    db_results= []
    IP_db_results = []
    table_names = []
    for table in tables:
        table_names += [str(table[0])]
    for table in table_names:
        #empty_table = 0
        lat_name = ''
        long_name = ''
        date_name = ''
        try:
            cursor.execute("SELECT * FROM "+ str(table))
        except Exception, e:
            if(MORE):
                print e
            return None, None
        culum_names = list(map(lambda x: x[0], cursor.description))
        #print culum_names
        IP_culums =[]
        list_valid_culums = []
        for name in culum_names:
            if("IP" in str(name).upper()):
                IP_culums +=[name]
            if (wlist[0] in str(name).upper()):
                #print "found1"
                if(lat_name):
                    list_valid_culums += [name]
                else:
                    lat_name = str(name)
            elif wlist[1] in str(name).upper():
                #print "found2"
                if (long_name):
                    list_valid_culums += [name]
                else:
                    long_name = str(name)
            elif wlist[2] in str(name).upper():
                #print "found3"
                if(date_name):
                    list_valid_culums += [name]
                else:
                    date_name = str(name)
            else:
                for word in wlist[3:]:
                    if(word in str(name).upper() ):
                        list_valid_culums += [name]
        if((lat_name !='') and (long_name != '')):
            if(date_name):
                list_valid_culums = [lat_name, long_name, date_name ] + list_valid_culums
            else:
               list_valid_culums = [lat_name, long_name] + list_valid_culums
        valid_rows = []
        valid_IP_info_list = []
        query = "SELECT "
        all_culums =list_valid_culums
        if(IP):
            all_culums = all_culums + IP_culums
        if(len(all_culums)):
            for v_culum in all_culums[:-1]:
                query += v_culum + ", "         
            query += all_culums[-1] + "  FROM "+ str(table)
            for crow in con.execute(query):
                row =crow
                add_geo_row = []  
                add_IP_row = []
                add_add_info = []
                for i in range(len(row)):
                    if(row[i]):
                        current_culum = all_culums[i]
                        if(current_culum in IP_culums):
                            IP_info = IP_info_By_IP(row[i])
                            if(IP_info):
                                IP_info["ip"] = row[i]
                                add_IP_row += [[current_culum, IP_info]]
                        if(current_culum in list_valid_culums):
                            ts = converTS(row[i])
                            if(ts):
                                add_add_info +=  [ [current_culum, ts ]]
                            else:
                                add_add_info +=  [ [current_culum, row[i]] ]

                if((lat_name !='') and (long_name != '')):  
                    if (row[0] and row[1]):
                        add_geo_row = add_add_info
                if(len(add_geo_row)):
                    valid_rows += [add_geo_row]
                if(len(add_IP_row)):
                    valid_IP_info_list = [[add_IP_row, add_add_info]]
            if(len(valid_rows)):
                db_results += [   [str(table),   valid_rows]     ]
            if(len(valid_IP_info_list)):
                IP_db_results += [   [str(table),   valid_IP_info_list]     ]
    GEO_LIST = []
    IP_LIST = []
    if (len(db_results)):
        GEO_LIST = [dbName+'\n' + fileName, db_results]
    else:
        GEO_LIST = None
    if (len(IP_db_results)):
        IP_LIST = [dbName+'\n' + fileName, IP_db_results]
    else:
        IP_LIST = None

    return GEO_LIST, IP_LIST 


def printProgress(nFiles,counter,percent):
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


def getint(data, offset, intsize):
    """Retrieve an integer (big-endian) and new offset from the current offset"""
    value = 0
    while intsize > 0:
        value = (value<<8) + ord(data[offset])
        offset = offset + 1
        intsize = intsize - 1
    return value, offset

def getstring(data, offset):
    """Retrieve a string and new offset from the current offset into the data"""
    if data[offset] == chr(0xFF) and data[offset+1] == chr(0xFF):
        return '', offset+2 # Blank string
    length, offset = getint(data, offset, 2) # 2-byte length
    value = data[offset:offset+length]
    return value, (offset + length)

def process_mbdb_file(filename):
    mbdb = {} # Map offset of info in this file => file info
    data = open(filename).read()
    if data[0:4] != "mbdb": raise Exception("This does not look like an MBDB file")
    offset = 4
    offset = offset + 2 # value x05 x00, not sure what this is
    while offset < len(data):
        fileinfo = {}
        fileinfo['start_offset'] = offset
        fileinfo['domain'], offset = getstring(data, offset)
        fileinfo['filename'], offset = getstring(data, offset)
        fileinfo['linktarget'], offset = getstring(data, offset)
        fileinfo['datahash'], offset = getstring(data, offset)
        fileinfo['unknown1'], offset = getstring(data, offset)
        fileinfo['mode'], offset = getint(data, offset, 2)
        fileinfo['unknown2'], offset = getint(data, offset, 4)
        fileinfo['unknown3'], offset = getint(data, offset, 4)
        fileinfo['userid'], offset = getint(data, offset, 4)
        fileinfo['groupid'], offset = getint(data, offset, 4)
        fileinfo['mtime'], offset = getint(data, offset, 4)
        fileinfo['atime'], offset = getint(data, offset, 4)
        fileinfo['ctime'], offset = getint(data, offset, 4)
        fileinfo['filelen'], offset = getint(data, offset, 8)
        fileinfo['flag'], offset = getint(data, offset, 1)
        fileinfo['numprops'], offset = getint(data, offset, 1)
        fileinfo['properties'] = {}
        for ii in range(fileinfo['numprops']):
            propname, offset = getstring(data, offset)
            propval, offset = getstring(data, offset)
            fileinfo['properties'][propname] = propval
        mbdb[fileinfo['start_offset']] = fileinfo
        fullpath = fileinfo['domain'] + '-' + fileinfo['filename']

        id = hashlib.sha1(fullpath)
        mbdx[fileinfo['start_offset']] = id.hexdigest()
        hash_dic[id.hexdigest()] = fullpath
    return mbdb

def modestr(val):
    def mode(val):
        if (val & 0x4): r = 'r'
        else: r = '-'
        if (val & 0x2): w = 'w'
        else: w = '-'
        if (val & 0x1): x = 'x'
        else: x = '-'
        return r+w+x
    return mode(val>>6) + mode((val>>3)) + mode(val)

def fileinfo_str(f, verbose=False):
    if not verbose: return "(%s)%s::%s" % (f['fileID'], f['domain'], f['filename'])
    if (f['mode'] & 0xE000) == 0xA000: type = 'l' # symlink
    elif (f['mode'] & 0xE000) == 0x8000: type = '-' # file
    elif (f['mode'] & 0xE000) == 0x4000: type = 'd' # dir
    else: 
        if(MORE):
            print >> sys.stderr, "Unknown file type %04x for %s" % (f['mode'], fileinfo_str(f, False))
        type = '?' # unknown
    info = ("%s%s %08x %08x %7d %10d %10d %10d (%s)%s::%s" % 
            (type, modestr(f['mode']&0x0FFF) , f['userid'], f['groupid'], f['filelen'], 
             f['mtime'], f['atime'], f['ctime'], f['fileID'], f['domain'], f['filename']))
    if type == 'l': info = info + ' -> ' + f['linktarget'] # symlink destination
    for name, value in f['properties'].items(): # extra properties
        info = info + ' ' + name + '=' + repr(value)
    return info

def manifestParse(dirName=""):
    '''
    This Code was mostly taken from http://stackoverflow.com/questions/3085153/how-to-parse-the-manifest-mbdb-file-in-an-ios-4-0-itunes-backup
    '''
    verbose = True
    mbdx = {}
    hash_dic = {}
    mbdb = process_mbdb_file(dirName + "Manifest.mbdb")
    fily = open(output_dir + "/Manifest.mbdb_Report.txt", 'w')
    sizes = {}
    for offset, fileinfo in mbdb.items():
        if offset in mbdx:
            fileinfo['fileID'] = mbdx[offset]
        else:
            fileinfo['fileID'] = "<nofileID>"
            if(MORE):
                print >> sys.stderr, "ERROR:No fileID found for %s" % fileinfo_str(fileinfo)
        #print fileinfo_str(fileinfo, verbose)
        fily.write(fileinfo_str(fileinfo, verbose))
        fily.write("\n")
        if (fileinfo['mode'] & 0xE000) == 0x8000:
            sizes[fileinfo['domain']]= sizes.get(fileinfo['domain'],0) + fileinfo['filelen']
    for domain in sorted(sizes, key=sizes.get):
        #print "%-60s %11d (%dMB)" % (domain, sizes[domain], int(sizes[domain]/1024/1024))
        temp = "%-60s %11d (%dMB)" % (domain, sizes[domain], int(sizes[domain]/1024/1024))
        fily.write(temp)
        fily.write("\n")
    fily.close()
    return mbdx, hash_dic

def printHelp(argv):
    print 
    print "This is Help for", argv[0], "script  created by Alexander Ryzhko for Iphone Geolocation Forensics." 
    print "The script goes through all files crowling through images and databases extracting IPs and Geolocation information" 
    print "Also creates KML files importable to Google Earth"
    print "How to use:\n\t$ python", argv[0],  "FileSourceFolder"
    print "Optional Parameters:"
    print "  -h \t             -> Output this help message"
    print "  -z \t             -> save as KMZ instead of KML"
    print "  -a \t             -> save all in one kml/kmz file instead one per a database"
    print "  -m \t             -> print more information downing scipt run"
    print "  -hit \t             -> save files with GEOlocation info"
    print "  -st \t             -> sort files in folders based on the fie type"
    print "  -so \t             -> parse the files based on original names"
    print "  -rn \t             -> rename files with found original names"
    print "  -o DirName \t     -> specify output directory name (within running directory)"
    print "  -db dbName \t     -> database for IP geolocation, default = GeoLiteCity.dat"
    print "  -json fileName     -> add hash dictionary to load from a json file"
    print "  -s FileName \t     -> save hash dictionary created from manifest as json"
    print "  -d exDiscr \t     -> add additional discription for databases pull out"
    exit()
def setup(argv):
    global hash_dic
    hash_dic = {}
    Manifest_mbdb = 1
    jsonf = 1
    hash_dic_name = 'hash_dic.json'
    #main argument
    if("-h" in argv ):
            printHelp(argv)
    if len(argv) > 1:
        dir_name = argv[1]
    else:
        print "ERROR: No direcoroty given"
        printHelp(argv)

    #optional arguments
    if len(argv) > 2:
        argstr = " ".join(argv[2:])
        argstr = ' ' + argstr + ' '
        if("-z" in argv):
            global KMZ
            KMZ = True
        if("-a" in argv):
            global BIG_KML
            BIG_KML = True
        if("-m" in argv):
            global MORE
            MORE = True
        if("-hit" in argv):
            global HIT
            HIT = True
        if("-st" in argv):
            global SORT_TYPE
            SORT_TYPE = True
            print "Sorting by Type"
        if("-so" in argv):
            global SORT_ORIGINAL 
            SORT_ORIGINAL = True
            print "Sorting in Original Order"
        if("-rn" in argv):
            global RENAME
            RENAME = True
            print "File Renaming"
        if("-o" in argv):
            global output_dir
            tmp = argstr.split(" -o ")[1].split()
            if tmp:
                output_dir = tmp[0]

        if("-db" in argv):
            global IPGeoDB
            tmp = argstr.split(" -db ")[1].split()
            if(tmp):
                IPGeoDB = tmp[0]
            #IPGeoDB = argstr.split(" -db ")[1].split()[0]
        if("-json" in argv):
            tmp = argstr.split(" -json ")[1].split()
            if(tmp):
                hash_dic_name = tmp[0]
        if("-d" in argv):
            words = []
            x = argstr.split(" -d ")[-1].split()
            if(x):
                x = x[0]
            while(x):
                words +=[x]
                print "The following additional words:"
                for word in words:
                    print word,
                x = raw_inpt("additional words or press ENTER:")
            global wlist
            wlist = wlist + words
        if("-s" in argv):
            x = argstr.split(" -s ")[-1].split()
            global SAVE_JSON
            if(x): 
                SAVE_JSON = x[0]
            else: 
                SAVE_JSON = "Hash_dictionary_iphone_Files.json"
    makeOutputDir(output_dir)
    try:
        with open(hash_dic_name) as f:
            print "Loading", hash_dic_name
            hash_dic = dict(hash_dic.items() + (json.load(f)).items() )
    except:
        if(hash_dic_name != 'hash_dic.json'):
            print "Couldn't load hash_dictionary"
        jsonf = 0
    try:
        print "Processing Manifest.mbdb ..."
        #print dir_name
        mbdx, hd = manifestParse(dir_name + '/')
        hash_dic = dict(hash_dic.items() + (hd.items() ))
    except Exception, e:
        #a =e
        print "Couldn't process Manifest.mbdb"
        Manifest_mbdb = 0 
        #do import of dictionary from json file
    if(not(Manifest_mbdb + jsonf)):
        #print a
        print "ERROR:Couldn't craete Hash dictionary, DICTIONARY:",
        #print hash_dic 
        if(raw_input("Please press ENTER to comtinue or enter anything else to quit")):
            exit()
        
    return dir_name 

def main(argv):
    IpDBs = [] 
    SQlDbs = []
    FOLDERS = []
    dir_name = setup(argv)  
    try:
        print "Loading", IPGeoDB
        global gi
        gi = pygeoip.GeoIP(IPGeoDB, pygeoip.MEMORY_CACHE)  
    except:
        print "ERROR: couln't load IP database"
        IP = False
    ImgaDatas = []
    types = []
    counter = 0
    percent = 0
    #print "Sorting",
    # try:
    #     typ = subprocess.check_output(["mkdir",output_dir])
    #     typ = subprocess.check_output(["mkdir",output_dir +'/' + GEO_IP_folder[:-1]])
    #     typ = subprocess.check_output(["mkdir",output_dir +'/' + GEO_found_folder[:-1]])
    # except:
    #     #print e
        # pass
    #print "HAHA"
    #print "Directory Name", dir_name
    for dirname, dirnames, filenames in os.walk(dir_name):
        nFiles = len(filenames)
        print "Number of Files:", nFiles
        # if(not(counter)):
        #     print  nFiles, "files",
        #print filenames
        for fn in filenames:
            #print "File:", fn
            counter += 1
            if(counter % 100 == 0):
                print "\t\t\t\tProcessed:", str(100*counter/nFiles) + "% (" , counter, "out of", nFiles, ")" 
            ffn = dirname  + '/' + fn
            try:
                typ = subprocess.check_output(["file",ffn])
            except Exception, e:
                if(MORE):
                    print e
                continue
            #print typ
            typ = typ.split(":")[1]
            typ1 = typ.split()[0]
            typ = typ1 + "_folder"
            file_type = typ1.lower()
            if (fn in hash_dic ):
                new_fn = hash_dic[fn]#.split('/')[-1]
            else:
                new_fn = fn
            if file_type == "sqlite":
                geolist, iplist = sqlCrowle(ffn, new_fn)
                if(geolist):
                    if(BIG_KML):
                        SQlDbs += [geolist]
                    else:
                        SQL_KML(geolist)
                    #subprocess.check_output(["cp",ffn, '2iphoneData2/' + fn])
                    if(MORE):
                        print "found Geo", new_fn
                    if(HIT):
                        try:
                            message = subprocess.check_output(["cp", ffn, output_dir+ '/'  +GEO_hit_files_folder+ '/' + ffn.split("/")[-1]])
                        except:
                            pass
                if(iplist):
                    if(BIG_KML):
                        IpDBs += [iplist]
                    else: 
                        SQL_IP_KML(iplist)
                    #subprocess.check_output(["cp",ffn, '2iphoneData2/' + fn])
                    if(MORE):
                        print "found valid IPs"
                    if(HIT):
                        try:
                            message = subprocess.check_output(["cp", ffn, output_dir+ '/'  +GEO_hit_files_folder+ '/' + ffn.split("/")[-1]])
                        except:
                            pass
            if file_type == "jpeg" :
                point = imageData(ffn)
                if(point != None):
                   # subprocess.check_output(["cp",ffn, '2iphoneData2/' + fn])
                    #print [ point + [new_fn]]
                    ImgaDatas += [ point + [new_fn + '\n' + ffn]]
                    if(HIT):
                        try:
                            message = subprocess.check_output(["cp", ffn, output_dir+ '/'  +GEO_hit_files_folder+ '/' + ffn.split("/")[-1]])
                        except:
                            pass
            #print "SORT_ORIGINAL", SORT_ORIGINAL
            if(SORT_ORIGINAL):
                #print "try"
                folderString = dirname 
                for folder in new_fn.split('/')[:-1]:
                    folderString = folderString + '/' +  folder
                    if(not( folderString in FOLDERS)):
                        try:
                         message = subprocess.check_output(["mkdir", folderString ])
                         FOLDERS+=[folderString]
                        except:
                          pass
                try:
                    subprocess.check_output(["mv",ffn, dirname + '/' +  new_fn])
                    #subprocess.check_output(["rm", ffn  ])
                except Exception, e:
                    if(MORE):
                        print e  
            elif(SORT_TYPE):
                if (not( typ in types)):
                    types +=[typ]
                    try:
                         message = subprocess.check_output(["mkdir", dirname+ '/'  +typ])
                    except:
                        pass
                try:
                    subprocess.check_output(["mv",ffn, dirname + '/' + typ + '/' + new_fn.split('/')[-1]])
                    #subprocess.check_output(["rm", ffn  ])
                except Exception, e:
                    if(MORE):
                        print e
            elif(RENAME):
                #print "REEEEEEEEEEEEEEEEEEEEEENNNNNNNNNNNNNNNNNNNNNAAAAAAAAAAAME!"
                try:
                    subprocess.check_output(["mv",ffn, dirname + '/' +  new_fn.split('/')[-1] ])
                except Exception, e:
                    if(MORE):
                        print e
            #printProgress(nFiles,counter,percent)
    if(BIG_KML):
        print "Saving KML/KMZ"
        kmlAll([save_KML_IMG_as, ImgaDatas], IpDBs, SQlDbs)
    else:
        IMG_KML([save_KML_IMG_as, ImgaDatas]) 
    if(SAVE_JSON):
        with open(output_dir + '/'+ SAVE_JSON, 'wb') as fp:
            json.dump(hash_dic, fp)
    print "[Done]"
if __name__ == '__main__':
    main(sys.argv)