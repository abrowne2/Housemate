#Haversine algorithm
from math import radians, cos, sin, asin, sqrt

#used to calculate distance between two points of long / lat
#credit: James Inman, Florian Cajori,  & José de Mendoza y Ríos
#NOTE: introducing a factor of 1.3 will make the result closer to the actual.
def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return ((2 * asin(sqrt(a))) * 3956) * 1.3 #3956 is the earth's radius in miles.