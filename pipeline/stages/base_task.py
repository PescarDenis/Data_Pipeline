from abc import ABC, abstractmethod
class BaseTask(ABC):

    def __init__(self, context):
        self.context = context #the context defines how data is passed during pipeline stages

    def run(self) -> bool: #each task will implement the run method , ret T or F
        pass
