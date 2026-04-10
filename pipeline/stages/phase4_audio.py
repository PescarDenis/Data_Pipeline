import os
import subprocess
from pipeline.stages.base_task import BaseTask
from pipeline.utils.logger import log

#How these run practically in a pipeline :
# SpeechTotext -> sequentially because Translator is dependent on it
# Translator and AiDubber can be run in parallel
class SpeechToText(BaseTask):
    def run(self) -> bool:
        text_dir = os.path.join(self.context.output_dir, "text")
        os.makedirs(text_dir, exist_ok=True)
        transcript_path = os.path.join(text_dir, "source_transcript.txt")
        transcript_content = "Roby Roberto speaks with his BFF Malone"

        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript_content)

        self.context.metadata["source_text"] = transcript_content
        log(f"[SpeechToText] Generated source transcript at {transcript_path}")

        return True


class Translator(BaseTask):
    def run(self) -> bool:
        text_dir = os.path.join(self.context.output_dir, "text")
        os.makedirs(text_dir, exist_ok=True)
        trans_path = os.path.join(text_dir, "ro_translation.txt")
        translated_content = "Roby Roberto vorbeste cu BFFu Malone"

        with open(trans_path, "w", encoding="utf-8") as f:
            f.write(translated_content)

        self.context.metadata["ro_translation"] = translated_content
        log(f"[Translator] Generated Romanian translation at {trans_path}")

        return True


class AIDubber(BaseTask):
    def run(self) -> bool:
        audio_dir = os.path.join(self.context.output_dir, "audio")
        os.makedirs(audio_dir, exist_ok=True)
        dub_path = os.path.join(audio_dir, "ro_dub_synthetic.aac")

        #https://superuser.com/questions/724391/how-to-generate-a-sine-wave-with-ffmpeg
        cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", "sine=frequency=1000:duration=5",
            "-c:a", "aac",  # same audio encoding as the file
            "-y",  # added this, because i want to overwrite the file and not crash the program when i run the pipeline multiple times
            dub_path
        ]

        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # add the DEVNULL because
            #we don t want any outputs from the ffmpeg command in the terminal
            log(f"[AIDubber] Generated playable synthetic audio dub at {dub_path}")
            return True
        except Exception as e:
            log(f"[AIDubber] Failed to generate audio: {e}")
            return False