# azimuth_and_elevation_determintaion
Program calculate positions of choosen satelites (from celectrack site) at the sky in any time when they are above horizont using tle format. 
So you can use this data for authomatical navigation of antenna.
Incoming data are:
1) Names of necessary satelite (tle upload from celestrak.com, you can choose source of tle in SatProc.py file)
2) Time of observation - time for which flyovers will be calculated
3) Latitude and longitude of observation place
4) UTC time of observation place is need for getting flyover time at obcervation place time
5) Calculation interval between flyovers - we are checking if satelite is above horizont each choosen time
6) Calculation interval during flyovers - we are calculate sky position of satelite each choosen time interval

You can see type of data we getting in sorted_satellite_flyovers.txt file that appearing after playing program.
