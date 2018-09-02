

class User:
    def __init__(self):
        self.FirstName = ""
        self.LastName = ""
        self.Username = ""
        self.Password = ""
        self.EmailAddress = ""
        self.PhoneNumber = ""
        self.DefaultFileDirectory = ""

    def __init__(self, _customerId, _username, _password, _emailAddress, _phoneNumber, _firstName, _lastName, _account, _emailOptOut, _mailAddr1, _mailAddr2, _city, _state, _zip, _defaultFileDirectory):
        self.CustomerID = _customerId
        self.Username = _username
        self.Password = _password
        self.EmailAddress = _emailAddress
        self.PhoneNumber = _phoneNumber
        self.FirstName = _firstName
        self.LastName = _lastName
        self.Account = _account
        self.EmailOptOut = _emailOptOut
        self.MailAddr1 = _mailAddr1
        self.MailAddr2 = _mailAddr2
        self.City = _city
        self.State = _state
        self.Zip = _zip
        self.DefaultFileDirectory = _defaultFileDirectory


