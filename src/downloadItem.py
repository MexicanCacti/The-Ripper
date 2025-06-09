from utils import checkValidUrl, getOnlyDirName

class DownloadItem:
    def __init__(self):
        self.url = ""
        self.urlType = -1
        self.downloadDir = ""
        self.downloadPath = ""
        self.songName = ""
        self.playlistLen = 0
        self.playlistName = ""
        self.isPlaylist = False
    
    def setUrl(self, url):
        self.url = url
        self.urlType = checkValidUrl(url)
    
    def getUrl(self):
        return self.url
    
    def getUrlType(self):
        return self.urlType
    
    def setDownloadPath(self, fullPath):
        self.downloadPath = fullPath
    
    def getDownloadPath(self):
        return self.downloadPath
    
    def setDownloadDir(self, downloadDir):
        self.downloadDir = downloadDir

    def getDownloadDir(self):
        return self.downloadDir
    
    def setSongName(self, songName):
        self.songName = songName
    
    def getSongName(self):
        return self.songName

    def setPlaylistLen(self, playlistLen):
        self.playlistLen = playlistLen
    
    def getPlaylistLen(self):
        return self.playlistLen
    
    def setPlaylistName(self, playlistName):
        self.playlistName = playlistName
    
    def getPlaylistName(self):
        return self.playlistName
    
    def setIsPlaylist(self, isPlaylist):
        self.isPlaylist = isPlaylist
    
    def checkIsPlaylist(self):
        return self.isPlaylist
    
    def __str__(self):
        return self.songName

    # For Debugging
    def __repr__(self):
        return f"URL: {self.url}, URLTYPE: {self.urlType}, SONGNAME: {self.songName}"

