import os
import hashlib
from pipeline.stages.base_task import BaseTask
from pipeline.utils.logger import log


#Check if the file is not corrupted any how
class IntegrityCheck(BaseTask):
    def run(self) -> bool:
        path = self.context.input_path #this is the video path

        if not os.path.isfile(path):
            log(f"[IntegrityCheck] File not found: {path}")
            return False

        checksum = self._sha256(path)
        self.context.metadata["checksum"] = checksum #save the checksum into the shared metadata
        log(f"[IntegrityCheck] SHA-256: {checksum}")
        return True

    def _sha256(self, path):
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest() #compute the checksum via sha256 encoding


#check if the file is actually a video or not
class FormatValidator(BaseTask):

    #dict to check the magic bytes -> offset and their bytes
    #https://en.wikipedia.org/wiki/List_of_file_signatures
    magic_bytes = {
        ".mkv": (0, b"\x1A\x45\xDF\xA3"),  # Matroska
        ".webm": (0, b"\x1A\x45\xDF\xA3"),  # WebM
        ".flv": (0, b"\x46\x4C\x56"),  # FLV
        ".mp4": (4, b"\x66\x74\x79\x70"),  # ftyp
        ".mov": (4, b"\x66\x74\x79\x70"),  # ftyp
        ".avi": (0, b"\x52\x49\x46\x46"),  # RIFF
    }

    def run(self) -> bool:
        with open(self.context.input_path, "rb") as f:
            header = f.read(32) # read only 32 bytes

        for extension, (offset, signature) in self.magic_bytes.items():
            if header[offset:offset + len(signature)] == signature:
                log(f"[FormatValidator] Detected: {extension}")
                self.context.metadata["format"] = extension
                return True

        log(f"[FormatValidator] Unknown format: {header[:8].hex()}")
        return False