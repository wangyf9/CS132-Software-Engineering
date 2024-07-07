import time
import zmq
import threading
import sys
import os
import queue


class ZmqServerThread(threading.Thread):
    _port = 27132
    clients_addr=set()

    def __init__(self, server_port:int = None) -> None:
        threading.Thread.__init__(self)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.bindedClient = None
        self._receivedMessage:str = None
        self._messageTimeStamp:int = None # UNIX Time Stamp, should be int
        self._sentTimeStamp:int = None
        self.msgQueue:queue.Queue = queue.Queue()
        self.e1_buffer = []
        self.e2_buffer = []


        if(server_port is not None):
            self.port  = server_port

        print("Start hosting at port:{port}".format(port = self._port))
        self.t = threading.Thread(target=self.listen_queue)
        self.t.start()
        print("Start listening queue")
        self.start()


    @property
    def port(self):
        return self._port
    
    @port.setter
    def port(self,value:int):
        if(value < 0 or value > 65535):
            raise ValueError('score must between 0 ~ 65535!')
        self._port = value

    @property
    def messageTimeStamp(self)->int:
        if(self._messageTimeStamp == None):
            return -1
        else:
            return self._messageTimeStamp

    @messageTimeStamp.setter
    def messageTimeStamp(self,value:int):
        self._messageTimeStamp = value

    @property
    def receivedMessage(self)->str:
        if(self._receivedMessage == None):
            return ""
        else:
            return self._receivedMessage

    @receivedMessage.setter
    def receivedMessage(self,value:str):
        self._receivedMessage = value

    @property
    def sentTimeStamp(self)->int:
        if(self._sentTimeStamp == None):
            return -1
        else:
            return self._sentTimeStamp
        
    @sentTimeStamp.setter
    def sentTimeStamp(self,value:int):
        self._sentTimeStamp = value

    #start listening
    def hosting(self, server_port:int = None)-> None:

        if(server_port is not None):
            self.port  = server_port
        self.socket.bind("tcp://{0}:{1}".format("127.0.0.1", self.port))

        while True:
            [address,contents]=self.socket.recv_multipart()
            address_str = address.decode()
            contents_str = contents.decode()
            self.clients_addr.add(address_str)
            self.messageTimeStamp = int(round(time.time() * 1000)) #UNIX Time Stamp
            self.receivedMessage = contents_str
            if contents_str.endswith("#1"):
                self.e1_buffer.append(contents_str)
            elif contents_str.endswith("#2"):
                self.e2_buffer.append(contents_str)
            print("client:[%s] message:%s Timestamp:%s\n"%(address_str,contents_str,str(self.messageTimeStamp)))

    def listen_queue(self):
        while True:
            if((not self.msgQueue.empty()) and ((int(round(time.time() * 1000)) - self.sentTimeStamp) > 500)):
                self.sentTimeStamp = int(round(time.time() * 1000))
                self.__send_string(self.bindedClient,self.msgQueue.get())

    def send_string(self,address:str,msg:str =""):
        self.msgQueue.put(msg)


    def __send_string(self,address:str,msg:str =""):
        if not self.socket.closed:
            print("Server:[%s] message:%s Timestamp:%s\n"%(str(address),str(msg),str(self.sentTimeStamp)))
            self.socket.send_multipart([address.encode(), msg.encode()]) #send msg to address
        else:
            print("socket is closed,can't send message...")

    #override
    def run(self):
        self.hosting()


