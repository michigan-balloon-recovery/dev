import balloon

## INPUTS ##
flightID = "07"  # Flight ID of the flight you want to plot
predTotal = 231  # How many total predictions were made during the flight
predLow, predHigh = 1, 231  # The range of predictions that you are interested in
plotEnsem = False  # Plot all of the ensembles? Simplifies plot a lot if this is false.
plotType = "2A"  # 2A (Altitude vs. time), 2L (long vs. lat), 3 (3D plot)
##########

# Plot data
AllData, data, FlightPath = balloon.plotFlight(
    flightID, predTotal, predLow, predHigh, plotEnsem, plotType
)
