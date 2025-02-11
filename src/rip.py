import queue
import yt_dlp
from pathlib import Path
from utils import trimFile, extractFileName, find_ffmpeg
import os, time

class Ripper():
    def __init__(self, window):
        self.window = None
        self.ripQueue = queue.Queue()
        self.workQueue = queue.Queue()
        self.doneQueue = queue.Queue()
        self.activePlaylistLength = -1
        self.activePlaylistName = None
        self.downloadDir = Path().absolute() / "music"
        self.downloadDir.mkdir(parents=True, exist_ok=True)  # Make sure directory exists
    
    def downloadProgress(self, download):
        if self.activePlaylistLength >= 0:
            if download['status'] == 'finished':
                self.doneQueue.put(trimFile(download['filename']))
                self.activePlaylistLength -= 1
                if self.activePlaylistLength == 0:
                    self.activePlaylistLength -= 1
                    self.window.updateQueueSignal.emit((self.activePlaylistName, 1))
                    self.activePlaylistName = None
            elif download['status'] == 'downloading':
                self.window.updateProgressSignal.emit({
                'status': 'downloading',
                'filename': download['filename'],
                '_percent_str': download['_percent_str'],
                '_speed_str': download['_speed_str'],
                '_eta_str': download['_eta_str']
            })  
            elif download['status'] == 'error':
                self.doneQueue.put(f"[ERROR]: {trimFile(download['filename'])}")
                self.activePlaylistLength -= 1
        else:
            if download['status'] == 'finished':
                self.doneQueue.put(trimFile(download['filename']))
                self.window.updateQueueSignal.emit((extractFileName(download['filename']), 1))
            elif download['status'] == 'downloading':
                self.window.updateProgressSignal.emit({
                'status': 'downloading',
                'filename': download['filename'],
                '_percent_str': download['_percent_str'],
                '_speed_str': download['_speed_str'],
                '_eta_str': download['_eta_str']
            })  
            elif download['status'] == 'error':
                self.doneQueue.put(f"[ERROR]: {trimFile(download['filename'])}")
                self.window.updateQueueSignal.emit((extractFileName(download['filename']), 1))

    def processRipQueue(self):
        while True:
            try:
                item = self.ripQueue.get(timeout = 5.0)
                print(f"Processing: {item[0]}")

                downloadPath = item[2] / '%(title)s.%(ext)s'

                yt_dlp_options = {
                    'quiet' : True,
                    'extract_flat' : True,
                    'skip_download' : True
                }

                with yt_dlp.YoutubeDL(yt_dlp_options) as ytdl:
                    info = ytdl.extract_info(item[0])

                if item[1] == 1:
                    playlistLen = len(info['entries'])
                    playlistName = info.get('title', 'Unknown Playlist')
                    self.workQueue.put((item[0], playlistName, downloadPath, playlistLen))
                    self.window.updateQueueSignal.emit((playlistName, 0))
                else:
                    songName = info.get('title', 'Unknown Title')
                    self.workQueue.put((item[0], songName, downloadPath))
                    self.window.updateQueueSignal.emit((songName, 0))
                time.sleep(5)
                self.ripQueue.task_done()
            except queue.Empty:
                pass
            except Exception as e:
                self.doneQueue.put(f"[ERROR]: {item[0]}")
                print(f"[ERROR]: ProcessRipQueue: {e}")

    def processWorkQueue(self):
        while True:
            try:
                item = self.workQueue.get(timeout=5.0)
                print(f"Processing: {item[1]}")

                downloadPath = item[2]
                print(f"Download Path: {downloadPath}")

                # check if start of a new playlist
                if len(item) == 4:
                    if(self.activePlaylistLength == -1):
                        self.activePlaylistLength = item[3]
                        self.activePlaylistName = item[1]

                yt_dlp_options = {
                    'format' : 'bestaudio/best',
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
                    
                with yt_dlp.YoutubeDL(yt_dlp_options) as ytdl:
                    ytdl.download([item[0]])

                time.sleep(5)
                self.workQueue.task_done()

            except queue.Empty:
                pass
            except Exception as e:
                print(f"[ERROR]: processWorkQueue: {e}")

    def getQueue(self):
        return list(self.workQueue.queue)
    
    def addToQueue(self, item):
        if not isinstance(item, tuple):  
            print("Error: Item must be tuple!")
            return

        self.ripQueue.put(item)
        print(self.getQueue())

    def getWorkItem(self):
        if not self.workQueue.empty():
            return self.workQueue.get()[1]
        return None

    def getFinishedItem(self):
        if not self.doneQueue.empty():
            return self.doneQueue.get()
        return None
    
    def setPath(self, path):
        path = Path(path)
        # Check if directory is writable
        if not os.access(self.downloadDir, os.W_OK):
            print(f"Error: No write permission for directory {path}")
        else:
            print(f"Write permission granted for {path}")
            self.downloadDir = path
    
    def getPath(self):
        return self.downloadDir
    
        