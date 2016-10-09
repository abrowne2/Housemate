'''
Off campus housing aggregator
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

#used as ACParser
def autoComplete(input):
    # rent.com uses "ONESEARCH", and you can make calls to their query endpoint for JSON responses, nifty:
    univJSON = requests.get('http://onesearch.svc.primedia.com/autocomplete?q=' + input + '&application=rent')
    univJSON = json.loads(univJSON.text)  # parse the JSON response.

    # use the seopath to retrieve the listing ids.
    universities = [[x['name'], x['seopath'], x['geocode']] for x in univJSON]

    return universities

def performChoice(hbool, abool, seopath, budget, beds):
    listIds = '' #list of listing ids used for traversal

    if hbool is True and abool is True: #User does not care. Fetch both houses/apartments.
        haws = requests.get('http://rent.com' + seopath + 'condos_houses_townhouses' + (('_max-price-' + budget) + '_' + beds + '-bedroom'))
        cribz = requests.get('http://rent.com' + seopath + 'apartments_condos_townhouses' + (('_max-price-' + budget) + '_' + beds + '-bedroom'))
        listIds = ','.join(BeautifulSoup(haws.text, "html.parser").find(attrs={"name": "listing_ids"})['content'].split(';')) +\
            ','.join(BeautifulSoup(cribz.text, "html.parser").find(attrs={"name": "listing_ids"})['content'].split(';'))
    elif hbool and abool is False: #user wants to find a house.
        haws = requests.get('http://rent.com' + seopath + 'condos_houses_townhouses' + (('_max-price-' + budget) + '_' + beds + '-bedroom'))
        listIds = ','.join(BeautifulSoup(haws.text, "html.parser").find(attrs={"name": "listing_ids"})['content'].split(';'))
    else: #user wants an apartment
        cribz = requests.get('http://rent.com' + seopath + 'apartments_condos_townhouses' + (('_max-price-' + budget) + '_' + beds + '-bedroom'))
        listIds = ','.join(BeautifulSoup(cribz.text, "html.parser").find(attrs={"name": "listing_ids"})['content'].split(';'))

    return listIds

#given a url_path, fetch more information about the specified property
def rentPropertyTraversal(listIds, univLoc, usrDist):
    #make a call to the rent.com listings.json endpoint, and get all the data required for interpretation.
    propJSON = json.loads(requests.get('http://rent.com/account/myrent/listings.json?ids=' + listIds).text)

    #list comprehension technique here: this is actually a dictionary inside a list. refer to the values by key,
    properties = [{'url_path': x['url_path'], 'name': x['name'], 'address': x['address'], 'city': x['city'],
                    'state': x['state'], 'price_range': x['price_range'], 'bedroom_range': x['bedroom_range'],
                    'bathroom_range': x['bathroom_range'], 'image_url': x['image_url']} for x in propJSON['listings']]
    for x in properties:
        propInfo = BeautifulSoup(requests.get('http://rent.com' + x['url_path']).text, "html.parser")
        geocode = propInfo.findAll(True, {"property": ['place:location:longitude', 'place:location:latitude']})
        x['dist_campus'] = distance.haversine(float(univLoc[1]), float(univLoc[0]), float(geocode[0]['content']),
                                              float(geocode[1]['content']))
        x['withinRange'] = True if x['dist_campus'] < usrDist else False
        if x['withinRange']:
            x['crime'] = crime.fetch(geocode[0]['content'], geocode[1]['content'])
    return properties

