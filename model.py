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
        # get the university output & TODO: use university class
        universities = aggregation.autoComplete(arg)
        # university names are located at the first index:
        for univ in universities:
            self.acResults.append(univ)

    def pricePrs(self, arg):
        # 4 cases: From $$$, $$$ - $$$, $$$, & No price listed
        self.setPref(Global_States.BUDGET, int(arg))

    def optionPrs(self, arg):
        # Apartment, House, or Both
        # (Will lead to specific cases)
        arg = arg.lower()
        if arg == "house":
            house = True
        elif arg == "apartment":
            apartment = True
        else:
            house = True
            apartment = True

    def bedBathPrs(self, arg):
        # typically a range #-# Beds / # Bath
        numBeds = int(arg)

    def acIndexParse(self, arg):
        acIndex = int(arg)

    def acResultsToString(self):
        output = ""
        for index, univ in enumerate(self.acResults):
            output += str(index + 1) + '. ' + univ[0] + '\n'
        return output

    def preferentialSearch(self):
        pass




#testModel = Model(1)
