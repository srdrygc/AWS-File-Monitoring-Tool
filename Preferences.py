import RDS

class Preferences:
    def __init__(self):
        #initialize everything
        self.DefaultDirectory = ""
        self.Email = ""

    def loadPreferences(self, _username, _password):
        db = RDS.RDS()

        # open the database
        db.Connect()

        # get our preferences and assign them
        preferences = db.ExecuteGetUserPreferences(_username, _password)
        self.Email = str(preferences[0])
        self.DefaultDirectory = str(preferences[1])

        # close the connection
        db.Disconnect()

    #def savePreferences(self, newDefaultDirectory, newEmail):


