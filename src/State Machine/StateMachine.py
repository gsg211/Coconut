from abc import *


class StateMachine:
    def __init__(self, startState):
        self.state = startState

    def action(self):
        self.state.action()

    def changeState(self, newState):
        self.state = newState

class IState(ABC):
    @abstractmethod
    def action(self):
        pass


class State(IState, ABC):
    def __init__(self, stateMachine: StateMachine):
        self.context = stateMachine

    def changeState(self,newState):
        self.context.changeState(newState)



