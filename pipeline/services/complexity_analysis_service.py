from pipeline.services.base_service import BaseService
from pipeline.stages.phase2_analysis import IntroOutroDetector, CreditRoller, SceneIndexer

class ComplexityAnalysisService(BaseService):
    def execute(self):
        ok = self.run_parallel([IntroOutroDetector, CreditRoller, SceneIndexer])
        if ok:
            self.mediator.process_event("SUCCESS")
        else:
            self.mediator.process_event("FAILED")
