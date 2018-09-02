# Tkinter Project

import boto3
import botocore
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import tkinter.messagebox as tkMessageBox
from botocore.errorfactory import ClientError
import RDS
import S3
import User
import Preferences
import PreferencesWindow
import ETag

USER = User.User("", "", "", "", "", "", "", "", "", "", "", "", "", "", "")
ANALYSIS = ""

class awsFileCheckerUtilityApp(tk.Tk):



    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        self.maxsize(650, 450)

        container.pack()




        container.grid_rowconfigure(0, weight=1)
        for i in range(6):
            container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (LoginWindow, MainWindow, RegisterWindow):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky=tk.E + tk.W + tk.N + tk.S)

        # for F in (MainWindow, PrefsWindow):
        #   frame = F(container, self)
        #  self.frames[F] = frame
        # frame.grid(row=0, column=3, sticky="nsew")

        self.show_frame(LoginWindow)

    def updatePreferences(self):
        db = RDS.RDS()
        db.Connect()
        #email = e_email.get()
        #directory = e_directory.get()
        email = self.e_email.get()
        directory = self.e_directory.get()
        db.UpdateUserPreferences(email, directory, USER.Username, USER.Password)
        db.Disconnect()
        self.prefsWindow.destroy()


    def dirSelectPrefs_btnClick(self):
        dirPath = filedialog.askdirectory()

        if(dirPath != ""):
            # clear the old directory path
            self.e_directory.delete(0,'end')

            # add the new directory path
            self.e_directory.insert(0, dirPath)

    def exportFileAnalysis(self):
        analysis = ANALYSIS
        exportFile = filedialog.asksaveasfile(mode='w', defaultextension=".txt")

        if exportFile is None:
            return
        exportFile.write(analysis)
        exportFile.close()
        tkMessageBox.showinfo("Export Complete!", "Your analysis summary was successfully exported!")





    def openPreferences(self):

        self.prefsWindow = tk.Toplevel(self)
        self.prefsWindow.minsize(500, 90)

        # create frame to house widgets
        prefControls_frame = tk.Frame(self.prefsWindow)
        prefControls_frame.pack(fill=tk.BOTH)

        # add controls to preferences window
        self.l_directory = ttk.Label(prefControls_frame, text="Default File(s) Directory:")
        self.b_dirSelectPrefs = ttk.Button(prefControls_frame, text="Select Directory", command=self.dirSelectPrefs_btnClick)
        self.l_email = ttk.Label(prefControls_frame, text="Email:")
        self.e_directory = ttk.Entry(prefControls_frame)
        self.e_email = tk.Entry(prefControls_frame)
        self.b_save = ttk.Button(prefControls_frame, text="Save", command=self.updatePreferences)

        for i in range(5):
            if (i == 1):
                prefControls_frame.columnconfigure(i, weight=2)
            prefControls_frame.rowconfigure(i, weight=1)
        # prefControls_frame.columnconfigure(1, minsize=100)

        # add all widgets to grid
        self.l_directory.grid(row=0, column=0, sticky=tk.W + tk.E)
        self.l_email.grid(row=1, sticky=tk.W + tk.E)
        self.e_directory.grid(row=0, column=1, columnspan=1, sticky=tk.W + tk.E)
        self.e_email.grid(row=1, column=1, columnspan=1, sticky=tk.W + tk.E)
        self.b_dirSelectPrefs.grid(row=0, column=2, sticky=tk.W + tk.E)
        self.b_save.grid(row=2, column=2, sticky=tk.W + tk.E)

        # populate the widgets with our users' preferences
        userPrefs = Preferences.Preferences()
        userPrefs.loadPreferences(USER.Username, USER.Password)
        self.e_directory.insert(0, userPrefs.DefaultDirectory)  # "test"
        self.e_email.insert(0, userPrefs.Email)  # "test"

    def show_frame(self, cont):

        # creates the preferences window and open it
        #   only used by MainWindow frame

        # adds menu to window when the MainWindow Frame is displayed
        if (cont == MainWindow):
            m_mainWindowMenu = tk.Menu(self)
            self.config(menu=m_mainWindowMenu)

            subMenuFile = tk.Menu(m_mainWindowMenu)
            m_mainWindowMenu.add_cascade(label="File", menu=subMenuFile)
            subMenuFile.add_command(label="Export" , command=self.exportFileAnalysis)
            subMenuFile.add_command(label="Preferences", command=self.openPreferences)

        frame = self.frames[cont]
        frame.tkraise()


