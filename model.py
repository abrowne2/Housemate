import requests, json, sys
sys.path.insert(0, 'aggregation/')
import aggregation

#makeshift enum for states
class Global_States:
    LOCATION = 0
    BUDGET = 1
    CRIMERATING = 2

# class University:


#model class for modeling the conversation
class Conversation:
    prefs = {Global_States.LOCATION:"", Global_States.BUDGET:"",Global_States.CRIMERATING:""}
    curState = 0
    id = 0
    numBeds=0

    #constructor
    def __init__(self, arg):
        global Global_States
        self.id = arg

    def incrState(self):
        self.curState+= 1

    #setter for pref hash
    def setPref(self, prefName, newVal):
        self.prefs[prefName] = newVal

    #begin parsing functions
    def ACParser(self, arg):
        #get the university output
        universities = aggregation.autoComplete(arg)
        output = ''
        #university names are located at the first index:
        for index, univ in enumerate(universities):
            output += str(index + 1) + '. ' + univ[0] + '\n'
        print(output)
        return output

x = Conversation(243)
x.ACParser("University of Michigan")
#testModel = Model(1)
