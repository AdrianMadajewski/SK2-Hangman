import sys
import threading
import socket
import PyQt5.QtCore as Qt
import PyQt5.QtWidgets as qtw
from PyQt5.QtGui import QIcon, QPixmap
from connection import Communication
from FlowLayout import FlowLayout
from enum import Enum
from connection import Message
from typing import Type


class Code(Enum):
        Initalize = 1
        Letter = 2
        Reconnect = 3
        
        
class MainWindow(qtw.QDialog):
        life = ['./resources/'+f'life{i}.png' for i in range(5)]
        alphabet = list("abcdefghijklmnopqrstuwxyz".upper())
        lifeCounter = -len(alphabet) #buttons fire callbacks when created
        password = "mlibuda".upper()
        guessedpassword = ['_' for _ in password]
        passwordLabel = 0
        playersCount  = 0
        
        
        def __init__(self):
            
            super(MainWindow, self).__init__()
            self.setWindowIcon(QIcon("./resources/LogoBlue.png"))
            self.setupUi()
           
            
        
        def setupUi(self):
            
            self.QtStack = qtw.QStackedWidget()
            self.QtStack.setWindowTitle("Hangman!")
            self.QtStack.setMinimumSize(1000,600)
            self.WelcomeScene = qtw.QWidget()
            self.WaitingRoom = qtw.QWidget()
            self.GameScene = qtw.QWidget()
            stylesheet = open('stylesheet.css').read()
            scenes = [self.WelcomeScene,self.WaitingRoom,self.GameScene]
            for scene in scenes:
                scene.setStyleSheet(stylesheet)
                self.QtStack.addWidget(scene)
                
            self.setWelcomePage()
            self.initWaitingRoom()
            self.initGameScene()
            
            self.QtStack.show()
      
    
        def setWelcomePage(self):
            
            layout = qtw.QGridLayout()
            hostButton = qtw.QPushButton("I'm a host")
            connectButton = qtw.QPushButton("I want to join")
            
            ipField = qtw.QLineEdit()
            
            ipField.setPlaceholderText("Enter ip:")
            ipField.setMinimumWidth(100)
            ipField.setAlignment(Qt.Qt.AlignCenter)
            nameField = qtw.QLineEdit()
            nameField.setPlaceholderText("Enter nickname:")
            nameField.setMinimumWidth(100)
            nameField.setAlignment(Qt.Qt.AlignCenter)
            
            
            hostButton.clicked.connect(lambda :
                self.goToWaitingRoom("Waiting for players...",ipField,nameField,hostButton=True))
            
            # connectButton.clicked.connect(lambda :
            #    self.goToWaitingRoom("Waiting for players...",ipField,nameField,hostButton=False)) #TODO:Disabled for tests without networking layers
           
            connectButton.clicked.connect(lambda :self.QtStack.setCurrentWidget(self.GameScene) )
            
            layout.addWidget(hostButton,0,0)
            layout.addWidget(connectButton,1,0,)
            layout.addWidget(ipField,1,1)
            layout.addWidget(nameField,0,1)
            
            for id in range(layout.count()):
                item = layout.itemAt(id).widget()
                item.setSizePolicy(qtw.QSizePolicy(qtw.QSizePolicy.Ignored,
                                                qtw.QSizePolicy.Ignored))
                item.setMaximumHeight(100)
           
            self.WelcomeScene.setLayout(layout)
        
        def setReady(self,btn:qtw.QPushButton):
            self.ready = 1
            btn.setDown(True)
            btn.setStyleSheet('color: "#E5E5E5"')
            self.com.addTexttoQueue(Message(self.ready,1)) #FIXME: READY MESSAGE TO SERVER
            
            
        
        def updatePlayersInfo(self):
            if self.playersCount==1:
                self.playersCountInfo.setText("Currently 1 player")
            else:
                self.playersCountInfo.setText(f"Currently {self.playersCount} players")
                        
        def initWaitingRoom(self):
            self.ready = 0
            layout = qtw.QGridLayout()
            textLabel = qtw.QLabel()
            textLabel.setAlignment(Qt.Qt.AlignCenter)
            playersCountLabel = qtw.QLabel("Currently 1 player")
            self.playersCountInfo = playersCountLabel
            playersCountLabel.setAlignment(Qt.Qt.AlignCenter)
            
            
            
            readyButton = qtw.QPushButton("I'm Ready")
            
            cancelButton = qtw.QPushButton("Cancel")
            self.ready = readyButton.isChecked()
            
            layout.addWidget(textLabel,0,0)
            layout.addWidget(playersCountLabel,1,0)
            layout.addWidget(readyButton)
            layout.addWidget(cancelButton)
            
            
            cancelButton.clicked.connect(self.cancelConnection)
            readyButton.clicked.connect(lambda: self.setReady(readyButton))
            self.WaitingRoom.setLayout(layout)
            
        def cancelConnection(self):
            self.QtStack.setCurrentWidget(self.WelcomeScene)
            del self.com
            
        def goToWaitingRoom(self,text:str,ip:str,name:str,hostButton = False):
            
            try:
                socket.inet_aton(ip.text())
            except socket.error:
                ip.setText("Please enter valid ip address")
                return
            
            if not(name.text().isalnum()):
                name.setText("Please enter valid nickname")
                return
                
                
            

            #initialize comunication
            self.WaitingRoom.findChild(qtw.QLabel).setText("Waiting for other players...")
            self.QtStack.setCurrentWidget(self.WaitingRoom)
            
            self.com = Communication(GUIReference=self ,address=ip.text(),port=2137,isHost=hostButton)
            threading.Thread(target = self.com.run).start()
            msg = Message(name.text(),Code.Initalize.value)
            
            self.com.addTexttoQueue(msg)
            

           
            

            
                
        
        def updateLeaderBoard(self):
            items = 0
            self.playersTable.setRowCount(0)
            #FIXME: format score pewnie sie zmieni na cos w stylu trafione/stracone wiec klucz bedize do zmiany
            #ale działa póki co
            for desc, price in sorted(self.playersDict.items(),key = lambda x: -int(x[1])):
                self.playersTable.insertRow(0)
                name = qtw.QTableWidgetItem(desc)
                name.setFlags(Qt.Qt.ItemFlag.ItemIsEnabled)
                score = qtw.QTableWidgetItem(str(price))
                score.setFlags(Qt.Qt.ItemFlag.ItemIsEnabled)                
                self.playersTable.setItem(items, 0, name)
                self.playersTable.setItem(items, 1, score)
                           
        def initGameScene(self):
            self.HangmanImage = qtw.QLabel()
            layout = qtw.QGridLayout()
            playersTable = qtw.QTableWidget() #Table widget IS scrollable by default
            playersDict = {"Player1":1,"Player2":5,"p3":123,"p5":2137,"p4":12213}
            self.playersDict = playersDict
            self.playersTable = playersTable
            
            playersTable.setColumnCount(2)
            playersTable.setHorizontalHeaderLabels(["Name","score"])
            playersTable.verticalHeader().hide()
            playersTable.setHorizontalScrollBarPolicy(Qt.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            
            self.updateLeaderBoard()

            layout.addWidget(playersTable,0,0,5,2)       
            
            self.passwordLabel = qtw.QLabel(' '.join(self.guessedpassword))
            gameMainWidget = qtw.QWidget()
            hangmanLayout = qtw.QVBoxLayout()
            self.HangmanImage.setAlignment(Qt.Qt.AlignCenter)
            self.passwordLabel.setAlignment(Qt.Qt.AlignCenter)
            
            hangmanLayout.addWidget(self.HangmanImage,30)
            hangmanLayout.addWidget(self.passwordLabel,20)
            lettersWidget = qtw.QWidget()
            self.letterLayout =FlowLayout()
            for letter in self.alphabet:
                
                letterButton = LetterButton(letter)
                letterButton.clicked.connect(self.gameLogic)
                self.letterLayout.addWidget(letterButton)
            
            self.setImage()  
            lettersWidget.setLayout(self.letterLayout)
            hangmanLayout.addWidget(lettersWidget,30)
            

            
            gameMainWidget.setLayout(hangmanLayout)
            # gameMainWidget.setStyleSheet("background-color:red;")
            layout.addWidget(gameMainWidget,0,2,5,5)
            
            self.GameScene.setLayout(layout)
            
        def gameLogic(self):
            
            letter = self.sender().text()
            isAlive = 0<=self.lifeCounter<4

            if isAlive:
                print("alive")
                self.sender().deleteLater()
                
                if letter in self.password:
                    self.com.addTexttoQueue(Message("1",Code.Letter.value))
                    
                    for id in self.findAllOccurencies(letter):
                        self.guessedpassword[id]=letter
                        
                    self.passwordLabel.setText(' '.join(self.guessedpassword))
                        
                    if self.password==''.join(self.guessedpassword):
                        self.deleteAllLetters()
                        self.passwordLabel.setText(' '.join(self.guessedpassword)+"\n\nYou Won!")
                else:
                    self.com.addTexttoQueue(Message("0",Code.Letter.value))
                    self.lifeCounter+=1
                    self.setImage(self.lifeCounter)
                    
                    
                if self.lifeCounter==4:
                    self.passwordLabel.setText(' '.join(self.guessedpassword)+"\n\nYou Lost! ;-)")
            else:
                self.lifeCounter+=1 #to handle click send on create
                
        
            
                
                

                    
        def setImage(self,id = 0):
            pixmap = QPixmap(self.life[id])
            self.HangmanImage.setPixmap(pixmap.scaled(256,256))
            
        def deleteAllLetters(self):
            for id in range(self.letterLayout.count()):
                self.letterLayout.itemAt(id).widget().deleteLater()
                
            
        def findAllOccurencies(self,letter :str)->list[int]:
            return [i for i, l in enumerate(self.password) if l == letter]
        
        def terminate(self):
            Qt.QCoreApplication.quit()
            #TODO: FORCE APP TO QUIT
            

class LetterButton(qtw.QPushButton):
    def __init__(self,text : str):
        super().__init__() 
        self.setText(text)     
        self.animateClick(1)

    

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec())
