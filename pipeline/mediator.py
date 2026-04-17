from abc import ABC, abstractmethod
from pipeline.workflow import BaseWorkflow, State
from pipeline.utils.logger import log

class Mediator(ABC):
    @abstractmethod
    def process_event(self, event: str):
        pass

class WorkflowOrchestrator(Mediator):
    def __init__(self, workflow: BaseWorkflow):
        self.workflow = workflow
        self.services = {}

    def register_service(self, state: State, service):
        self.services[state] = service
        #allows each service to hold a reference back to the Orchestrator so it can notify it when finished
        service.set_mediator(self)

    def execute_current_state(self):
        current_state = self.workflow.state
        if current_state in [State.DONE, State.FAILED, State.IDLE]:
            if current_state == State.IDLE:
                self._transition_and_execute(State.INGESTING)
            return

        service = self.services.get(current_state)
        if service :
            log(f"[Mediator] Delegating to {service.__class__.__name__}")
            service.execute()
        else:
            log(f"[Mediator] No service registered for state {current_state.name}. Failing.")
            self.workflow.transition_to(State.FAILED)

    def process_event(self, event: str):
        log(f"[Mediator] Received notification from {self.__class__.__name__}: {event}")
        current_state = self.workflow.state

        if event == "FAILED":
            self.workflow.transition_to(State.FAILED)
            return

        if event == "SUCCESS":
            next_state_mapping = {
                State.INGESTING: State.ANALYSING,
                State.ANALYSING: State.VISUALS,
                State.VISUALS: State.AUDIO_TEXT,
                State.AUDIO_TEXT: State.COMPLIANCE,
                State.COMPLIANCE: State.PACKAGING,
                State.PACKAGING: State.DONE,
            }

            next_state = next_state_mapping.get(current_state, State.DONE)
            self._transition_and_execute(next_state)

    def _transition_and_execute(self, new_state: State):
        if self.workflow.transition_to(new_state):
            self.execute_current_state()
        else:
            self.workflow.transition_to(State.FAILED)
