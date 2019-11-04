import re
import datetime
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import mpl_toolkits.mplot3d.axes3d as p3
import sys
import random
import time
import pandas
import json
import requests
import pickle
import math
import gmplot 
import statistics
import pandas as pd
import subprocess
from math import sin, cos, sqrt, atan2, radians

from mpl_toolkits.mplot3d import Axes3D

import plotly
import plotly.graph_objs as go
import plotly.express as px


#-----------------------------------------------------------------------------
# Written by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def APRS(callsign_entry,APRS_apikey):
    # Figure out what variable type "callsign" is and convert them to appropriate type
    if (isinstance(callsign_entry,str) == True):
        callsign = callsign_entry
    if (isinstance(callsign_entry,list) == True):
        callsign = ",".join(callsign_entry)
        
    # Pull data from APRS
    json_response= requests.get("http://api.aprs.fi/api/get?name="+callsign+"&what=loc&apikey="+APRS_apikey+"&format=json")
    aprs_dict = json.loads(json_response.text) 
    
    # If callsign is a string, just take the data from that as output
    if (isinstance(callsign_entry,str) == True):
        APRS_data = aprs_dict['entries'][0]
        
    # If multiple callsigns are given, find one that has the most recent data and use that for output
    if (isinstance(callsign_entry,list) == True): 
        latestTime = 0;
        for callsign_instance in range(1,len(aprs_dict['entries'])):
            last_time = int(aprs_dict['entries'][callsign_instance]['lasttime'])
            if (last_time > latestTime):
                lastestTime = last_time
                bestCallsign = callsign_instance;
        APRS_data = aprs_dict['entries'][bestCallsign]
        
    return APRS_data

#-----------------------------------------------------------------------------
# Written by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def send_slack(messageString,messageType,recipient,slackURL):
    icon = "ghost"
    botUsername = "Python Bot"
   
    if messageType == 'dm':
        messageType = "message"
        
    if messageType == 'channel':
        messageType = "channel"
    
    curlcommand = "curl -X POST --data-urlencode "
    payloadcommand = '"payload={\\"'+messageType+'\\": \\"'+recipient+'\\", \\"username\\": \\"' + botUsername + '\\", \\"text\\": \\"' + messageString + '\\", \\"icon_emoji\\": \\":' + icon + ':\\"}" ' + slackURL
    command = curlcommand+payloadcommand
    #os.system(command)
    subprocess.run(command)

#-----------------------------------------------------------------------------
# Written by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def package(dataset,prediction_ID,flightID):
    pickle_out = open(flightID+'_'+str(prediction_ID)+".pickle","wb")
    pickle.dump(dataset, pickle_out)
    pickle_out.close()
    
#-----------------------------------------------------------------------------
# Written by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def unpackage(prediction_ID,flightID):
    #path = ''
    #pickle_in = open(path+'\\'+prediction_ID+".pickle","rb")
    pickle_in = open(flightID+'_'+str(prediction_ID)+".pickle","rb")
    dataset = pickle.load(pickle_in)
    return dataset

#-----------------------------------------------------------------------------
# Written by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def unpackageGroup(flightID,numPredictions):
    allPredictions = dict()
    for predictionID in range(1,numPredictions+1):
        data = unpackage(predictionID,flightID)
        allPredictions[str(predictionID)] = data
    return allPredictions

#----------------------------------------------------------------------------- 
# Written by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def launchPrediction(payload,balloon,parachute,helium,lat,lon,launchTime,tolerance,ARcorr):
    
    # Do initial prediction with lanuch from desired lat/lon landing spot
    data = prediction(payload,balloon,parachute,helium,lat,lon,-1,1,launchTime,-1,0.1,0,-1)
    # find difference in lat and lon (desired - actual)
    deltaLat = lat - data['Landing Lat']
    deltaLon = lon - data['Landing Lon']
    
    newLat = lat + deltaLat
    newLon = lon + deltaLon    
    
    withinBounds = 0
    degrees_to_radians = math.pi/180.0
    
    while withinBounds == 0:
        data = prediction(payload,balloon,parachute,helium,newLat,newLon,-1,1,launchTime,-1,0.1,0,-1)
        
        # phi = 90 - latitude
        phi1 = (90.0 - lat)*degrees_to_radians
        phi2 = (90.0 - data['Landing Lat'])*degrees_to_radians
        
        # theta = longitude
        theta1 = lon*degrees_to_radians
        theta2 = data['Landing Lon']*degrees_to_radians
               
        cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + math.cos(phi1)*math.cos(phi2))
        arc = math.acos(cos)
        distance = arc*3958.8*5280
        
        if distance <= tolerance:
            #print('Reached distance: '+str(distance)+' ft')
            break
        #print('Failed: '+str(distance)+' ft')
        
        # find difference in lat and lon (desired - actual)
        deltaLat = lat - data['Landing Lat']
        deltaLon = lon - data['Landing Lon']
        
        newLat = newLat + deltaLat
        newLon = newLon + deltaLon 
     
    launchLoc = dict()
    launchLoc['Lat'] = newLat
    launchLoc['Lon'] = newLon
    launchLoc['Tolerace'] = distance
    return launchLoc

#-----------------------------------------------------------------------------
# Written by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def coordShift(Lat1,Lon1,Lat2,Lon2):
#    deltaLat = Lat2 - Lat1
#    deltaLon = Lon2 - Lon1
#    degrees_to_radians = math.pi/180.0
#    
#    # phi = 90 - latitude
#    phi1 = (90.0 - Lat1)*degrees_to_radians
#    phi2 = (90.0 - Lat2)*degrees_to_radians
#    
#    # theta = longitude
#    theta1 = Lon1*degrees_to_radians
#    theta2 = Lon2*degrees_to_radians
#           
#    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + math.cos(phi1)*math.cos(phi2))
#    arc = math.acos(cos)
#    distance = arc*3958.8*5280
    
    # approximate radius of earth in km
    R = 6373.0
    
    lat1 = radians(Lat1)
    lon1 = radians(Lon1)
    lat2 = radians(Lat2)
    lon2 = radians(Lon2)
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c * 3280.84
    
    return distance
    
#-----------------------------------------------------------------------------
# Written by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def plotPrediction(data):
    fig = plt.figure(figsize=(40,35))
    ax = fig.gca(projection='3d')
    
    # Plot nominal prediction
    Color = 'red'
    lineWidth = 5
    Alpha=1
    ax.plot(data['TimeData']['Latitude'], data['TimeData']['Longitude'], data['TimeData']['Altitude'],color=Color,linewidth=lineWidth,alpha=Alpha)
    
    # Plot ensembles
    lineWidth = 1
    Alpha=0.4
    Color = 'blue'
    for ensembles in data['Secondary Tracks']:
        ax.plot(data['Secondary Tracks'][str(ensembles)]['Lat'],data['Secondary Tracks'][str(ensembles)]['Lon'],data['Secondary Tracks'][str(ensembles)]['Alt'],color=Color,linewidth=lineWidth,alpha=Alpha)
    
    plt.show()

