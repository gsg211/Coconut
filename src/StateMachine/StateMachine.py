from __future__ import annotations

from abc import *


class StateMachine:
    def __init__(self, startState:IState):
        self.state = startState
        self.state.set_context(self)

    def action(self):
        self.state.action()

    def change_state(self, new_state:IState):
        self.state = new_state
        self.state.set_context(self)


class IState(ABC):
    @abstractmethod
    def action(self):
        pass

    @abstractmethod
    def set_context(self, context: StateMachine):
        pass

    @abstractmethod
    def change_state(self, new_state: IState):
        pass

class ConcreteState(IState, ABC):
    def __init__(self):
        self.context = None

    def set_context(self, context:StateMachine):
        self.context=context

    def change_state(self, new_state:IState):
        if self.context is None:
            raise RuntimeError("State has no context assigned.")
        self.context.change_state(new_state)

    @abstractmethod
    def action(self):
        pass

