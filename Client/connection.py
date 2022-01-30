import logging
from multiprocessing.sharedctypes import Value
import select
import socket
import threading
from os.path import dirname, exists
from queue import Empty, Queue
import sys
directory = dirname(__file__)


class Communication:
    messageQueue: Queue = Queue()
    timeLimit: int = 15
    connectionStable: bool = True
    forceQuit = False
    def __init__(
        self,
        GUIReference: "MainWindow" = None,
        address: str = "127.0.0.1",
        port: int = 2137,
        isHost: bool = False,
        queue=None,
    ):
        if queue is not None:
            self.messageQueue = queue
        self.address: str = address
        self.port: int = port
        self.isHost: bool = isHost
        self.GUI: "MainWindow" = GUIReference

    def listen(self, s: socket):
        while self.connectionStable:
            try:
                ready_to_read_message, _, _ = select.select([s], [], [], self.timeLimit)
            except ValueError:
                logging.info("connection closed,cant read")
                return 
            if ready_to_read_message:

                msg_size_bytes = self.read_n_bytes(s, 2)
                if msg_size_bytes:
                    try:
                        msg_size = int(msg_size_bytes.decode("UTF-8"))
                    except AttributeError:
                        logging.error("Received unknown message")
                
                if self.connectionStable and msg_size_bytes:
                    message = self.read_n_bytes(s, msg_size).decode("UTF-8")
                    self.handleMessage(Message(message))

            else:
                logging.warning("timed out on select")
                if self.forceQuit:
                    break
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
                    s.close()
                    logging.warning("Connection closed")
                    if self.GUI.QtStack.currentWidget() in (self.GUI.WaitingRoom,self.GUI.GameScene):
                        self.GUI.setErrorScene(
                            "Server closed connection", allowReconnect=True
                        )
                    if self.GUI.forceCancel:
                        self.GUI.forceCancel=True
                    else:
                        self.connectionStable = False

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
        info = Message.fromString(data)
        logging.info(f"Sent message {info.text} with code {info.code}")
        return ret

    def write(self, s: socket):

        # it is blocking, but it blocks in a thread, so it doesnt really matter
        # theoretically it will block until it gets message from queue,
        # then it will block on select, which should respect timeout unlike get

        while self.connectionStable:

            
            try:
                message: str = self.messageQueue.get(block=True,timeout=self.timeLimit)
            except Empty:
                logging.warning("Timed out on write queue")
                self.mysendall(s,str(Message("",Message.REMOVE)).encode("UTF-8"))            
                self.GUI.hideAllLetters(False)
                
                self.GUI.lifeCounter = 0
                self.GUI.setImage()
                self.GUI.setErrorScene("Kicked out due to inactivity")
                s.close()
            
            try:
                _, ready_to_write, _ = select.select([], [s], [], self.timeLimit)
            except ValueError:
                logging.info("connection closed,cant write")
                return 

            if ready_to_write:

                logging.info(f"Sending {message.text} with code: {message.code}")
                self.mysendall(s, (str(message)).encode("UTF-8"))

            else:
                logging.warning("timed out on write Queue")
                self.GUI.cancelConnection()
                self.GUI.setErrorScene("Kicked due to inactivity")
                # TODO: handling timeout + change time limit to 30(?)

    def addTexttoQueue(self, text):
        self.messageQueue.put(text)

    def run(self):
        self.messageQueue.queue.clear()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            self.sock = s
            try:
                s.connect((self.address, self.port))
            except (socket.timeout):
                logging.error("Timeout on establishing connection")
                self.GUI.setErrorScene("Couldn't connect to the server", True)
                return
            except  ConnectionRefusedError:
                logging.error("Connection refused")
                self.GUI.setErrorScene("Couldn't connect to the server", True)
                return
                
            readerThread = threading.Thread(target=self.listen, args=(s,))
            writerThread = threading.Thread(target=self.write, args=(s,))

            readerThread.start()
            writerThread.start()

            readerThread.join()
            writerThread.join()
            logging.info("Communication thread finished")

    def handleMessage(self, msg: "Message") -> None:
        logging.info(
            f"Received Message {'<empty>' if len(msg.text)==0 else msg.text} with code:{msg.code}"
        )

        if msg.code == msg.NEW_PLAYER:
            self.GUI.playersDict[msg.text] = (0, 0)
            # if msg.text.isnumeric():  # received id, need to save it to file
            #     with open(f"{directory}/id.txt", "w+") as f:
            #         f.write(msg.text)


        elif msg.code == msg.NICK_TAKEN:
            self.GUI.setErrorScene(
                """This nick is taken!
                \nPlease connect once more with different name ;-)"""
            )
        elif msg.code == msg.HOST_INIT:

            if msg.text.isnumeric():  # received id, need to save it to file
                # FIXME: Czy host musi zapisywać id? Gra bez hosta chyba powinna sie skończyć
                with open("id.txt", "w+") as f:
                    f.write(msg.text)
            else:
                if msg.text == "NOHOST":
                    self.GUI.setErrorScene("""There is no host in this game""")
                else:
                    self.GUI.setErrorScene(
                        """There is already another host in this game"""
                    )

        elif msg.code == msg.GUESS:
            player, guessed, missed = msg.text.split(":")
            self.GUI.playersDict[player] = (int(guessed), int(missed))
            self.GUI.updateLeaderBoard()

        elif msg.code == msg.WINNER:
            self.GUI.disableAllLetters()
            if msg.text == self.GUI.nickname:
                self.GUI.passwordLabel.setText(
                    " ".join(self.GUI.guessedpassword) + "\n\nYou Won!"
                )
            else:
                self.GUI.passwordLabel.setText(
                    " ".join(self.GUI.guessedpassword) + "\n\nYou Lost! ;-)\n" + f"{msg.text} won the game"
                )
        elif msg.code == msg.RESET:
            self.GUI.goBack(playerisSending=False)
            
        elif msg.code == msg.RECONNECT:

            if msg.text == "sendID":
                if exists(f"{directory}id.txt"):
                    with open(f"{directory}id.txt", "r+") as f:
                        self.id = f.readline()
                    # send id to let server verify if i was connected
                    self.addTexttoQueue(Message(id, msg.RECONNECT))
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

        elif msg.code == msg.PASSWORD:
            self.GUI.updateLeaderBoard()
            self.GUI.setPassword(msg.text)
            self.GUI.hideAllLetters(False)
            self.GUI.disableAllLetters(False)
            self.GUI.QtStack.setCurrentWidget(self.GUI.GameScene)

        elif msg.code == msg.REMOVE:
            if msg.text != "":
                self.GUI.playersDict.pop(msg.text)

        else:  # default case
            self.GUI.setErrorScene("No idea what happened")
            self.connectionStable = False
            # TODO: Handle socket error


class Message:

    ERROR = -1
    HOST_INIT = 0
    NEW_PLAYER = 1
    NICK_TAKEN = 2
    HOST_READY = 3
    PASSWORD = 4
    GUESS = 5
    WINNER = 6
    RESET = 7
    RECONNECT = 8
    REMOVE = 9

    def __init__(self, text: str, code=None):
        if code is not None:
            self.code: int = int(code)
            self.text: str = text

        else:
            self.code = int(text[0])
            self.text = text[1:]
        self.length = str(len(self.text) + 1)  # +1 because of code

    def __str__(self):
        return f"{self.length.zfill(2)}{self.code}{self.text}"

    @staticmethod
    def fromString(string: str):
        data = string[2:]
        code = data[0]
        text = data[1:]
        return Message(text, int(code))


if __name__ == "__main__":
    from main import MainWindow

    pass
