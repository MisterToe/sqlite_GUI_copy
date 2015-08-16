from __future__ import unicode_literals
import datetime
import glob
import os
import shutil
import sqlite3
import wx

class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(500, 200))
        
        panel = wx.Panel(self, -1)
        wx.StaticText(panel, -1, "Copy text files modified since:", (120,10))

        # Get the last row in the table
        lastRowA = getLastRow()

        # Display the last date and time files were transferred
        self.LastTransferDate = wx.StaticText(panel, -1, lastRowA[1], (285,10))
        
        # Create the origin folder label, textbox, and button
        wx.StaticText(panel, -1, "Origin Folder:", (34,43))
        self.OriginFilePath = wx.TextCtrl(panel, pos=(120,40), size=(250,25), name="Origin", style=wx.TE_READONLY)
        wx.Button(panel, 1, "Browse", (375, 40))
        self.Bind(wx.EVT_BUTTON, self.originBrowse, id=1)

        # Create the destination folder label, textbox, and button
        wx.StaticText(panel, -1, "Destination Folder:", (5,73))
        self.DestFilePath = wx.TextCtrl(panel, pos=(120,70), size=(250,25), name="Dest", style=wx.TE_READONLY)
        wx.Button(panel, 2, "Browse", (375, 70))
        self.Bind(wx.EVT_BUTTON, self.destBrowse, id=2)

        # Create the copy files button
        wx.Button(panel, 3, "Copy Files", (190,100))
        self.Bind(wx.EVT_BUTTON, self.copyFiles, id=3)

        self.Show(True)
        
    def originBrowse(self, event):
        '''
        Dialog box for the origin folder
        '''
        
        dlg = wx.DirDialog(self, "Choose a Origin Folder:")

        if dlg.ShowModal() == wx.ID_OK:
            self.OriginFilePath.WriteText(dlg.GetPath())
            
        dlg.Destroy()

    def destBrowse(self, event):
        '''
        Dialog box for the destination folder
        '''
        
        dlg = wx.DirDialog(self, "Choose a Destination Folder:")

        if dlg.ShowModal() == wx.ID_OK:
            self.DestFilePath.WriteText(dlg.GetPath())
            
        dlg.Destroy()

    def copyFiles(self, event):
        '''
        Copy files modified since the last transfer date from origin to destination folder
        '''

        originPath = self.OriginFilePath.GetValue() + "\\"
        destPath = self.DestFilePath.GetValue() + "\\"
        fileType = ".txt"

        # Get the last row in the database
        lastRowB = getLastRow()
        
        id = lastRowB[0] + 1
        dtLastDateTime = datetime.datetime.strptime(lastRowB[1], "%m-%d-%Y %H:%M:%S")

        # Create list of text filenames in origin folder
        fileList = glob.glob(originPath + "*" + fileType)

        # Connect to database
        conn = sqlite3.connect("copy_text_files.db")
        c = conn.cursor()

        # Loop through the filenames
        for file in fileList:
            # Get last modified date and today's date
            modifyDate = datetime.datetime.fromtimestamp(os.path.getmtime(file))
    
            filePathList = file.split("\\") # Create a list from the filepath
            filename = filePathList[-1] # The last element is a the filename

            if modifyDate > dtLastDateTime:
                shutil.copy2(file, destPath + filename)

        # Insert new row into the database
        todaysDate = datetime.datetime.today().strftime("%m-%d-%Y %H:%M:%S")

        c.execute("INSERT INTO DateTime VALUES(?,?)",(id, todaysDate))
        conn.commit()
        conn.close()

        # Update GUI with new date and time
        self.LastTransferDate.SetLabel(todaysDate)

def getLastRow():
    '''
    Get the last date and time the files were copied
    '''

    conn = sqlite3.connect("copy_text_files.db")
    c = conn.cursor()
    c.execute("SELECT * FROM DateTime WHERE ID = (SELECT MAX(ID) FROM DateTime)")
    row = c.fetchone()
    conn.close()
    return row

if __name__=="__main__":    
    app = wx.App(False)
    frame = MainWindow(None, "Transfer Process")
    app.MainLoop()
