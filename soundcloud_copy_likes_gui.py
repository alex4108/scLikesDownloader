import easygui as eg
import scLikesDownloader
import urllib2
from time import time
import sys

class guiController:
    def __init__(self):
        #constructor
        
        self.version = '1.0.0-beta1'
        self.title = "SoundCloud Likes Downloader " + str(self.version)
        self.desc = "Controller Class for EasyGui"
    def newDownload(self):
        msg         = "Enter the download information"
        title       = self.title
        fieldNames  = ["SoundCloud Profile URL"]
        fieldValues = ['http://www.soundcloud.com/']  # we start with blanks for the values
        fieldValues = eg.multenterbox(msg,title, fieldNames, values=fieldValues)
        
        
        # make sure that none of the fields was left blank
        while 1:  # do forever, until we find acceptable values and break out
            if fieldValues == None: 
                break
            errmsg = ""
            
            # look for errors in the returned values
            for i in range(len(fieldNames)):
                if fieldValues[i].strip() == "" :
                    errmsg = errmsg + ('"%s" is a required field.\n\n' % fieldNames[i])
                if i == 0:
                    self.url = fieldValues[0]
                   
            # Designate save folder as PATH
            path = eg.diropenbox(msg="Select a folder to save the mp3 files to", title=self.title)
            self.downloader = scLikesDownloader.downloader(fieldValues[0], path)

            if not self.downloader:
                errmsg = "Invalid Path or SoundCloud Profile URL.  Please try again."
            elif True:
                eg.msgbox(msg='Press start to begin retrieving this user\'s likes (This may take a while)', title=self.title, ok_button='Start Retrieval')
                favorites = self.downloader.trackList()
                eg.msgbox(msg='We have all their favorites.  There are ' + str(len(favorites)) + ' to download.  Press start to begin download', title=self.title, ok_button='Start Download')
                reply = self.downloadFavs(favorites)
                eg.msgbox(msg='Completed!  Downloaded ' + str(reply['numFiles']) + ' in ' + str(reply['delta']) + ' seconds', title=self.title, ok_button='Main menu')
                break
            else:
                # show the box again, with the errmsg as the message    
                fieldValues = eg.multenterbox(errmsg, title, fieldNames, fieldValues)
        self.mainMenu()
        
    def downloadFavs(self, favorites):
        time_start = time()
        x = 0
        while(x < len(favorites)):
            print 'Saving file ' + str(x) + ' of ' + str(len(favorites)-1)
            result = self.downloader.saveFile(favorites[x])
            if result:
                x += 1
            else:
                print 'Retrying #' + str(x) + ' | '
                
                break

        deltaTime = time() - time_start

        eg.msgbox(msg='Displaying error reports.... if none are displayed this was a complete success!', title=self.title)
        
        if (len(self.downloader.getReports()) > 0):
            for report in self.downloader.getReports():
                eg.msgbox('(REPORT) ' + report, title=self.title, ok_button='OK')
        return {'delta': deltaTime, 'numFiles': str(len(favorites))}
    def about(self):
        license = open('LICENSE', 'r').read()
        
        text = [
            'Version ' + self.version + ' by alex4108@live.com\n',
            'https://github.com/alex4108/scLikesDownloader\n',
            'For support, please open an issue on GitHub @ https://github.com/alex4108/scLikesDownloader/issues/new\n',
            'OR: Email, alex4108@live.com',
            '\n',
            '\n',
            str(license)
        ]
        eg.textbox(msg="About SoundCloud Likes Downloader " + str(self.version), title=self.title, text=text)
        self.mainMenu()
    def mainMenu(self):
        msg = "Please select an action"
        title = self.title
        choices = ['New Download', 'About', 'Exit']
        selection = eg.buttonbox(msg, title=title, choices=choices)
        if selection == 'New Download':
            self.newDownload()
        elif selection == 'About':
            self.about()
        else:
            sys.exit(0)
    
gui = guiController()
gui.mainMenu()