#-----------------------------------------------------------------------------
# Written by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def PredictionAni(PredData,saving):
    def update_lines(num, dataLines, lines):
        for line, data in zip(lines, dataLines):
            line.set_data(data[0:2, :num])
            line.set_3d_properties(data[2, :num])
                    
        return lines
    
    # Make 3D figure
    fig = plt.figure(figsize=(30,25))
    ax = p3.Axes3D(fig)
    
    # Get lines
    flight = list()
    flight.append(np.array(PredData['TimeData'][['Latitude','Longitude','Altitude']]).transpose())
    for track in range(0,len(PredData['Secondary Tracks'])):
        newArray1 = np.array(PredData['SecTracksTimeDomain']['Lat'][str(track)].values)
        newArray2 = np.array(PredData['SecTracksTimeDomain']['Lon'][str(track)].values)
        newArray3 = np.array(PredData['SecTracksTimeDomain']['Alt'][str(track)].values)
        new = np.column_stack((newArray1,newArray2,newArray3))
        new = new.transpose()
        flight.append(new)
    data=flight
    
    # Create line objects
    lines = [ax.plot(dat[0, 0:1], dat[1, 0:1], dat[2, 0:1])[0] for dat in data]
    lines[0].set_alpha(1)
    lines[0].set_color('blue')
    lines[0].set_linewidth = 10
        
    for line in range(1,len(lines)):
        lines[line].set_alpha(0.20)
        lines[line].set_color('red')
        lines[line].set_linewidth = 1
    
    # Set Axes
    fontSize = 30
    ax.set_xlim3d([min(PredData['TimeData']['Latitude']), max(PredData['TimeData']['Latitude'])])
    #ax.set_xlabel('Latitude',fontsize=fontSize)
    
    ax.set_ylim3d([min(PredData['TimeData']['Longitude']), max(PredData['TimeData']['Longitude'])])
    #ax.set_ylabel('Longitude',fontsize=fontSize)
    
    ax.set_zlim3d([min(PredData['TimeData']['Altitude']), max(PredData['TimeData']['Altitude'])])
    #ax.set_zlabel('Altitude',fontsize=fontSize)
    
    # Create Animation
    line_ani = animation.FuncAnimation(fig, update_lines,frames=max(data[0].shape[1],data[1].shape[1]), fargs=(data, lines),interval=0.1, blit=True)
    plt.show()
    
    if saving == 1:
        print('Saving File...')
        line_ani.save('FlightPath.gif')

#-----------------------------------------------------------------------------
# Written by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def heatMap(data,apikey):
    lat_list = list(data['Landing Deviations']['Lat'])
    lon_list = list(data['Landing Deviations']['Lon'])   
    gmap = gmplot.GoogleMapPlotter(statistics.mean(lat_list),statistics.mean(lon_list),10)
    gmap.heatmap(lat_list,lon_list) 
    gmap.apikey = apikey
    gmap.draw( "C:\\dev\\MBURSTPython\\map.html" ) 

#-----------------------------------------------------------------------------
# Written by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def plotStations(loc):
    if loc == 'US':
        stationData = pd.read_csv(os.getcwd()+'\\StationList.txt',delimiter=' ',header=None)
    return stationData

#-----------------------------------------------------------------------------
# Written by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def plotFlight(flightID,predTotal,predLow,predHigh,plotEnsem,plotType):
    # Set plotly credentials 
    plotly.offline.init_notebook_mode()
    
    # Get all predictions data
    AllData = unpackageGroup(flightID,predTotal)
    print("All data read in")
    
    # Initialize variables 
    data = list()
    j = 0
    lat = list()
    lng = list()
    alt = list()
    times = list()
      
    # Iterate through predictions
    for prediction in AllData:
        ID = str(AllData[prediction]['Inputs']['Status']) + ',' + str(math.trunc(AllData[prediction]['Inputs']['Altitude']))
        
        # Get actual flight path
        lat.append(AllData[prediction]['Inputs']['Lat'])
        lng.append(AllData[prediction]['Inputs']['Lon'])
        alt.append(AllData[prediction]['Inputs']['Altitude'])
        times.append(AllData[prediction]['Inputs']['Launch Time'])
        
        # Plot nominal prediction data
        if predLow < int(prediction) < predHigh:  
            if plotType == '3':
                traceNom = go.Scatter3d(x = AllData[prediction]['TimeData']['Latitude'],y = AllData[prediction]['TimeData']['Longitude'],z = AllData[prediction]['TimeData']['Altitude'],mode='lines', line=dict(color='blue',width=1),name = str(AllData[prediction]['Inputs']['Status']) + ',' + str(math.trunc(AllData[prediction]['Inputs']['Altitude'])))
                data.append(traceNom)
            if plotType == '2A':
                traceNom = go.Scatter(x = AllData[prediction]['TimeData']['Altitude'].index,y = AllData[prediction]['TimeData']['Altitude'],mode='lines', line=dict(color='blue',width=1),name = str(AllData[prediction]['Inputs']['Status']) + ',' + str(math.trunc(AllData[prediction]['Inputs']['Altitude'])))
                data.append(traceNom)
            if plotType == '2L':
                traceNom = go.Scatter(x = AllData[prediction]['TimeData']['Longitude'],y = AllData[prediction]['TimeData']['Latitude'],mode='lines', line=dict(color='blue',width=1),name = str(AllData[prediction]['Inputs']['Status']) + ',' + str(math.trunc(AllData[prediction]['Inputs']['Altitude'])))
                data.append(traceNom)            
        
        
        # Plot ensemble data
        if predLow < int(prediction) < predHigh:  
            if plotEnsem:
                for track in AllData[prediction]['Secondary Tracks']:
                    if plotType == '3':
                        traceEns = go.Scatter3d(x = AllData[prediction]['Secondary Tracks'][track]['Lat'],y = AllData[prediction]['Secondary Tracks'][track]['Lon'],z = AllData[prediction]['Secondary Tracks'][track]['Alt'],mode='lines', line=dict(color='#1f77b4',width=0.2))
                        data.append(traceEns)
                    if plotType == '2A':
                        traceEns = go.Scatter(x = AllData[prediction]['Secondary Tracks'][track]['Alt'].index,y = AllData[prediction]['Secondary Tracks'][track]['Alt'],mode='lines', line=dict(color='#1f77b4',width=0.2))
                        data.append(traceEns)
                    if plotType == '2L':
                        traceEns = go.Scatter(x = AllData[prediction]['Secondary Tracks'][track]['Lon'],y = AllData[prediction]['Secondary Tracks'][track]['Lat'],mode='lines', line=dict(color='#1f77b4',width=0.2))
                        data.append(traceEns)
            
    # Arrange flight data in dataframe
    FlightPath = pd.DataFrame(index=times)
    FlightPath['lat'] = lat
    FlightPath['lon'] = lng
    FlightPath['alt'] = alt
    if plotType == '3':
        traceFlightPath = go.Scatter3d(x = FlightPath['lat'],y = FlightPath['lon'],z = FlightPath['alt'],mode='lines', line=dict(color='black',width=3),text=FlightPath.index,name='Flight Path')
        data.append(traceFlightPath)
    if plotType == '2A':
        traceFlightPath = go.Scatter(x = FlightPath['alt'].index,y = FlightPath['alt'],mode='lines', line=dict(color='black',width=3),text=FlightPath.index,name='Flight Path')
        data.append(traceFlightPath)
    if plotType == '2L':
        traceFlightPath = go.Scatter(x = FlightPath['lon'],y = FlightPath['lat'],mode='lines', line=dict(color='black',width=3),text=FlightPath.index,name='Flight Path')
        data.append(traceFlightPath)
      
    # Plot data      
    plotly.offline.plot(data, filename='Flight_'+flightID+'_'+plotType+'.html')
    
    return (AllData,data,FlightPath)
    
