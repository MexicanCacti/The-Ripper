import threading, time, re
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QFileDialog, QTextEdit, QProgressBar
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
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
        threading.Thread(target = self.checkDoneQueue, daemon=True).start()
        self.updateProgressSignal.connect(self.updateProgress)
        #self.testLabel = QLabel("Test", self)
        #self.testLabel.setGeometry(0, 0, 100, 100)

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
        url = self.urlEdit.text()
        urlType = checkValidUrl(self.urlEdit.text())
        if(urlType == -1):
            print(f"{url} not a valid youtube url")
        else:
            self.ripper.addToQueue((url, 0, self.ripper.getPath()))

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

    def demoLabel(self):
        labelStyle = loadCSS("styles/text.css", "QLabel")
        label = QLabel("Test", self)
        label.setGeometry(0, 0, 500, 100)
        label.setStyleSheet(labelStyle)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def demoBackgroundImage(self):
        background = QLabel(self)
        background.setGeometry(0, 0, self.width, self.height)
        backgroundImage = QPixmap("images/background.jpg")
        background.setPixmap(backgroundImage)
        background.setScaledContents(True)
        # Center Image
        background.setGeometry(
            (self.width - background.width()) // 2,
            (self.height - background.height()) // 2,
            background.width(),
            background.height()
        )

    def demoButton(self):
        self.testLabel = QLabel("Test", self)
        self.testLabel.setGeometry(0, 0, 100, 100)
        self.button = QPushButton("Rip", self)
        self.button.setGeometry(200, 200, 100, 100)
        self.button.clicked.connect(self.demoClick)
        self.testLabel.setGeometry(150, 300, 200, 100)

    def demoClick(self):
        print("Clicked! :)")
        self.button.setText("Pressed!")
        self.button.setDisabled(True)
        self.testLabel.setText("Clicked the button!")

    def demoUI(self):
        CW = QWidget()
        self.setCentralWidget(CW)
        labelStyle = loadCSS("styles/text.css", "QLabel")

        labels = []

        label1 = QLabel("#1")
        label2 = QLabel("#2")
        label3 = QLabel("#3")
        label4 = QLabel("#4")
        label5 = QLabel("#5")

        labels.append(label1)
        labels.append(label2)
        labels.append(label3)
        labels.append(label4)
        labels.append(label5)

        for label in labels:
            label.setStyleSheet(labelStyle)
        
        label1.setStyleSheet("background-color: green")
        label2.setStyleSheet("background-color: red")
        label3.setStyleSheet("background-color: blue")
        label4.setStyleSheet("background-color: yellow")
        label5.setStyleSheet("background-color: white")

        gridLayout = QGridLayout()
        gridLayout.addWidget(label1, 0, 0)
        gridLayout.addWidget(label2, 0, 1)
        gridLayout.addWidget(label3, 1, 0)
        gridLayout.addWidget(label4, 1, 1)
        gridLayout.addWidget(label5, 2, 0)
        
        CW.setgridLayout(gridLayout)

    
        
        
