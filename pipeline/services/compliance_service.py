from pipeline.services.base_service import BaseService
from pipeline.stages.phase5_compliance import SafetyScanner, RegionalBranding

class ComplianceService(BaseService):
    def execute(self):
        ok = self.run_parallel([SafetyScanner, RegionalBranding])
        if ok:
            self.mediator.process_event("SUCCESS")
        else:
            self.mediator.process_event("FAILED")