#-----------------------------------------------------------------------------
# Written by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def dataToCSV(FlightPath,flightID):
    FlightPath.to_csv('Flight'+flightID+'.csv',index_label = 'Time')    

#-----------------------------------------------------------------------------
# Originally written by Aaron J Ridley - https://github.com/aaronjridley/Balloons
# Modified by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def get_args(argv,queryTime,TESTINGtimeDiff):
    payload   = -1.0
    balloon   = -1.0
    parachute = -1.0
    helium    = -1.0
    lat       = -91.0
    lon       = -361.0
    alt       = -1.0

    nEnsembles = -1
    errors     = 0.2
    
    CurrentTime = 0.0

    CurrentYear  = int(time.strftime("%Y"))
    CurrentMonth = int(time.strftime("%m"))
    CurrentDay   = int(time.strftime("%d"))
    CurrentHour  = int(time.strftime("%H"))

    Day = -1
    Hour = -1

    date = datetime.datetime.now()
    sTimeNow = date.strftime('%Y-%m-%d %H:%M:%S')

    callsign = 'abcdef'
    BurstTime = 7.0*24.0*60.0*60.0
    hover = 50000.0

    IsZeroPressure = 0
    BalloonR = 0.0
    BalloonV = 0.0

    UseAprs = 0
    IsDescent = 0

    loss = 0.0

    update = 0

    for arg in argv:
        m = re.match(r'-callsign=(.*)',arg)
        if m:
            callsign = m.group(1)
        m = re.match(r'-payload=(.*)',arg)
        if m:
            payload = float(m.group(1))*LbsToKgs
        m = re.match(r'-balloon=(.*)',arg)
        if m:
            balloon = float(m.group(1))
        m = re.match(r'-r=(.*)',arg)
        if m:
            BalloonR = float(m.group(1))
        m = re.match(r'-v=(.*)',arg)
        if m:
            BalloonV = float(m.group(1))
        m = re.match(r'-zero',arg)
        if m:
            IsZeroPressure = 1
        m = re.match(r'-aprs',arg)
        if m:
            UseAprs = 1
        m = re.match(r'-update',arg)
        if m:
            update = 1
        m = re.match(r'-parachute=(.*)',arg)
        if m:
            parachute = float(m.group(1))*FtToMeters/2
        m = re.match(r'-helium=(.*)',arg)
        if m:
            helium = float(m.group(1))
        m = re.match(r'-loss=(.*)',arg)
        if m:
            loss = float(m.group(1))
        m = re.match(r'-de',arg)
        if m:
            IsDescent = 1
        m = re.match(r'-alt=(.*)',arg)
        if m:
            alt = float(m.group(1))
        m = re.match(r'-lat=(.*)',arg)
        if m:
            lat = float(m.group(1))
        m = re.match(r'-lon=(.*)',arg)
        if m:
            lon = float(m.group(1))
        m = re.match(r'-day=(.*)',arg)
        if m:
            Day = int(m.group(1))
        m = re.match(r'-currenttime=(.*)',arg)
        if m:
            CurrentTime = float(m.group(1))*60.0
        m = re.match(r'-ymd=(.*)',arg)
        if m:
            Ymd = m.group(1)
            m = re.match(r'(\d\d\d\d)(\d\d)(\d\d)',Ymd)
            if m:
                CurrentYear  = int(m.group(1))
                CurrentMonth = int(m.group(2))
                CurrentDay   = int(m.group(3))
            else:
                m = re.match(r'(\d\d)(\d\d)(\d\d)',Ymd)
                if m:
                    CurrentYear  = 2000 + int(m.group(1))
                    CurrentMonth = int(m.group(2))
                    CurrentDay   = int(m.group(3))
                else:
                    print("Can not understand format of -ymd=YYYYMMDD")
                    help = 1

        m = re.match(r'-hour=(.*)',arg)
        if m:
            Hour = int(m.group(1))

        m = re.match(r'-n=(.*)',arg)
        if m:
            nEnsembles = float(m.group(1))

        m = re.match(r'-error=(.*)',arg)
        if m:
            errors = float(m.group(1))
            if (errors > 1.0):
                errors=errors/100

        m = re.match(r'-bursttime=(.*)',arg)
        if m:
            BurstTime = float(m.group(1))*60.0

        m = re.match(r'-hover=(.*)',arg)
        if m:
            hover = float(m.group(1))
            print("Hover Altitude set!")
            print(hover)

    help = 0
    if payload < 0:
        print("Set payload=")
        help = 1
    if parachute < 0:
        print("Set parachute=")
        help = 1
    if balloon < 0: 
        print("Set balloon=")
        help = 1
    if helium < 0:
        print("Set helium=")
        help = 1
    if lat < -90:
        print("Set lat=")
        help = 1
    if lon < -360:
        print("Set lon=")
        help = 1
    if (IsZeroPressure):
        if (BalloonR == 0):
            print ("For Zero Pressure Balloon, must set balloon radius (-r=???)")
            help = 1
        if (BalloonV == 0):
            print ("For Zero Pressure Balloon, must set balloon volume (-v=???)")
            help = 1
        
    if help == 1:
        balloon = -1.0
        print("./balloon.py options:")
        print("            -balloon=mass of the balloon, acceptable values:")
        print("                     200, 300, 350, 450, 500, 600, 700, 800,")
        print("                     1000, 1200, 1500, 2000, 3000")
        print("                     for a zero pressure balloon, put the ")
        print("                     real mass of the balloon in grams.")
        print("            -payload=WEIGHT of payload (in lbs)")
        print("            -parachute=diameter of parachute (in feet)")
        print("            -helium=tanks of helium (typically between 1-2)")
        print("            -lat=Initial Latitude")
        print("            -lon=Initial Longitude")
        print("            -alt=Initial Altitude (feet)")
        print("            -descent (force descent mode - no ascent!)")
        print("        optional:")
        print("            -bursttime=N (time in minutes for FTU initiation)")
        print("            -update  (Update the weather file based on position - slow!)")
        print("            -aprs  (use the current APRS position as starting point - for real time!)")
        print("            -zero  (simulate a zero pressure balloon)")
        print("            -r=radius (for zero pressure balloon, in meters)")
        print("            -v=total volume of balloon (for zero pressure balloon, in meters^3)")
        print("            -hover=Altitude of neutral buoyant point (ZP balloon - although automatic now)")
        print("            -loss=percentage loss rate of helium through balloon (% per minute)")
        print("            -n=Number of Ensembles to run")
        print("            -error=fractional error for winds")
        print("                   (error in burst diam = error/4")
        print("                   (error in moles of helium = error/4")
        print("            -callsign=call sign of person running code ")
        print("            -html=html output file")
        print("            -cleanup will delete temporary files ")
        print("example: ")
        print("  ./balloon.py -payload=6.0 -balloon=1000 -parachute=6.0 -helium=1.5 -lat=42.0 -lon=-84.0")

    area = 2*pi*(parachute * ParachuteFudge)**2

    Year  = CurrentYear
    Month = CurrentMonth
    if (Day > -1):
        if (Day < CurrentDay):
            Month = Month + 1
            if (Month > 12):
                Month = 1
                Year = Year + 1
    else:
        Day = CurrentDay

    if (Hour < 0):
        Hour = CurrentHour

    #LaunchTime = datetime.datetime(Year,Month,Day,Hour,0,0)
    
    if queryTime == 'now':
        LaunchTime = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=TESTINGtimeDiff)
    if queryTime != 'now':
        LaunchTime = datetime.datetime.strptime(queryTime, '%Y-%m-%d %H:%M:%S')
        
    Year = LaunchTime.year
    Month = LaunchTime.month
    Day = LaunchTime.day
    Hour = LaunchTime.hour

    args = {'balloon':balloon, 
            'payload':payload,
            'helium':helium,
            'descent':IsDescent,
            'altitude':alt*0.3048,
            'latitude':lat,
            'longitude':lon,
            'parachute':parachute,
            'area':area,
            'errors':errors,
            'nEnsembles':nEnsembles,
            'year':Year,
            'month':Month,
            'day':Day,
            'hour':Hour,
            'callsign':callsign,
            'loss':loss,
            'update':update,
            'hover':hover,
            'bursttime':BurstTime,
            'r':BalloonR,
            'v':BalloonV,
            'zero':IsZeroPressure,
            'aprs':UseAprs,
            'currenttime':CurrentTime,
            'launchtime':LaunchTime,
            'stime':sTimeNow}
    return args

