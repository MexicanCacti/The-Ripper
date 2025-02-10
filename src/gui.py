import threading, time, sys, os
from pathlib import Path
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QFileDialog, QTextEdit, QProgressBar
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import pyqtSignal
from utils import loadCSS, checkValidUrl, removeAnsiEscape, trimFile


class MainWindow(QMainWindow):
    updateProgressSignal = pyqtSignal(dict)
    def __init__(self, ripper):
        super().__init__()
        self.ripper = ripper
        self.width = 800
        self.height = 600
        self.setWindowTitle("The Ripper")
        self.setGeometry(0, 0, self.width, self.height)
        self.setWindowIcon(QIcon("images/icon.jpg"))
        
        self.initUI()
        self.loadStyles()
        threading.Thread(target = self.checkDoneQueue, daemon=True).start()
        self.updateProgressSignal.connect(self.updateProgress)

    def loadStyles(self):
        if hasattr(sys, 'frozen'):
            css = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        else:
            css = Path().absolute()
        
        css = os.path.join(css, "styles", "global.css")

        if not os.path.exists(css):
            print(f"[Error]: Couldn't find global style at {css}")
            raise FileNotFoundError("global.css not found")

        try:
            with open(css, "r") as css_file:
                style = css_file.read()
                self.setStyleSheet(style)
        except Exception as e:
            print(f"Error opening {css}: e")

        

    def checkDoneQueue(self):
        while True:
            item = self.ripper.getFinishedItem()
            if item == None:
                time.sleep(10)
                continue
            self.finishedBox.append(item)

    def finishedItemsField(self):
        self.finishedLabel = QLabel("Finished Items", self)
        self.finishedBox = QTextEdit(self)
        self.finishedBox.setReadOnly(True)
        self.progressText = QLineEdit(self)
        self.progressText.setReadOnly(True)
        self.progressBar = QProgressBar(self)

    def updateProgress(self, download):
        progress = removeAnsiEscape(download['_percent_str'].strip())
        progress = progress.replace('%', '')
        try:
            self.progressBar.setValue(int(float(progress))) 
        except ValueError:
            print(f"Error: Invalid progress value '{progress}'")
            progress = 0

        self.progressText.setText(f"Downloading {trimFile(download['filename'])} - {progress} at {removeAnsiEscape(download['_speed_str'])} ETA {removeAnsiEscape(download['_eta_str'])}")

    def inputUrl(self):
        # Probably want to include check boxes so that it knows the flags to put into yt-dlp!
        self.urlSubmit.setDisabled(True)
        url = self.urlEdit.text()
        urlType = checkValidUrl(self.urlEdit.text())
        if(urlType == -1):
            print(f"{url} not a valid youtube url")
        else:
            self.ripper.addToQueue((url, 0, self.ripper.getPath()))
        time.sleep(2)
        self.urlSubmit.setDisabled(False)

    def inputField(self):
        self.urlLabel = QLabel("URL: ", self)
        self.urlEdit = QLineEdit(self)
        self.urlSubmit = QPushButton("Rip", self)
        self.urlSubmit.clicked.connect(self.inputUrl)

    def changeDirectory(self):
        options = QFileDialog.Options()
        dir = QFileDialog.getExistingDirectory(self, "Select Directory", str(self.ripper.getPath()), options=options)

        if dir:
            self.ripper.setPath(dir)
            self.directoryPath.setText(dir)
    
    def directoryField(self):
        self.directoryLabel = QLabel("Directory Path: ", self)
        self.directoryPath = QLabel(str(self.ripper.getPath()), self)
        self.directoryButton = QPushButton("Change Directory Path", self)
        self.directoryButton.clicked.connect(self.changeDirectory)

    def layout(self):
        self.CW = QWidget()
        self.setCentralWidget(self.CW)
        self.mainLayout = QVBoxLayout()

        self.inputField()

        self.finishedItemsField()

        self.directoryField()

        # Url input section
        self.urlLayout = QHBoxLayout()
        self.urlLayout.addWidget(self.urlLabel)
        self.urlLayout.addWidget(self.urlEdit)
        self.urlLayout.addWidget(self.urlSubmit)

        # Progress Section
        self.progressLayout = QVBoxLayout()
        self.progressLayout.addWidget(self.progressText)
        self.progressLayout.addWidget(self.progressBar)

        # Directory Section
        self.directoryLayout = QHBoxLayout()
        self.directoryLayout.addWidget(self.directoryLabel) 
        self.directoryLayout.addWidget(self.directoryPath)
        self.directoryLayout.addWidget(self.directoryButton)

        self.mainLayout.addLayout(self.urlLayout)
        self.mainLayout.addLayout(self.progressLayout)
        self.mainLayout.addWidget(self.finishedLabel)
        self.mainLayout.addWidget(self.finishedBox)
        self.mainLayout.addLayout(self.directoryLayout)

        self.CW.setLayout(self.mainLayout)

    def initUI(self):
        self.layout()
        
