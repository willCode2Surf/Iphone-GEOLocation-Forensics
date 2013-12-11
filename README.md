Iphone GEOLocation Forensics
============================
https://github.com/AlexanderRyzhko/Iphone-GEOLocation-Forensics

https://www.youtube.com/watch?v=E-de1qtjdDY

Script analyzing Iphone files looking for GeoLocations
To run the script the following extra modials have to be installed:
  pygeoip - for ip geolocation lookup
  PIL    - for Image metadata extraction
  simplekml - for creating kml file with cordinates for google map
  sqlite3   - for crowling though sqls on iphone

Also database for IP look up is needed, if not given script will not collect IP info.
  Database used was GeoLiteCity.dat from http://dev.maxmind.com/geoip/legacy/geolite/

For information hot to use it run the script with -h option

Firt the script decodes the hashed names of the file from monifest file. Then the script goes 
through every single file in the folder.  
If the file is an image script tries to extract geolocation information from it.
If file is SQL database scripts looks for geolocations and Date or timestamps along 
with any additional discription specified by user. Script also looks for IP information in SQL databases.
Once IP information is observed it is traslated using GeoLiteCity.dat or any other users database.

Once information is collected it is ploted in KML or KMZ file format which is easy importable to Google Earth.
User may save the dictionary produce ti crach the hashed filenames and use it for other analysis. 
Script has also option of saving files with geolocation as well as sorting file and putting in the directories 
as if they were on the phone orinaly. Also script can sort files based on the files type. 
