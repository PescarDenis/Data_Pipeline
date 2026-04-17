from pipeline.services.base_service import BaseService
from pipeline.stages.phase3_visuals import SceneComplexity, Transcoder, SpriteGenerator

class VideoEncodingService(BaseService):
    def execute(self):
        ok = self.run_sequential([SceneComplexity])
        if not ok:
            self.mediator.process_event("FAILED")
            return

        ok = self.run_parallel([Transcoder, SpriteGenerator])
        if ok:
            self.mediator.process_event("SUCCESS")
        else:
            self.mediator.process_event("FAILED")
