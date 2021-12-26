import socket 
import time
import threading
from queue import Queue


HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 2137       # Port to listen on (non-privileged ports are > 1023)
import select

    
class Communication:
    messageQueue = Queue()
    timeLimit = 5
    
    def __init__(self,address=HOST,port=PORT,isHost=0):
        self.address = address
        self.port = port
        self.isHost = isHost
        
        
    def listen(self,s):
        print(s)
        while True:
                ready_to_read, _,_=  select.select( [s],[],[],self.timeLimit)
                if ready_to_read:
                    buf = s.recv(1024)
                    print(buf)
                else:
                    print("timed out")
                    
                    
    def write(self,s):
        while True:
            s.send(self.messageQueue.get(block=True).encode("UTF-8"))
                

    def addLettertoQueue(self,letter):
        self.messageQueue.put(letter)
        
    
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print("socket jest")
            s.connect((self.address,self.port))
            t1 = threading.Thread(target = self.listen,args = (s,))
            t2 = threading.Thread(target = self.write, args = (s,))
            t1.start()
            t2.start()
        
            t1.join()
        # t2.join()
        
        
        
        
        
        
        
            
                    
        
        


























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
