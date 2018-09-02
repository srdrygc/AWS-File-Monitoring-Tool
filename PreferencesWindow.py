import boto3
import botocore
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import tkinter.messagebox as tkMessageBox

import RDS
import S3
import User
import Preferences
import ETag


class PreferencesWindow():

    def UpdatePreferences(self, _user):
        db = RDS.RDS()
        db.Connect()
        db.UpdateUserPreferences(self.e_email.get(), self.e_directory.get(), self.USER.Username, self.USER.Password)
        db.Disconnect()

    def __init__(self, _user, *args, **kwargs):

        self.USER = _user
        #tk.Tk.__init__(self, *args, **kwargs)
        #container = tk.Frame(self)

        #self.maxsize(650, 450)

        #container.pack()

        prefControls_frame = tk.Frame(self)
        prefControls_frame.pack(fill=tk.BOTH)

        # add controls to preferences window
        self.l_directory = ttk.Label(prefControls_frame, text="Default File(s) Directory:")
        self.l_email = ttk.Label(prefControls_frame, text="Email:")
        self.e_directory = ttk.Entry(prefControls_frame)
        self.e_email = tk.Entry(prefControls_frame)
        self.b_save = ttk.Button(prefControls_frame, text="Save", command=self.UpdatePreferences)

        for i in range(5):
            if (i == 1):
                prefControls_frame.columnconfigure(i, weight=4)
            prefControls_frame.rowconfigure(i, weight=1)
        # prefControls_frame.columnconfigure(1, minsize=100)

        # add all widgets to grid
        self.l_directory.grid(row=0, sticky=tk.W + tk.E)
        self.l_email.grid(row=1, sticky=tk.W + tk.E)
        self.e_directory.grid(row=0, column=1, columnspan=2, sticky=tk.W + tk.E)
        self.e_email.grid(row=1, column=1, columnspan=2, sticky=tk.W + tk.E)
        self.b_save.grid(row=2, column=2, sticky=tk.W + tk.E)

        # populate the widgets with our users' preferences
        userPrefs = Preferences.Preferences()
        userPrefs.loadPreferences()
        self.e_directory.insert(0, userPrefs.DefaultDirectory)  # "test"
        self.e_email.insert(0, userPrefs.Email)  # "test"