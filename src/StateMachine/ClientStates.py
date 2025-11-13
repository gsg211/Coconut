from __future__ import annotations
from StateMachine.StateMachine import ConcreteState


class Idle_State(ConcreteState):

    def action(self):
        pass
class Send_Sync_Init_State(ConcreteState):

    def action(self):
        pass

class Sync_Init_Wait_State(ConcreteState):

    def action(self):
        pass


class Send_Config_State(ConcreteState):

    def action(self):
        pass


class Ack_Config_Wait_State(ConcreteState):

    def action(self):
        pass


class Send_Final_Ack_State(ConcreteState):

    def action(self):
        pass


class Receive_Final_SynAck_State(ConcreteState):

    def action(self):
        pass


class Connection_Established_State(ConcreteState):

    def action(self):
        pass
