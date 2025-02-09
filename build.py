import os, subprocess, sys
from pathlib import Path

MAIN = "main.py"
ICON = "images/icon.ico"
EXE = "The Ripper"
FFMPEG = "ffmpeg/ffmpeg.exe"

def installReqs():
    if os.path.exists("packages.txt"):
        print("[INFO] Installing dependencies from packages.txt...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "packages.txt"], check=True)
    else:
        print("[WARNING] No packages.txt found. Skipping dependency installation.")

def build():
    print("[INFO] Building executable with PyInstaller...")

    # Build the command dynamically
    command = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        f"--name={EXE}",
        f"--add-data={FFMPEG};ffmpeg",
        f"--add-data=packages.txt;.",
        f"--add-data=styles/text.css;styles",
        f"--add-data=images/background.jpg;images",
        f"--add-data=images/icon.jpg;images", 
        "--clean",               
        "--noconfirm",            
        MAIN               
    ]

    if os.path.exists(ICON):
        command.append(f"--icon={ICON}")

    subprocess.run(command, check=True)

if __name__ == "__main__":
    installReqs()
    build()
    print(f"[SUCCESS] Build complete! Your .exe is in the dist/ folder as {EXE}.exe")