#-----------------------------------------------------------------------------
# Originally written by Aaron J Ridley - https://github.com/aaronjridley/Balloons
# Modified by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def get_station(longitude, latitude):
    #print("get_station")
    
    # Set min distance to some huge number
    MinDist = 1.0e32

    IsNam = 1
    SaveLat = 0.0
    SaveLon = 0.0

    # Cycle through all stations in the united states
    stationData = pd.read_csv(os.getcwd()+'\\StationList.txt',delimiter=' ',header=None)
    stationData[10] = ((stationData[3]-latitude)**2+(stationData[6]-longitude)**2)**0.5
    MinDistIndex = stationData[10].idxmin()
    MinDist = stationData[10][MinDistIndex]
    StatSave = stationData[0][MinDistIndex]
    SaveLat = stationData[3][MinDistIndex]
    SaveLon = stationData[6][MinDistIndex]
    DistSave = MinDist
    # At this point, we found the closest station in the united states, and the distance is saved in MinDist

    # If that distance (MinDist) is still too large
    if (MinDist > math.sqrt(500)):
        stationDataWorld = pd.read_csv(os.getcwd()+'\\StationListWorld.txt',delimiter=' ',header=None)
        stationDataWorld[10] = ((stationDataWorld[3]-latitude)**2+(stationDataWorld[6]-longitude)**2)**0.5
        MinDistIndex = stationDataWorld[10].idxmin()
        MinDist = stationDataWorld[10][MinDistIndex]
        StatSave = stationDataWorld[0][MinDistIndex]
        SaveLat = stationDataWorld[3][MinDistIndex]
        SaveLon = stationDataWorld[6][MinDistIndex]

    stat = StatSave
    date = datetime.datetime.now()
    sDateHour = date.strftime('%Y.%m.%d.%H')

    # If the station that we found is in the united states
    if (MinDist == DistSave):
        url = 'http://www.meteor.iastate.edu/~ckarsten/bufkit/data/nam/nam_'+stat+'.buf'
        #url = 'ftp://ftp.meteo.psu.edu/pub/bufkit/latest/nam_'+stat+'.buf'
    # If the station we found was from the worldwide list
    else:
        url = 'ftp://ftp.meteo.psu.edu/pub/bufkit/GFS/latest/gfs3_'+stat+'.buf'
        IsNam = 0

    # Define text file that we will write data to
    outfile = stat+'.'+sDateHour+'.txt'

    if (not os.path.isfile(outfile)):
        #print("trying to read: ")
        #print(url)
        #print(outfile)
        command = 'curl -o '+outfile+' '+url
        os.system(command)
    if (not os.path.isfile(outfile)):
        print("Could not get data from weather station URL. Check URL.")
        print(url)
    #print('Done get station '+outfile)
    return (outfile,IsNam,SaveLat,SaveLon,MinDist)

