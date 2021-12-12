from PyQt5.QtGui import QIcon
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as Qt
import sys


class MainWindow(qtw.QWidget):
        layout =  qtw.QGridLayout()
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Hangman!")
            
            self.setWindowIcon(QIcon("./resources/LogoBlue.png"))
            self.setStyleSheet(open('stylesheet.css').read())
            
            self.setWelcomePage()
    
        def setWelcomePage(self):
            self.setLayout(self.layout)
            self.resize(500,200)
            self.setMaximumSize(1000,500)
            
            self.hostButton = qtw.QPushButton("I'm a host")
            self.connectButton = qtw.QPushButton("I want to join")
            self.ipField = qtw.QLineEdit()
            self.ipField.setPlaceholderText("Enter ip:")
            self.ipField.setMinimumWidth(100)
            self.hostButton.clicked.connect(lambda :self.initWaitingWindowPlayerWindow("Waiting for Players..."))
            self.connectButton.clicked.connect(lambda :self.initWaitingWindowPlayerWindow("Connecting..."))
            self.layout.addWidget(self.hostButton,0,0,1,2)
            self.layout.addWidget(self.connectButton,1,0)
            self.layout.addWidget(self.ipField,1,1)
            
            
            for id in range(self.layout.count()):
                item = self.layout.itemAt(id).widget()
                item.setSizePolicy(qtw.QSizePolicy(qtw.QSizePolicy.Ignored,
                                                qtw.QSizePolicy.Ignored))
                item.setMaximumHeight(100)
            self.show()
            
            
        def cleanWindow(self):
            for id in range(self.layout.count()):
                self.layout.itemAt(id).widget().deleteLater()
                
            
     
            
            
        def initWaitingWindowPlayerWindow(self,text):
            
            self.cleanWindow()
            textLabel = qtw.QLabel(text)
            textLabel.setAlignment(Qt.Qt.AlignCenter)
            self.layout.addWidget(textLabel,0,0)
            
            
            
            
                
       
            
    
        



if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec())