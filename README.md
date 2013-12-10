Iphone_GEOLocation_Forensics
============================
Script analyzing Iphone files looking for GeoLocations
To run the script the following extra modials have to be installed:
  pygeoip - for ip geolocation lookup
  PIL    - for Image metadata extraction
  simplekml - for creating kml file with cordinates for google map
  sqlite3   - for crowling though sqls on iphone

Also database for IP look up is needed, if not given script will not collect IP info.
  Database used was GeoLiteCity.dat from http://dev.maxmind.com/geoip/legacy/geolite/

for run the script with -h option
