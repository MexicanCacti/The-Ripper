from utils import inArchive, extractFileName
import yt_dlp
from pathlib import Path

class Worker():
    def __init__(self, ripper, item):
        self.ripper = ripper
        self.url = item.getUrl()
        self.downloadPath = item.getDownloadPath()
        self.activePlaylist = None
        self.activePlaylistLen = -1
        self.activePlaylistSongCount = 0
        self.item = item

    def downloadProgress(self, download):
        # Not a playlist, singular song download!
        if self.activePlaylist is None:
            if download['status'] == 'finished':
                self.ripper.updateQueue.put(f"[SUCCESS]: {extractFileName(download['filename'])}")
                self.ripper.window.updateQueueSignal.emit((self.item.getSongName(), 1))
            elif download['status'] == 'downloading':
                self.ripper.window.updateProgressSignal.emit({
                    'status' : download['status'],
                    'filename' : download['filename'],
                    '_percent_str' : download['_percent_str'],
                    '_speed_str' : download['_speed_str'],
                    '_eta_str' : download['_eta_str']
                })
            elif download['status'] == 'already_downloaded':
                self.ripper.updateQueue.put(f"[SKIPPED]: {extractFileName(download['filename'])} (Already in archive)")
                self.ripper.window.updateQueueSignal.emit((self.item.getSongName(), 1))
            elif download['status'] == 'error':
                self.ripper.updateQueue.put(f"[ERROR]: {extractFileName(download['filename'])}")
                self.ripper.window.updateQueueSignal.emit((self.item.getSongName(), 1))
        else:
            if download['status'] == 'finished':
                self.ripper.updateQueue.put(f"[SUCCESS]: Song[{self.activePlaylistSongCount}]: {extractFileName(download['filename'])}")
                self.activePlaylistSongCount += 1
                self.activePlaylistLen -= 1
            elif download['status'] == 'downloading':
                self.ripper.window.updateProgressSignal.emit({
                    'status' : download['status'],
                    'filename' : download['filename'],
                    '_percent_str' : download['_percent_str'],
                    '_speed_str' : download['_speed_str'],
                    '_eta_str' : download['_eta_str']
                })
            elif download['status'] == 'already_downloaded':
                self.ripper.updateQueue.put(f"[SKIPPED]: Playlist: {self.activePlaylist} Song[{self.activePlaylistSongCount}]: {extractFileName(download['filename'])} (Already in archive)")
                self.activePlaylistSongCount += 1
                self.activePlaylistLen -= 1
            elif download['status'] == 'error':
                self.ripper.updateQueue.put(f"[ERROR]: {extractFileName(download['filename'])}")
                self.activePlaylistLen -= 1
            
            if self.activePlaylistLen == 0:
                self.ripper.window.updateQueueSignal.emit((self.activePlaylist, 1))
                self.ripper.window.updateProgressSignal.emit({
                    'status' : download['status'],
                    'filename' : download['filename'],
                    '_percent_str' : '100',
                })

    def processItem(self, isPlaylist):
        try:
            songName = self.item.getSongName()
            if isPlaylist:
                playlistName = self.item.getPlaylistName()
                playlistLen = self.item.getPlaylistLen()

            if isPlaylist:
                print(f"Processing: {playlistName}")
            else:
                print(f"Processing: {songName}")
            
            print(f"Download Path: {self.downloadPath}")

            if isPlaylist:
                self.activePlaylist = playlistName
                self.activePlaylistLen = playlistLen
            
            downloadArchive = Path(self.downloadPath).parent / 'archive.txt'
            print(f"Archive path: {downloadArchive}")
            print(f"Parent directory exists: {downloadArchive.parent.exists()}")
            downloadArchive.parent.mkdir(parents=True, exist_ok=True)
            print(f"Parent directory exists after mkdir: {downloadArchive.parent.exists()}")
            if not downloadArchive.exists():
                print("Creating archive.txt file...")
                downloadArchive.touch()
                print(f"Archive file exists after creation: {downloadArchive.exists()}")
            else:
                print("Archive file already exists")

            yt_dlp_options = {
                'format' : 'bestaudio/best',
                'download_archive' : str(downloadArchive),
                'extract_audio' : True,
                'audio_format' : 'mp3',
                'audio_quality' : '192K',
                'noplaylist' : False,
                'ffmpeg_location' : self.ripper.ffmpegPath,
                'postprocessors' : [{
                    'key' : 'FFmpegExtractAudio',
                    'preferredcodec' : 'mp3',
                    'preferredquality' : '192',
                }],
                'outtmpl' : str(self.downloadPath),
                'progress_hooks' : [self.downloadProgress],
                'noprogress' : True,
                'restrict_filenames' : True,
                'ignoreerrors' : True
            }
            
            if isPlaylist:
                yt_dlp_options['noplaylist'] = True
            
            shouldSkip, notInArchiveCount = inArchive(self.url, downloadArchive, isPlaylist)

            if shouldSkip:
                if isPlaylist and notInArchiveCount == 0:
                    self.activePlaylist = self.item.getPlaylistName()
                    self.activePlaylistLen = 0
                    self.activePlaylistSongCount = 0
                    self.ripper.window.updateQueueSignal.emit((self.activePlaylist, 1))
                    self.ripper.updateQueue.put(f"[SKIPPED]: Playlist: {self.activePlaylist} (All songs already in archive)")
                    return
                else:
                    self.downloadProgress({
                        'status' : 'already_downloaded',
                        '_percent_str' : '100',
                        'filename' : songName
                    })
            else:
                # Either single song or playlist with every song not in archive
                self.activePlaylistLen = notInArchiveCount
                with yt_dlp.YoutubeDL(yt_dlp_options) as ytdl:
                    ytdl.download(self.url)
        except Exception as e:
            print(f"[ERROR]: processItem: {e}")


