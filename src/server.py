from __future__ import annotations

import socket as s
from abc import ABC, abstractmethod
from typing import override

import logs as l
open('../logs/sv_log.log', 'w').close()



class I_State(ABC):
    @abstractmethod
    def run(self,server:I_StateMachine):
        pass
    @abstractmethod
    def next(self,server:I_StateMachine):
        pass
    
class State_Idle(I_State):
    @override
    def run(self,server:I_StateMachine):
        server.sv_socket = s.socket(s.AF_INET,s.SOCK_DGRAM)
        server.sv_socket.bind(server.sv_addr_pair)
        server.current_state.next(server)
        
        

    @override       
    def next(self,server:I_StateMachine):
        server.current_state = State_Working()
        l.sv_logger.info('State changed: now is working')
        server.current_state.run(server)



class State_Working(I_State):
    @override
    def run(self,server:I_StateMachine):
        data,addr = server.sv_socket.recvfrom(1024)
        l.sv_logger.info("Received message from {}: {}".format(addr,data))
            
    @override        
    def next(self,server:I_StateMachine):
        server.current_state = State_Idle()
        l.sv_logger.info('State changed: now is idle')



    
class I_StateMachine(ABC):
    current_state: I_State
    sv_socket: s.socket
    sv_addr_pair = ('0.0.0.0',8080)
    is_connected: bool = False
    
    @abstractmethod
    def run(self):
        pass
    
class Server(I_StateMachine):
    def __init__(self):
        super().__init__()
        self.current_state = State_Idle()
    
    @override
    def run(self):
        self.current_state.run(self)
        
        
if __name__ == '__main__':
    my_sv = Server()
    my_sv.run()