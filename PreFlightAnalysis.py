import balloon
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

## INPUTS ##
payload = 6.0
balloonWeight = 1000
parachuteDia = 6.0
helium = 1.5
desiredLat = 42.290977
desiredLon = -83.717548
launchTime = '2019-08-23 23:00:00'
tolerace = 5 #ft
######################


# Do a single prediction
data = balloon.prediction(payload,balloonWeight,parachuteDia,helium,desiredLat,desiredLon,-1,1,launchTime,100,0.2)

# Animate the result
balloon.PredictionAni(data,0)


# Do backwards prediction calculation
launchLoc = balloon.launchPrediction(payload,balloonWeight,parachuteDia,helium,desiredLat,desiredLon,launchTime,tolerace)
print('Distance reached: '+str(launchLoc['Tolerace']))
# Check work
data = balloon.prediction(payload,balloonWeight,parachuteDia,helium,launchLoc['Lat'],launchLoc['Lon'],-1,1,launchTime,50,0.2)
balloon.plotPrediction(data)