#-----------------------------------------------------------------------------
# Originally written by Aaron J Ridley - https://github.com/aaronjridley/Balloons
# Modified by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def read_rap(file,args,IsNam):
    #print("read_rap")
    
    # Different search criteria depending on which file type is used
    if (IsNam):
        SearchString = 'CFRL HGHT'
    else:
        SearchString = 'HGHT'
        Hour = args['hour']
        Hour = int(Hour/3)*3
        args['hour'] = Hour
        print("modifying hour to be : "+str(args['hour']))

    # Open file with data from station of interest
    fpin = open(file,'r')
    pressure = []
    altitude = []
    direction = []
    speed = []
    temperature = []

    # Search through file line by line in order to find the right forcast time
    IsDone = 0;
    while (IsDone == 0):
        line = fpin.readline()
        if (not line):
            IsDone = 2
        else:
            # Search for a line with this defined format
            m = re.search(r"TIME = (\d\d)(\d\d)(\d\d)/(\d\d)(\d\d)",line)
            # If such a line is found,
            if m:
                # Assign variables
                h = int(m.group(4))
                d = int(m.group(3))
                y = int(m.group(1)) + 2000
                m = int(m.group(2))
                # If the time that we just found match the time that we want...
                if (y == args['year'] and m == args['month'] and d == args['day'] and h == args['hour']):
                    # Break out of the loop
                    IsDone = 1
                    #print('Forcast Time used for prediction: '+str(y)+' '+str(m)+' '+str(d)+' '+str(h))
    
    # Set forcast time
    forcastTime = str(y)+'-'+str(m)+'-'+str(d)+' '+str(h)
    
    # If finding our time was successful, reset "IsDone" variable
    if (IsDone == 1):
        IsDone = 0
    else:
        print("Could not find requested time! Just using first time in file!")
        fpin.seek(0,0)
        IsDone = 0

    # Run through line by line, after the line that we found the right time in
    while (IsDone == 0):
        line = fpin.readline()
        m = re.search(r"SLAT = (.*) SLON = (.*) SELV = (.*)",line)
        # If the line matches the format above, 
        if m:
            # Save the variables
            lat = m.group(1)
            lon = m.group(2)
            alt = m.group(3)
            #print(lat,lon,alt)

        # If the line matches the format described by "SearchString",
        m = re.search(SearchString,line)
        if m:
            # Read in all of the height data:
            # read first line
            line = fpin.readline()
            while (len(line) > 40):
                line = line.strip()
                column = line.split()
                pressure.append(float(column[0]))
                temperature.append(float(column[1]))
                direction.append(float(column[5]))
                speed.append(float(column[6])*KnotsToMps)
                #read second line
                line = fpin.readline()
                line = line.strip()
                column = line.split()
                #print(column)
                altitude.append(float(column[IsNam]))
                #read first line (put here to check for zero size)
                line = fpin.readline()
            IsDone = 1
            
    fpin.close

    altitude = np.array(altitude)
    pressure = np.array(pressure)*100.0
    temperature = np.array(temperature)+273.15
    dir = np.array(direction)
    speed = np.array(speed)
    vn = speed * np.sin((270.0-dir)*dtor)
    ve = speed * np.cos((270.0-dir)*dtor)

    data = {'Altitude':altitude, 'Pressure':pressure, 'Temperature':temperature,
            'Veast':ve, 'Vnorth':vn}
    #print('end read rap')        
    return (data,forcastTime)

#-----------------------------------------------------------------------------
# Originally written by Aaron J Ridley - https://github.com/aaronjridley/Balloons
# Modified by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def KaymontBalloonBurst(BalloonMass):
    # Balloon Masses
    kaymontMass = [200, 300, 350, 450, 500, 
                   600, 700, 800, 1000, 1200, 
                   1500, 2000, 3000]

    # Burst diameter in meters
    kaymontBurstDiameter = [3.00, 3.78, 4.12, 4.72, 4.99, 
                            6.02, 6.53, 7.00, 7.86, 8.63, 
                            9.44, 10.54, 13.00]
    burst = -1.0
    i = 0
    for mass in kaymontMass:
        if (BalloonMass == mass):
            burst = kaymontBurstDiameter[i]
        i=i+1

    return burst

#-----------------------------------------------------------------------------
# Originally written by Aaron J Ridley - https://github.com/aaronjridley/Balloons
# Modified by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def calculate_helium(NumberOfTanks):
    # Assumes Room Temperature:
    RoomTemp = 294.261

    # Assumes K-size cylinder:
    TankVolume = 43.8 * 0.001

    # Assumes Tank Pressure
    TankPressure = 14500*1000.0

    #NumberOfMoles = NumberOfTanks * TankPressure * TankVolume / UniversalGasConstant / RoomTemp
    NumberOfHe = NumberOfTanks * TankPressure * TankVolume / Boltzmann / RoomTemp

    return NumberOfHe

#-----------------------------------------------------------------------------
# Originally written by Aaron J Ridley - https://github.com/aaronjridley/Balloons
# Modified by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def calc_ascent_rate(RapData, NumberOfHelium, args, altitude):
    # Get temp and pressure at specified altitude
    Temperature,Pressure = get_temperature_and_pressure(altitude,RapData)

    Volume = NumberOfHelium * Boltzmann * Temperature/Pressure

    # If it is a zero pressure balloon, do this
    if (args['zero'] == 1):
        if (Volume > args['v']):
            NumberOfHelium = args['v'] * Pressure / (Boltzmann * Temperature)
        Radius = args['r']
        Diameter = Radius * 2
    # If not a zero pressure balloon, do this
    else:
        Diameter =  2.0 * (3.0 * Volume / (4.0*pi))**(1.0/3.0)
        Radius   = Diameter/2.0

    # Find gravity at specified altitude
    Gravity = SurfaceGravity * (EarthRadius/(EarthRadius+altitude))**2

    NetLiftMass = NumberOfHelium * (MassOfAir - MassOfHelium)

    NetLiftForce = (NetLiftMass - args['payload'] - args['balloon']/1000) * Gravity;

    MassDensity = MassOfAir * Pressure / (Boltzmann * Temperature)

    Area = pi * Radius * Radius

    if (args['zero'] == 0):
        # With the real formula for the balloon ascent rate, the balloon accelerates
        # upward.  This doesn't seem to be the case in real launches.  A more
        # uniform ascent rate is often observed.  Through trial and error, we found
        # that using a corrector as below is good...
        t,p = get_temperature_and_pressure(1000.0,RapData)
        v = NumberOfHelium * Boltzmann * t/p
        r = (3.0 * v / (4.0*pi))**(1.0/3.0)
        # This is basically assuming that the first ascent rate is the correct on,
        # while the higher ones are a bit too fast, so they have to be slowed down:
        corrector = r/Radius
    else:
        corrector = 1.0

    if (NetLiftForce > 0.0):
        AscentRate = np.sqrt(2*NetLiftForce * corrector / (BalloonDragCoefficient*Area*MassDensity))
    else:
        AscentRate = -np.sqrt(-2*NetLiftForce * corrector / (BalloonDragCoefficient*Area*MassDensity))

    #print(AscentRate,Volume,Diameter,corrector)

    return (AscentRate, Diameter)

#-----------------------------------------------------------------------------
# Originally written by Aaron J Ridley - https://github.com/aaronjridley/Balloons
# Modified by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def calc_descent_rate(RapData, args, altitude):
    # Get gravity at specified altitude
    Gravity = SurfaceGravity * (EarthRadius/(EarthRadius+altitude))**2

    # Get temp and pressure at specified altitude 
    Temperature,Pressure = get_temperature_and_pressure(altitude,RapData)
    
    # Get mass density at the found atmospheric conditions 
    MassDensity = MassOfAir * Pressure / (Boltzmann * Temperature)

    # Calculate descent rate
    DescentRate = np.sqrt(2 * args['payload'] * Gravity / (MassDensity * ParachuteDragCoefficient * args['area']));

    return DescentRate

