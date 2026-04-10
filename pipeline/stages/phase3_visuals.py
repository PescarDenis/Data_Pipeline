import concurrent.futures
import subprocess
import json
from pipeline.stages.base_task import BaseTask
from pipeline.utils.logger import log
from PIL import Image
import os

class SceneComplexity(BaseTask):
    def run(self) -> bool:
        cmd = [
            "ffprobe",
            "-v", "quiet",          # suppress all warnings from ffprobe itself
            "-print_format", "json", # output the result as JSON so we can parse it
            "-show_streams",         # include stream info (video, audio, bitrate, codec)
            "-i",self.context.input_path  # the input file
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(result.stdout)

            # a video file can have multiple streams (video, audio, subtitles)
            # we only care about the video stream for complexity analysis
            for stream in data.get("streams", []):
                if stream.get("codec_type") == "video":
                    # bit_rate is in bits per second — default to 2Mbps if missing
                    bitrate = int(stream.get("bit_rate", 2_000_000))
                    # normalise to a 0.0–1.0 scale where 8Mbps = maximum complexity
                    complexity = round(min(bitrate / 8_000_000, 1.0), 2)
                    # CRF (Constant Rate Factor) controls quality vs file size
                    # range 18–28: lower = better quality, larger file
                    # high complexity video needs lower CRF to preserve detail
                    crf = int(28 - complexity * 10)
                    self.context.metadata["complexity_score"] = complexity
                    self.context.metadata["crf"] = crf
                    log(f"[SceneComplexity] bitrate={bitrate} complexity={complexity} crf={crf}")
                    return True

            # no video stream found in the file
            self.context.metadata["crf"] = 23
            log("[SceneComplexity] No video stream, using default crf=23")
            return True

        except Exception as e:
            # pipeline continues with a default CRF value
            self.context.metadata["crf"] = 23
            log(f"[SceneComplexity] Failed: {e}, using default crf=23")
            return True


class Transcoder(BaseTask):
    # (resolution label, ffmpeg scale value)
    profiles = [
        ("4k",    "3840x2160"),
        ("1080p", "1920x1080"),
        ("720p",  "1280x720"),
    ]
    # (folder name, ffmpeg codec, file extension)
    formats = [
        ("h264", "libx264",    "mp4"),
        ("vp9",  "libvpx-vp9", "webm"),
        ("hevc", "libx265",    "mkv"),
    ]

    def run(self) -> bool:
        crf = self.context.metadata.get("crf", 23)
        output_root = os.path.join(self.context.output_dir, "video")
        os.makedirs(output_root, exist_ok=True)

        commands_to_run = []

        # 1. Build the list of commands
        for fmt_name, codec, ext in self.formats:
            fmt_dir = os.path.join(output_root, fmt_name)
            os.makedirs(fmt_dir, exist_ok=True)
            for label, resolution in self.profiles:
                output_file = os.path.join(fmt_dir, f"{label}_{fmt_name}.{ext}")
                cmd = self._build_cmd(codec, resolution, crf, output_file)
                commands_to_run.append((f"{label}_{fmt_name}.{ext}", cmd))

        # 2. Execute them in parallel
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Submit all ffmpeg jobs to the pool
                futures = {
                    executor.submit(subprocess.run, cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL): name
                    for name, cmd in commands_to_run
                }

                # Wait for them to finish and log
                for future in concurrent.futures.as_completed(futures):
                    name = futures[future]
                    future.result()  # Will raise an exception if the subprocess failed
                    log(f"[Transcoder] -> Created {name}")

            return True

        except Exception as e:
            log(f"[Transcoder] Failed: {e}")
            return False

    def _build_cmd(self, codec, resolution, crf, output_file):
        cmd = [
            "ffmpeg",
            "-hide_banner",          # suppress thr. Since Scene ffmpeg version/config header
            "-i", self.context.input_path,  # -i input file
            "-vf", f"scale={resolution}",   # resize to target resolution
            "-c:v", codec,           # video codec to encode with
            "-crf", str(crf),        # quality level computed by SceneComplexity
        ]

        # preset controls encoding speed
        # fast  quicker encode, slightly larger file
        # only h264 and hevc support -preset, vp9 does not
        if codec in ("libx264", "libx265"):
            cmd += ["-preset", "fast"]

        # vp9 extra flags:
        # b:v 0 enables CRF mode
        # deadline realtime fastest encoding speed
        # use 8 threads
        if codec == "libvpx-vp9":
            cmd += ["-b:v", "0", "-deadline", "realtime", "-cpu-used", "8"]
        cmd += ["-y", output_file]  # -y overwrite output file if it already exists
        return cmd


class SpriteGenerator(BaseTask):
    def run(self) -> bool:
        thumbs_dir = os.path.join(self.context.output_dir, "images", "thumbnails")
        os.makedirs(thumbs_dir, exist_ok=True)

        try:
            cmd = [
                "ffmpeg",
                "-hide_banner",
                "-i", self.context.input_path,
                # fps=1/10  extract one frame every 10 seconds
                # scale=160:-1 →resize to 160px wide, height calculated automatically to preserve the original aspect ratio (-1)
                "-vf", "fps=1/10,scale=160:-1",
                "-y", f"{thumbs_dir}/thumb_%03d.jpg"
            ]
            subprocess.run(cmd,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            log("[SpriteGenerator] Thumbnails extracted")
            self._create_sprite(thumbs_dir)
            return True

        except Exception as e:
            log(f"[SpriteGenerator] Failed: {e}")
            return False

    def _create_sprite(self, thumbs_dir):
        images = sorted([os.path.join(thumbs_dir, f)for f in os.listdir(thumbs_dir)if f.endswith(".jpg")])

        if not images:
            log("[SpriteGenerator] No thumbnails found")
            return

        thumbs = [Image.open(img) for img in images]
        width, height = thumbs[0].size

        # arrange thumbnails in a grid — 5 columns, as many rows as needed
        cols = 5
        rows = (len(thumbs) + cols - 1) // cols  # ceiling division
        sprite = Image.new("RGB", (cols * width, rows * height))

        # paste each thumbnail into its correct position in the grid
        for i, img in enumerate(thumbs):
            x = (i % cols) * width   # column position in pixels
            y = (i // cols) * height  # row position in pixels
            sprite.paste(img, (x, y))

        sprite_path = os.path.join(self.context.output_dir, "images", "sprite_map.jpg")
        sprite.save(sprite_path)
        log(f"[SpriteGenerator] Sprite map saved to: {sprite_path}")