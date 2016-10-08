
#makeshift enum for states
class Global_States:
    LOCATION = 0
    BUDGET = 1
    CRIMERATING = 2



#model class for modeling the conversation
class Model:
    prefs = {Global_States.LOCATION:"", Global_States.BUDGET:"",Global_States.CRIMERATING:"" }
    curState = 0
    id = 0
    
    #constructor
    def __init__(self, arg):
        global Global_States
        self.id = arg
    
    def incrState(self):
        self.curState+= 1
        
    #setter for pref hash    
    def setPref(self, prefName, newVal):
        self.prefs[prefName] = newVal

#testModel = Model(1)
