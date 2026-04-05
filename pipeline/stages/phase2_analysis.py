from pipeline.stages.base_task import BaseTask
from pipeline.utils.logger import log

class IntroOutroDetector(BaseTask):
    def run(self) -> bool:
        self.context.metadata["intro_end_seconds"] = 15.0 #just put a stub value as requested
        log(f"[IntroOutroDetector] Stub — intro ends at {self.context.metadata["intro_end_seconds"]}")
        return True

class CreditRoller(BaseTask):
    def run(self) -> bool:
        self.context.metadata["credits_start_seconds"] = 200.0
        log(f"[CreditRoller] Stub — credits start at {self.context.metadata["credits_start_seconds"]}")
        return True

class SceneIndexer(BaseTask):
    def run(self) -> bool:
        scenes = [
            {"segment_id": 0, "start_time": 20.0,  "label": "establishing_shot"},
            {"segment_id": 1, "start_time": 40.0, "label": "dialogue"},
            {"segment_id": 2, "start_time": 90.0, "label": "action"},
        ]
        self.context.metadata["scene_count"] = len(scenes)
        self.context.metadata["scenes"] = scenes
        log(f"[SceneIndexer] Stub — {len(scenes)} scenes classified")
        return True