import balloon
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import matplotlib
import requests
import json

###### INPUTS ########
payload = 8                          # lbs
balloonWeight = 1500                    # g
parachuteDia = 6.0                      # ft
helium = 2                            # tanks
desiredLat = 42.066068
desiredLon = -83.814432
launchTime = '2019-11-24 11:00:00'      # Best guess of when balloon will be launched, local time
tolerace = 10                           # ft - how close the conversion has to get 
ensem = 50;
ensem_per = 0.3;
UTCdiff = 5;
doDrivingCalc = True
######################


# Do backwards prediction calculation
launchLoc = balloon.launchPrediction(payload,balloonWeight,parachuteDia,helium,desiredLat,desiredLon,launchTime,tolerace,0,UTCdiff)
print('Launch Location: ' + str(launchLoc['Lat']) + ',' + str(launchLoc['Lon']))
print('Distance reached: '+str(launchLoc['Tolerace']))

# Check work from backwards calculation
data = balloon.prediction(payload,balloonWeight,parachuteDia,helium,launchLoc['Lat'],launchLoc['Lon'],-1,1,launchTime,ensem,ensem_per,0,-1,UTCdiff)
#balloon.plotPrediction(data)
print('Requested: ' + str(desiredLat) + ',' + str(desiredLon))
print('Actual: ' + str(data['Landing Lat']) + ',' + str(data['Landing Lon']))
print('Popping Altitude: ' + str(data['Burst Altitude']) + ' ft')
popTime = data['TimeData'].loc[data['TimeData']['Status'] == 1].index[-1]
print('Rise time: ' + str(popTime - data['Inputs']['Launch Time']))
print('Flight time: ' + str(data['Landing Time'] - data['Inputs']['Launch Time']))
if (doDrivingCalc == True):
    origin = str(launchLoc['Lat']) + ',' + str(launchLoc['Lon'])
    destination = str(data['Landing Lat']) + ',' + str(data['Landing Lon'])
    string = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=' + origin + '&destinations=' + destination + '&key=' + apikey
    json_response= requests.get(string)
    dis_dict = json.loads(json_response.text) 
    drivingTime = dis_dict['rows'][0]['elements'][0]['duration']['text']
    drivingDistance = dis_dict['rows'][0]['elements'][0]['distance']['text']
    print('Driving Time: ' + drivingTime)
    print('Driving Distance: ' + drivingDistance)

balloon.heatMap(data,'')


# Cost function stuff
def costFunction(x,lower,costType):
    # Function for defining and evaluating a deadband cost function with user declared cost type.
    # Inputs are dataset, upper and lower bound of deadband, and type of end condition.
    # Returns cost vector of input x.
    conds = [x <= lower, (x > lower)]
    if costType == 'linear':
        funcs = [lambda x: -1*(x-lower)+0, 
                 0]
    if costType == 'quad':
        funcs = [lambda x: (x-lower)**2, 
                 0]   
    cost = np.piecewise(x, conds, funcs)
    return cost

