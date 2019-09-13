import balloon
import datetime
import time
import numpy as np
import math

# User Inputs
flightID = '02'
APRScallsign = 'P2130072'   # APRS Callsign
APRS_apikey = ''
slackURL = ''
messageType = 'dm'          # 'dm' or 'predictions'
recipient = 'Robby'         # dm format: 'Robby', channel format: '#predictions'
APRSfreq = 30               # Seconds
UpperFreqToleraceWarn = 3   # minutes
UpperFreqToleraceTerm = 5   # minutes
payload = 6.0               # lbs
balloonWeight = 1000        # g
parachuteDia = 6.0          # ft
helium = 1.5                # tanks
ensembles = 30              # Number of ensembles to run for each prediction
errInEnsembles = 0.5        # Error setting for each ensemble
approxLaunchAlt = 500      # Estimation for what altitude balloon is initially launched from
reqPred = 10000             # Altitude on the descent that has a required prediction notification
tolerace = 3000             # [ft] How much of a landing corrdinate change warrents a message to the group
TESTINGtimeDiff = 6

# Set things up
tracking = True
status = 1
predictionNum = 1
alt = list()
lat = list()
lng = list()
predLat = list()
predLon = list()
lastTrackerTimes = list()
LastAPRSCheck = time.time() - (APRSfreq + 1)
programStart = time.time()      # unix time
errorNum = 0
FirstNotificationSent = False
deviation = 0
warned = 0
lastNotLat = 0
lastNotLon = 0
CycleError = False
ErrorCode = 0

