import threading, time
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QFileDialog, QTextEdit, QProgressBar
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import pyqtSignal, QTimer, Qt
from utils import loadCSS, checkValidUrl, removeAnsiEscape, trimFile


class MainWindow(QMainWindow):
    updateProgressSignal = pyqtSignal(dict)
    updateQueueSignal = pyqtSignal(tuple)
    def __init__(self, ripper):
        super().__init__()
        self.ripper = ripper
        self.width = 800
        self.height = 600
        self.setWindowTitle("The Ripper")
        self.setGeometry(0, 0, self.width, self.height)
        self.setWindowIcon(QIcon("images/icon.jpg"))
        
        self.initUI()
        globalCSS = loadCSS("global.css")
        print("Couldn't open global.css") if globalCSS == -1 else self.setStyleSheet(globalCSS)

        threading.Thread(target = self.checkDoneQueue, daemon=True).start()
        self.updateProgressSignal.connect(self.updateProgress)
        self.updateQueueSignal.connect(self.updateQueue) 

    def updateQueue(self, item):
        if len(item) < 2:
            print(f"Invalid Item Sent to: updateQueue")

        if item[1] == 0:
            self.queuedBox.append(item[0])
            print(f"Adding: {item[0]}")
        elif item[1] == 1:
            self.removeQueueItem(item[0])
            print(f"Removing: {item[0]}")
        else:
            print(f"[ERROR]: updateQueue: {item[0]}, {item[1]}")     

    def updateProgress(self, download):
        progress = removeAnsiEscape(download['_percent_str'].strip())
        progress = progress.replace('%', '')
        try:
            self.progressBar.setValue(int(float(progress))) 
        except ValueError:
            print(f"[Error]: Invalid progress value: '{progress}'")
            progress = 0

        self.progressText.setText(f"Downloading {trimFile(download['filename'])} - {progress} at {removeAnsiEscape(download['_speed_str'])} ETA {removeAnsiEscape(download['_eta_str'])}")

    def removeQueueItem(self, item):
        curr = self.queuedBox.toPlainText()
        new = curr.replace(item, "", 1)
        new = "\n".join([line for line in new.splitlines() if line.strip()])  # Removes empty lines
        self.queuedBox.setPlainText(new)

    def checkDoneQueue(self):
        while True:
            item = self.ripper.getFinishedItem()
            if item == None:
                time.sleep(5)
                continue
            self.finishedBox.append(item)

    def clearFinished(self):
        self.clearFinishedButton.setDisabled(True)
        self.finishedBox.clear()
        QTimer.singleShot(2000, lambda: self.clearFinishedButton.setDisabled(False))


    def finishedItemsField(self):
        self.finishedLabel = QLabel("Finished Items", self)
        self.clearFinishedButton = QPushButton("Clear Items", self)
        self.clearFinishedButton.setMaximumSize(120, 30) 
        self.clearFinishedButton.clicked.connect(self.clearFinished)
        self.queuedLabel = QLabel("Queued Items", self)

        self.finishedBox = QTextEdit(self)
        self.finishedBox.setReadOnly(True)

        self.queuedBox = QTextEdit(self)
        self.queuedBox.setReadOnly(True)

        self.submitInfoText = QLineEdit(self)
        self.submitInfoText.setReadOnly(True)
        self.progressText = QLineEdit(self)
        self.progressText.setReadOnly(True)
        self.progressBar = QProgressBar(self)

    def inputUrl(self):
        # Probably want to include check boxes so that it knows the flags to put into yt-dlp!
        self.urlSubmit.setDisabled(True)
        url = self.urlEdit.text()
        urlType = checkValidUrl(self.urlEdit.text())
        if(urlType == -1):
            self.submitInfoText.setText(f"{url} not a valid youtube url")
        else:
            self.ripper.addToQueue((url, urlType, self.ripper.getPath()))
            self.submitInfoText.setText(f"Added {url} to rip list")

        QTimer.singleShot(2000, lambda: self.urlSubmit.setDisabled(False))

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
        self.progressLayout.addWidget(self.submitInfoText)
        self.progressLayout.addWidget(self.progressText)
        self.progressLayout.addWidget(self.progressBar)

        # Work Top
        self.workTopLayout = QHBoxLayout()
        self.workTopLayout.addWidget(self.finishedLabel)
        self.workTopLayout.addWidget(self.queuedLabel)

        # Work Formatting
        self.workTopLayout.setAlignment(self.finishedLabel, Qt.AlignLeft)
        self.workTopLayout.setAlignment(self.queuedLabel, Qt.AlignLeft)

        # Work Box
        self.workBoxLayout = QHBoxLayout()
        self.workBoxLayout.addWidget(self.finishedBox)
        self.workBoxLayout.addWidget(self.queuedBox)

        # Misc Buttons
        self.miscButtonLayout = QHBoxLayout()
        self.miscButtonLayout.addWidget(self.clearFinishedButton)

        #Misc Button Formating
        self.miscButtonLayout.setAlignment(self.clearFinishedButton, Qt.AlignLeft)

        # Directory Section
        self.directoryLayout = QHBoxLayout()
        self.directoryLayout.addWidget(self.directoryLabel) 
        self.directoryLayout.addWidget(self.directoryPath)
        self.directoryLayout.addWidget(self.directoryButton)

        self.mainLayout.addLayout(self.urlLayout)
        self.mainLayout.addLayout(self.progressLayout)
        self.mainLayout.addLayout(self.workTopLayout)
        self.mainLayout.addLayout(self.workBoxLayout)
        self.mainLayout.addLayout(self.miscButtonLayout)
        self.mainLayout.addLayout(self.directoryLayout)

        self.CW.setLayout(self.mainLayout)

    def initUI(self):
        self.layout()
        