#-----------------------------------------------------------------------------
# Originally written by Aaron J Ridley - https://github.com/aaronjridley/Balloons
# Modified by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def get_temperature_and_pressure(altitude,RapData):
    i = 0

    while (altitude > RapData['Altitude'][i] and i < len(RapData['Altitude'])-1):
        i=i+1

    if (i == 0 or i == len(RapData['Altitude'])):
        temp = RapData['Temperature'][i]
        pres = RapData['Pressure'][i]
    else:
        da = RapData['Altitude'][i]-RapData['Altitude'][i-1]
        x = (altitude-RapData['Altitude'][i-1])/da
        temp = x*RapData['Temperature'][i] + (1-x)*RapData['Temperature'][i-1]
        pres = x*RapData['Pressure'][i] + (1-x)*RapData['Pressure'][i-1]
        alt = x*RapData['Altitude'][i] + (1-x)*RapData['Altitude'][i-1]

    return (temp,pres)


#-----------------------------------------------------------------------------
# Originally written by Aaron J Ridley - https://github.com/aaronjridley/Balloons
# Modified by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def get_wind(RapData,altitude):

    i = 0

    while (altitude > RapData['Altitude'][i] and i < len(RapData['Altitude'])-1):
        i=i+1

    if (i == 0 or i == len(RapData['Altitude'])):
        vn = RapData['Vnorth'][i]
        ve = RapData['Veast'][i]
    else:
        da = RapData['Altitude'][i]-RapData['Altitude'][i-1]
        x = (altitude-RapData['Altitude'][i-1])/da
        vn = x*RapData['Vnorth'][i] + (1-x)*RapData['Vnorth'][i-1]
        ve = x*RapData['Veast'][i] + (1-x)*RapData['Veast'][i-1]

    return (ve,vn)


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

ParachuteFudge = 0.333
BalloonDragCoefficient = 0.5
ParachuteDragCoefficient = 1.5

dt = 10.0

KnotsToMps = 0.514444
LbsToKgs = 0.453592
pi = 3.1415927
FtToMeters = 0.3048
dtor = pi/180.0
MilesPerMeter = 0.000621371

#UniversalGasConstant = 8.31432
#AirGasConstant = 286.9     # Joules / mol / K
#HeliumGasConstant = 2077.0 # Joules / mol / K

Boltzmann = 1.38070e-23

MassOfAir = 4.88e-26 # kg
MassOfHelium = 6.69e-27 # kg

SurfaceGravity = 9.80665 # m/s2
EarthRadius = 6372000.0 # m

#-----------------------------------------------------------------------------
# Originally written by Aaron J Ridley - https://github.com/aaronjridley/Balloons
# Modified by members of Michigan Balloon Recovery and Satellite Testbed at the University of Michigan
#-----------------------------------------------------------------------------
def prediction(payload,balloon,parachute,helium,lat,lon,alt,status,queryTime,nEnsembles,errors,TESTINGtimeDiff,ARcorr):
    # Define Input List
    start_time = time.time()
    Inputs = ['balloon.py','-payload='+str(payload), '-balloon='+str(balloon), '-parachute='+str(parachute), '-helium='+str(helium), '-lat='+str(lat), '-lon='+str(lon),'-alt='+str(alt),'-n='+str(nEnsembles),'-error='+str(errors)]
    
    if status == -1:
        Inputs.append('-de')
       
    #args = get_args(sys.argv)
    args = get_args(Inputs,queryTime,TESTINGtimeDiff)   
    
    if (args['balloon'] > 0):
    
        BurstDiameter = KaymontBalloonBurst(args['balloon'])
        if (BurstDiameter < 0 and args['zero'] == 1):
            BurstDiameter = args['r']*2.001
    
        if (BurstDiameter < 0):
            print("Could not determine burst diameter! Stopping!")
    
        NumberOfHelium = calculate_helium(args['helium'])
    
        #TotalKm = 0.0
    
        if (BurstDiameter > 0):
    
            longitude = args['longitude']
            latitude = args['latitude']
            
            # Get weather station
            filename,IsNam,StatLat,StatLon,MinDist = get_station(longitude, latitude)
            StationLat = [StatLat]
            StationLon = [StatLon]
            
            # Get weather data from that station
            RapData,forcastTime = read_rap(filename,args,IsNam)
    
            Diameter = 0.0
            AscentTime = 1.0
    
            if (args['altitude'] < 0.0):
                altitude = RapData['Altitude'][0]
            else:
                altitude = args['altitude']
                if (args['descent']):
                    Diameter = BurstDiameter*2.0
                    AscentRate = 0.0
    
            AscentLongitude = []
            AscentLatitude  = []
            AscentAltitude  = []
    
            DescentLongitude = []
            DescentLatitude  = []
            DescentAltitude  = []
    
            FinalLongitudes = []
            FinalLatitudes  = []
    
            # Ascent:
            
            AscentLongitude.append(longitude)
            AscentLatitude.append(latitude)
            AscentAltitude.append(altitude)
    
            TotalDistance = 0.0
    
            WindSpeed = []
            TotalTime = []
            Altitudes = []
            Latitudes = []
            Longitudes = []
            Status = []
    
            # I DON'T KNOW WHY THIS IS HERE OR WHY IT IS NEEDED
#            if (args['update'] == 1):
#                oldfilename,IsNam,StatLat,StatLon,MinDist = get_station(longitude, latitude)
#                if (StatLat != StationLat[-1]):
#                    StationLat.append(StatLat)
#                    StationLon.append(StatLon)
#                RapData,forcastTime = read_rap(oldfilename,args,IsNam)
#            else:
#                filename,IsNam,StatLat,StatLon,MinDist = get_station(longitude, latitude)
#                if (StatLat != StationLat[-1]):
#                    StationLat.append(StatLat)
#                    StationLon.append(StatLon)
#                RapData,forcastTime = read_rap(filename,args,IsNam)
            
            # Main Ascent Loop
            while (Diameter < BurstDiameter and altitude > -1.0):
