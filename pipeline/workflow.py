from enum import Enum, auto
from pipeline.utils.logger import log
from abc import ABC, abstractmethod

class State(Enum):
    IDLE      = 1
    INGESTING = 2
    ANALYSING = 3
    VISUALS   = 4
    AUDIO_TEXT = 5
    COMPLIANCE = 6
    PACKAGING = 7
    DONE      = 8
    FAILED    = 9

class BaseWorkflow(ABC):
    def __init__(self):
        self.state = State.IDLE

    def transition_to(self, new_state: State) -> bool:
        if self._is_valid_transition(new_state):
            self.state = new_state
            return True
        log(f"[Workflow] Invalid transition from {self.state.name} to {new_state.name}")
        return False

    @abstractmethod
    def _is_valid_transition(self, new_state: State) -> bool:
        pass

class StubMovieWorkflow(BaseWorkflow):
    def _is_valid_transition(self, new_state: State) -> bool:
        valid_transitions = {
            State.IDLE: [State.INGESTING, State.FAILED],
            State.INGESTING: [State.ANALYSING, State.FAILED],
            State.ANALYSING: [State.VISUALS, State.FAILED],
            State.VISUALS: [State.AUDIO_TEXT, State.FAILED],
            State.AUDIO_TEXT: [State.COMPLIANCE, State.FAILED],
            State.COMPLIANCE: [State.PACKAGING, State.FAILED],
            State.PACKAGING: [State.DONE, State.FAILED],
            State.DONE: [],
            State.FAILED: []
        }
        return new_state in valid_transitions.get(self.state, [])
