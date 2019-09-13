import balloon

## INPUTS ##
flightID = '01'                 # Flight ID of the flight you want to plot
predTotal = 209                 # How many total predictions were made during the flight
predLow,predHigh = 1,20         # The range of predictions that you are interested in
plotEnsem = True                # Plot all of the ensembles? Simplifies plot a lot if this is false.
plotType = '2L'                 # 2A (Altitude vs. time), 2L (long vs. lat), 3 (3D plot)
##########

# Plot data
AllData,data,FlightPath = balloon.plotFlight(flightID,predTotal,predLow,predHigh,plotEnsem,plotType)
