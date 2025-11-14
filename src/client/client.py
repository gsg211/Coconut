from __future__ import annotations

import socket as s
from abc import ABC, abstractmethod
from typing import override

import debugging.logs as l
open('../logs/cl_log.log', 'w').close()


class I_State(ABC):
    @abstractmethod
    def run(self,client:I_StateMachine):
        pass
    @abstractmethod
    def next(self,client:I_StateMachine):
        pass

class State_Working(I_State):
    @override
    def run(self,client:I_StateMachine):
        try:
            client.src_socket.sendto(b'HELLO',client.dst_socket)
        except Exception as e:
            l.cl_logger.info(e)
            
    @override        
    def next(self,client:I_StateMachine):
        client.current_state = State_Idle()
        l.cl_logger.info('State changed: now is idle')

class State_Idle(I_State):
    @override
    def run(self,client:I_StateMachine):
        client.src_socket = s.socket(s.AF_INET,s.SOCK_DGRAM)
        client.current_state.next(client)

    @override       
    def next(self,client:I_StateMachine):
        client.current_state = State_Working()
        l.cl_logger.info('State changed: now is working')
        client.current_state.run(client)

class I_StateMachine(ABC):
    current_state: I_State
    src_socket: s.socket
    dst_socket = ('127.0.0.1',8080)
    is_connected: bool = False
    
    @abstractmethod
    def run(self):
        pass
    
class Client(I_StateMachine):
    def __init__(self):
        super().__init__()
        self.current_state = State_Idle()
    
    @override
    def run(self):
        self.current_state.run(self)
         

