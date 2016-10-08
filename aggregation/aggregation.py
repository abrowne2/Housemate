'''
Off Campus Housing Aggregator
Author: Adam Browne
'''

import requests, json, crime, distance
from bs4 import BeautifulSoup


'''Rent.com Aggregation

http://onesearch.svc.primedia.com/autocomplete?q=[QUERY]&application=rent

One you've extracted the listing id's from the request, send them here:

http://www.rent.com/account/myrent/listings.json?ids=[IDS]
for a json object containing pertinent information.

First, the user's query is sent through the autocomplete endpoint.
A list of colleges will be retrieved, and then the request will be made.
Pertinent information is stored accordingly.

'''


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

    univ = int(input()) - 1

    choice = requests.get('http://rent.com' + universities[univ][1])

    #retrieve the list of listing_ids, which we can use to obtain a JSON object of all the properties.
    listIds = ','.join(BeautifulSoup(choice.text, "html.parser").find(attrs={"name":"listing_ids"})['content'].split(';'))

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
        propInfo = BeautifulSoup(requests.get('http://rent.com' + x['url_path']).text, "html.parser")
        geocode = propInfo.findAll(True, {"property": ['place:location:longitude', 'place:location:latitude']})
        x['crime'] = crime.fetch(geocode[0]['content'], geocode[1]['content'])
        x['dist_campus'] = distance.haversine(float(univLoc[1]), float(univLoc[0]), float(geocode[0]['content']),
                                     float(geocode[1]['content']))

print("Please enter your University name.\n")
rentCom(input())
