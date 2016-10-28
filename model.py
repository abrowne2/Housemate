import requests, json, sys
sys.path.insert(0, 'aggregation/')
import aggregation


#model class for modeling the conversation
class Conversation:

    #constructor-> a bit over the top, but it works
    #set default curState to be one.
    def __init__(self, arg, budget=1000, curState=1, numBeds=0, house=False,
        apartment=False, acResults=[], acIndex=0):
        self.id = arg; self.budget = budget
        self.curState = curState; self.numBeds = numBeds
        self.house = house; self.apartment = apartment
        self.acResults = acResults; self.acIndex = acIndex

    # begin parsing functions
    def ACParser(self, arg):
        # get the university output
        universities = aggregation.autoComplete(arg)
        print(universities)
        # university names are located at the first index:
        for univ in universities:
            self.acResults.append(univ)

    def pricePrs(self, arg):
        # 4 cases: From $$$, $$$ - $$$, $$$, & No price listed
        if int(arg) > 5000: #input validation for rent.com
            arg = 5000
        self.budget = int(arg)


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
        output = ''
        for index, univ in enumerate(self.acResults):
            output = output+ str(index + 1) + '. ' + univ[0] + '\n'
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
            self.house, self.apartment, seopath, str(self.budget), str(self.numBeds)),
            self.acResults[univIndex][2].split(','), 3.5)
        return properties

        #use the below to test
        # print('User wants to be ' + str(self.prefs[Global_States.LOCATION]) + ' mi from campus, budget: ' +
        #       str(self.prefs[Global_States.BUDGET]) + ', up to ' + str(self.numBeds) + ' beds')
        # for x in properties:
        #     if x['withinRange'] is True:
        #         print(x['name'] + ' ' + str(x['price_range']) + ' ' + x['bedroom_range'] +
        #               ' , dist: ' + str(x['dist_campus']) + ' mi, Crime: ' + str(x['crime']))
