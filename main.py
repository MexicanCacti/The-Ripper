import subprocess, sys, importlib.util, threading, os
from PyQt5.QtWidgets import QApplication
import gui as myGui
import rip
import utils

def checkPackage(package, altName=None):
    packageName = package
    if altName is not None:
        packageName = altName
    
    try:
        importlib.import_module(package)
        print(f'.', end="")
    except ImportError:
        print(f"{packageName} not Found! Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", packageName], check = True)

def getPackages(packageFile):
    packages = []
    try:
        f = open("packages.txt", "r")
        packages = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Error: packages.txt not found!")
    except PermissionError:
        print("Error: Permission denied when trying to read packages.txt.")
    except OSError as e:
        print(f"OS error: {e}")
    finally:
        f.close()
    
    print(f"Checking packages...", end="")
    for package in packages:
        checkPackage(package)
    print(f"\nDone!")
    return

def main():
    packageFile = "packages.txt"
    getPackages(packageFile)    

    ripper = rip.Ripper()
    threading.Thread(target = ripper.processQueue, daemon=True).start()

    app = QApplication(sys.argv)
    window = myGui.MainWindow(ripper)
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()


