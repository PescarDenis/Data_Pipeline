import sys
from dataclasses import dataclass, field
from pipeline.utils.logger import log
from pipeline.workflow import State, StubMovieWorkflow
from pipeline.mediator import WorkflowOrchestrator
from pipeline.services.ingest_service import IngestService
from pipeline.services.complexity_analysis_service import ComplexityAnalysisService
from pipeline.services.video_encoding_service import VideoEncodingService
from pipeline.services.timed_text_service import TimedTextService
from pipeline.services.compliance_service import ComplianceService
from pipeline.services.packaging_service import PackagingService

@dataclass
class PipelineContext:
    input_path: str
    output_dir: str
    metadata: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)

class Orchestrator:
    def __init__(self, input_path, output_dir):
        self.context = PipelineContext(input_path=input_path, output_dir=output_dir)
        self.workflow = StubMovieWorkflow()
        self.mediator = WorkflowOrchestrator(self.workflow)
        self.mediator.register_service(State.INGESTING, IngestService(self.context))
        self.mediator.register_service(State.ANALYSING, ComplexityAnalysisService(self.context))
        self.mediator.register_service(State.VISUALS, VideoEncodingService(self.context))
        self.mediator.register_service(State.AUDIO_TEXT, TimedTextService(self.context))
        self.mediator.register_service(State.COMPLIANCE, ComplianceService(self.context))
        self.mediator.register_service(State.PACKAGING, PackagingService(self.context))
        
    def run(self):
        log(f"Starting {self.workflow.__class__.__name__} for {self.context.input_path}...")
        self.mediator.execute_current_state()
        if self.workflow.state == State.DONE:
            log(f"Pipeline finished successfully! All assets saved to ./{self.context.output_dir}/")
        else:
            log(f"Pipeline failed with final state: {self.workflow.state.name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 -m pipeline.orchestrator <video_file>")
        sys.exit(1)

    iinput_path = sys.argv[1]

    orch = Orchestrator(input_path = iinput_path, output_dir="movie_101")
    orch.run()