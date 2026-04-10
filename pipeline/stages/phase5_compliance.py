from pipeline.stages.base_task import BaseTask
from pipeline.utils.logger import log

#checks the scenes if there is some scence that needs special atention, like violence or whatever scene is in that movie
class SafetyScanner(BaseTask):
    def run(self) -> bool:
        # grab the scenes that were indexed back in analysis
        scenes = self.context.metadata.get("scenes", [])
        # we will flag any scene labeled "action" as needing a blur
        non_safe_scenes = {} # scenes that will need to apply the blur or some action
        flagged_scenes= []  # Keep track of what we flag for the logs
        for scene in scenes:
            if scene.get("label") == "action":
                non_safe_scenes[scene["segment_id"]] = {
                    "action": "blur",
                    "reason": "Violence",
                    "start_time": scene["start_time"]
                }
                flagged_scenes.append(str(scene["segment_id"]))

        self.context.metadata["non_safe_scenes"] = non_safe_scenes
        if flagged_scenes:
            segments_str = ", ".join(flagged_scenes) # so i will have them as a single string and not multiple strings
            log(f"[SafetyScanner] Action: Blurring segment(s) [{segments_str}] due to Violence.")
        else:
            log("[SafetyScanner] Clean scan: Safe!!")
        return True


#displays the needed branding logo of that video in that specific area, where the user is watching
class RegionalBranding(BaseTask):
    def run(self) -> bool:
        branding_logos = {
                "RO": "Baieti_De_Oras_Original.png",
                "DE": "Baieti_De_Deutschland.png",
                "JP": "Anime_Baieti_De_Oras.png"
        }

        self.context.metadata["regional_branding"] = branding_logos
        regions_overlaped = ", ". join(branding_logos.keys())
        log(f"[RegionalBranding] Applied overlay branding for regions : {regions_overlaped}.")

        return True