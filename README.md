# ny-ride-share-analysis
An analysis of ride share information based on the FOI request to TLC in regards to ride share data concerning taxis, uber and competitors

<!-- GETTING STARTED -->
## Purpose

The data provided by TLC in response to a FoI request from a Mr. Bialik, provides an excellent view into the movements of Taxi and Rideshares in NY city in 2016.

## Steps

1. Seek business scope and client use cases
	No scope limitations were available, the exercise is left completly open
2. Work through the data
	a. Visualise geo data
	b. Plot other data points
3. Identify any data catagories of note and spot check for trends
4. Analyse
5. Visualise
6. Produce report


## Diary

1. Setup Workspace
2. Download data
3. Read through TLC and go through csvs in excel
4. csvs are somewhat clunky or weird row usage, minor edits to make it easier to traverse.
5. Import Jul14 Uber raw data into QGIS to visualise,
6. Visualise by base, notice immediantly the sheer ammount of overlap, bases almost seem like a null indicator
	- IDEA: Looks like theres alot of pickups around the airport almost as much as in
	- IDEA: How useless is the base value for ubers compared to taxis, possible to compare pickup vs base?
7. Graphed all FHV data and noticed that there are cycle, also that 1st of september is taxis worst day then skyrockets from there?
8. Something happened on the 1st of september 2014, googling showed there was uber protests about fare price being cut in july 2014 and a limit of surge pricing https://money.com/uber-price-cut-fare-new-york-city/ https://www.mercurynews.com/2014/07/07/uber-temporarily-cuts-prices-on-taxi-like-service-in-new-york-city/

"Uber will keep 20 percent commission for each ride, and drivers will make less per trip, though they should see more riders in a day, Mohrer said. In all other cities where Uber has initiated price cuts for UberX, trips per hour have increased, he said."

https://data.cityofnewyork.us/ to get borough

9. Pivot to looking at QGIS again, Download NYC and NJ borough GIS polygon
10. Isolate Bronx as a representaive suburb to test on  
11. Clustering points using DBScan to cluster close points and heatmap to visualise shows points of heavy use for the whole month
12. Get a week breakdown instead of month


