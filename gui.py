import threading, time
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QGridLayout, QPushButton, QLineEdit, QFileDialog, QTextEdit
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from utils import loadCSS, checkValidUrl


class MainWindow(QMainWindow):
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

        self.gridLayout.addWidget(self.finishedLabel, 1, 0, 1, 3)
        self.gridLayout.addWidget(self.finishedBox, 2, 0, 1, 3)


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

        self.gridLayout.addWidget(self.urlLabel, 0, 0)
        self.gridLayout.addWidget(self.urlEdit, 0, 1)
        self.gridLayout.addWidget(self.urlSubmit, 0, 2)

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

        self.gridLayout.addWidget(self.directoryLabel, 3, 0)
        self.gridLayout.addWidget(self.directoryPath, 3, 1)
        self.gridLayout.addWidget(self.directoryButton, 3, 2)

    def layout(self):
        self.CW = QWidget()
        self.setCentralWidget(self.CW)
        self.gridLayout = QGridLayout()

        self.inputField()

        self.finishedItemsField()

        self.directoryField()

        self.CW.setLayout(self.gridLayout)

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

    
        
        
