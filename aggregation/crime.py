import requests, json
from collections import Counter

'''ADAM'S MIDNIGHT NOTE:
I wrote a weight based algorithm for crime. The results were interesting, and clearly not that good. Entertaining however,
Exploring an unsupervised learning algorithm with ML would be very useful and good for the accuracy of this.'''


#fetch crime based on geocode: Lat, Longitude
def fetch(lon, lat):
    crimeInfoJSON = json.loads(requests.get('https://api.spotcrime.com/crimes.json?lat=' + lat + '&lon=' + lon + '&radius=0.04&key=.').text)
    crimes = dict(Counter([ _['type'] for _ in crimeInfoJSON['crimes']])) #count the occurences of the crimes
    return computeScore(crimes)

#crime algorithm based on the weights of certain crimes.
def computeScore(crimes):
    return (crimes.get('Shooting', 0) * 10) + (crimes.get('Assault', 0) * 4) + (crimes.get('Robbery', 0) * 8) +\
            (crimes.get('Theft', 0) * 3) + (crimes.get('Burglary', 0) * 7) + (crimes.get('Arson', 0) * 3) + crimes.get('Vandalism', 0)
