import re, sys, os
from pathlib import Path

def loadCSS(cssFileName):
    if hasattr(sys, 'frozen'):
        css = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        css = Path().absolute()
    
    css = os.path.join(css, "styles", cssFileName)

    if not os.path.exists(css):
        print(f"[Error]: Couldn't find {cssFileName}")
        return -1

    try:
        with open(css, "r") as css_file:
            style = css_file.read()
            return style
    except Exception as e:
        print(f"Error opening {css}: e")
        return -1

# Use Regex to Match this better!    
def checkValidUrl(url):
    validPattern = re.compile(r"^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|v\/|shorts\/)[a-zA-Z0-9_-]{11}|youtu\.be\/[a-zA-Z0-9_-]{11})$")
    playlistPattern = re.compile(r"^(?:https?:\/\/)?(?:www\.)?youtube\.com\/(?:playlist\?list=)[a-zA-Z0-9_-]+$")
    
    if re.match(playlistPattern, url):
        return 1
    elif re.match(validPattern, url):
        return 0
    else:
        return -1

# Remove Extension
def trimFile(filePath):
    return str(re.sub(r'\.[^.]+$', '', filePath))

# Remove Everything But Filename
def extractFileName(filePath):
    return str(re.sub(r'.*\\(.*)\.[^.]+$', r'\1', filePath))

def removeAnsiEscape(text):
    return re.sub(r'\x1b\[[0-9;]*m', '', text)

def find_ffmpeg():
    if hasattr(sys, 'frozen'):
        ffmpegPath = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        ffmpegPath = Path().absolute()
    
    ffmpegPath = os.path.join(ffmpegPath, "ffmpeg", "ffmpeg.exe")

    if not os.path.exists(ffmpegPath):
        print(f"[Error]: Couldn't find ffmpeg at {ffmpegPath}")
        raise FileNotFoundError("ffmpeg.exe not found")

    return ffmpegPath