#                if (args['update'] == 1):
#                    filename,IsNam,StatLat,StatLon,MinDist = get_station(longitude, latitude)
#                    if (StatLat != StationLat[-1]):
#                        StationLat.append(StatLat)
#                        StationLon.append(StatLon)
#                    if (filename != oldfilename):
#                        RapData,forcastTime = read_rap(filename,args,IsNam)
#                        oldfilename = filename
                
                NumberOfHelium = NumberOfHelium * (1.0-args['loss']/100.0/60.0*dt)
    
                Veast,Vnorth = get_wind(RapData,altitude)
                DegPerMeter = 360.0 / (2*pi * (EarthRadius + altitude))
                longitude = longitude + Veast  * DegPerMeter * dt / np.cos(latitude*dtor)
                latitude  = latitude  + Vnorth * DegPerMeter * dt
    
                WindSpeed.append(np.sqrt(Veast*Veast + Vnorth*Vnorth))
                TotalDistance += np.sqrt(Veast*Veast + Vnorth*Vnorth)*dt*MilesPerMeter
    
                AscentRate,Diameter = calc_ascent_rate(RapData, NumberOfHelium, args, altitude)
                #AR_corrected = AscentRate
                ### Reset ascentRate here? ###
                if (ARcorr != -1):
                    AR_calc = AscentRate
                    AscentRate = ARcorr
                    
                ##############################
                
                
                
                if (altitude < args['hover']):
                    altitude = altitude + AscentRate*dt
    
                AscentLongitude.append(longitude)
                AscentLatitude.append(latitude)
                AscentAltitude.append(altitude)
    
                AscentTime = AscentTime + dt
    
                TotalTime.append(AscentTime)
                Altitudes.append(altitude)
                Latitudes.append(latitude)
                Longitudes.append(longitude)
                Status.append(1)
    
                if (AscentTime > args['bursttime']):
                    Diameter = BurstDiameter*2
            # End of main ascent loop
    
            PeakAltitude = altitude
            AscentRateSave = (altitude-AscentAltitude[0])/AscentTime
            #print('Ascent Rate :',AscentRate,' m/s')
            #AscentTimeSave = AscentTime
    
            BurstAltitude  = altitude 
            BurstLatitude  = latitude
            BurstLongitude = longitude
            
            # Descent:
            
            DescentTime = 0.0
    
            DescentLongitude.append(longitude)
            DescentLatitude.append(latitude)
            DescentAltitude.append(altitude)
    
            if (altitude < 0.0):
                altitude = RapData['Altitude'][0] + 1.0
    
            # Main Decent Loop
            while (altitude > RapData['Altitude'][0]):
                Veast,Vnorth = get_wind(RapData,altitude)
                DegPerMeter = 360.0 / (2*pi * (EarthRadius + altitude))
                longitude = longitude + Veast  * DegPerMeter * dt / np.cos(latitude*dtor)
                latitude  = latitude  + Vnorth * DegPerMeter * dt
    
                WindSpeed.append(np.sqrt(Veast*Veast + Vnorth*Vnorth))
                TotalDistance += np.sqrt(Veast*Veast + Vnorth*Vnorth)*dt*MilesPerMeter
    
                DescentRate = calc_descent_rate(RapData, args, altitude)
                altitude = altitude - DescentRate*dt
    
                DescentLongitude.append(longitude)
                DescentLatitude.append(latitude)
                DescentAltitude.append(altitude)
    
                DescentTime = DescentTime + dt
                TotalTime.append(AscentTime+DescentTime)
                Altitudes.append(altitude)
                Latitudes.append(latitude)
                Longitudes.append(longitude)
                Status.append(-1)
            # End of main decent loop
    
            #DescentRateSave = (DescentAltitude[0]-altitude)/DescentTime
            #print('Descent Rate :',DescentRate,' m/s')
    
            #-----------------------------------------------------------------
            # Ensembles
            #-----------------------------------------------------------------
    
            i = 0
            nEnsembles = args['nEnsembles']
            errors     = args['errors']
            
            DifferenceInPeakAltitude = 0.0
            secondaryTracks = dict()
            secondaryTracksN = dict()
            
            numPoints = len(Altitudes)
            
            # Main Ensemble iterative loop
            while (i < nEnsembles):
                secLat = list()
                secLon = list()
                secAlt = list()
                
                #secLat=secLon=secAlt = np.full(int(math.floor(numPoints*1.2)), np.nan)
    
                longitude = AscentLongitude[0]
                latitude = AscentLatitude[0]
                altitude = AscentAltitude[0]
                
                Diameter = 0
    
                NumberOfHelium = calculate_helium(args['helium'])
                NumberOfHeliumPerturbed = random.normalvariate(NumberOfHelium,NumberOfHelium*errors/4)
                #BurstDiameterPertrubed = random.normalvariate(BurstDiameter,BurstDiameter*errors/4)
    
                #bt = random.normalvariate(args['bursttime'],args['bursttime']*errors/4)
                
                TotalTimeEnsem = []
                AscentTime = 0
                jA = 0
                
                if status != -1:
                    # Main Ascent Loop
                    
                    while (Diameter < BurstDiameter and altitude > -1.0):
                        NumberOfHelium = NumberOfHelium * (1.0-args['loss']/100.0/60.0*dt)
        
