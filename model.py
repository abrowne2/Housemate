import requests, json, sys
sys.path.insert(0, 'aggregation/')
import aggregation

#makeshift enum for states
class Global_States:
    LOCATION = 0
    BUDGET = 1
    CRIMERATING = 2

class University:
    def __init__(self, name, seopath, geocode):
        self.name = name
        self.seopath = seopath
        self.geocode = geocode
    #continue with this further...

#model class for modeling the conversation
class Conversation:
    prefs = {Global_States.LOCATION:"", Global_States.BUDGET:"",Global_States.CRIMERATING:""}
    curState = 0
    id = 0
    numBeds = 0
    house = False
    apartment = False
    acResults = []
    acIndex = 0

    #constructor
    def __init__(self, arg):
        global Global_States
        self.id = arg

    def incrState(self):
        self.curState+= 1

    #setter for pref hash
    def setPref(self, prefName, newVal):
        self.prefs[prefName] = newVal

    # begin parsing functions
    def ACParser(self, arg):
        # get the university output
        universities = aggregation.autoComplete(arg)
        # university names are located at the first index:
        for univ in universities:
            self.acResults.append(univ)

    def pricePrs(self, arg):
        # 4 cases: From $$$, $$$ - $$$, $$$, & No price listed
        if int(arg) > 5000: #input validation for rent.com
            arg = 5000
        self.setPref(Global_States.BUDGET, int(arg))


    def optionPrs(self, arg):
        # Apartment, House, or Both
        # (Will lead to specific cases)
        arg = arg.lower()
        if arg == "house":
            self.house = True
        elif arg == "apartment":
            self.apartment = True
        else:
            self.house = True
            self.apartment = True

    def bedBathPrs(self, arg):
        # typically a range #-# Beds / # Bath
        self.numBeds = int(arg)
        if self.numBeds > 4: #input validation for rent.com
            self.numBeds = 4

    def acIndexParse(self, arg):
        self.acIndex = int(arg)

    def acResultsToString(self):
        output = ""
        for index, univ in enumerate(self.acResults):
            output += str(index + 1) + '. ' + univ[0] + '\n'
        return output

    def preferentialSearch(self):
        '''
        1. Get the seopath from the selected university (acIndex - 1)
        2. Make the search based on budget, option, etc
        3. Use aggregator module for further depth
        '''
        univIndex = self.acIndex - 1
        seopath = self.acResults[univIndex][1]
        name = self.acResults[univIndex][0]
        properties = aggregation.rentPropertyTraversal(aggregation.performChoice(
            self.house, self.apartment, seopath, str(self.prefs[Global_States.BUDGET]), str(self.numBeds)),
            self.acResults[univIndex][2].split(','), 3)

        return properties

        #use the below to test
        # print('User wants to be ' + str(self.prefs[Global_States.LOCATION]) + ' mi from campus, budget: ' +
        #       str(self.prefs[Global_States.BUDGET]) + ', up to ' + str(self.numBeds) + ' beds')
        # for x in properties:
        #     if x['withinRange'] is True:
        #         print(x['name'] + ' ' + str(x['price_range']) + ' ' + x['bedroom_range'] +
        #               ' , dist: ' + str(x['dist_campus']) + ' mi, Crime: ' + str(x['crime']))