class MainWindow(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        for i in range(3):
            self.columnconfigure(i, weight=1)
            if (i == 2):
                self.rowconfigure(i, weight=3)

        self.l_directory = ttk.Label(self, text="Directory:")
        self.e_directory = ttk.Entry(self)
        self.b_dirSelect = ttk.Button(self, text="Select Directory", command=self.dirSelect_btnClick)
        self.l_blank = ttk.Label(self, text="        ")
        self.b_submit = ttk.Button(self, text="Submit", command=lambda: self.RunFileAnalysis())  # , command=self.submit_btnClick
        self.t_log = tk.Text(self, bg="black", fg="white", insertbackground="white")

        # position the widgets on the screen
        # row 0
        self.l_directory.grid(row=0, column=0, sticky=tk.E)
        self.columnconfigure(1, minsize=100)  # row=0, column=1
        self.e_directory.grid(row=0, column=1, columnspan=3, sticky=tk.W + tk.E)
        self.b_dirSelect.grid(row=0, column=4, columnspan=2, sticky=tk.W + tk.E, padx=5, pady=2)
        # row 1
        self.b_submit.grid(row=1, column=4, columnspan=2, sticky=tk.W + tk.SE, padx=5, pady=2)
        # row 3
        self.t_log.grid(row=2, column=0, columnspan=5, rowspan=2, sticky=tk.W + tk.E + tk.S + tk.N, padx=5, pady=2)


    def getDetailsFromUploadedFile(self, fileName, bucketName):

        details = ""

        for currentBucket in boto3.resource('s3').buckets.all():
            if currentBucket.name == bucketName:
                for item in currentBucket.objects.all():
                    # get the contents of the bucket
                    key = item.key
                    if (item.key == fileName):
                        last_modified = str(item.last_modified)
                        contents = str(item.get()['Body'].read()).split("'")[1]
                        if contents is None:
                            contents = "N/A"
                        #                    fileContents = formatter.format(key, last_modified, contents)
                        details += "File Name: {}\nLast Modified Date: {}\nContents: {}".format(key, last_modified,
                                                                                                contents)
                        print(details)

        return details


    def createNewS3Bucket(self, bucketName):
        try:
            boto3.resource('s3').create_bucket(Bucket=bucketName, CreateBucketConfiguration={'LocationConstraint': 'us-east-2'})
            print("Created new bucket: {}".format(bucketName))
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'BucketAlreadyExists':
                print("Adding to existing {} bucket.".format(bucketName))
            elif error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                print("Adding to existing {} bucket.".format(bucketName))
            else:
                print('Error creating new bucket: ' + error.response['Error']['Code'])
                print(error)


    def getBoto3ResponseUsingLocalFileEtag(self, bucketName, fileName, localFilePath):
        etag = ETag.ETag()
        return boto3.resource('s3').meta.client.head_object(Bucket=bucketName, Key=fileName, IfMatch=etag.getLocalFileEtag(localFilePath))

    def getAllFileNamesInDirectory(self, folderDirectory):
        uploadFileNames = []

        for (folderDirectory, dirname, filename) in os.walk(folderDirectory):
            uploadFileNames.extend(filename)
            break

        return uploadFileNames


    def getSelectedFolderDirectory(self):
        selectedFolderDirectory = self.e_directory.get()

        if(selectedFolderDirectory != ""):
            # return the directory path if it has been set
            return selectedFolderDirectory
        else:
            #return "INVALID" if the directory is NOT set
            return "INVALID"


    def addTextHighlightingToFileAnalysis(self):
        self.t_log.tag_configure("keyword", foreground="yellow")
        self.t_log.tag_configure("fileGood", foreground="green")
        self.t_log.tag_configure("fileBad", foreground="red")
        self.t_log.tag_configure("fileNew", foreground="cyan")


    def RunFileAnalysis(self):
        # Main program/ file analysis will happen here.

        uploadFileNames = ""
        directoryValid = False

        # check to see if the directory entry box has been set. If not, prompt the user.
        # Repeat until the directory is set
        folderDirectory = self.getSelectedFolderDirectory()

        # if the directory is not set
        if (folderDirectory == "INVALID"):
            tkMessageBox.showinfo("Alert!", "Please select a file directory to analyze")

        # if directory is successfully set
        else:
            uploadFileNames = self.getAllFileNamesInDirectory(folderDirectory)
            directoryValid = True
            print("Valid directory!")

        if(directoryValid):

            self.t_log.insert(tk.INSERT, "Analyzing files in: ", "generalStatement")
            self.t_log.insert(tk.INSERT, folderDirectory + "\n", "keyword")
            self.addTextHighlightingToFileAnalysis()
            self.t_log.insert(tk.INSERT, "\n      Files\n===================", "generalStatement")

            bucket = S3.S3()
            self.createNewS3Bucket(bucket.BucketName)

            for fileName in uploadFileNames:

                localFilePath = os.path.join(folderDirectory + "\\" + fileName)
                response = {}
                print("\n-----\n\nUploading '{}' to Amazon S3 bucket '{}'".format(localFilePath, bucket.BucketName))

                # check metadata of local file and corresponding file in amazon s3
                try:
                    # update the current file in the bucket with the local file's contents
                    bucket.uploadFileToBucket(fileName, localFilePath)

                    response = self.getBoto3ResponseUsingLocalFileEtag(bucket.BucketName, fileName, localFilePath)
                except ClientError:
                    # Not found
                    print("No file '{}' found in bucket '{}'. Continuing upload...".format(fileName, bucket.BucketName))
                    self.t_log.insert(tk.INSERT, "\n" + fileName, "fileNew")
                    self.addTextHighlightingToFileAnalysis()

                if response != {}:
                    # reads the file back and displays the name from the file
                    print("The following was added to your '{}' bucket:".format(bucket.BucketName))
                    self.getDetailsFromUploadedFile(fileName, bucket.BucketName)

                    db = RDS.RDS()
                    db.Connect()
                    # connect to database and add new entry for response
                    db.uploadBucketFileContentsToDatabase(response, localFilePath, fileName, bucket.BucketName, USER.Username, USER.Password,
                                                       USER.EmailAddress, USER.PhoneNumber, USER.FirstName, USER.LastName)
                    self.t_log.insert(tk.INSERT, "\n" + fileName, db.OutputTextFileStatus)
                    self.addTextHighlightingToFileAnalysis()
                    db.Disconnect()

            # get the analysis in case the user wishes to export it to a text file
            global ANALYSIS
            ANALYSIS = str(self.t_log.get(1.0, tk.END))
            print('\n\nClosing program...')


    def dirSelect_btnClick(self):
        prefs = Preferences.Preferences()
        prefs.loadPreferences(USER.Username, USER.Password)
        dirPath = filedialog.askdirectory(initialdir=prefs.DefaultDirectory)
        self.e_directory.insert(0, dirPath)


class RegisterWindow(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.Controller = controller
        #l_RegisterHeader = ttk.Label(self, text="Register")
        self.l_username = ttk.Label(self, text="Username:")# *required
        self.l_usernameReq = ttk.Label(self, text="*", foreground="red")
        self.l_password = ttk.Label(self, text="Password:")# *required
        self.l_passwordReq = ttk.Label(self, text="*", foreground="red")
        self.l_email = ttk.Label(self, text="Email:")# *required
        self.l_emailReq = ttk.Label(self, text="*", foreground="red")
        self.l_phone = ttk.Label(self, text="Phone #:")# *required
        self.l_phoneReq = ttk.Label(self, text="*", foreground="red")
        self.l_firstName = ttk.Label(self, text="First Name:")  # *required
        self.l_firstNameReq = ttk.Label(self, text="*", foreground="red")
        self.l_lastName = ttk.Label(self, text="Last Name:")  # *required
        self.l_lastNameReq = ttk.Label(self, text="*", foreground="red")
        self.l_account = ttk.Label(self, text="Account #:") # required???
        self.l_directory = ttk.Label(self, text="File Directory Path:")
        self.l_mailAddr1 = ttk.Label(self, text="Mailing Address 2:")
        self.l_mailAddr2 = ttk.Label(self, text="Mailing Address 2:")
        self.l_city = ttk.Label(self, text="City:")
        self.l_state = ttk.Label(self, text="State:")
        self.l_zip = ttk.Label(self, text="Zip Code:")



        self.e_directory = ttk.Entry(self)
        self.b_directory = ttk.Button(self, text="Select Directory", command=self.dirSelect_btnClick)
        self.e_firstName = ttk.Entry(self)
        self.e_lastName = ttk.Entry(self)
        self.e_account = ttk.Entry(self)
        self.e_username = ttk.Entry(self)
        self.e_password = ttk.Entry(self)
        self.e_email = ttk.Entry(self)
        self.e_phone = ttk.Entry(self)
        self.e_city = ttk.Entry(self)
        self.cb_state = ttk.Combobox(self)
        self.e_zip = ttk.Entry(self)
        self.b_register = ttk.Button(self, text="Register", command=self.registerUser)#lambda: controller.show_frame(LoginWindow))

        self.columnconfigure(1, minsize=10)
        self.columnconfigure(2, minsize=100, weight=3)

        # Add widgets to layout
        #
        # Labels
        #l_RegisterHeader.grid(row=0, column=0, columnspan=2, sticky="we")
        self.l_directory.grid(row=0, column=0, sticky="e")
        self.l_firstName.grid(row=1, column=0, sticky="e")
        self.l_firstNameReq.grid(row=1, column=1, sticky="w")
        self.l_lastName.grid(row=2, column=0, sticky="e")
        self.l_lastNameReq.grid(row=2, column=1, sticky="w")
        #self.l_account.grid(row=3, column=0, sticky="e")
        self.l_username.grid(row=3, column=0, sticky="e")
        self.l_usernameReq.grid(row=3, column=1, sticky="w")
        self.l_password.grid(row=4, column=0, sticky="e")
        self.l_passwordReq.grid(row=4, column=1, sticky="w")
        self.l_email.grid(row=5, column=0, sticky="e")
        self.l_emailReq.grid(row=5, column=1, sticky="w")
        self.l_phone.grid(row=6, column=0, sticky="e")
        #self.l_city.grid(row=8, column=0, sticky="e")
        #self.l_state.grid(row=9, column=0, sticky="e")
        #self.l_zip.grid(row=10, column=0, sticky="e")

        # Entrys
        self.e_directory.grid(row=0, column=2, sticky="we")
        self.b_directory.grid(row=0, column=3, sticky="we")
        self.e_firstName.grid(row=1, column=2, columnspan=2, sticky="we")
        self.e_lastName.grid(row=2, column=2, columnspan=2, sticky="we")
        self.e_username.grid(row=3, column=2, columnspan=2, sticky="we")
        self.e_password.grid(row=4, column=2, columnspan=2, sticky="we")
        self.e_email.grid(row=5, column=2, columnspan=2, sticky="we")
        self.e_phone.grid(row=6, column=2, columnspan=2, sticky="we")
        #self.e_city.grid(row=8, column=2, columnspan=2, sticky="we")
        #self.cb_state.grid(row=9, column=2, columnspan=2, sticky="we")
        #self.cb_state.state(['readonly'])
        #self.e_zip.grid(row=10, column=2, columnspan=2, sticky="we")
        # Submit Button
        self.b_register.grid(row=7, column=2, columnspan=2, sticky="we")


        # populate the 'State' combobox
        states = self.PopulateStatesList()
        self.cb_state['values'] = list(states)

    def registerUser(self):
        username = self.e_username.get()
        password = self.e_password.get()
        firstName = self.e_firstName.get()
        lastName = self.e_lastName.get()
        email = self.e_email.get()
        phone = self.e_phone.get()
        defaultFileDirectory = self.e_directory.get()

        requiredFieldsComplete = self.checkRequiredFields()

        #print("All required fields complete: " + str(requiredFieldsComplete))

        if(requiredFieldsComplete == True):
            db = RDS.RDS()
            db.Connect()

            # if the user does not exist already in the database, add them to it
            if db.UserExists(username, password) != True:
                db.ExecuteRegisterUser(username, password, email, phone, firstName, lastName, defaultFileDirectory)
                self.Controller.show_frame(LoginWindow)
                self.destroy() #???

            else:
                tkMessageBox.showinfo("Alert!", "The username you have selected already exists. \n\nPlease choose a different one.")
            db.Disconnect()

    def checkRequiredFields(self):
        username = self.e_username.get()
        password = self.e_password.get()
        firstName = self.e_firstName.get()
        lastName = self.e_lastName.get()
        email = self.e_email.get()

        if(username != ""):
            if(password != ""):
                if (firstName != ""):
                    if (lastName != ""):
                        if (email != ""):
                            return True
                        else:
                            tkMessageBox.showinfo("Alert!", "Please complete the following field: 'Email'")
                            return False
                    else:
                        tkMessageBox.showinfo("Alert!", "Please complete the following field: 'Last Name'")
                        return False
                else:
                    tkMessageBox.showinfo("Alert!", "Please complete the following field: 'First Name'")
                    return False
            else:
                tkMessageBox.showinfo("Alert!", "Please complete the following field: 'Password'")
                return False
        else:
            tkMessageBox.showinfo("Alert!", "Please complete the following field: 'Username'")
            return False


    #
    # creates a dialog box that allows the user to select a directory to be used
    #
    def dirSelect_btnClick(self):
        dirPath = filedialog.askdirectory()
        self.e_directory.insert(0, dirPath)

    #
    # creates a list that's used to populate the 'State' comboBox on the registration page
    #
    def PopulateStatesList(self):

        states = list()
        states.append("Alabama")
        states.append("Alaska")
        states.append("Arizona")
        states.append("Arkansas")
        states.append("California")
        states.append("Colorado")
        states.append("Connecticut")
        states.append("Delaware")
        states.append("Florida")
        states.append("Georgia")
        states.append("Hawaii")
        states.append("Idaho")
        states.append("Ilinois")
        states.append("Indiana")
        states.append("Iowa")
        states.append("Kansas")
        states.append("Kentucky")
        states.append("Louisiana")
        states.append("Maine")
        states.append("Maryland")
        states.append("Massachusetts")
        states.append("Michigan")
        states.append("Minnesota")
        states.append("Mississippi")
        states.append("Missouri")
        states.append("Montana")
        states.append("Nebraska")
        states.append("Nevada")
        states.append("New Hampshire")
        states.append("New Jersey")
        states.append("New Mexico")
        states.append("New York")
        states.append("North Carolina")
        states.append("North Dakota")
        states.append("Ohio")
        states.append("Oklahoma")
        states.append("Oregon")
        states.append("Pennsylvania")
        states.append("Rhode Island")
        states.append("South Carolina")
        states.append("South Dakota")
        states.append("Tennessee")
        states.append("Texas")
        states.append("Utah")
        states.append("Vermont")
        states.append("Virginia")
        states.append("Washington")
        states.append("West Virginia")
        states.append("Wisconsin")
        states.append("Wyoming")

        return states



class LoginWindow(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.Controller = controller
        # Create widgets for preferences window
        self.l_LoginHeader = ttk.Label(self, text="Login")
        self.l_username = ttk.Label(self, text="Username:")
        self.l_password = ttk.Label(self, text="Password:")
        self.e_username = ttk.Entry(self)
        self.e_password = ttk.Entry(self)
        self.b_submit = ttk.Button(self, text="Login", command=self.UserLogin)
        self.b_register = ttk.Button(self, text="Register", command=lambda: controller.show_frame(RegisterWindow))

        self.columnconfigure(1, minsize=200, weight=4)

        # Add widgets to layout
        #
        # Labels
        self.l_LoginHeader.grid(row=0, column=0, columnspan=2, sticky="we")
        self.l_username.grid(row=1, column=0, sticky="we")
        self.l_password.grid(row=2, column=0, sticky="we")
        # l_EmptyRow.grid(row=5, column=0, sticky="we")

        # Entrys
        self.e_username.grid(row=1, column=1, sticky="we")
        self.e_password.grid(row=2, column=1, sticky="we")

        # Submit Buttons
        self.b_submit.grid(row=3, column=1, sticky="we")
        self.b_register.grid(row=4, column=1, sticky="we")


        # FOR TESTING PURPOSES
        #self.e_username.insert(0,"dhargett")
        #self.e_password.insert(0,"test")

    #
    # Checks to see if the username/ password combo exists. If so, the user is granted access.
    #
    def UserLogin(self):

        username = self.e_username.get()
        password = self.e_password.get()
        db = RDS.RDS()
        db.Connect()

        # check to see if the user exists in the database
        if db.UserExists(username, password):
            # if the user exists, load their info and display the main window of the application
            global USER # use the keyword "global" when modifying our global "USER" variable
            USER = db.LoadUser(username, password) # load the user data into the object
            self.Controller.show_frame(MainWindow)
        else:
            tkMessageBox.showinfo("Error", "Invalid credentials. \n\nPlease register or try again.")

        db.Disconnect()

app = awsFileCheckerUtilityApp()
app.mainloop()
