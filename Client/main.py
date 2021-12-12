from PyQt5.QtGui import QIcon,QPixmap
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as Qt

import sys


class MainWindow(qtw.QDialog):
    
    
        def __init__(self, parent=None):
            super(MainWindow, self).__init__(parent)
            self.setWindowIcon(QIcon("./resources/LogoBlue.png"))
            self.setStyleSheet(open('stylesheet.css').read())
            self.setupUi()

        
        def setupUi(self):
            self.resize(600, 400)

            self.QtStack = qtw.QStackedWidget()
            self.QtStack.setWindowTitle("Hangman!")
            self.WelcomePage = qtw.QWidget()
            self.WaitingRoom = qtw.QWidget()
            self.setWelcomePage()
            self.QtStack.setMaximumSize(1000,500)
            self.QtStack.resize(700,200)
            self.QtStack.addWidget(self.WelcomePage)
            self.QtStack.addWidget(self.WaitingRoom)
            
            self.QtStack.show()
      
    
        def setWelcomePage(self):
            layout = qtw.QGridLayout()
           
            
            hostButton = qtw.QPushButton("I'm a host")
            connectButton = qtw.QPushButton("I want to join")
            ipField = qtw.QLineEdit()
            ipField.setPlaceholderText("Enter ip:")
            ipField.setMinimumWidth(100)
            hostButton.clicked.connect(lambda :
                self.initWaitingWindowPlayerWindow("Waiting for players..."))
            
            connectButton.clicked.connect(lambda :
                self.initWaitingWindowPlayerWindow("Connecting..."))
            
            layout.addWidget(hostButton,0,0,1,2)
            layout.addWidget(connectButton,1,0)
            layout.addWidget(ipField,1,1)
            
            for id in range(layout.count()):
                item = layout.itemAt(id).widget()
                item.setSizePolicy(qtw.QSizePolicy(qtw.QSizePolicy.Ignored,
                                                qtw.QSizePolicy.Ignored))
                item.setMaximumHeight(100)
           
            self.WelcomePage.setLayout(layout)
            
            
        def initWaitingWindowPlayerWindow(self,text):
            layout = qtw.QGridLayout()
            textLabel = qtw.QLabel(text)
            textLabel.setAlignment(Qt.Qt.AlignCenter)
            cancelButton = qtw.QPushButton("Cancel")
            
            layout.addWidget(textLabel,0,0)
            layout.addWidget(cancelButton)
            cancelButton.clicked.connect(self.goBackToWelcome)
            self.WaitingRoom.setLayout(layout)
            self.QtStack.setCurrentWidget(self.WaitingRoom)
            
        def goBackToWelcome(self):
            self.QtStack.setCurrentWidget(self.WelcomePage)
            
            for x in self.WaitingRoom.children():
                x.deleteLater()
            
          
    
 
if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec())