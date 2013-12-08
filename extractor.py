from PIL import Image
from PIL.ExifTags import TAGS
import os
import simplekml
import sqlite3
import time
import datetime
import hashlib
import pygeoip

IP = True
wlist = ["LATITUDE", "LONGITUDE", "TIMESTAMP", "DATE"]
gi = pygeoip.GeoIP('GeoLiteCity.dat', pygeoip.MEMORY_CACHE)

'''
Check for images only for CamerasPhotoes
'''

def IP_info_By_IP(IP):
    '''returns IP info dictionary including location based on the IP adres, if failed returns None'''
    try:
        return gi.record_by_addr(IP)
    except Exception, e:
        #print e
        return None


def converTS(TS, earliest_possible_date = '2001-01-01 00:00:00' ):
    unix_base_TS = int(time.mktime(time.strptime('2001-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')))
    before_iphone_time = int(time.mktime(time.strptime('2006-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')))
    trashold = before_iphone_time - unix_base_TS 
    if (type(TS) == type("String")):
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
        return str(datetime.datetime.fromtimestamp(TS)) + " #(UNIX TS)"

def imageData(ffn):
    "This function is modification of a method written by Grisha Kumar"
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
        #print exifTime
        e_time = ('-'.join(exifTime.split()[0].split(":"))) + ' ' + exifTime.split()[1]
        # e_timeTemp = exifTime.split()[0].split(":")
        # e_time = str(e_timeTemp[1]) + "/" + str(e_timeTemp[2]) + "/" + str(e_timeTemp[0][2:]) + " " + str(exifTime.split()[1]) 
        #print "latitude:", lat,
        #print "longtitude:",lon, 
       # print "Time:", e_time 
        return [lat, lon, e_time, ffn.split('/')[-1]]
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
    #print imglist
    kml = simplekml.Kml()
    for point in imglist[-1]:
        # try:
            #for kml logtitude goes first
        kml.newpoint(name=point[2], description=point[-1], coords=[(point[1], point[0])] )
        # except Exception, e:
        #     print point
        #     print e
        #     exit()
    kml.save(imglist[0] + '.kml')
    #print imglist[0] + '.kml'


#IMG_KML(extractImage("iphonedata/JPEG_folder"))
def SQL_KML(dataBaseList):
    #print dataBaseList
    #print imglist
    #print
    db_name = dataBaseList[0]
    #print "DB_name: ", db_name
    kml = simplekml.Kml()
    #print
    #print "LISTS:",dataBaseList[1]
    for table in dataBaseList[1]:
        table_name = table[0]
       # print
      #  print "table: ",  table

        for point in table[1]:
         #   print "point: ", point
            # try:
            #for kml logtitude goes first
           #print point
            discr = ""
            #discr = str(point[1][0]) + ":Longtitude " + str(point[0][1]) + ":Latitute\n"
            for i in point:
                discr += str(i[0]) + ":" + str(i[1]) +'\n'


            discr += "table:" + table_name +'\n'
            discr += db_name 
            point_name = ''
            isTS =0;
            for i in point:
                if(wlist[2] in i[0].upper()):
                    isTS =1
                    point_name = i[1]
                    break 
                if(wlist[3] in i[0].upper()):
                    isTS =1
                    point_name = i[1]

            if(not(isTS)):
                #point_name = table_name+':'+db_name.split('/')[-1] +':' + hashlib.md5(str(point[0][1]) + str (point[1][1])).hexdigest()[:8]
                point_name =  hashlib.md5(str(point[0][1]) + str (point[1][1])).hexdigest()[:8]

                
            kml.newpoint(name=point_name , description=discr, coords=[(point[1][1], point[0][1])] )
          


          
                
               
    save_as = db_name.split('/')[-1] + '.kml'
    kml.save(save_as)


def sqlCrowle(dbName):
    
    wlistStr = ' '.join(wlist)
    con = sqlite3.connect(dbName)
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    db_results= []
    table_names = []
    for table in tables:
        table_names += [str(table[0])]
    for table in table_names:
        #empty_table = 0
        lat_name = ''
        long_name = ''
        date_name = ''
        cursor.execute("SELECT * FROM "+ str(table))
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
        if(date_name):
            list_valid_culums = [lat_name, long_name, date_name ] + list_valid_culums
        else:
           list_valid_culums = [lat_name, long_name] + list_valid_culums
        

        #culum_names_str = ' '.join(culum_names_str)
        #list_valid_culums = []
        valid_rows = []
        valid_IP_info = []
        #locations = []
        #if((wlist[0] in culum_names_str) and (wlist[1] in culum_names_str)):
        if((lat_name !='') and (long_name != '')):
            query = "SELECT "
            all_culums =list_valid_culums
            if(IP):
                all_culums = all_culums + IP_culums

            #for v_culum in list_valid_culums[:-1]:
            for v_culum in all_culums[:-1]:
                query += v_culum + ", "
            # if(IP)
            #     for IP_culum in IP_culums:
            #         if(not(IP_culum in list_valid_culums)):
            #             query += IP_culum + ", "
            query += list_valid_culums[-1] + "  FROM "+ str(table)
            not_empty = 0
            for crow in con.execute(query):
                row =crow
                if (row[0] and row[1]):
                    add_row = []
                    #table_results += [row]
                    not_empty = 1
                    for i in range(len(row)):
                        # if list_valid_culums[i] =='Timestamp':
                        #     print row[i], type(row[i])
                        if(row[i]):
                            current_culum = all_culums[i]
                            if(current_culum in IP_culums):
                                IP_info = 
                            if(current_culum in list_valid_culums): 
                                ts = converTS(row[i])
                                if(ts):
                                    add_row += [ [all_culums[i], ts] ]
                                else:
                                    add_row += [ [all_culums[i], row[i]] ]


                    valid_rows += [add_row]
            if(not_empty):
                db_results += [   [str(table),   valid_rows]     ]



            # for column in culum_names:
            #     for word in wlist:
            #         if word in column:
            #             list_valid_culums += [column]
            #             break
            #for column in list_valid_culums:
            #none_empty = 1
            #while(1):
            #cursor.execute("SELECT " + str(column) + " FROM"+ str(table))
            # condition = 0
            # if(date_name!=''):
            #     #print "No date"
            #     #cursor.execute("SELECT " + lat_name + ", " + long_name + ", " + date_name +"  FROM "+ str(table))
            #     for row in con.execute("SELECT " + lat_name + ", " + long_name + ", " + date_name + "  FROM "+ str(table)):
            #         condition = 1
            #         print row
            #         table_results += [row]

            # else:
            #     #print "here"
            #     for row in con.execute("SELECT " + lat_name + ", " + long_name + "  FROM "+ str(table)):
            #         condition = 1
            #         table_results += [row]

            #     exit(0)
            #     cursor.execute("SELECT " + lat_name + ", " + long_name + "  FROM "+ str(table))

            # result = cursor.fetchall()
            # print result
            # if(len(result[0])<1):
            #     break
            # table_results += [result]
            # if(condition):
            #     db_results += [    [ str(table), lat_name, long_name,  date_name ],  table_results      ]
    if (len(db_results)):
        return [dbName, db_results]

#print sqlCrowle("b.db")
            #     if (result )
            #     if len(result <1):
            #         empty_table = 1
            #         break
            #     results +=[colum, [result]]
            # if(not(empty_table = 0)):
            #     while (len(results[0][1])>0):
            #         for result in results:
            #             if wlist[0] in result[0]:
d_name = "/media/heisenberg/0f5746c4-8ff7-45b4-acd1-3a1bedd9d050/iphonedata/SQLite_folder"
x =0
# for dirname, dirnames, filenames in os.walk(d_name):
#         for fn in filenames:
#             r =  sqlCrowle(d_name+'/'+fn)
            
            # if(r):
                #SQL_KML(r)

                # if(x>1):
                #     SQL_KML(r)

                # x +=1
                
            #     # print r
            #     # print 20*'='
IP = "sdasdadsdfsdfsdfsdfsdfsdfsdfsdfsdfsfsdfsdf.sdf.sdf.sdf.sdfs.df.asd"
inf0 =[]

