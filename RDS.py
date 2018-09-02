import boto3
import hashlib
import pymssql
import tkinter.messagebox as tkMessageBox
from tkinter import filedialog
import Email
import User



class RDS:
    def __init__(self):
        #initialize everything
        self.Server = "sqlsv-cs633cs.cbpyuvpamt0n.us-east-2.rds.amazonaws.com"
        self.DbUser = "admin1"
        self.DbPassword = "sqlsv-cs633cs!"
        self.DataBase = "s3bucketmon"
        self.Port = "1433"
        self.Conn = ""
        self.Cursor = ""
        self.OutputTextFileStatus = ""

    def Connect(self):
        self.Conn = pymssql.connect(server=self.Server, user=self.DbUser, password=self.DbPassword, database=self.DataBase, port=self.Port)
        self.Cursor = self.Conn.cursor()

    def Disconnect(self):
        self.Conn.close()

    def UserExists(self, _username, _password):
        command = "SELECT * FROM Customer WHERE Username = '{}'".format(_username, _password)
        self.Cursor.execute(command)
        customerRow = self.Cursor.fetchone()

        if(customerRow != None):
            return True
        else:
            return False

    def LoadUser(self, _username, _password):
        command = "SELECT * FROM Customer WHERE Username = '{}' AND Password = '{}'".format(_username, _password)
        self.Cursor.execute(command)
        customerRow = self.Cursor.fetchone()

        user = User.User(str(customerRow[0]), str(customerRow[1]), str(customerRow[2]), str(customerRow[3]), str(customerRow[4]), str(customerRow[5]), str(customerRow[6]), str(customerRow[7]), str(customerRow[8]), str(customerRow[9]), str(customerRow[10]), str(customerRow[11]), str(customerRow[12]), str(customerRow[13]), str(customerRow[14]))
        return user

    def ExecuteRegisterUser(self, _username, _password, _email, _phone, _firstName, _lastName, _defaultFileDirectory):
        command = "INSERT INTO Customer (Username, Password, Email, Phone, FirstName, LastName, DefaultFileDirectory) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        self.Cursor.execute(command,(_username, _password, _email, _phone, _firstName, _lastName, _defaultFileDirectory))
        self.Conn.commit()
        print("user registered!")

    def ExecuteGetUserPreferences(self, _username, _password):
        command = "SELECT Email, DefaultFileDirectory FROM Customer WHERE Username = '{}' AND Password = '{}'".format(_username, _password)
        self.Cursor.execute(command)
        preferencesRow = self.Cursor.fetchone()

        return preferencesRow # [0] = Email [1] = DefaultDirectory

    def UpdateUserPreferences(self, _email, _defaultDirectory, _username, _password):
        command = "UPDATE Customer SET Email = '{}', DefaultFileDirectory = '{}' WHERE Username = '{}' AND Password = '{}'".format(_email,_defaultDirectory, _username, _password)
        self.Cursor.execute(command)
        self.Conn.commit()


    def uploadBucketFileContentsToDatabase(self,response, localFilePath, fileName, bucketName, userName, password, emailAddress, phoneNumber, firstName, lastName):

        print("\nConnecting and updating values in the rds database table ...")

        self.Connect()
        #conn = pymssql.connect(server=self.Server, user=self.DbUser, password=self.DbPassword, database=self.Database, port=self.Port)
        #cursor = conn.cursor()

        print(response)
        if response is not None:

            bucketEtag = str(response['ResponseMetadata']['HTTPHeaders']['etag'])
            localEtag = self.getLocalFileEtag(localFilePath)
            createdDate = str(response['ResponseMetadata']['HTTPHeaders']['date'])
            lastModifiedDate = str(response['ResponseMetadata']['HTTPHeaders']['date'])
            versionId = str(response['VersionId'])
            isMissingTag = "0"
            print("KeyFile: " + fileName)
            print("FilePath: " + localFilePath)
            print("bucket: " + bucketName)
            print("ETagS3: " + bucketEtag)
            print("ETagMy: " + localEtag)
            print("CreateDate: " + createdDate)
            print("LastModified: " + lastModifiedDate)
            print("VersionId: " + versionId)
            print("IsMissing: " + isMissingTag)

            #        cursor.execute("INSERT into dbo.Customer (Username, Password, Email, Phone, FirstName, LastName) VALUES (%s, %s, %s, %s, %s, %s) Select %s Where not exists(Select * from dbo.Customer where Username=%s)", (userName, password, emailAddress, phoneNumber, firstName, lastName, userName, userName))
            self.Cursor.execute(
                "If Not Exists (Select * from dbo.Customer where Username=%s) INSERT into dbo.Customer (Username, Password, Email, Phone, FirstName, LastName) VALUES (%s, %s, %s, %s, %s, %s)",
                (userName, userName, password, emailAddress, phoneNumber, firstName, lastName))
            self.Conn.commit()

            # Retrieving CustomerID that was added to the Customer table
            #        cursor.execute('SELECT max(CustomerID) FROM dbo.Customer')
            self.Cursor.execute(
                'SELECT CustomerID FROM dbo.Customer Where Username=%s and Password=%s and Email=%s and Phone=%s',
                (userName, password, emailAddress, phoneNumber))
            customerId = 0
            print(self.Cursor)
            for row in self.Cursor:
                customerId = row[0]

            # Check if the FileMon table already has an entry for the customer
            dbEtag = ""
            dbVersionId = versionId
            existsInFileMonTable = "No"
            print("Username: {}".format(userName))
            print("CustomerId: {}".format(customerId))
            self.Cursor.execute(
                'SELECT ETags3, VersionId from dbo.FileMon where CustomerID=%s and Username=%s and KeyFile=%s and FilePath=%s and Bucket=%s',
                (customerId, userName, fileName, localFilePath, bucketName))
            for row in self.Cursor:
                existsInFileMonTable = "Yes"
                dbEtag = row[0]
                dbVersionId = row[1]
                self.OutputTextFileStatus = "fileGood"

            print(dbEtag)
            if existsInFileMonTable == "No":
                # add new entry into the FileMon table
                self.Cursor.execute(
                    "INSERT into dbo.FileMon (CustomerID, Username, KeyFile, FilePath, Bucket, ETagS3, ETagMy, CreateDate, LastModified, VersionId, IsMissing) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (customerId, userName, fileName, localFilePath, bucketName, bucketEtag, localEtag, createdDate,
                     lastModifiedDate, dbVersionId, isMissingTag))
                self.Conn.commit()
                self.OutputTextFileStatus = "fileGood"
            elif dbEtag != bucketEtag:
                # Send email and text to the user asking about the change
                print("BucketEtag: {}".format(bucketEtag))
                print("DbEtag: {}".format(dbEtag))



                userModifiedFile = tkMessageBox.askquestion("Alert!", "Did you modify the file: '{}'? ".format(fileName))
                if userModifiedFile == "yes":
                    wasFileHacked = "No"
                    self.Cursor.execute(
                        "UPDATE dbo.FileMon SET ETagS3=%s, ETagMy=%s where CustomerId=%s and Username=%s and KeyFile=%s and FilePath=%s and Bucket=%s",
                        (bucketEtag, localEtag, customerId, userName, fileName, localFilePath, bucketName))
                    self.Conn.commit()
                    self.OutputTextFileStatus = "fileGood"

                else:
                    wasFileHacked = "Yes"
                    retrieveLastGoodVersion = tkMessageBox.askquestion("Alert!", "Would you like to retrieve the last known good of this file? ({})".format(fileName))
                    if retrieveLastGoodVersion == "yes":
                        etagResponse = boto3.resource('s3').meta.client.head_object(Bucket=bucketName, Key=fileName,
                                                                                    VersionId=dbVersionId)
                        folderToSendInfo = ""
                        overwriteFile = tkMessageBox.askquestion("Alert!", "Do you want to download and overwrite your local copy of: {}?".format(fileName))
                        if overwriteFile == "yes":
                            folderToSendInfo = localFilePath
                        else:
                            folderToSendInfo = filedialog.askdirectory(title="Select destination for last known good file: {}".format(fileName))
                            if (folderToSendInfo != ""):
                                folderToSendInfo += "\\" + fileName
                            else:
                                tkMessageBox.showinfo("Alert!","\nLast known good was not downloaded.")

                        print(folderToSendInfo)
                        try:
                            boto3.resource('s3').meta.client.download_file(Bucket=bucketName, Key=fileName,
                                                                           Filename=folderToSendInfo,
                                                                           ExtraArgs={'VersionId': dbVersionId})
                        except:
                            print("Couldn't download file")
                    else:
                        tkMessageBox.showinfo("Alert!","\nThe last known good for '{}' was not downloaded.".format(fileName))
                    self.OutputTextFileStatus = "fileBad"

                mailClient = Email.Email()
                mailClient.sendEmail(emailAddress, fileName, bucketName, dbVersionId)



            else:
                self.Cursor.execute(
                    "UPDATE dbo.FileMon SET ETagS3=%s, ETagMy=%s where CustomerId=%s and Username=%s and KeyFile=%s and FilePath=%s and Bucket=%s",
                    (bucketEtag, localEtag, customerId, userName, fileName, localFilePath, bucketName))
                self.Conn.commit()

            print("'{}' database is updated. Closing the connection...".format(self.DataBase))

            #    cursor.execute('SELECT * FROM dbo.FileMonitor')
            #    print(cursor)
            #    for row in cursor:
            #        print('row = %r' % (row,))
            self.Conn.close()
            print("The database connection is closed.")
        else:
            print("Empty response")


    def getLocalFileEtag(self, localFilePath):

        md5s = []

        with open(localFilePath, 'rb') as fp:
            while True:
                data = fp.read(8 * 1024 * 1024)
                if not data:
                    break
                md5s.append(hashlib.md5(data))

        if len(md5s) == 1:
            localFileEtag = '"{}"'.format(md5s[0].hexdigest())
        else:
            digests = b''.join(m.digest() for m in md5s)
            digests_md5 = hashlib.md5(digests)
            localFileEtag = '"{}-{}"'.format(digests_md5.hexdigest(), len(md5s))

        return localFileEtag