# YouTube Music Ripper

This is a Python-based application that allows you to download and convert YouTube videos to MP3 format. It includes a graphical user interface (GUI) built with PyQt5. The application uses `yt-dlp` to handle video downloading and `FFmpeg` to convert the audio to MP3.

## Features

- **Download YouTube Videos and Playlists**: Download individual videos or entire playlists.
- **MP3 Conversion**: Automatically converts the audio to MP3 format after downloading.
- **User-Friendly GUI**: Simple interface for inputting URLs and choosing download paths.
- **Download Progress**: Displays download progress, speed, and ETA (in console).
- **Finished Items Display**: A section showing completed downloads.
  
## Requirements

Before you can run the application, you need to install Python and some dependencies.

### Prerequisites:
- **Python 3**: The application is built in Python 3.
- **PyInstaller**: Used for packaging the application into a standalone executable.

### Install Dependencies

1. Install Python 3 from [here](https://www.python.org/downloads/) if you don't have it installed.

### Build
```bash
python build.py
