from PyQt5.QtGui import QIcon,QPixmap
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as Qt
import sys
from FlowLayout import FlowLayout
from connection import Communication
import threading
class MainWindow(qtw.QDialog):
        life = ['./resources/'+f'life{i}.png' for i in range(5)]
        alphabet = list("abcdefghijklmnopqrstuwxyz".upper())
        lifeCounter = -len(alphabet) #buttons fire callbacks when created
        password = "mlibuda".upper()
        guessedpassword = ['_' for letter in password]
        passwordLabel = 0
        
        
        def __init__(self, parent=None):
            
            super(MainWindow, self).__init__(parent)
            self.setWindowIcon(QIcon("./resources/LogoBlue.png"))
            self.setupUi()
            self.com = Communication()
            #run communication in a thread
            threading.Thread(target = self.com.run).start()
            
        
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
            hostButton.clicked.connect(lambda :
                self.goToWaitingRoom("Waiting for players..."))
            
            # connectButton.clicked.connect(lambda : 
            #     self.goToWaitingRoom("Connecting...")) #TODO:Disabled for tests without networking layers
           
            connectButton.clicked.connect(lambda :self.QtStack.setCurrentWidget(self.GameScene) )
            
            layout.addWidget(hostButton,0,0,1,2)
            layout.addWidget(connectButton,1,0)
            layout.addWidget(ipField,1,1)
            
            for id in range(layout.count()):
                item = layout.itemAt(id).widget()
                item.setSizePolicy(qtw.QSizePolicy(qtw.QSizePolicy.Ignored,
                                                qtw.QSizePolicy.Ignored))
                item.setMaximumHeight(100)
           
            self.WelcomeScene.setLayout(layout)
            
            
        def initWaitingRoom(self):
            
            layout = qtw.QGridLayout()
            textLabel = qtw.QLabel()
            textLabel.setAlignment(Qt.Qt.AlignCenter)
            cancelButton = qtw.QPushButton("Cancel")
            layout.addWidget(textLabel,0,0)
            layout.addWidget(cancelButton)
            cancelButton.clicked.connect(lambda :self.QtStack.setCurrentWidget(self.WelcomeScene))
            self.WaitingRoom.setLayout(layout)
            
            
        def goToWaitingRoom(self,text):
            
            self.WaitingRoom.findChild(qtw.QLabel).setText(text)
            self.QtStack.setCurrentWidget(self.WaitingRoom)
        
                           
        def initGameScene(self):
            self.HangmanImage = qtw.QLabel()
            layout = qtw.QGridLayout()
            playersTable = qtw.QTableWidget()
            playersDict = {"Player1":1,"Player2":5,"p3":123,"p5":2137,"p4":12213}
            playersTable.setColumnCount(2)
            playersTable.setHorizontalHeaderLabels(["Name","score"])
            playersTable.verticalHeader().hide()
            playersTable.setHorizontalScrollBarPolicy(Qt.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            items = 0
            for desc, price in playersDict.items():
                playersTable.insertRow(items)
                name = qtw.QTableWidgetItem(desc)
                name.setFlags(Qt.Qt.ItemFlag.ItemIsEnabled)
                score = qtw.QTableWidgetItem(str(price))
                score.setFlags(Qt.Qt.ItemFlag.ItemIsEnabled)                
                playersTable.setItem(items, 0, name)
                playersTable.setItem(items, 1, score)

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
            if self.password!=''.join(self.guessedpassword):

                if letter in self.password and isAlive:
                    for id in self.findAllOccurencies(letter):
                        self.guessedpassword[id]=letter
                        self.passwordLabel.setText(' '.join(self.guessedpassword))
                
                else:
                    self.lifeCounter+=1
                    
                    
                if isAlive:
                    
                    self.sender().deleteLater()
                    self.com.addLettertoQueue(f"##{letter}##")
                    
                    self.setImage(self.lifeCounter)
                    if self.lifeCounter==4:
                        self.passwordLabel.setText(' '.join(self.guessedpassword)+"\n\nYou Lost! ;-)")
                    
                
                if self.password==''.join(self.guessedpassword):
                    self.deleteAllLetters()
                    self.passwordLabel.setText(' '.join(self.guessedpassword)+"\n\nYou Won!")
                
                

                    
        def setImage(self,id = 0):
            pixmap = QPixmap(self.life[id])
            self.HangmanImage.setPixmap(pixmap.scaled(256,256))
            
        def deleteAllLetters(self):
            for id in range(self.letterLayout.count()):
                self.letterLayout.itemAt(id).widget().deleteLater()
                
            
        def findAllOccurencies(self,letter):
            return [i for i, l in enumerate(self.password) if l == letter]

class LetterButton(qtw.QPushButton):
    def __init__(self,text):
        super().__init__() 
        self.setText(text)     
        self.animateClick(1)

    
 
if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec())