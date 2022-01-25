import logging
import select
import socket
import threading
from os.path import exists
from queue import Queue

import PyQt5.QtWidgets as qtw


class Communication:
    messageQueue: Queue = Queue()
    timeLimit: int = 15
    connectionStable: bool = True

    def __init__(
        self,
        GUIReference: qtw.QDialog = None,
        address: str = "127.0.0.1",
        port: int = 2137,
        isHost: bool = False,
    ):
        self.address: str = address
        self.port: int = port
        self.isHost: bool = isHost
        self.GUI = GUIReference

    def listen(self, s: socket):
        while self.connectionStable:

            ready_to_read_message, _, _ = select.select([s], [], [], self.timeLimit)

            if ready_to_read_message:

                msg_size_bytes = self.read_n_bytes(s, 2)
                if msg_size_bytes:
                    msg_size = int(msg_size_bytes.decode("UTF-8"))


                if self.connectionStable:
                    message = self.read_n_bytes(s, msg_size).decode("UTF-8")
                    self.handleMessage(Message(message))

            else:
                logging.warning("timed out on select")
                # TODO: handling timeout + change time limit to 30(?)

    def read_n_bytes(self, s: socket, bytes_count: int) -> bytes:
        chunks = []
        bytes_recd = 0
        while bytes_recd < bytes_count:
            try:
                chunk = s.recv(bytes_count - bytes_recd)
                chunks.append(chunk)
                bytes_recd += len(chunk)
                logging.info(f"Message chunks: {chunks} incoming chunk: {chunk}")
                self.GUI.QtStack.setWindowTitle("Hangman!")

                if chunk == b"":
                    self.connectionStable = False
                    self.GUI.setErrorScene(
                        "Server closed connection", allowReconnect=True
                    )
                    return None
            except socket.timeout as e:

                logging.error("Timed out on socket read between chunks")
                self.GUI.QtStack.setWindowTitle("Warning, connection unstable!")

            except socket.error as e:
                self.connectionStable = False  # jakis bardzo zły błąd
                logging.error(e)
                break

        return b"".join(chunks)

    def mysendall(self, s: socket, data: str):
        ret = 0
        while ret < len(data):
            try:
                sent = s.send(data[ret:])
                ret += sent
                self.GUI.QtStack.setWindowTitle("Hangman!")

            except socket.timeout as e:
                logging.warning("socket timeout on send")
                self.GUI.QtStack.setWindowTitle("Warning, connection unstable!")

                # FIXME: HANDLE TIMEOUT
            except socket.error as e:
                logging.error(e)
                self.conectionstable = False
                break
        
        return ret

    def write(self, s: socket):

        # it is blocking, but it blocks in a thread, so it doesnt really matter
        # theoretically it will block until it gets message from queue,
        # then it will block on select, which should respect timeout unlike get

        while self.connectionStable:
            message: str = self.messageQueue.get(block=True)
            _, ready_to_write, _ = select.select([], [s], [], self.timeLimit)

            if ready_to_write:
               
                logging.info(f"Sending {message.text} with code: {message.code}")
                self.mysendall(s, (str(message)).encode("UTF-8"))
                
            else:
                logging.warning("timed out on write Queue")
                # TODO: handling timeout + change time limit to 30(?)

    def addTexttoQueue(self, text):
        self.messageQueue.put(text)

    def getMessage(self) -> "Message":
        try:
            msg = self.readQueue.get(block=True, timeout=self.timeLimit)
        except BaseException:
            msg = "9##!"
        return msg

    def run(self):
        self.messageQueue.queue.clear()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)

            try:
                s.connect((self.address, self.port))
            except (socket.timeout, ConnectionRefusedError):
                logging.error("Timeout on establishing connection")
                self.GUI.setErrorScene("Couldn't connect to the server", True)
                return
            readerThread = threading.Thread(target=self.listen, args=(s,))
            writerThread = threading.Thread(target=self.write, args=(s,))

            readerThread.start()
            writerThread.start()

            readerThread.join()
            writerThread.join()

    def handleMessage(self, msg: "Message") -> None:
        logging.info(f"Received Message {'<empty>' if len(msg.text)==0 else msg.text} with code:{msg.code}")
        
        if msg.code == msg.new_player:
            if msg.text.isnumeric():  # received id, need to save it to file
                with open("id.txt", "w+") as f:
                    f.write(msg.text)
            else:
                self.GUI.setErrorScene(
                    """This nick is taken!
                    \nPlease connect once more with different name ;-)"""
                )

        elif msg.code == msg.ready_code:
            self.GUI.QtStack.setCurrentWidget(self.GUI.GameScene)

        elif msg.code == msg.new_host:

            if msg.text.isnumeric():  # received id, need to save it to file
                self.GUI.QtStack.setCurrentWidget(self.GUI.GameScene)

                # FIXME: Czy host musi zapisywać id? Gra bez hosta chyba powinna sie skończyć
                # with open("id.txt", "w+") as f:
                #     f.write(msg.text)
            else:
                self.GUI.setErrorScene(
                    """This nick is taken!
                    \nPlease connect once more with different name ;-)"""
                )

        elif msg.code == msg.guessed_letter:
            player, guessed, missed = msg.text.split(":")
            self.GUI.playersDict[player] = f"{guessed}/{missed}"
            self.GUI.updateLeaderBoard()

        elif msg.code == msg.winner_code:
            self.GUI.disableAllLetters()
            if msg.text == self.GUI.nickname:
                self.GUI.passwordLabel.setText(
                        " ".join(self.GUI.guessedpassword) + "\n\nYou Won!"
                    )
            else:
                self.GUI.passwordLabel.setText(
                    " ".join(self.GUI.guessedpassword) + "\n\nYou Lost! ;-)"
                )
                
                
                
            pass

        elif msg.code == msg.reconnect_code:

            if msg.text == "sendID":
                if exists("id.txt"):
                    with open("id.txt", "r+") as f:
                        self.id = f.readline()
                    # send id to let server verify if i was connected
                    self.addTexttoQueue(Message(id, msg.reconnect_code))
                else:  # cant find id file
                    self.GUI.setErrorScene(
                        "You weren't playing in this game\n Please wait for the game to end"
                    )

            elif msg.text == "valid":
                self.GUI.QtStack.setCurrentWidget(self.GUI.GameScene)

            elif msg.text == "invalid":
                self.GUI.setErrorScene(
                    """Someone else was playing under this nickname,
                        \nEnter your nickname or wait for the game to end"""
                )
            else:
                logging.error("Unknown Message Code")

        elif msg.code == msg.new_password:
            self.GUI.setPassword(msg.text)

        else:  # default case
            self.GUI.setErrorScene("No idea what happened")
            self.connectionStable = False
            # TODO: Handle socket error


class Message:
    # TODO: ZMIENIC NA ZNAKI
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
        self.length = str(len(self.text) + 1)  # +1 because of code

    def __str__(self):
        return f"{self.length.zfill(2)}{self.code}{self.text}"
    @staticmethod
    def fromString(string:str):
        data = string[2:]
        code = data[0]
        text = data[1:]
        return Message(text,int(code))
