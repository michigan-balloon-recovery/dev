Property of Michigan Balloon Recovery and Satellite Testbed and Aaron J Ridley
University of Michigan, Ann Arbor MI
Last Updated: 09/13/2019

The following are descriptions of python scripts and .txt files associated with all things high altitude balloons.

---------------- Balloon.py -------------------------------------
DESCRIPTION:
- Contains multiple functions that can be called from external scripts.
- "import balloon" on any script that uses one of these functions.

FUNCTIONS:
- APRS_data = APRS(callsign,APRS_apikey)
	- Function to get aprs data. 
	- Returns dictionary with lots of info from the aprs packet
	- "callsign" and "APRS_apikey" are strings

- send_slack(messageString,messageType,recipient,slackURL)
	- Function to send a slack message
	- Inputs are:
		- messageString (string)
		- 'dm' for direct message, 'channel' for channel
		- recipient - name of person like 'Robby', or channel like '#predictions'
		- slackURL - url for sending messages to this slack account. Available in settings.

- package(dataset,prediction_ID, flightID)
	- Function to save a variable with any nesting degree
	- Inputs are variable name (dict), prediction ID (string), and flightID (string)

- dataset = unpackage(prediction_ID, flightID)
	- Function to read in a saved variable
	- Input is prediction number (string) 
	- Returns new variable (dict) 

- allPredictions = unpackageGroup(flightID,numPredictions)
	- Function to read in multiple saved variables.
	- Input is flightID (str) and number of predictions (int)
	- Returns dictionary filled with prediction elements

- launchLoc = launchPrediction(payload,balloon,parachute,helium,lat,lon,launchTime,tolerance)
	- Function to run prediction backwards
	- Outputs launching location based on desired landing location
	- payload	- See prediction function
	- balloon 	- ""
	- parachute	- ""
	- helium	- ""
	- lat		- ""
	- lon		- ""
	- launchTime	- ""
	- tolerace	- Number of ft that the backwards prediction is allowed to be off by. 

- coordshift(Lat1,Lon1,Lat2,Lon2)
	- Computes distance in ft between two sets of coordinates.
	- Inputs are floats

- plotPrediction(data)
	- Function to plot one prediction worth of data statically in 3D space
	- Input is data structure returned by prediction().

