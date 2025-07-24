import queue
import yt_dlp
from pathlib import Path
from utils import extractFileName, getOnlyDirName, find_ffmpeg, inArchive
import os, time, sys
from downloadItem import DownloadItem
from worker import Worker
import threading

class Ripper():
    def __init__(self, window):
        self.devMode = True
        self.window = None
        self.ripQueue = queue.Queue()
        self.updateQueue = queue.Queue()

        if getattr(sys, 'frozen', False):
            defaultDir = Path.home() / "Downloads" / "Ripper"
        else:
            defaultDir = Path().absolute() / "music"
            self.devMode = False
        self.downloadDir = getOnlyDirName(defaultDir)
        self.downloadPath = defaultDir
        self.fullDownloadPath = self.downloadPath
        self.fullDownloadPath.mkdir(parents=True, exist_ok=True)  # Make sure directory exists
        self.ffmpegPath = find_ffmpeg()

    def processRipQueue(self):
        while True:
            try:
                item = self.ripQueue.get(timeout = 5.0)
                url = item.getUrl()
                urlType = item.getUrlType()
                dirName = item.getDownloadDir()

                if self.devMode:
                    print(f"Processing: {url}")

                downloadPath = self.fullDownloadPath / '%(title)s.%(ext)s'
                item.setDownloadPath(downloadPath)
                item.setDownloadDir(dirName)

                yt_dlp_options = {
                    'quiet' : False,
                    'extract_flat' : True,
                    'skip_download' : True,
                    'ffmpeg_location' : str(find_ffmpeg()),
                    'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                    'nopostoverwrites' : True
                    }]
                }
                
                # TODO: Change urlType to enum for easier reading
                if urlType == 1:
                    yt_dlp_options['noplaylist'] = False
                    yt_dlp_options['force_generic_extractor'] = True
                    yt_dlp_options['extract_flat'] = True
                elif urlType == 2:
                    yt_dlp_options['noplaylist'] = True
                    yt_dlp_options['extract_flat'] = True
                else:
                    yt_dlp_options['noplaylist'] = True
                    yt_dlp_options['extract_flat'] = True
            

                with yt_dlp.YoutubeDL(yt_dlp_options) as ytdl:
                    info = ytdl.extract_info(url, download=False)

                if urlType == 0:
                    songName = info.get('title', 'Unknown Title')
                    if self.devMode:
                        print(f"SongName: {songName}")
                    item.setSongName(songName)
                    self.window.updateQueueSignal.emit((songName, 0))
                elif urlType == 1:
                    playlistLen = len(info['entries'])
                    playlistName = info.get('title', 'Unknown Playlist')
                    item.setIsPlaylist(True)
                    item.setPlaylistLen(playlistLen)
                    item.setPlaylistName(playlistName)
                    self.window.updateQueueSignal.emit((playlistName, 0))
                elif urlType == 2:
                    songName = info.get("title", "Unknown Title")
                    if self.devMode:
                        print(f"SongName: {songName}")
                    item.setSongName(songName)

                worker = Worker(self, item)
                threading.Thread(target=worker.processItem, args=(item.checkIsPlaylist(),), daemon=True).start()
                time.sleep(5)
                self.ripQueue.task_done()
            except queue.Empty:
                pass
            except Exception as e:
                self.updateQueue.put(f"[ERROR]: {item.getUrl()}")
                print(f"[ERROR]: ProcessRipQueue: {e}")

    # 0: URL
    # 1 : URLTYPe
    # 2 : SongName  || PlaylistName
    # 3 : DownloadPath
    # 4 : playlistLen


    def getQueue(self):
        return list(self.ripQueue.queue)
    
    def addToQueue(self, item):
        if not isinstance(item, DownloadItem):
            if self.devMode:
                print("Error: Item must be an instance of DownloadItem!")
            return

        item.setDownloadPath(self.downloadPath)
        item.setDownloadDir(self.downloadDir)

        self.ripQueue.put(item)
        if self.devMode:
            print(self.getQueue())

    def getFinishedItem(self):
        if not self.updateQueue.empty():
            return self.updateQueue.get()
        return None
    
    def setPath(self, path=None):
        path = Path(path).resolve()

        # Check if directory is writable
        if not os.access(path, os.W_OK):
            if self.devMode:
                print(f"[ERROR] No write permission to {path}")
            return

        if self.devMode:
            print(f"Write permission granted for {path}")
        
        self.downloadPath = path
        self.downloadDir = path.name
        self.fullDownloadPath = self.downloadPath

        self.fullDownloadPath.mkdir(parents=True, exist_ok=True)
        if self.devMode:
            print(f"SET DOWNLOAD PATH: {self.downloadPath}")
    
    def getFullPath(self):
        return self.fullDownloadPath

    def getPath(self):
        return self.downloadDir

    
        