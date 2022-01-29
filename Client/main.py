import logging
import sys
import threading
import warnings
from os.path import exists,dirname

import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as qtw
from PyQt5.QtGui import QIcon, QPixmap

from connection import Communication, Message
from FlowLayout import FlowLayout


logging.basicConfig()
logging.root.setLevel(logging.INFO)
directory = dirname(__file__)

class MainWindow(qtw.QDialog):
    life = [f"{directory}/resources/" + f"life{i}.png" for i in range(5)]
    alphabet = list("abcdefghijklmnopqrstuwxyz".upper())
    lifeCounter = -len(alphabet)  # buttons fire callbacks when created
    password = "_".upper()
    guessedpassword = ["_" for _ in password]
    passwordLabel = 0
    connected = False
    playersCount = 0
    nickname = ""
    MessageQueueCopy = None
    forceCancel = False

    def __init__(self):

        super().__init__()

        self.setWindowIcon(QIcon(f"{directory}/resources/LogoBlue.png"))
        self.setupUi()
        with open("config.txt", "r+") as f:
            self.ip = f.readline()[:-1]
            self.port = int(f.readline())

    def setupUi(self):

        self.QtStack = qtw.QStackedWidget()
        self.QtStack.setWindowTitle("Hangman!")
        self.QtStack.setMinimumSize(1000, 600)
        self.WelcomeScene = qtw.QWidget()
        self.WaitingRoom = qtw.QWidget()
        self.GameScene = qtw.QWidget()
        self.ErorrScene = qtw.QWidget()

        stylesheet = open(f"{directory}/stylesheet.css").read()
        scenes = [self.WelcomeScene, self.WaitingRoom, self.GameScene, self.ErorrScene]
        for scene in scenes:
            scene.setStyleSheet(stylesheet)
            self.QtStack.addWidget(scene)

        self.setWelcomePage()
        self.initWaitingRoom()
        self.initGameScene()
        self.initErrorScene()

        self.QtStack.show()

    def setErrorScene(self, text: str, allowReconnect=False):
        self.QtStack.setCurrentWidget(self.ErorrScene)
        self.ErorrScene.findChild(qtw.QLabel).setText(text)
        if allowReconnect:
            self.ErorrScene.findChild(qtw.QPushButton).show()
        else:
            self.ErorrScene.findChild(qtw.QPushButton).hide()

    def setWelcomePage(self):

        layout = qtw.QGridLayout()
        hostButton = qtw.QPushButton("I'm a host")
        connectButton = qtw.QPushButton("I want to join")

        nameField = qtw.QLineEdit()
        nameField.setMaxLength(20)  # set max name legnth to 20 chars
        nameField.setPlaceholderText("Enter nickname:")
        nameField.setMinimumWidth(100)
        nameField.setAlignment(QtCore.Qt.AlignCenter)

        hostButton.clicked.connect(
            lambda: self.goToWaitingRoom(
                "Waiting for players...", nameField, hostButton=True
            )
        )

        connectButton.clicked.connect(
            lambda: self.goToWaitingRoom(
                "Waiting for players...", nameField, hostButton=False
            )
        )

        layout.addWidget(hostButton, 1, 0)
        layout.addWidget(connectButton, 1, 1)
        layout.addWidget(nameField, 0, 0, 1, 2)

        for id in range(layout.count()):
            item = layout.itemAt(id).widget()
            item.setSizePolicy(
                qtw.QSizePolicy(qtw.QSizePolicy.Ignored, qtw.QSizePolicy.Ignored)
            )
            item.setMaximumHeight(100)

        self.WelcomeScene.setLayout(layout)

    def setReady(self, btn: qtw.QPushButton):
        btn.setDown(True)
        btn.setStyleSheet('color: "#E5E5E5"')
        # FIXME: READY MESSAGE TO SERVER
        self.com.addTexttoQueue(Message("", Message.HOST_READY))

    def updatePlayersInfo(self):
        if self.playersCount == 1:
            self.playersCountInfo.setText("Currently 1 player")
        else:
            self.playersCountInfo.setText(f"Currently {self.playersCount} players")

    def initWaitingRoom(self):
        self.ready = 0
        layout = qtw.QGridLayout()
        textLabel = qtw.QLabel()
        textLabel.setAlignment(QtCore.Qt.AlignCenter)
        playersCountLabel = qtw.QLabel("Currently 1 player")
        self.playersCountInfo = playersCountLabel
        playersCountLabel.setAlignment(QtCore.Qt.AlignCenter)

        readyButton = qtw.QPushButton("I'm Ready")
        cancelButton = qtw.QPushButton("Cancel")
        self.ready = readyButton.isChecked()
        layout.addWidget(textLabel, 0, 0)
        layout.addWidget(playersCountLabel, 1, 0)
        layout.addWidget(readyButton)
        layout.addWidget(cancelButton)

        cancelButton.clicked.connect(self.cancelConnection)
        readyButton.clicked.connect(lambda: self.setReady(readyButton))
        self.WaitingRoom.setLayout(layout)

    def initErrorScene(self):
        layout = qtw.QGridLayout()
        textLabel = qtw.QLabel(
            "There was problem with server.\n You can try to reconnect or go back to main menu"
        )
        textLabel.setAlignment(QtCore.Qt.AlignCenter)
        reconnectButton = qtw.QPushButton("Try to Reconnect")
        cancelButton = qtw.QPushButton("Go Back to main menu")
        layout.addWidget(textLabel, 0, 0)
        layout.addWidget(reconnectButton)
        layout.addWidget(cancelButton)
        cancelButton.clicked.connect(self.cancelConnection)
        reconnectButton.clicked.connect(self.reconnect)
        self.ErorrScene.setLayout(layout)

    def reconnect(self):

        self.com = Communication(GUIReference=self, address=self.ip, port=self.port,queue = self.MessageQueueCopy)
        threading.Thread(target=self.com.run).start()

        with open(f"{directory}/id.txt", "r") as f:
            self.id = f.readline()
        self.com.isHost = id == 0
        self.com.addTexttoQueue(Message(str(self.id), code=Message.RECONNECT))
        logging.info("Reconnect Attempt")

    def cancelConnection(self):
        self.QtStack.setCurrentWidget(self.WelcomeScene)
        self.forceCancel = True
        if self.com is not None:
            self.com.addTexttoQueue(Message("",Message.REMOVE))
            self.com.connectionStable = False
            self.MessageQueueCopy = self.com.messageQueue
            self.com = None


    def goToWaitingRoom(self, text: str, name: str, hostButton=False):


        # initialize comunication

        self.QtStack.setCurrentWidget(self.WaitingRoom)

        
        self.com = Communication(
            GUIReference=self, address=self.ip, port=self.port, isHost=hostButton,queue = self.MessageQueueCopy
        )

        threading.Thread(target=self.com.run).start()

        self.WaitingRoom.findChild(qtw.QLabel).setText("Waiting for other players...")
        self.nickname = name.text()
        if hostButton:
            self.GameScene.findChildren(qtw.QPushButton)[-1].show()
            
            self.WaitingRoom.findChild(qtw.QPushButton).show()
            
            msg = Message(self.nickname, Message.HOST_INIT)
        else:
            self.GameScene.findChildren(qtw.QPushButton)[-1].hide()
            
            self.WaitingRoom.findChild(qtw.QPushButton).hide()
            msg = Message(self.nickname, Message.NEW_PLAYER)

        self.com.addTexttoQueue(msg)

    def updateLeaderBoard(self):
        items = 0
        self.playersTable.setRowCount(0)
        # FIXME: format score pewnie sie zmieni na cos w stylu trafione/stracone wiec klucz bedize do zmiany
        # ale działa póki co
        for desc, price in sorted(self.playersDict.items(), key=lambda x: x[1][0]/x[1][1] if x[1][1]>0 else x[1][0]):
            self.playersTable.insertRow(0)
            name = qtw.QTableWidgetItem(desc)
            name.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled)
            score = qtw.QTableWidgetItem(str(price))
            score.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.playersTable.setItem(items, 0, name)
            self.playersTable.setItem(items, 1, score)

    def initGameScene(self):
        self.HangmanImage = qtw.QLabel()
        layout = qtw.QGridLayout()
        playersTable = qtw.QTableWidget()  # Table widget IS scrollable by default
        playersDict = {}
        self.playersDict = playersDict
        self.playersTable = playersTable

        playersTable.setColumnCount(2)
        playersTable.setHorizontalHeaderLabels(["Name", "score"])
        playersTable.verticalHeader().hide()
        playersTable.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.updateLeaderBoard()

        layout.addWidget(playersTable, 0, 0, 5, 2)

        self.passwordLabel = qtw.QLabel(" ".join(self.guessedpassword))
        gameMainWidget = qtw.QWidget()
        hangmanLayout = qtw.QVBoxLayout()
        self.HangmanImage.setAlignment(QtCore.Qt.AlignCenter)
        self.passwordLabel.setAlignment(QtCore.Qt.AlignCenter)

        hangmanLayout.addWidget(self.HangmanImage, 30)
        hangmanLayout.addWidget(self.passwordLabel, 20)
        lettersWidget = qtw.QWidget()
        self.letterLayout = FlowLayout()
        self.generateLetters()
        

        self.setImage()
        lettersWidget.setLayout(self.letterLayout)

        hangmanLayout.addWidget(lettersWidget, 30)

        gameMainWidget.setLayout(hangmanLayout)

        # gameMainWidget.setStyleSheet("background-color:red;")
        layout.addWidget(gameMainWidget, 0, 2, 5, 5)
        goBackToLobby = qtw.QPushButton("Go Back!")
        goBackToLobby.clicked.connect(lambda :self.goBack(True))
        layout.addWidget(goBackToLobby, 6, 6, 1, 1)

        self.GameScene.setLayout(layout)

    def goBack(self,playerisSending = True):
        self.QtStack.setCurrentWidget(self.WaitingRoom)
    
        self.playersDict = {key:(0,0) for key in self.playersDict}
        self.lifeCounter = 0
        self.hideAllLetters()
        
        if playerisSending: #To prevent loops of messages
            self.com.addTexttoQueue(Message("",Message.RESET))
            
            
        self.setImage()
        
    def generateLetters(self):
            for letter in self.alphabet:
                letterButton = LetterButton(letter)
                letterButton.clicked.connect(self.gameLogic)
                self.letterLayout.addWidget(letterButton)
                
    def gameLogic(self):

        letter = self.sender().text()
        isAlive = 0 <= self.lifeCounter < 4

        if isAlive:
            self.sender().hide()
            print(self.sender())

            if letter in self.password:
                self.com.addTexttoQueue(Message("1", Message.GUESS))

                for id in self.findAllOccurencies(letter):
                    self.guessedpassword[id] = letter

                self.passwordLabel.setText(" ".join(self.guessedpassword))

                if self.password == "".join(self.guessedpassword):
                    self.disableAllLetters()
                    self.passwordLabel.setText(
                        " ".join(self.guessedpassword) + "\n\nYou Won!"
                    )
            else:
                self.com.addTexttoQueue(Message("0", Message.GUESS))
                self.lifeCounter += 1
                self.setImage(self.lifeCounter)

            if self.lifeCounter == 4:
                self.passwordLabel.setText(
                    " ".join(self.guessedpassword) + "\n\nYou Lost! ;-)"
                )
        else:
            self.lifeCounter += 1  # to handle click send on create

    def setImage(self, id=0):
        pixmap = QPixmap(self.life[id])
        self.HangmanImage.setPixmap(pixmap.scaled(256, 256))

    def hideAllLetters(self,hide = True):
        if hide:
            for id in range(self.letterLayout.count()):
                self.letterLayout.itemAt(id).widget().hide()
        else:
            for id in range(self.letterLayout.count()):
                self.letterLayout.itemAt(id).widget().show()

    def disableAllLetters(self,disable = True):
        for id in range(self.letterLayout.count()):
            self.letterLayout.itemAt(id).widget().setDisabled(disable)

    def findAllOccurencies(self, letter: str) -> list[int]:
        return [i for i, l in enumerate(self.password) if l == letter]

    def setPassword(self, password: str):
        self.password = password.upper()
        self.guessedpassword = ["_" for _ in password]
        self.passwordLabel.setText(" ".join(self.guessedpassword))

    def terminate(self):
        Qt.QCoreApplication.quit()
        # TODO: FORCE APP TO QUIT


class LetterButton(qtw.QPushButton):
    def __init__(self, text: str):
        super().__init__()
        self.setText(text)
        self.animateClick(1)


if __name__ == "__main__":
    app = qtw.QApplication([])
    w = MainWindow()
    sys.exit(app.exec())