- PredictionAni(PredData,saving)
	- Function to animate one prediction in 3D space as time progresses.
	- PredData	- Data structure returned by prediction()
	- saving	- 1 (save animation as GIF), or 0 (don't).
			- Saving GIF takes significant time and memory allocation.

- heatMap(data, apikey)
	- Function to create a 2D heatmap of landing probabilities overlaid on google maps
	- Saves an html file to local directory.
	- Requires google maps api key (string)

- plotStations()
	- Not completed
	- Meant to plot map of all weather stations in list on a map, to visualze which ones are closest. 

- plotFlight(flightID,predTotal,predLow,predHigh,plotEnsem,plotType)
	- Plots all data from an entire flight in one plot
	- 3D and 2D plots possible
	- Inputs
		- flightID (string)
		- predTotal (int) - How many total predictions were made during the flight
		- predLow (int), predHigh (int) - The range of predictions that you are interested in
		- plotEnsem (bool) - Plot all of the ensembles? Simplifies plot a lot if this is false.
		- plotType (string) - 2A (Altitude vs. time), 2L (long vs. lat), 3 (3D plot)

- dataToCSV(FlightPath, flightID)
	- Converts a dataframe with datetime index and keys that describe 3D location to a CSV.
	- FlightPath (dataframe)
	- flightID (str)

- get_args(argv,queryTime)
	- Referenced by other functions
	- Function to figure out prediction arguments 

- get_station(longitude, latitude)
	- Referenced by other functions
	- Determine which station(s) is(are) closest to the given latitude and longitude

- get_stations(longitude, latitude, max_distance)
    - Referenced by other functions
    - Determine which stations are within max_distance of given latitude and longitude

- get_station_data(stations, args)
    - Referenced by other functions

- read_rap(file,args,IsNam)
	- Referenced by other functions
	- Reads RAP file

- KaymontBalloonBurst(BalloonMass)
	- Referenced by other functions

- calculate_helium(NumberOfTanks)
	- Referenced by other functions

- calc_ascent_rate(StationData, NumberOfHelium, args, altitude)
	- Referenced by other functions

- calc_descent_rate(StationData, args, altitude)
	- Referenced by other functions

- get_temperature_and_pressure(altitude,RapData)
	- Referenced by other functions

- get_temperature_and_pressure(altitude,latitude,longitude,StationData)
    - Referenced by other functions

- get_wind(RapData,altitude)
	- Referenced by other functions

- get_wind(StationData,altitude,latitude,longitude)
    - Referenced by other functions

- data = prediction(payload weight,balloon mass,parachute diameter,helium tanks,latitude,longitude,current altitude,status,query time,# of ensembles, error in ensembles, TESTINGtimeDiff)
	- payload weight        - lbs (float)
	- balloon mass          - grams (float)
	- parachute diameter    - ft (float)
	- helium tanks          - # of tanks (float)
	- latitude              - deg (float)
	- longitude             - deg (float)
	- current altitude      - ft (float)
	- status                - ascent (1) or descent (-1) (int)
	- query time            - string: 'now' or 'YYYY-MM-DD hh:mm:ss'. 
	- # of ensembles 	      - Number of ensembles to run (int). -1 if none. 
	- error in ensembles    - Amount of error to run with each ensemble (float). Usually between 0 and 1.
	- TESTINGtimeDiff	- Number of hours that the package is off from the local time. Use if testing balloons on APRS in different time zones.

	Function returns a dictionary, which consists of keys:
	..['Ascent Rate']         - ft/s
	..['Burst Altitude']      - ft
	..['Burst Latitude']      - deg
	..['Burst Longitude']     - deg
	..['Landing Lat']         - deg
	..['Landing Lon']         - deg
	..['Landing Time']        - Timestamp (when balloon is predicted to land, absolute time)
	..['TimeData']            - Timeseries Dataframe, consisting of (below) as a function of absolute future time
					- Status (ascent or descent)
					- Latitude (deg)
					- Longitude (deg)
					- Altitude (ft) 
	..['Inputs']		- Data used to preform prediction. Consists of keys:
				..['Launch Time']				
					- Timestamp (what time the prediction was preformed at, absolute time)	
				..['Altitude']
					- ft
				..['Lat']
					- deg
				..['Lon']
					- deg
				..['Status']
					- 1 or 0, Ascent or Descent
				..['ForcastFile']
					- str, name of file used to do prediction
				..['ForcastTime']
					- str, rounded hour used for prediction
	..['Landing Devaiations']	- Dataframe with final landing locations of non-nominal ensembles. Columns of:
						- 'Lat'
						- 'Lon'
					- Number of elements = number of ensembles. 
	..['Secondary Tracks']	- Dictionary. 
				- Each element is a dataframe. 
				- Each dateframe is a complete track of (below) as a function of absolute future time for a single ensemble
					- ['Lat']
					- ['Lon']
					- ['Alt'] 
				- Example: data['Secondary Tracks'][13]['Lat']
	..['SecTracksTimeDomain']	- Same data as ['Secondary Tracks']
					- Saved as a dataframe synchronized in the time domain 

	..['RapData']		- Dictionary containing Rap data used to do prediction
				- Contains arrays:
					..['Altitude']
					..['Pressure']
					..['Temperature']
					..['Veast']
					..['Vnorth']
	..['StationDist']	- Distance of prediction coordinate to the weather station used for calculations (decimal degrees)
		
	Example:
	data = balloon.prediction(6.0,1000,6.0,1,41.64,-83.243,40000,1,'now',110,0.2,0)


---------------- StationList.txt -------------------------------------
- Contains a list of weather stations
- Does not need to be altered.

---------------- StationListWorld.txt -------------------------------------
- Contains a list of weather stations
- Does not need to be altered.

---------------- PreFlightAnalysis.py -------------------------------------
- under development 
- Does a prediction backwards to find best launch location for a desired landing location, animates the result, and does a checksum by doing prediction forwards from given launch location

---------------- PostFlightAnalysis.py -------------------------------------
- under development 
- can be used for a variety of purposes

---------------- TrackingCode(APRS).py -------------------------------------
- Main commanding script used to track and record data for a single flight, if APRS trackers are being used.
- Notifications are sent via slack 
	- initially after launch
	- immediatly before landing
	- during flight if the predicted landing coordinates shift more than a set threshold from the last slack notification. 
- All data is saved from all predictions.
	- Data is saved iteratively to prevent data loss associated with program failure. 
- Able to send warnings via slack if tracker preformance or gps reception is not nominal. 
- Able to self-diagnose code errors and attempt to solve them in order to keep tracking.  








