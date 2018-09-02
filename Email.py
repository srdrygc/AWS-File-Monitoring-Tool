import smtplib
import boto3
import tkinter.messagebox as tkMessageBox

class Email:

    def __init__(self):
        self.FromEmailAddress = "lbalfourboto3@gmail.com"
        self.FromEmailPassword = "Crusaders18"

    def sendEmail(self, toEmailAddress, fileName, bucketName, versionId):
        wasFileHacked = "No"
        wasFileChanged = "No"
        fromEmailAddress = ""
        fromEmailPassword = ""
        isModifiedFile = "No"

        serverType = str("smtp.{}".format(self.FromEmailAddress.split("@", 1)[1]))
        serverSsl = smtplib.SMTP_SSL(serverType, 465)
        serverSsl.ehlo()

        fileStatus = "of modified"
        if wasFileHacked == "Yes":
            fileStatus = "recovered from hacked"
        subject = "Contents {} file '{}' in bucket '{}'".format(fileStatus, fileName, bucketName)
        messageText = self.getDetailsFromUploadedFile(fileName, bucketName)
        message = "From: '{}'\nTo: '{}'\nSubject: {}\n\n'{}'".format(self.FromEmailAddress, toEmailAddress, subject,
                                                                       messageText)

        url = boto3.session.Session().client('s3').generate_presigned_url('get_object',
                                                                          Params={'Bucket': bucketName, 'Key': fileName,
                                                                                  'VersionId': versionId},
                                                                          ExpiresIn=100).split('?')[0]
        message += "\n\nYou can view and download the contents of your file in the url below: \n" + url

        serverSsl.login(self.FromEmailAddress, self.FromEmailPassword)
        serverSsl.sendmail(self.FromEmailAddress, toEmailAddress, message)
        tkMessageBox.showinfo("Alert!", "\nAn email notification has been sent to '{}'".format(toEmailAddress))
        serverSsl.quit()


    def getDetailsFromUploadedFile(self, fileName, bucketName):

        details = ""

        for currentBucket in boto3.resource('s3').buckets.all():
            if currentBucket.name == bucketName:
                for item in currentBucket.objects.all():
                    # get the contents of the bucket
                    key = item.key
                    if (item.key == fileName):
                        last_modified = str(item.last_modified)
                        contents = str(item.get()['Body'].read()).split("'")[1].split("\\r\\n") #'
                        print("pre: " + str(contents))
                        if contents is None:
                            contents = "N/A"
                        #                    fileContents = formatter.format(key, last_modified, contents)
                        details += "File Name: {}\nLast Modified Date: {}\nFile Contents: \n================".format(key, last_modified)
                        #contents
                        for fileLine in contents:
                            details += "\n" + str(fileLine)
                        details += "\n================"

        return details