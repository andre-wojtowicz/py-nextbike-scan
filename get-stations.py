#!/usr/bin/python3

# run as PYTHONIOENCODING=utf-8 python3 -i get-stations.py

import datetime
import json
import logging
import os
import requests
import sys
import tempfile
import zipfile

SCRIPT_RUN_DATE_TIME   = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")

DATA_DIR               = "data"
ZIP_STATIONS_LIST      = "{0}_sl.zip".format(SCRIPT_RUN_DATE_TIME)
JSON_STATIONS_LIST     = "{0}_sl.json".format(SCRIPT_RUN_DATE_TIME)
ZIP_BIKES_LIST         = "{0}_bl.zip".format(SCRIPT_RUN_DATE_TIME)
XML_BIKES_LIST         = SCRIPT_RUN_DATE_TIME + "_{0}.xml"

LOGGING_FILENAME       = "py-nextbike.log"
LOGGING_ENCODING       = "utf-8"
LOGGING_FORMAT         = "%(asctime)s : %(levelname)s : %(message)s"
LOGGING_DATE_FORMAT    = "%Y-%m-%d %H:%M:%S"
LOGGING_LEVEL          = logging.WARNING

URL_STATIONS_LIST      = "https://api.nextbike.net/maps/nextbike-live.json?lat={0}&lng={1}&distance={2}"
URL_BIKE_LIST          = "https://api.nextbike.net/api/getBikeList.xml?apikey={0}&place={1}&show_errors={2}"

DATA_LAT               = "52.4086"
DATA_LNG               = "16.9341"
DATA_DISTANCE          = "45000"
DATA_APIKEY            = "TR6EHaaNTSFGFmMt"
DATA_SHOW_ERRORS       = "1"

HEADER_ACCEPT          = "application/json, text/plain, */*"
HEADER_ACCEPT_ENCODING = "gzip, deflate"
HEADER_ACCEPT_LANGUAGE = "pl-PL"
HEADER_CONNECTION      = "Keep-Alive"
#HEADER_CONTENT_LENGTH  = "0"
HEADER_HOST            = "api.nextbike.net"
HEADER_ORIGIN          = "https://webview.nextbike.net"
HEADER_REFERER         = "https://webview.nextbike.net/"
HEADER_USER_AGENT      = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586"

HEADER_CONTENT_TYPE    = "Content-Type: application/x-www-form-urlencoded; charset=utf-8"

HTTP_STATUS_CODE_OK    = 200

# -------------------------------------------------------------------

logging_handler = logging.FileHandler(filename = LOGGING_FILENAME, 
                                      encoding = LOGGING_ENCODING)
logging_formatter = logging.Formatter(fmt      = LOGGING_FORMAT,
                                      datefmt  = LOGGING_DATE_FORMAT)
logging_handler.setFormatter(logging_formatter)
logging_handler.setLevel(LOGGING_LEVEL)

logger = logging.getLogger()
logger.addHandler(logging_handler)

# -------------------------------------------------------------------

if os.environ.get("PYTHONIOENCODING") != "utf-8":
    logger.error("Run script with system env PYTHONIOENCODING=utf-8")
    sys.exit(1)

# TODO: add proxy

if not os.path.isdir(DATA_DIR):
    os.mkdir(DATA_DIR)

try:
    sl_r = requests.post(
                url = URL_STATIONS_LIST.format(DATA_LAT, DATA_LNG, DATA_DISTANCE), 
                headers = { "Accept" :          HEADER_ACCEPT,
                            "Accept-Encoding" : HEADER_ACCEPT_ENCODING,
                            "Accept-Language" : HEADER_ACCEPT_LANGUAGE,
                            "Connection" :      HEADER_CONNECTION,
                            #"Content-Length" :  HEADER_CONTENT_LENGTH,
                            "Host" :            HEADER_HOST,
                            "Origin" :          HEADER_ORIGIN,
                            "Referer" :         HEADER_REFERER,
                            "User-Agent" :      HEADER_USER_AGENT }
            )
except Exception as e:
    logger.error(e.strerror)
    sys.exit(1)

if sl_r.status_code == HTTP_STATUS_CODE_OK:

    if len(sl_r.text) == 0:
        logger.error("Stations list empty text")
        sys.exit(1)

    try:
        sl_data = sl_r.json()
    except Exception as e:
        logger.error(e.strerror)
        sys.exit(1)

    tmp = tempfile.mkstemp()
    f = open(tmp[1], "w")
    json.dump(sl_r.json(), open(f.name, "w", encoding = "utf-8"), ensure_ascii = False)
    f.close()
    sl_zf = zipfile.ZipFile(os.path.join(DATA_DIR, ZIP_STATIONS_LIST), "w", zipfile.ZIP_DEFLATED)
    sl_zf.write(f.name, JSON_STATIONS_LIST)
    sl_zf.close()
    os.unlink(f.name)
    
    bl_zf = zipfile.ZipFile(os.path.join(DATA_DIR, ZIP_BIKES_LIST), "w", zipfile.ZIP_DEFLATED)  
    
    if "countries" not in sl_data.keys():
        logger.error("Stations list no countries")
        sys.exit(1)
    
    for country_data in sl_data["countries"]:
        
        if "cities" not in country_data.keys():
            logger.error("Stations list no cities")
            sys.exit(1)
        
        for city_data in country_data["cities"]:
            
            if "places" not in city_data.keys():
                logger.error("Stations list no places")
                sys.exit(1)
            
            for place_data in city_data["places"]:
                
                if "number" not in place_data.keys():
                    logger.error("Stations list no number")
                    sys.exit(1)
                
                try:
                    bl_r = requests.post(
                        url = URL_BIKE_LIST.format(DATA_APIKEY, place_data["uid"], DATA_SHOW_ERRORS),
                        headers = { "Accept" :          HEADER_ACCEPT,
                                    "Accept-Encoding" : HEADER_ACCEPT_ENCODING,
                                    "Accept-Language" : HEADER_ACCEPT_LANGUAGE,
                                    "Connection" :      HEADER_CONNECTION,
                                    "Content-Type" :    HEADER_CONTENT_TYPE,
                                    #"Content-Length" :  HEADER_CONTENT_LENGTH,
                                    "Host" :            HEADER_HOST,
                                    "Origin" :          HEADER_ORIGIN,
                                    "Referer" :         HEADER_REFERER,
                                    "User-Agent" :      HEADER_USER_AGENT }
                    )
                except Exception as e:
                    logger.error(e.strerror)
                    sys.exit(1)
                
                if bl_r.status_code == HTTP_STATUS_CODE_OK:
                    
                    if len(bl_r.text) == 0:
                        logger.warning("Bikes list [{0} - {1} - {2} - {3}] empty text".format(country_data["country_name"], city_data["name"], place_data["name"], place_data["number"]))
                        sys.exit(1)
                    
                    bl_zf.writestr(XML_BIKES_LIST.format(place_data["uid"]), bl_r.text)
                    
                else:
                    logger.warning("Bikes list [{0} - {1} - {2} - {3}] status code {4}".format(country_data["country_name"], city_data["name"], place_data["name"], place_data["number"], bl_r.status_code))
        
    bl_zf.close()
                    
else:
    logger.error("Stations list status code {0}".format(sl_r.status_code))
    sys.exit(1)
    