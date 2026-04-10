import os
import json
from pipeline.stages.base_task import BaseTask
from pipeline.utils.logger import log

#encrypt executable files
class DRMWrapper(BaseTask):
    def run(self) -> bool:
        self.context.metadata["drm_status"] = {
            "encrypted": True, #determine if the video is ecrypted or not
            "scheme": "cenc",  # encryption type : https://docs.unified-streaming.com/documentation/drm/common-encryption.html key mapping method
            "key_systems": ["widevine","fairplay"] #google and apple keys
            #https://www.vdocipher.com/blog/2020/08/video-encryption-protection/
        }

        log("[DRMWrapper] Stub — Applied encryption to all the videos")
        return True


class ManifestBuilder(BaseTask):
    def run(self) -> bool:
        meta_dir = os.path.join(self.context.output_dir, "metadata")
        os.makedirs(meta_dir, exist_ok=True)
        scenes = self.context.metadata.get("scenes", [])
        scene_path = os.path.join(meta_dir, "scene_analysis.json")
        with open(scene_path, "w", encoding="utf-8") as f:
            json.dump({"scene_count": len(scenes), "scenes": scenes}, f, indent=4)
        log(f"[ManifestBuilder] Saved scene JSON to {scene_path}")

        manifest_data = {
            "id": "movie_101",
            "ingest_checksum": self.context.metadata.get("checksum"),
            "format": self.context.metadata.get("format"),
            "drm": self.context.metadata.get("drm_status"),
            "compliance": {
                "non_safe_scenes": self.context.metadata.get("non_safe_scenes", {}),
                "regional_branding": self.context.metadata.get("regional_branding", {})
            },
            "encoding_profile": {
                "complexity_score": self.context.metadata.get("complexity_score"),
                "crf_used": self.context.metadata.get("crf", 23)
            }
        }

        manifest_path = os.path.join(meta_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=4)
        log(f"[ManifestBuilder] Saved manifest JSON to {manifest_path}")
        return True