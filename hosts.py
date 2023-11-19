from dataclasses import dataclass
from enum import Enum

@dataclass
class NarratorInfo:
    voice_id: str
    file_id: str

class Narrator(Enum):
    CONAN_O_BRIEN = NarratorInfo(voice_id="hpf9PPFCikOMXsxDRivV", file_id="conan_o_brien")
    SAM_ALTMAN = NarratorInfo(voice_id="XmgN3vGiZJ2K8Baq6Fbx", file_id="sam_altman")
    DAVID_ATTENBOROUGH = NarratorInfo(voice_id="ChvVWzx9qSQwzu3Ur9M1", file_id="david_attenborough")

# Create a mapping of friendly names to enum members
narrator_mapping = {
    "Conan O’Brien": Narrator.CONAN_O_BRIEN,
    "Sam Altman": Narrator.SAM_ALTMAN,
    "David Attenborough": Narrator.DAVID_ATTENBOROUGH
}