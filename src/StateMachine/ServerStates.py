from __future__ import annotations
from StateMachine.StateMachine import ConcreteState


class Idle_State(ConcreteState):

    def action(self):
        pass

class Is_Syn_Received_State(ConcreteState):

    def action(self):
        pass

class Is_Client_Registered_State(ConcreteState):

    def action(self):
        pass

class Req_Config_Start_State(ConcreteState):

    def action(self):
        pass
class Wait_For_Config_State(ConcreteState):

    def action(self):
        pass
class Is_Config_Received_State(ConcreteState):

    def action(self):
        pass
class Is_Timeout_State(ConcreteState):

    def action(self):
        pass

class Retransmitted_Max_Times_State(ConcreteState):

    def action(self):
        pass

class Client_Found_State(ConcreteState):

    def action(self):
        pass

class Wait_For_Final_Ack_State(ConcreteState):

    def action(self):
        pass

class Is_Final_Ack_Received_State(ConcreteState):

    def action(self):
        pass

class Connection_Established_State(ConcreteState):
    def action(self):
        pass
