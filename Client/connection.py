import socket 
import threading
from queue import Queue
import select

class Communication:
    messageQueue: Queue[str] = Queue()
    timeLimit = 5
    
    def __init__(self,address='127.0.0.1' ,port=2137,isHost=0):
        self.address = address
        self.port = port
        self.isHost = isHost
        
        
    def listen(self,s:socket):
        while True:
                ready_to_read, _,_=  select.select( [s],[],[],self.timeLimit)
                if ready_to_read:
                    buf: bytes = s.recv(1024)
                    print(buf)
                else:
                    print("timed out")
                    #TODO: handling timeout + change time limit to 30(?)
                    
                    
    def write(self,s:socket):
        #it is blocking, but it blocks in a thread, so it doesnt really matter
        
        while True:
            s.send(self.messageQueue.get(block=True).encode("UTF-8"))
                

    def addTexttoQueue(self,text):
        self.messageQueue.put(text)
        
    
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.address,self.port))
            readerThread = threading.Thread(target = self.listen,args = (s,))
            writerThread = threading.Thread(target = self.write, args = (s,))
            
            readerThread.start()
            writerThread.start()
        
            readerThread.join()
            writerThread.join()
        
        
        
        
        
        
        
            
                    
        
        


























#class Communication:
#     messageQueue = []
#     timeLimit = 10
    
#     def __init__(self,address=HOST,port=PORT,isHost=0):
#         self.address = address
#         self.port = port
#         self.isHost = isHost
        
        
#     def listen(self):
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#             s.setblocking(False)
#             s.connect((HOST, PORT))
#             while True:
#                 print(self.messageQueue)
#                 if self.messageQueue != []:
#                     s.sendall(self.messageQueue.pop().encode("UTF-8"))
#                 data = s.recv(1024)
#                 self.refreshTimer()
#                 if data!='#':
#                     print(data)
                
                
#     def timer(self,thread):
#         self.endTime = time.time()+self.timeLimit
#         while time.time()<self.endTime:
#             time.sleep(1)
#         return thread.kill()
    
#     def refreshTimer(self):
#         self.endTime = time.time()+self.timeLimit
        
#     def run(self):
#         p1 = multiprocessing.Process(target = self.listen)
#         p2 = multiprocessing.Process(target = self.timer,args = (p1,))
#         p1.start()
#         p2.start()
        

# com = Communication(HOST,PORT,0)
# com.run()
