'''
Off Campus Housing Aggregator
Author: Adam Browne
'''

import requests, json, crime
from bs4 import BeautifulSoup
from math import radians, cos, sin, asin, sqrt


'''Rent.com Aggregation

http://onesearch.svc.primedia.com/autocomplete?q=[QUERY]&application=rent

One you've extracted the listing id's from the request, send them here:

http://www.rent.com/account/myrent/listings.json?ids=[IDS]
for a json object containing pertinent information.

First, the user's query is sent through the autocomplete endpoint.
A list of colleges will be retrieved, and then the request will be made.
Pertinent information is stored accordingly.

'''

#used to calculate distance between two points of long / lat
#credit: James Inman, Florian Cajori,  & José de Mendoza y Ríos
#NOTE: introducing a factor of 1.3 will make the result closer to the actual.
def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return ((2 * asin(sqrt(a))) * 3956) * 1.3 #3956 is the earth's radius in miles.

def fetchUniversities(input):
    # rent.com uses "ONESEARCH", and you can make calls to their query endpoint for JSON responses, nifty:
    univJSON = requests.get('http://onesearch.svc.primedia.com/autocomplete?q=' + input + '&application=rent')
    univJSON = json.loads(univJSON.text)  # parse the JSON response.

    # use the seopath to retrieve the listing ids.
    universities = [[x['name'], x['seopath'], x['geocode']] for x in univJSON]

    print("Please select your university: \n")
    for index, univ in enumerate(universities):
        print(str(index + 1) + ' ' + str(univ[0]))

    return universities

def rentCom(college):
    universities = fetchUniversities(college)

    #TODO: implement choice between house or apartment, or both. If both, fetch top

    univ = int(input()) - 1
    choice = requests.get('http://rent.com' + universities[univ][1])

    #retrieve the list of listing_ids, which we can use to obtain a JSON object of all the properties.
    listIds = ','.join(BeautifulSoup(choice.text).find(attrs={"name":"listing_ids"})['content'].split(';'))

    #below, you don't even have to be authenticated to provide the list of listing_ids...
    propJSON = requests.get('http://rent.com/account/myrent/listings.json?ids=' + listIds)
    propJSON = json.loads(propJSON.text)
    #list comprehension technique here: this is actually a dictionary inside a list. refer to the values by key,
    properties = [{'url_path': x['url_path'], 'name': x['name'], 'address': x['address'], 'city': x['city'],
                    'state': x['state'], 'price_range': x['price_range'], 'bedroom_range': x['bedroom_range'],
                    'bathroom_range': x['bathroom_range'], 'image_url': x['image_url']} for x in propJSON['listings']]

    rentPropertyTraversal(properties, universities[univ][2].split(','))


#given a url_path, fetch more information about the specified property
def rentPropertyTraversal(properties, univLoc):
    for x in properties:
        propInfo = BeautifulSoup(requests.get('http://rent.com' + x['url_path']).text)
        geocode = propInfo.findAll(True, {"property":['place:location:longitude', 'place:location:latitude']})
        x['dist_campus'] = haversine(float(univLoc[1]), float(univLoc[0]), float(geocode[0]['content']), float(geocode[1]['content']))
        x['crime'] = crime.fetch(geocode[0]['content'], geocode[1]['content'])
        # print(x['name'] + ' ' str(x['crime']))
        # print(x['name'] + ': ' + str(x['dist_campus']))
        #uncomment below when ready to test crime score. we don't want to spam spotcrime's API...
        #print(x['name'] + ' Safety: ' + str(x['crime']))

print("Please enter your University name.\n")
rentCom(input())
