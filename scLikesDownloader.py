import soundcloud as sc
from soundcloud.resource import Resource
import sys
import os
import urllib2
import re

class downloader:
    

    def __init__(self, UserURL, PATH):
        try:
            self.client = sc.Client(client_id='',
                client_secret='',
                )
            self.user = self.client.get('/resolve', url=UserURL)
            self.path = PATH
            self.reports = list()
        except:
            self.report('Constructor Exception Raised!')
            self.report(sys.exc_info()[0])
            self.report(sys.exc_info()[1])
            return False
        
        # Constructor
    def __str__(self):
        return 'Downloader Client v1 | Username: ' + self.user.username
    
    def isMp3Valid(self, file_path):
        is_valid = False

        f = open(file_path, 'r')
        block = f.read(1024)
        frame_start = block.find(chr(255))
        block_count = 0 #abort after 64k
        while len(block)>0 and frame_start == -1 and block_count<64:
            block = f.read(1024)
            frame_start = block.find(chr(255))
            block_count+=1
           
        if frame_start > -1:
            frame_hdr = block[frame_start:frame_start+4]
            is_valid = frame_hdr[0] == chr(255)
           
            mpeg_version = ''
            layer_desc = ''
            uses_crc = False
            bitrate = 0
            sample_rate = 0
            padding = False
            frame_length = 0
           
            if is_valid:
                is_valid = ord(frame_hdr[1]) & 0xe0 == 0xe0 #validate the rest of the frame_sync bits exist
               
            if is_valid:
                if ord(frame_hdr[1]) & 0x18 == 0:
                    mpeg_version = '2.5'
                elif ord(frame_hdr[1]) & 0x18 == 0x10:
                    mpeg_version = '2'
                elif ord(frame_hdr[1]) & 0x18 == 0x18:
                    mpeg_version = '1'
                else:
                    is_valid = False
               
            if is_valid:
                if ord(frame_hdr[1]) & 6 == 2:
                    layer_desc = 'Layer III'
                elif ord(frame_hdr[1]) & 6 == 4:
                    layer_desc = 'Layer II'
                elif ord(frame_hdr[1]) & 6 == 6:
                    layer_desc = 'Layer I'
                else:
                    is_valid = False
           
            if is_valid:
                uses_crc = ord(frame_hdr[1]) & 1 == 0
               
                bitrate_chart = [
                    [0,0,0,0,0],
                    [32,32,32,32,8],
                    [64,48,40,48,16],
                    [96,56,48,56,24],
                    [128,64,56,64,32],
                    [160,80,64,80,40],
                    [192,96,80,96,40],
                    [224,112,96,112,56],
                    [256,128,112,128,64],
                    [288,160,128,144,80],
                    [320,192,160,160,96],
                    [352,224,192,176,112],
                    [384,256,224,192,128],
                    [416,320,256,224,144],
                    [448,384,320,256,160]]
                bitrate_index = ord(frame_hdr[2]) >> 4
                if bitrate_index==15:
                    is_valid=False
                else:
                    bitrate_col = 0
                    if mpeg_version == '1':
                        if layer_desc == 'Layer I':
                            bitrate_col = 0
                        elif layer_desc == 'Layer II':
                            bitrate_col = 1
                        else:
                            bitrate_col = 2
                    else:
                        if layer_desc == 'Layer I':
                            bitrate_col = 3
                        else:
                            bitrate_col = 4
                    bitrate = bitrate_chart[bitrate_index][bitrate_col]
                    is_valid = bitrate > 0
           
            if is_valid:
                sample_rate_chart = [
                    [44100, 22050, 11025],
                    [48000, 24000, 12000],
                    [32000, 16000, 8000]]
                sample_rate_index = (ord(frame_hdr[2]) & 0xc) >> 2
                if sample_rate_index != 3:
                    sample_rate_col = 0
                    if mpeg_version == '1':
                        sample_rate_col = 0
                    elif mpeg_version == '2':
                        sample_rate_col = 1
                    else:
                        sample_rate_col = 2
                    sample_rate = sample_rate_chart[sample_rate_index][sample_rate_col]
                else:
                    is_valid = False
           
            if is_valid:
                padding = ord(frame_hdr[2]) & 1 == 1
               
                padding_length = 0
                if layer_desc == 'Layer I':
                    if padding:
                        padding_length = 4
                    frame_length = (12 * bitrate * 1000 / sample_rate + padding_length) * 4
                else:
                    if padding:
                        padding_length = 1
                    frame_length = 144 * bitrate * 1000 / sample_rate + padding_length
                is_valid = frame_length > 0
               
                # Verify the next frame
                if(frame_start + frame_length < len(block)):
                    is_valid = block[frame_start + frame_length] == chr(255)
                else:
                    offset = (frame_start + frame_length) - len(block)
                    block = f.read(1024)
                    if len(block) > offset:
                        is_valid = block[offset] == chr(255)
                    else:
                        is_valid = False
           
        f.close()
        return is_valid
    def directory(self, path,extension = ''):
      list_dir = []
      list_dir = os.listdir(path)
      count = 0
      for file in list_dir:
        if file.endswith(extension): # eg: '.txt'
          count += 1
      return count


           
    '''
        Gets list of likes
    '''
    def trackList(self, downloadable_only = False):
        # API: Get favorites count, save data from /users/{id}/favorites
        
        offset = 0
        limit = 1
        favorites = list()
        retry = 0
        #self.user.public_favorites_count = 5 # Test data
        while offset < self.user.public_favorites_count:
            if offset is -1:
                break
            
            
            try:
                uri = '/users/' + str(self.user.id) + '/favorites'
                favoritesToJoin = self.client.get(uri, offset=offset, limit=limit)
                
                if len(favoritesToJoin) == 0 or not favoritesToJoin:
                    print str(offset) + ' of ' + str(self.user.public_favorites_count) + ' is hiding.  Trying again.'
                    if retry != 0 :
                        retry = retry + 1
                    else:
                        retry = 1
                    print '(Retry ' + str(retry) + ')'
                    if retry >= 5:
                        print str(offset) + ' of ' + str(self.user.public_favorites_count) + ' won\'t retrieve.  Aborting...'
                        self.report('(trackList) Can\'t select track #' + str(offset))
                        self.report('To download this manually, please visit https://api.soundcloud.com/users/' + str(self.user.id) + '/favorites/' + str(offset) + '.json')
                        
                        retry = 0
                        offset += 1
                
                elif hasattr(self.trackData(favoritesToJoin[0].id), 'download_url'):
                    if len(favoritesToJoin) < limit:
                            offset = offset + limit - len(favoritesToJoin)
                    
                    if len(favorites) == 0:
                            print str(offset) + ' of ' + str(self.user.public_favorites_count) + ' retrieved from API '
                            favorites.append(favoritesToJoin[0])
                            if offset + 1 < self.user.public_favorites_count:
                                offset += 1
                            else:
                                offset = -1    
                    elif len(favorites) != 0 and not favorites[len(favorites)-1] == favoritesToJoin[0]:
                            print str(offset) + ' of ' + str(self.user.public_favorites_count) + ' retrieved from API '
                            favorites.append(favoritesToJoin[0])
                            if offset + 1 < self.user.public_favorites_count:
                                offset += 1
                            else:
                                offset = -1
                
                else:
                     print str(offset) + ' of ' + str(self.user.public_favorites_count) + ' isn\'t downloadable.  Skipping...'
                     offset += 1
            
            except:
                self.report('(trackList) ' + str(sys.exc_info()[0]))
                self.report('(trackList) ' + str(sys.exc_info()[1]))
                self.report('(trackList) ' + str(favoritesToJoin[0].download_url))
        print 'All tracks have been retrieved'
        return favorites
    '''
        Adds a report for later viewing

        :param str msg Message to report
    '''
    def report(self, msg):
        self.reports.append(msg)

            
    '''
        Gets data on specific track

        :param int trackid The Track's API ID

        :return (Resource|Boolean) Track Resource or false on failure
    '''
    def trackData(self, trackid):
        try:
            track = self.client.get('/tracks/' + str(trackid))
        except:
            self.report('(trackData) Failed to select Track ID ' + str(trackid))                        
            return False
        return track

    '''
        Get data on specific user

        :param int User's ID in the API

        :return Resource User Resource
    '''
    def getUser(self, userid):
        try:
            user = self.client.get('/users/' + str(userid))
        except:
            self.report('(getUser) Failed to select User ID ' + str(userid))
            return False
        return user
    '''
        Takes the inputted path and makes it system-safe by stripping characters

        :param str path Path to clean

        :return str Clean path
    '''
    def validPath(self, path):
            cleaned_up_filename = re.sub(r'[\/\\\:\*\?\"\<\>\|]', '', path)
            return self.path + "".join(c for c in cleaned_up_filename if c.isalnum()).rstrip()
                                    
    def getReports(self):
        return self.reports

    '''
        Saves a file

        :param (Resource|int) the Track Resource to download or the track's ID

        :param bool False on failure, True on success
    '''
    def saveFile(self, track):
        if isinstance(track, int):
            track = trackData(track.id)
        
        artist = self.getUser(track.user_id)

        
        filepath = self.validPath(artist.username + '_' + track.permalink + '.' + track.original_format)
        url = track.download_url + '?client_id=1fbdfddf1e6711cd0aff00f3b92e7cbf'
        try:
            req = urllib2.urlopen(urllib2.Request(url=url))
            if req.getcode() != 200:
                self.report('HTTPError Code: ' + str(req.getcode()) + ' url: ' + req.geturl())
                return False

            try:
                if not os.path.exists(self.path):
                    os.makedirs(self.path)
            
                if os.path.exists(filepath):
                    os.remove(filepath)
                
                
                file = open(filepath, 'wb')
                file.write(req.read())
                file.close()
            except:
                raise
            	
        except:
            self.report('(saveFile) Failed to save file!  Manual download required! URL: ' + req.geturl())
            self.report('(saveFile)' + str(sys.exc_info()[0]))
            self.report('(saveFile)' + str(sys.exc_info()[1]))
            return False
                        
        return True
