import select
import socket
import threading
from queue import Queue


class Communication:
    messageQueue: Queue[str] = Queue()
    timeLimit: int = 5

    def __init__(self, address: str = '127.0.0.1', port: int = 2137, isHost: bool = False):
        self.address: str = address
        self.port: int = port
        self.isHost: bool = isHost

    def listen(self, s: socket):
        while True:
            ready_to_read, _, _ = select.select([s], [], [], self.timeLimit)
            if ready_to_read:
                buf: bytes = s.recv(5)
                print(buf)
                # handle message
            else:
                print("timed out")
                # TODO: handling timeout + change time limit to 30(?)

    def write(self, s: socket):

        # it is blocking, but it blocks in a thread, so it doesnt really matter
        # theoretically it will block until it gets message from queue,
        # then it will block on select, which should respect timeout unlike get

        while True:
            message: str = self.messageQueue.get(block=True)
            _, ready_to_write, _ = select.select([], [s], [], self.timeLimit)
            if ready_to_write:
                sent = s.send(message.encode("UTF-8"))
            else:
                print("timed out")
                # TODO: handling timeout + change time limit to 30(?)

    def addTexttoQueue(self, text):
        self.messageQueue.put(text)

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.address, self.port))
            readerThread = threading.Thread(target=self.listen, args=(s,))
            writerThread = threading.Thread(target=self.write, args=(s,))

            readerThread.start()
            writerThread.start()

            readerThread.join()
            writerThread.join()



