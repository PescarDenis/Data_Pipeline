from pipeline.services.base_service import BaseService
from pipeline.stages.phase1_ingest import IntegrityCheck, FormatValidator

class IngestService(BaseService):
    def execute(self):
        ok = self.run_sequential([IntegrityCheck, FormatValidator])
        if ok:
            self.mediator.process_event("SUCCESS")
        else:
            self.mediator.process_event("FAILED")