# Main Tracking Loop
while tracking == True:
    
    # If it has been at least [APRSfreq] seconds since the last time we queried APRS...
    if (time.time()-LastAPRSCheck) > APRSfreq:
        CycleError = False
        print('Start of 30 second chunk')
        
        # Try to get APRS position and preform prediction
        try:
            # Get Current Location, altitude
            print('Getting APRS data')
            APRS_data = balloon.APRS(APRScallsign,APRS_apikey)
            LastAPRSCheck = time.time()
            lastPacketTime = int(APRS_data['lasttime'])
            lastTrackerTimes.append(lastPacketTime)
            
            # Add current data to track
            alt.append(APRS_data['altitude'] * 3.281)   # m
            lat.append(APRS_data['lat'])
            lng.append(APRS_data['lng'])
            print('Altitude: ' + str(APRS_data['altitude'] * 3.281))
        
        except:
            CycleError = True
            ErrorCode = 1
                  
        # Figure out state of balloon
        if CycleError == False:
            try:
                
                if len(alt) > 1:
                    gradPrep = np.array(alt)
                    grad = np.diff(gradPrep)
                    
                    if grad[-1] > 0:    # ascent
                        status = 1
                    if (grad[-1] < -70):    # if it has fallen more than 50 ft, it is descending
                        status = -1
            except:
                CycleError = True
                ErrorCode = 2
        
        # Some Error Catching
        if CycleError == False:
            try:
                if len(alt) > 1:
                    if (max(alt) - min(alt)) > 200:
                        
                        # If last position report was more than (UpperFreqToleraceWarn*60) seconds ago and we have not been warned yet
                        if ((LastAPRSCheck - lastPacketTime) > (UpperFreqToleraceWarn*60)) and warned == 0:
                            message = 'Warning: Tracker may be malfunctioning. No new location data recieved in last ' + str(((LastAPRSCheck - lastPacketTime)/60)) + ' minutes.'
                            balloon.send_slack(message,messageType,recipient,slackURL)
                            warned = 1
                            
                        # If last position report was more than (UpperFreqToleraceTerm*60) seconds ago and we have already been warned
                        if ((LastAPRSCheck - lastPacketTime) > (UpperFreqToleraceTerm*60)) and warned == 1:
                            message = 'Error: Tracker malfunction.'
                            balloon.send_slack(message,messageType,recipient,slackURL)
                            print('break')
                            break
                            
                        # Check if location is reporting same position twice - If so send message to group 
                        if APRS_data['lasttime'] != APRS_data['time']:
                            message = 'Warning: Tracker may have lost GPS signal. Data transmission remains nominal.'
                            balloon.send_slack(message,messageType,recipient,slackURL)
            except:
                CycleError = True
                ErrorCode = 3
        
        # Do Prediction
        if CycleError == False:
            try:
                # Prediction
                print('Preforming Prediction: Status ' + str(status))
                data = balloon.prediction(payload,balloonWeight,parachuteDia,helium,APRS_data['lat'],APRS_data['lng'],APRS_data['altitude'] * 3.281,status,'now',ensembles,errInEnsembles,TESTINGtimeDiff)
                # Save prediction data to file
                balloon.package(data,predictionNum,flightID)
                predictionNum = predictionNum + 1
                # Stick landing coordinates in vector
                predLat.append(data['Landing Lat'])
                predLon.append(data['Landing Lon'])
                
            except:
                CycleError = True
                ErrorCode = 4
        
        # Do deviation calculation
        if CycleError == False:
            try:
                # If more than one predction exists, figure out if it has shifted by a certain tolerace since the last NOTIFICATION
                if len(predLat) > 1:
                    deviation = balloon.coordShift(predLat[-1],predLon[-1],lastNotLat,lastNotLon)
                    print('Deviation: ' + str(deviation) + ' ft')
            except:
                CycleError = True
                ErrorCode = 5
        
        # Send Slack Message
        if CycleError == False:
            try:
                # Send Messege to slack channel if: This is the first message 
                if FirstNotificationSent == False:
                    message = 'Initial Prediction: ' + 'https://www.google.com/maps/dir/?api=1&destination=' + str(data['Landing Lat']) + ',' + str(data['Landing Lon']) + '&travelmode=driving'
                    balloon.send_slack(message,messageType,recipient,slackURL)
                    print('New coord reference')
                    lastNotLat = data['Landing Lat']
                    lastNotLon = data['Landing Lon']
                    FirstNotificationSent = True
                    print('Sent first prediction')
                    
                    
                # Send Messege to slack channel if: Prediction has changed a lot
                if (deviation > tolerace):
                    message = str(math.trunc(deviation)) + 'ft landing deviation - Coordinate: ' + 'https://www.google.com/maps/dir/?api=1&destination=' + str(data['Landing Lat']) + ',' + str(data['Landing Lon']) + '&travelmode=driving'
                    balloon.send_slack(message,messageType,recipient,slackURL)
                    print('New coord reference')
                    lastNotLat = data['Landing Lat']
                    lastNotLon = data['Landing Lon']
            except:
                CycleError = True
                ErrorCode = 6

        if CycleError == False:
            try:
                # Give last precise prediction once it gets close enough to ground
                # If maximum point in track is reasonably above launch altitude and status is -1 and altitude is below [reqPred]
                if (max(alt) > (approxLaunchAlt + 3000)) and (status == -1) and (alt[-1] < reqPred):
                    message = 'Final Prediction, ' + str(alt[-1]) + 'ft: ' + 'https://www.google.com/maps/dir/?api=1&destination=' + str(data['Landing Lat']) + ',' + str(data['Landing Lon']) + '&travelmode=driving'
                    balloon.send_slack(message,messageType,recipient,slackURL)
                    print('Program Shutdown')
                    break
            except:
                CycleError = True
                ErrorCode = 7
            
        if CycleError == True:
            print('Error Code: ' + str(ErrorCode))
            errorNum = errorNum + 1
            
            # First time error happens, send a message
            if errorNum == 1:
                message = 'ALERT: Error #' + str(ErrorCode) + '. Attempting to fix...'
                balloon.send_slack(message,messageType,recipient,slackURL)
                time.sleep(10)
            if errorNum > 5:
                message = 'ALERT: Could not fix error. Program shutdown.'
                balloon.send_slack(message,messageType,recipient,slackURL)
                print('break')
                break
                
        print('Done with '+ str(APRSfreq) + ' second chunk')
                
    else:
        time.sleep(3)
    

message = 'Data saved, program shutdown'
balloon.send_slack(message,messageType,recipient,slackURL)

    
    
