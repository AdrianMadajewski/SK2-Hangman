from PyQt5.QtGui import QIcon,QPixmap
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as Qt
import sys


class MainWindow(qtw.QDialog):
    
    
        def __init__(self, parent=None):
            
            super(MainWindow, self).__init__(parent)
            self.setWindowIcon(QIcon("./resources/LogoBlue.png"))
            self.setupUi()

        
        def setupUi(self):
            
            self.resize(600, 400)
            self.QtStack = qtw.QStackedWidget()
            self.QtStack.setWindowTitle("Hangman!")
            
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
            
            self.WelcomeScene.setMinimumSize(400,300)
            self.QtStack.setMaximumSize(1000,500)
            self.QtStack.resize(700,200)
            
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
            connectButton.clicked.connect(self.initGameScene)
            
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
            alphabet = list("aąbcćdeęfghijklłmnńoópqrsśtuwxyzźż".upper())
            self.QtStack.setCurrentWidget(self.GameScene)
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
            
            dummyLabel = qtw.QLabel("XD")
            dummyLabel.setStyleSheet("background-color:red;")
            layout.addWidget(dummyLabel,0,2,5,5)
            self.GameScene.setLayout(layout)
            
        
    
 
if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec())