import re, sys, os
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import yt_dlp

# If song from a playlist, then download only that song not the playlist!
def loadCSS(cssFileName):
    if hasattr(sys, 'frozen'):
        css = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        css = os.path.join(css, "styles", cssFileName)
    else:
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent
        css = project_root / "styles" / cssFileName

    if not os.path.exists(css):
        print(f"[Error]: Couldn't find {cssFileName}")
        return -1

    try:
        with open(css, "r") as css_file:
            style = css_file.read()
            return style
    except Exception as e:
        print(f"Error opening {css}: {e}")
        return -1

# Use Regex to Match this better!    
def checkValidUrl(url):
    youtubePattern = re.compile(r"^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|v\/|shorts\/)[\w-]{11}(&.*)?|youtu\.be\/[\w-]{11}(&.*)?)$")
    youtubeMusicPattern = re.compile(r"^https:\/\/music\.youtube\.com\/watch\?v=[\w-]+(?:&[^ ]*)?$")
    
    youtubePlaylistPattern = re.compile(r"^(?:https?:\/\/)?(?:www\.)?youtube\.com\/playlist\?list=[\w-]+$")
    youtubeMusicPlaylistPattern = re.compile(r"^https:\/\/music\.youtube\.com\/playlist\?list=[\w-]+$")
    
    youtubeInPlaylistPattern = re.compile(r"^(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=[\w-]+(?:&list=[\w-]+)(&.*)?$")
    youtubeMusicInPlaylistPattern = re.compile(r"^https:\/\/music\.youtube\.com\/watch\?v=[\w-]+(?:&list=[\w-]+)(&.*)?$")

    
    if re.match(youtubeInPlaylistPattern, url) or re.match(youtubeMusicInPlaylistPattern, url):
        return 2
    elif re.match(youtubePlaylistPattern, url) or re.match(youtubeMusicPlaylistPattern, url):
        return 1
    elif re.match(youtubePattern, url) or re.match(youtubeMusicPattern, url):
        return 0
    else: return -1

# Remove Extension
def trimFile(filePath):
    return str(re.sub(r'\.[^.]+$', '', filePath))

# Remove Everything But Filename
def extractFileName(filePath):
    return str(re.sub(r'.*\\(.*)\.[^.]+$', r'\1', filePath))

def removeAnsiEscape(text):
    return re.sub(r'\x1b\[[0-9;]*m', '', text)

def getOnlyDirName(fullPath):
    dirName = ""
    fullPathString = str(fullPath)
    backIndex = len(fullPathString) - 1
    while fullPathString[backIndex] !='\\' and backIndex >= 0:
        backIndex -= 1  
    
    dirName = fullPathString[backIndex + 1:]

    return dirName

def getOnlyDirNameWithFile(fullPath):
    dirName = ""
    fullPathString = str(fullPath)
    backIndex = len(fullPathString) - 1
    backSlashCount = 0
    beginningSlashIndex = 0
    endingSlashIndex = 0
    while backSlashCount != 2 and backIndex >= 0:
        if fullPathString[backIndex] == '\\':
            backSlashCount += 1
            if backSlashCount == 1:
                endingSlashIndex = backIndex
            else:
                beginningSlashIndex = backIndex
                break
        backIndex -= 1  
    dirName = fullPathString[beginningSlashIndex + 1:endingSlashIndex]

    return dirName  


def find_ffmpeg():
    if hasattr(sys, 'frozen'):
        ffmpegPath = Path(sys._MEIPASS) / "ffmpeg" / "ffmpeg.exe"
    else:
        ffmpegPath = Path(__file__).resolve().parent.parent / "ffmpeg" / "ffmpeg.exe"

    if not os.path.exists(ffmpegPath):
        print(f"[Error]: Couldn't find ffmpeg at {ffmpegPath}")
        raise FileNotFoundError("ffmpeg.exe not found")

    return str(ffmpegPath)

def extractVideoId(url):
    parsed_url = urlparse(url)
    if 'youtu.be' in parsed_url.netloc:
        return parsed_url.path.strip("/")
    elif 'youtube.com' in parsed_url.netloc or 'music.youtube.com' in parsed_url.netloc:
        query_params = parse_qs(parsed_url.query)
        return query_params.get("v", [None])[0]
    return None

# Returns (shouldSkip, notInArchiveCount)
# shouldSkip: True if any videos in playlist are in archive, False otherwise
# notInArchiveCount: Number of videos in playlist that are not in archive
def inArchive(url, archivePath, isPlaylist):
    if not archivePath.exists():
        return (False, 0)

    if isPlaylist:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'skip_download': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' not in info:
                    return (False, 0)
                playlist_video_ids = [entry['id'] for entry in info['entries']]
        except Exception as e:
            print(f"[ERROR]: Failed to extract playlist: {e}")
            return (False, 0)

        with archivePath.open("r", encoding="utf-8") as archive:
            archiveLines = archive.read()

        notInArchiveCount = sum(1 for videoID in playlist_video_ids if videoID not in archiveLines)
        # Make sure all playlist video ids are in the archive
        return (notInArchiveCount == 0, notInArchiveCount)

    else:
        urlID = extractVideoId(url)
        if not urlID:
            return (False, 0)

        with archivePath.open("r", encoding="utf-8") as archive:
            for line in archive:
                if urlID in line:
                    return (True, 0)
        return (False, 0)