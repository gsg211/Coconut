import defines as d
import UDP_packet as u
import socket as s

import selectors as sel
import debugging.logs as l
import os

from queue import Queue,Empty
from threading import Thread,Lock

class SocketManager:
    def __init__(self,addr_own:str = d.LOCAL_HOST_ADDR_A,port_own:int = d.DEFAULT_PORT_A,dev_name:str = d.NAME_UNDEFINED):
        self.__selector = sel.DefaultSelector()
        
        self.__send_queue = Queue()
        self.__receive_queue = Queue()
        self.__addr_own = addr_own
        self.__dev_name = dev_name
        self.__port_own = port_own
        self.__reactor_thr = Thread(target=self.__worker,name='REACTOR_THREAD - device {}'.format(self.__dev_name))
        self.__mutex_own = Lock()
        
        
        self.__peer_addr:str = d.LOCAL_HOST_ADDR_A
        self.__peer_port:int = d.DEFAULT_PORT_B
        # default values, can be changed
        
        self.is_init = False
        self.is_started = False
        self.__pipe_fd_rd, self.__pipe_fd_wr= os.pipe()
        
        self.__is_signaled = False
        
        
        
        
        
    def set_peer_data(self,peer_addr:str, peer_port:int):
        self.__peer_addr = peer_addr
        self.__peer_port = peer_port
    
    def __initialize(self):
        if self.is_init:
            return
        
        self.__sck_own = s.socket(s.AF_INET,s.SOCK_DGRAM)

        self.__sck_own.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)

        self.__sck_own.bind((self.__addr_own,self.__port_own))
        self.__sck_own.setblocking(False)


        self.__selector.register(self.__sck_own,sel.EVENT_READ)
        self.__selector.register(self.__pipe_fd_rd,sel.EVENT_READ)
        
        self.is_init = True
        
    def signal_stop(self):
        with self.__mutex_own:
            os.write(self.__pipe_fd_wr,b'a')
            self.__is_signaled = True
       
            
    def q_snd_put(self,data:bytearray):
        was_empty:bool = (self.__send_queue.qsize() == 0)
        self.__send_queue.put(data)
        if was_empty:
            with self.__mutex_own:
                os.write(self.__pipe_fd_wr,b'a') # an event is generated to wake up the io thread
        
    
    def q_rcv_get(self) -> bytearray:
        try:
            elem = self.__receive_queue.get_nowait() ## NOT BLOCKING MUST NOT BLOCK THE STATE MACHINES
        except Empty as e:
            elem = None
        return elem
        
    def start(self):
        self.__initialize()
        self.__reactor_thr.start()
        self.is_started = True
            
        
    def __worker(self):
        while not self.__is_signaled:
            try:
            
                current_send_q_len = self.__send_queue.qsize()

                current_events = self.__selector.get_key(self.__sck_own).events
                if (current_events & sel.EVENT_WRITE) and current_send_q_len == 0:
                    self.__selector.modify(self.__sck_own,sel.EVENT_READ)
                if (not (current_events & sel.EVENT_WRITE)) and current_send_q_len !=0:
                    self.__selector.modify(self.__sck_own,sel.EVENT_READ | sel.EVENT_WRITE)
                
                events = self.__selector.select()
                for key, event in events:
                    
                    if key.fileobj is self.__pipe_fd_rd:
                        os.read(self.__pipe_fd_rd,1) # consume the special event, for the loop to go forward
                        
                    elif key.fileobj is self.__sck_own:
                        if event & sel.EVENT_READ:
                            data = self.__sck_own.recvfrom(d.UDP_Size.PAYLOAD_SZ)
                            if data:
                                self.__receive_queue.put(data)
                        if event & sel.EVENT_WRITE:
                            try:
                                data = self.__send_queue.get_nowait()
                                if data:
                                    self.__sck_own.sendto(data,(self.__peer_addr,self.__peer_port))
                            except Empty as e:
                                l.utils_logger.info("IO thread tried to send from empty queue")
                            
                        
            except Exception:
                self.signal_stop()
                l.utils_logger.info("IO thread failed - unknown reason")
                
        self.__is_signaled = False
        self.__selector.close()
        self.__sck_own.close()
        os.close(self.__pipe_fd_rd)
        os.close(self.__pipe_fd_wr)
                
        
    
        
        

    

