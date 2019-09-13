#!/usr/bin/python

import sys
from suds import null, WebFault
from suds.client import Client
import logging
import datetime
import numpy

username = 'fortmcas'
apiKey = '113dbde052d45892c914639637c8a6a41913ba6e'
url = 'http://flightxml.flightaware.com/soap/FlightXML2/wsdl'

logging.basicConfig(level=logging.INFO)
api = Client(url, username=username, password=apiKey)

api.service.SetMaximumResultSize(200)

def get_inflight_data(latitude, longitude, altitude_feet, delta_miles, delta_feet):
    delta_degrees = delta_miles/69.0
    min_lat = str(latitude - delta_degrees)
    max_lat = str(latitude + delta_degrees)
    min_long = str(longitude - delta_degrees)
    max_long = str(longitude + delta_degrees)
    min_alt = str((altitude_feet - delta_feet)/100)
    max_alt = str((altitude_feet + delta_feet)/100)


    search_string = "{range lat " + min_lat + " " + max_lat + "} {range lon "\
    + min_long + " " + max_long + "} {< alt " + max_alt + "} {> alt " + min_alt\
    + "}"

    print search_string
    result = api.service.SearchBirdseyeInFlight(search_string, 15, 0)
    return  result

def package(dataset, file_ID):
    print('starting historical dataset packaging')
    f = open(file_ID, 'w')
    f.write(repr(dataset))
    f.close()
    print('finished historical dataset packaging')

def get_preflight_data(latitude, longitude, max_ceiling, date_time_obj, time_delta_minutes):
    date_time_epoch = (date_time_obj - datetime.datetime(1970, 1, 1)).total_seconds()
    time_delta_seconds = time_delta_minutes * 60
    day_adjust = 24*60*60
    now_epoch = (datetime.datetime.now() - datetime.datetime(1970,1,1)).total_seconds()
    condition = (date_time_epoch - time_delta_seconds) < now_epoch
    date_time_epoch = date_time_epoch - day_adjust
    time_window_min = date_time_epoch - time_delta_seconds
    time_window_max = date_time_epoch + time_delta_seconds
    if(condition):
        raise InvalidTimeWindow('Runtime must be before launch window center minus time delta')
    delta_miles = (28/3) * time_delta_minutes
    delta_degrees = delta_miles/69.0
    min_lat = str(latitude - delta_degrees)
    max_lat = str(latitude + delta_degrees)
    min_long = str(longitude - delta_degrees)
    max_long = str(longitude + delta_degrees)
    max_ceiling = str(max_ceiling)
    time_window_min = str(int(time_window_min))
    time_window_max = str(int(time_window_max))
    now_epoch = str(int(now_epoch - day_adjust + (60*60*4)))
    search_string = "{range lat " + min_lat + " " + max_lat + "} {range lon " + min_long + " " + max_long + "}\
    {< alt " + max_ceiling + "} {range clock " + time_window_min + " " + time_window_max +  "}"
    flight_ids = []
    print search_string
    result = api.service.SearchBirdseyeInFlight(search_string, 200, 0)
    result = result.aircraft
    track_search_string = ''
    historical_tracks = []
    for i in result:
        historical_tracks.append(api.service.GetHistoricalTrack(i.faFlightID))
    package(historical_tracks, 'historical_tracks.txt')
    return historical_tracks
