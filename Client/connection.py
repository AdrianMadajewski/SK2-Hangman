import select
import socket
import threading
from os.path import exists
from queue import Queue

import PyQt5.QtCore as Qt
import PyQt5.QtWidgets as qtw


class Communication:
    messageQueue: Queue = Queue()
    timeLimit: int = 15
    connectionStable: bool = True

    def __init__(self, GUIReference=None, address: str = '127.0.0.1', port: int = 2137, isHost: bool = False):
        self.address: str = address
        self.port: int = port
        self.isHost: bool = isHost
        self.GUI = GUIReference

    def listen(self, s: socket):
        while self.connectionStable:
            ready_to_read, _, _ = select.select([s], [], [], self.timeLimit)
            if ready_to_read:
                try:
                    msg_size = int(s.recv(2, socket.MSG_WAITALL).decode("UTF-8"))

                    message = s.recv(msg_size, socket.MSG_WAITALL).decode("UTF-8")
                    print(message)
                    self.handleMessage(Message(message))
                except ValueError:
                    self.GUI.setErrorScene("Connection closed :(",True)
                    self.connectionStable = False
                    

                


            else:
                print("timedd out")
                # TODO: handling timeout + change time limit to 30(?)

    def write(self, s: socket):

        # it is blocking, but it blocks in a thread, so it doesnt really matter
        # theoretically it will block until it gets message from queue,
        # then it will block on select, which should respect timeout unlike get

        while self.connectionStable:
            message: str = self.messageQueue.get(block=True)
            _, ready_to_write, _ = select.select([], [s], [], self.timeLimit)
            if ready_to_write:
                sent = s.send((str(message)).encode("UTF-8"))
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
            try:
                s.connect((self.address, self.port))
            except ConnectionRefusedError:
                self.GUI.setErrorScene("Couldn't connect to the server",True)
                return
            readerThread = threading.Thread(target=self.listen, args=(s,))
            writerThread = threading.Thread(target=self.write, args=(s,))

            readerThread.start()
            writerThread.start()

            readerThread.join()
            writerThread.join()

    def handleMessage(self, msg: "Message") -> None:
        
        if msg.code ==msg.new_player:
            print(msg.text,msg.code)
            if msg.text.isnumeric():  # received id, need to save it to file
                with open("id.txt", "w+") as f:
                    f.write(msg.text)
            else:
                self.GUI.setErrorScene(
                    '''This nick is taken!
                    \nPlease connect once more with different name ;-)''')
        elif msg.code ==msg.ready_code:
            self.GUI.QtStack.setCurrentWidget(self.GUI.GameScene)
            
            
        elif msg.code == msg.new_host:
            
            if msg.text.isnumeric():  # received id, need to save it to file
                self.GUI.QtStack.setCurrentWidget(self.GUI.GameScene)
                
                #FIXME: Czy host musi zapisywać id? Gra bez hosta chyba powinna sie skończyć
                # with open("id.txt", "w+") as f:
                #     f.write(msg.text)
            else:
                self.GUI.setErrorScene(
                    '''This nick is taken!
                    \nPlease connect once more with different name ;-)''')
        
            


        elif msg.code ==msg.guessed_letter:
            player, score = msg.text.split('SCORE')
            self.GUI.playersDict[player] = score
            self.GUI.updateLeaderBoard()

        elif msg.code ==msg.winner_code:
            #TODO: 
            pass

        elif msg.code ==msg.reconnect_code:
            
                if msg.text == "sendID":
                    if exists("id.txt"):
                        with open("id.txt", "r+") as f:
                            id = f.readline()
                        # send id to let server verify if i was connected
                        self.addTexttoQueue(Message(id, msg.reconnect_code))
                    else:  # cant find id file
                        self.GUI.setErrorScene(
                            "You weren't playing in this game\n Please wait for the game to end")

                elif msg.text == "valid":
                    self.GUI.QtStack.setCurrentWidget(self.GUI.GameScene)

                elif msg.text == "invalid":
                    self.GUI.setErrorScene(
                        '''Someone else was playing under this nickname,
                        \nEnter your nickname or wait for the game to end''')
                else:
                    print("No idea what happened")

        elif msg.code == msg.new_password:
            self.GUI.setPassword(msg.text)

        else:  # default case
            self.GUI.setErrorScene("No idea what happened")
            self.connectionStable = False
            # TODO: Handle socket error


class Message:
    new_host = 1
    new_player = 2
    ready_code = 3
    guessed_letter = 4
    winner_code = 5
    reconnect_code = 6
    new_password = 7
    
    

    def __init__(self, text: str, code=None):
        if code:
            self.code: int = int(code)
            self.text: str = text

        else:
            self.code = int(text[0])
            self.text = text[1:]
            print(text[1:-1])
        self.length = str(len(self.text)+1)  # +1 because of code 

    def __str__(self):
        return f"{self.length.zfill(2)}{self.code}{self.text}"

