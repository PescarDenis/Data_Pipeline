from pipeline.services.base_service import BaseService
from pipeline.stages.phase6_packaging import DRMWrapper, ManifestBuilder

class PackagingService(BaseService):
    def execute(self):
        ok = self.run_sequential([DRMWrapper, ManifestBuilder])
        if ok:
            self.mediator.process_event("SUCCESS")
        else:
            self.mediator.process_event("FAILED")
