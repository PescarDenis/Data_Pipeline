from pipeline.services.base_service import BaseService
from pipeline.stages.phase4_audio import SpeechToText, Translator, AIDubber

class TimedTextService(BaseService):
    def execute(self):
        ok = self.run_sequential([SpeechToText])
        if not ok:
            self.mediator.process_event("FAILED")
            return

        ok = self.run_parallel([Translator, AIDubber])
        if ok:
            self.mediator.process_event("SUCCESS")
        else:
            self.mediator.process_event("FAILED")

