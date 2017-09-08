#!/usr/bin/python

import requests

URL_STATIONS_LIST = "https://api.nextbike.net/maps/nextbike-live.json?lat={0}&lng={1}&distance={2}"
URL_BIKE_LIST     = "https://api.nextbike.net/api/getBikeList.xml"

DATA_LAT      = "52.3588"
DATA_LNG      = "16.8456"
DATA_DISTANCE = "45000"

DATA_APIKEY      = "TR6EHaaNTSFGFmMt"
DATA_SHOW_ERRORS = "1"

HEADER_ACCEPT          = "application/json, text/plain, */*"
HEADER_ACCEPT_ENCODING = "gzip, deflate"
HEADER_ACCEPT_LANGUAGE = "pl-PL"
HEADER_CONNECTION      = "Keep-Alive"
#HEADER_CONTENT_LENGTH  = "0"
HEADER_HOST            = "api.nextbike.net"
HEADER_ORIGIN          = "https://webview.nextbike.net"
HEADER_REFERER         = "https://webview.nextbike.net/"
HEADER_USER_AGENT      = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586"

HEADER_CONTENT_TYPE = "Content-Type: application/x-www-form-urlencoded; charset=utf-8"

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

if sl_r.status_code == 200:
    sl_data = sl_r.json()
    