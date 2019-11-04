import balloon
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import matplotlib

###### INPUTS ########
payload = 6.0                           # lbs
balloonWeight = 1000                    # g
parachuteDia = 6.0                      # ft
helium = 1.5                            # tanks
desiredLat = 42.290977
desiredLon = -83.717548
launchTime = '2019-10-26 12:00:00'      # Best guess of when balloon will be launched
tolerace = 10                           # ft - how close the conversion has to get 
######################


# Do a single prediction
#data = balloon.prediction(payload,balloonWeight,parachuteDia,helium,desiredLat,desiredLon,-1,1,launchTime,5,0.2,0,-1)

# Animate the result
#balloon.PredictionAni(data,0)


# Do backwards prediction calculation
launchLoc = balloon.launchPrediction(payload,balloonWeight,parachuteDia,helium,desiredLat,desiredLon,launchTime,tolerace,0)
print('Distance reached: '+str(launchLoc['Tolerace']))

# Check work from backwards calculation
data = balloon.prediction(payload,balloonWeight,parachuteDia,helium,launchLoc['Lat'],launchLoc['Lon'],-1,1,launchTime,50,0.2,0,-1)
balloon.plotPrediction(data)
print('Actual Lat: ' + str(data['Landing Lat']))
print('Actual Lon: ' + str(data['Landing Lon']))


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

#def mapValue(value, leftMin, leftMax, rightMin, rightMax):
#    # Maps value or vector from one domain to another. 
#    # Returns new value or vector.
#    leftSpan = leftMax - leftMin
#    rightSpan = rightMax - rightMin
#    valueScaled = np.array(value - leftMin) / np.array(leftSpan)
#    return rightMin + (valueScaled * rightSpan)


weight_min = 0.6
weight_average = 1.0-weight_min

costType = 'quad'
labelSize = 30
lower = 5

xx = np.linspace(0, 10, 1000)
plt.figure(figsize=(20,15))
matplotlib.rc('xtick', labelsize=labelSize) 
matplotlib.rc('ytick', labelsize=labelSize) 

plt.plot(xx, costFunction(xx,lower,costType))

plt.xlabel('Distance (miles)',fontsize=labelSize)
plt.ylabel('Cost before weight',fontsize=labelSize)
plt.show() 