#                        if (args['update'] == 1):
#                            filename,IsNam,StatLat,StatLon,MinDist = get_station(longitude, latitude)
#                            if (StatLat != StationLat[-1]):
#                                StationLat.append(StatLat)
#                                StationLon.append(StatLon)
#                            if (filename != oldfilename):
#                                RapData,forcastTime = read_rap(filename,args,IsNam)
#                                oldfilename = filename
        
                        Veast,Vnorth = get_wind(RapData,altitude)
        
                        Veast  = random.normalvariate(Veast, np.abs(Veast)*errors)
                        Vnorth = random.normalvariate(Vnorth,np.abs(Vnorth)*errors)
        
                        DegPerMeter = 360.0 / (2*pi * (EarthRadius + altitude))
                        longitude = longitude + Veast  * DegPerMeter * dt / np.cos(latitude*dtor)
                        latitude  = latitude  + Vnorth * DegPerMeter * dt
        
                        AscentRate,Diameter = calc_ascent_rate(RapData, NumberOfHeliumPerturbed, args, altitude)
                        ### Reset ascentRate here? ###
                        if (ARcorr != -1):
                            AscentRate = ARcorr
                        ##############################
        
                        if (altitude < args['hover']):
                            altitude = altitude + AscentRate*dt
        
                        AscentTime = AscentTime + dt
                        TotalTimeEnsem.append(AscentTime)
                        
                        if (AscentTime > args['bursttime']):
                            Diameter = BurstDiameter*2
                        
                        secLat.append(latitude)
                        secLon.append(longitude)
                        secAlt.append(altitude)
                        
                        #secLat[jA] = latitude
                        #secLon[jA] = longitude
                        #secAlt[jA] = altitude
                        #jA = jA + 1
                    #End of main ascent loop
                    
                    DifferenceInPeakAltitude = DifferenceInPeakAltitude + (altitude-PeakAltitude)**2

                if (altitude < 0.0):
                    altitude = RapData['Altitude'][0] + 1.0
    
                # Main descent loop
                while (altitude > RapData['Altitude'][0]):
    
                    Veast,Vnorth = get_wind(RapData,altitude)
    
                    Veast  = random.normalvariate(Veast, np.abs(Veast)*errors)
                    Vnorth = random.normalvariate(Vnorth,np.abs(Vnorth)*errors)
    
                    DegPerMeter = 360.0 / (2*pi * (EarthRadius + altitude))
                    longitude = longitude + Veast  * DegPerMeter * dt / np.cos(latitude*dtor)
                    latitude  = latitude  + Vnorth * DegPerMeter * dt
    
                    DescentRate = calc_descent_rate(RapData, args, altitude)
                    altitude = altitude - DescentRate*dt
                    
                    AscentTime = AscentTime + dt
                    TotalTimeEnsem.append(AscentTime)
    
                    secLat.append(latitude)
                    secLon.append(longitude)
                    secAlt.append(altitude)
                    
                    #secLat[jA] = latitude
                    #secLon[jA] = longitude
                    #secAlt[jA] = altitude
                    #jA = jA + 1
                #End of main descent loop
    
                #secLat = secLat[~np.isnan(secLat)]
                #secLon = secLon[~np.isnan(secLon)]
                #secAlt = secAlt[~np.isnan(secAlt)]
                
                FinalLongitudes.append(longitude)
                FinalLatitudes.append(latitude)
                
                # Save all ensemble data
                secondaryTracks[str(i)] = pandas.DataFrame(index = pandas.to_datetime(pandas.to_datetime(args['launchtime']) + pandas.to_timedelta(TotalTimeEnsem, unit='s')))
                secondaryTracks[str(i)]['Lat'] = secLat
                secondaryTracks[str(i)]['Lon'] = secLon
                secondaryTracks[str(i)]['Alt'] = np.array(secAlt) * 3.28084
                if i == 0:
                    secondaryTracksN['Lat'] = pandas.DataFrame()
                    secondaryTracksN['Lat']['time'] = pandas.to_datetime(pandas.to_datetime(args['launchtime']) + pandas.to_timedelta(TotalTimeEnsem, unit='s'))
                    secondaryTracksN['Lat'][str(i)] = secLat
                    
                    secondaryTracksN['Lon'] = pandas.DataFrame()
                    secondaryTracksN['Lon']['time'] = pandas.to_datetime(pandas.to_datetime(args['launchtime']) + pandas.to_timedelta(TotalTimeEnsem, unit='s'))
                    secondaryTracksN['Lon'][str(i)] = secLon
                    
                    secondaryTracksN['Alt'] = pandas.DataFrame()
                    secondaryTracksN['Alt']['time'] = pandas.to_datetime(pandas.to_datetime(args['launchtime']) + pandas.to_timedelta(TotalTimeEnsem, unit='s'))
                    secondaryTracksN['Alt'][str(i)] = np.array(secAlt) * 3.28084
                if i > 0:
                    tempTrackLat = pandas.DataFrame()
                    tempTrackLat['time'] = pandas.to_datetime(pandas.to_datetime(args['launchtime']) + pandas.to_timedelta(TotalTimeEnsem, unit='s'))
                    tempTrackLat[str(i)] = secLat
                          
                    tempTrackLon = pandas.DataFrame()
                    tempTrackLon['time'] = pandas.to_datetime(pandas.to_datetime(args['launchtime']) + pandas.to_timedelta(TotalTimeEnsem, unit='s'))
                    tempTrackLon[str(i)] = secLon
                    
                    tempTrackAlt = pandas.DataFrame()
                    tempTrackAlt['time'] = pandas.to_datetime(pandas.to_datetime(args['launchtime']) + pandas.to_timedelta(TotalTimeEnsem, unit='s'))
                    tempTrackAlt[str(i)] = np.array(secAlt) * 3.28084
                    
                    secondaryTracksN['Lat'] = pandas.merge(secondaryTracksN['Lat'],tempTrackLat, sort=True, on='time', how='outer')
                    secondaryTracksN['Lon'] = pandas.merge(secondaryTracksN['Lon'],tempTrackLon, sort=True, on='time', how='outer')
                    secondaryTracksN['Alt'] = pandas.merge(secondaryTracksN['Alt'],tempTrackAlt, sort=True, on='time', how='outer')
               
                i=i+1
                
            if (nEnsembles > 1):
                DifferenceInPeakAltitude = np.sqrt(DifferenceInPeakAltitude/nEnsembles)
    
            #RealTimeLat = []
            #RealTimeLon = []
            #RealTimeAlt = []
           
    # Store time-domain data for nominal prediction
    AllData = dict()   
    AllData['TimeData'] = pandas.DataFrame(index = pandas.to_datetime(pandas.to_datetime(args['launchtime']) + pandas.to_timedelta(TotalTime, unit='s')))
    AllData['TimeData']['Status'] = Status
    AllData['TimeData']['Latitude'] = Latitudes
    AllData['TimeData']['Longitude'] = Longitudes
    AllData['TimeData']['Altitude'] = np.array(Altitudes) * 3.28084
    
    # Store prediction output stats for nominal prediction 
    AllData['Ascent Rate'] = AscentRateSave * 3.28084
    if (ARcorr != -1):
        AllData['AR_corrected'] = True
        AllData['AR_calc'] = AR_calc * 3.28084
    if (ARcorr == -1):
        AllData['AR_corrected'] = False
        AllData['AR_calc'] = AllData['Ascent Rate']
    AllData['Burst Altitude'] = BurstAltitude * 3.28084
    AllData['Burst Latitude'] = BurstLatitude 
    AllData['Burst Longitude'] = BurstLongitude 
    AllData['Landing Lat'] = Latitudes[-1]
    AllData['Landing Lon'] = Longitudes[-1]
    AllData['Landing Time'] = AllData['TimeData'].index[-1] 
    AllData['StationDist'] = MinDist
    AllData['RapData'] = RapData
    
    # Store data used for prediction input
    AllData['Inputs'] = dict() 
    AllData['Inputs']['Launch Time'] = pandas.to_datetime(args['launchtime'])
    AllData['Inputs']['Altitude'] = alt
    AllData['Inputs']['Lat'] = lat
    AllData['Inputs']['Lon'] = lon
    AllData['Inputs']['Status'] = status
    AllData['Inputs']['ForcastFile'] = filename
    AllData['Inputs']['ForcastTime'] = forcastTime
    
    # Store data related to ensembles
    AllData['Landing Deviations'] = pandas.DataFrame()
    AllData['Landing Deviations']['Lat'] = FinalLatitudes
    AllData['Landing Deviations']['Lon'] = FinalLongitudes 
    AllData['Secondary Tracks'] = secondaryTracks 
    AllData['SecTracksTimeDomain'] = secondaryTracksN
    
    #print("%s seconds" % (time.time() - start_time))
    return AllData

