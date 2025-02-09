import queue
import yt_dlp
from pathlib import Path
from utils import trimFile
import os, sys

class Ripper():
    def __init__(self):
        self.ripQueue = queue.Queue()
        self.doneQueue = queue.Queue()
        self.downloadDir = Path().absolute() / "music"
        self.downloadDir.mkdir(parents=True, exist_ok=True)  # Make sure directory exists
    
    def find_ffmpeg(self):
        if hasattr(sys, 'frozen'):
            ffmpegPath = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        else:
            ffmpegPath = Path().absolute()
        
        ffmpegPath = os.path.join(ffmpegPath, "ffmpeg", "ffmpeg.exe")

        if not os.path.exists(ffmpegPath):
            print(f"[Error]: Couldn't find ffmpeg at {ffmpegPath}")
            raise FileNotFoundError("ffmpeg.exe not found")

        return ffmpegPath

    def downloadProgress(self, download):
        if download['status'] == 'downloading':
            print(f"Downloading {download['filename']} - {download['_percent_str']} at {download['_speed_str']} ETA {download['_eta_str']}")
        if download['status'] == 'finished':
            self.doneQueue.put(trimFile(download['filename']))
        elif download['status'] == 'error':
            print(f"Error downloading: {download['filename']}")


    def processQueue(self):
        while True:
            try:
                item = self.ripQueue.get(timeout=10.0)
                print(f"Processing: {item[0]}")

                downloadPath = self.downloadDir / '%(title)s.%(ext)s'

                yt_dlp_options = {
                    'format' : 'bestaudio/best',
                    'extract_audio' : True,
                    'audio_format' : 'mp3',
                    'audio_quality' : '192K',
                    'noplaylist' : False,
                    'ffmpeg_location' : str(self.find_ffmpeg()),
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

                print("Download Path:", downloadPath)
                print("yt-dlp Options:", yt_dlp_options)


                with yt_dlp.YoutubeDL(yt_dlp_options) as ytdl:
                    ytdl.download([item[0]])


                self.ripQueue.task_done()

            except queue.Empty:
                pass
            except Exception as e:
                print(f"Unexpected Error: {e}!")    

    def addToQueue(self, item):
        if not isinstance(item, tuple):  
            print("Error: Item must be tuple!")
            return

        self.ripQueue.put(item)
        print(self.getQueue())

    def getQueue(self):
        return list(self.ripQueue.queue)

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
    
        