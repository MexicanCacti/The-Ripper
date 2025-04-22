import queue
import yt_dlp
from pathlib import Path
from utils import extractFileName, getOnlyDirName, find_ffmpeg, inArchive
import os, time, sys
from downloadItem import DownloadItem

class Ripper():
    def __init__(self, window):
        self.window = None
        self.ripQueue = queue.Queue()
        self.workQueue = queue.Queue()
        self.doneQueue = queue.Queue()
        self.activePlaylistLength = -1
        self.activePlaylistName = ""
        self.activePlaylistSongCount = 0
        if getattr(sys, 'frozen', False):
            defaultDir = Path.home() / "Downloads" / "Ripper"
        else:
            defaultDir = Path().absolute() / "music"
        self.downloadDir = getOnlyDirName(defaultDir)
        self.downloadPath = defaultDir
        self.fullDownloadPath = self.downloadPath
        self.fullDownloadPath.mkdir(parents=True, exist_ok=True)  # Make sure directory exists
    
    def downloadProgress(self, download):
        if self.activePlaylistLength >= 0:
            if download['status'] == 'finished':
                self.doneQueue.put(f"[SUCCESS]: Song[{self.activePlaylistSongCount}]: {extractFileName(download['filename'])}")
                self.activePlaylistSongCount += 1
                self.activePlaylistLength -= 1
                if self.activePlaylistLength == 0:
                    self.activePlaylistLength = -1
                    self.window.updateQueueSignal.emit((self.activePlaylistName, 1))
                    self.activePlaylistName = ""
                    self.window.updateProgressSignal.emit({
                        'status': download['status'],
                        '_percent_str': download['_percent_str'],
                        'filename': download['filename']
                    })  
            elif download['status'] == 'downloading':
                self.window.updateProgressSignal.emit({
                    'status': download['status'],
                    'filename': download['filename'],
                    '_percent_str': download['_percent_str'],
                    '_speed_str': download['_speed_str'],
                    '_eta_str': download['_eta_str']
                })
            elif download['status'] == 'already_downloaded':
                if self.activePlaylistLength == 0:
                    self.doneQueue.put(f"[SKIPPED]: Playlist: {self.activePlaylistName}")
                    self.window.updateQueueSignal.emit((self.activePlaylistName, 1))
                    return
                else:
                    self.doneQueue.put(f"[SKIPPED]: Playlist: {self.activePlaylistName} Song[{self.activePlaylistSongCount}]: {extractFileName(download['filename'])}")
                self.activePlaylistSongCount += 1
                self.activePlaylistLength -= 1 
                if self.activePlaylistLength == 0:
                    self.activePlaylistLength = -1
                    self.window.updateQueueSignal.emit((self.activePlaylistName, 1))
                    self.activePlaylistName = ""
                    self.window.updateProgressSignal.emit({
                        'status': download['status'],
                        'filename': download['filename'],
                        '_percent_str': download['_percent_str'],
                    })  
            elif download['status'] == 'error':
                self.doneQueue.put(f"[ERROR]: {extractFileName(download['filename'])}")
                self.activePlaylistLength -= 1
        else:
            if download['status'] == 'finished':
                self.doneQueue.put(f"[SUCCESS]: Song[{self.activePlaylistSongCount}]: {extractFileName(download['filename'])}")
                self.window.updateQueueSignal.emit((extractFileName(download['filename']), 1))
                self.window.updateProgressSignal.emit({
                    'status': download['status'],
                    '_percent_str': download['_percent_str'],
                    'filename': download['filename']
                })  
            elif download['status'] == 'downloading':
                self.window.updateProgressSignal.emit({
                    'status': download['status'],
                    'filename': download['filename'],
                    '_percent_str': download['_percent_str'],
                    '_speed_str': download['_speed_str'],
                    '_eta_str': download['_eta_str']
                })
            elif download['status'] == 'already_downloaded':
                self.doneQueue.put(f"[SKIPPED]: {extractFileName(download['filename'])}")
                self.window.updateQueueSignal.emit((extractFileName(download['filename']), 1))  
                self.window.updateProgressSignal.emit({
                    'status': download['status'],
                    '_percent_str': download['_percent_str'],
                    'filename': download['filename']
                })    
            elif download['status'] == 'error':
                self.doneQueue.put(f"[ERROR]: {extractFileName(download['filename'])}")
                self.window.updateQueueSignal.emit((extractFileName(download['filename']), 1))

    def processRipQueue(self):
        while True:
            try:
                item = self.ripQueue.get(timeout = 5.0)
                url = item.getUrl()
                urlType = item.getUrlType()
                dirName = item.getDownloadDir()

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
                
                if urlType == 1:
                    yt_dlp_options['noplaylist'] = False
                    yt_dlp_options['force_generic_extractor'] = True
                    yt_dlp_options['extract_flat'] = True
                elif urlType == 2:
                    yt_dlp_options['noplaylist'] = True
                    yt_dlp_options['force_generic_extractor'] = True
                    yt_dlp_options['extract_flat'] = False
                else:
                    yt_dlp_options['noplaylist'] = True
                    yt_dlp_options['extract_flat'] = True
            

                with yt_dlp.YoutubeDL(yt_dlp_options) as ytdl:
                    info = ytdl.extract_info(url, download=False)

                if urlType == 0:
                    songName = info.get('title', 'Unknown Title')
                    print(f"SongName: {songName}")

                    item.setSongName(songName)

                    self.workQueue.put(item)
                    self.window.updateQueueSignal.emit((songName, 0))
                elif urlType == 1:
                    playlistLen = len(info['entries'])
                    playlistName = info.get('title', 'Unknown Playlist')

                    item.setPlaylistLen(playlistLen)
                    item.setPlaylistName(playlistName)

                    self.workQueue.put(item)
                    self.window.updateQueueSignal.emit((playlistName, 0))
                elif urlType == 2:
                    songName = info.get("title", "Unknown Title")
                    print(f"SongName: {songName}")

                    item.setSongName(songName)

                    self.workQueue.put(item)
                    self.window.updateQueueSignal.emit((songName, 0))
                time.sleep(5)
                self.ripQueue.task_done()
            except queue.Empty:
                pass
            except Exception as e:
                self.doneQueue.put(f"[ERROR]: {item.getUrl()}")
                print(f"[ERROR]: ProcessRipQueue: {e}")

    # 0: URL
    # 1 : URLTYPe
    # 2 : SongName  || PlaylistName
    # 3 : DownloadPath
    # 4 : playlistLen
    def processWorkQueue(self):
        while True:
            try:
                item = self.workQueue.get(timeout=5.0)
                url = item.getUrl()
                urlType = item.getUrlType()
                songName = item.getSongName()
                playlistName = item.getPlaylistName()
                downloadPath = item.getDownloadPath()
                playlistLen = item.getPlaylistLen()

                if urlType == 0:
                    print(f"Processing: {songName}")
                else:
                    print(f"Processing: {playlistName}")

                print(f"Download Path: {downloadPath}")

                if urlType == 1:
                    if(self.activePlaylistLength == -1):
                        self.activePlaylistLength = playlistLen
                        self.activePlaylistName = playlistName
                        self.activePlaylistSongCount = 0

                downloadArchive = self.fullDownloadPath / 'archive.txt'

                yt_dlp_options = {
                    'format' : 'bestaudio/best',
                    'download_archive' : downloadArchive,
                    'extract_audio' : True,
                    'audio_format' : 'mp3',
                    'audio_quality' : '192K',
                    'noplaylist' : False,
                    'ffmpeg_location' : str(find_ffmpeg()),
                    'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                    }],
                    'outtmpl' : str(downloadPath),
                    'progress_hooks' : [self.downloadProgress],
                    'noprogress' : True,
                    'restrict_filenames' : True,
                    'ignoreerrors' : True
                }

                isPlaylist = False
                if urlType == 2:
                    yt_dlp_options['noplaylist'] = True
                else:
                    isPlaylist = True
                    yt_dlp_options['noplaylist'] = False
                
                shouldSkip, notInArchiveCount = inArchive(url, downloadArchive, isPlaylist)
                if shouldSkip:
                    if isPlaylist:
                        self.activePlaylistLength = 0
                        self.activePlaylistSongCount = playlistLen
                        self.downloadProgress({
                            'status': 'already_downloaded',
                            '_percent_str': '100',
                            'filename': playlistName
                        })
                    else:
                        # BUG: DOESN'T REMOVE FROM QUEUE ON GUI!
                        self.downloadProgress({
                            'status': 'already_downloaded',
                            '_percent_str': '100',
                            'filename': songName
                        })
                else:
                    if isPlaylist:
                        self.activePlaylistLength = notInArchiveCount
                        self.activePlaylistSongCount = playlistLen - notInArchiveCount
                    with yt_dlp.YoutubeDL(yt_dlp_options) as ytdl:
                        ytdl.download(url)

                time.sleep(5)
                self.workQueue.task_done()

            except queue.Empty:
                pass
            except Exception as e:
                print(f"[ERROR]: processWorkQueue: {e}")

    def getQueue(self):
        return list(self.workQueue.queue)
    
    def addToQueue(self, item):
        if not isinstance(item, DownloadItem):  
            print("Error: Item must be an instance of DownloadItem!")
            return

        item.setDownloadPath(self.downloadPath)
        item.setDownloadDir(self.downloadDir)

        self.ripQueue.put(item)
        print(self.getQueue())

    def getWorkItem(self):
        if not self.workQueue.empty():
            return self.workQueue.get()
        return None

    def getFinishedItem(self):
        if not self.doneQueue.empty():
            return self.doneQueue.get()
        return None
    
    def setPath(self, path=None):
        path = Path(path).resolve()

        # Check if directory is writable
        if not os.access(path, os.W_OK):
            print(f"[ERROR] No write permission to {path}")
            return

        print(f"Write permission granted for {path}")
        
        self.downloadPath = path
        self.downloadDir = path.name
        self.fullDownloadPath = self.downloadPath

        self.fullDownloadPath.mkdir(parents=True, exist_ok=True)
        print(f"SET DOWNLOAD PATH: {self.downloadPath}")
    
    def getFullPath(self):
        return self.fullDownloadPath

    def getPath(self):
        return self.downloadDir
    
    def checkInArchive(self, item):
        return

    
        