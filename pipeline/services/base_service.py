from abc import ABC, abstractmethod
import concurrent.futures
from pipeline.utils.logger import log

class BaseService(ABC):
    def __init__(self, context):
        self.context = context
        self.mediator = None

    #servicies aren't allowed to orchestrate themselves, add this to still notify the orch when the exec is finished
    def set_mediator(self, mediator):
        self.mediator = mediator

    @abstractmethod
    def execute(self):
            #should execute the underlying tasks and then call self.mediator.process_event('SUCCESS' or 'FAILED')
        pass

    def run_sequential(self, task_classes: list) -> bool:
        for task_class in task_classes:
            task = task_class(self.context)
            if not task.run():
                return False
        return True

    def run_parallel(self, task_classes: list) -> bool:
        results = {}
        with concurrent.futures.ThreadPoolExecutor() as pool:
            futures = {
                pool.submit(task_class(self.context).run): task_class.__name__
                for task_class in task_classes
            }
            for future in concurrent.futures.as_completed(futures):
                name = futures[future]
                try:
                    results[name] = future.result()
                    status = "PARALLEL OK" if results[name] else "FAIL"
                    log(f"[{status}] {name}")
                except Exception as e:
                    log(f"[ERROR] {name}: {e}")
                    results[name] = False
        return all(results.values())
