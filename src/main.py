import subprocess, sys, importlib.util, threading, os
from PyQt5.QtWidgets import QApplication
import gui as myGui
import rip as rip
import utils as utils

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
    f = None
    try:
        f = open(packageFile, "r")
        packages = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: {packageFile} not found!")
    except PermissionError:
        print(f"Error: Permission denied when trying to read {packageFile}.")
    except OSError as e:
        print(f"OS error: {e}")
    finally:
        if f:
            f.close()
    
    print(f"Checking packages...", end="")
    for package in packages:
        checkPackage(package)
    print(f"\nDone!")
    return

def main():
    baseDir = os.path.dirname(os.path.abspath(__file__))
    packageFile = os.path.join(baseDir, "..", "packages.txt")
    packageFile = os.path.abspath(packageFile)
    getPackages(packageFile)    

    app = QApplication(sys.argv)

    ripper = rip.Ripper(None)
    threading.Thread(target = ripper.processRipQueue, daemon=True).start()
    threading.Thread(target=ripper.processWorkQueue, daemon=True).start()

    window = myGui.MainWindow(ripper)

    ripper.window = window

    window.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()


