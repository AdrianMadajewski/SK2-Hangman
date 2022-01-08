import select
import socket
import sys
import threading
from enum import Enum
from queue import Queue
import PyQt5.QtCore as Qt
import PyQt5.QtWidgets as qtw

import sys
import threading
import socket
import PyQt5.QtCore as Qt
import PyQt5.QtWidgets as qtw
from PyQt5.QtGui import QIcon, QPixmap
from FlowLayout import FlowLayout
from enum import Enum
from typing import Type


class Communication:
    messageQueue: Queue = Queue()
    timeLimit: int = 15
    connectionStable:bool = True
    def __init__(self, GUIReference=None, address: str = '127.0.0.1', port: int = 2137, isHost: bool = False):
        self.address: str = address
        self.port: int = port
        self.isHost: bool = isHost
        self.GUI = GUIReference

    def listen(self, s: socket):
        while self.connectionStable:
            ready_to_read, _, _ = select.select([s], [], [], self.timeLimit)
            if ready_to_read:
                buf: bytes = s.recv(500)
                buf = buf[:-1].decode("utf-8")
                self.handleMessage(Message(buf))
                # handle message
                

            else:
                print("timed out")
                # TODO: handling timeout + change time limit to 30(?)

    def write(self, s: socket):

        # it is blocking, but it blocks in a thread, so it doesnt really matter
        # theoretically it will block until it gets message from queue,
        # then it will block on select, which should respect timeout unlike get

        while self.connectionStable:
            message: str = self.messageQueue.get(block=True)
            _, ready_to_write, _ = select.select([], [s], [], self.timeLimit)
            if ready_to_write:
                sent = s.send((str(message)+"\n").encode("UTF-8"))
            else:
                print("timed out")
                # TODO: handling timeout + change time limit to 30(?)

    def addTexttoQueue(self, text):
        self.messageQueue.put(text)

    def getMessage(self) -> "Message":
        try:
            msg = self.readQueue.get(block=True, timeout=self.timeLimit)
        except:
            msg = "9##!"
        return msg

    def run(self):
        self.messageQueue.queue.clear()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.address, self.port))
            readerThread = threading.Thread(target=self.listen, args=(s,))
            writerThread = threading.Thread(target=self.write, args=(s,))

            readerThread.start()
            writerThread.start()

            readerThread.join()
            writerThread.join()

    def handleMessage(self, msg: "Message") -> None:
        print(msg.code, type(msg.code))
        if msg.code == 1:
            if msg.text == "free":
                self.GUI.QtStack.setCurrentWidget(self.GUI.GameScene)
            elif msg.text == "taken":
                self.GUI.WaitingRoom.findChild(qtw.QLabel).setText(
                    '''This nick is taken!
                    \nPlease connect once more with different name ;-)''')
            else:
                print("something broke :( CODE 1")

        elif msg.code == 2:
            player,score = msg.text.split('SCORE')
            self.GUI.playersDict[player] = score
            self.GUI.updateLeaderBoard()
            pass

        elif msg.code == 3:
            pass

        elif msg.code == 4:
            pass

        else:
            self.GUI.setErrorScene()
            self.connectionStable=False
            #TODO: Handle socket error
            


class Message:

    def __init__(self, text: str, code=None):
        if code:
            self.code: int = int(code)
            self.text: str = text

        else:
            if text and text[0].isnumeric() and text[2:-2].isalnum():
                self.code = int(text[0])
                self.text = text[2:-2]
            else:
                print(text)
                self.code = 9
                self.text = ""

    def __str__(self):
        return f"{self.code}#{self.text}#!"
