from dataclasses import dataclass
from enum import Enum


@dataclass
class NarratorInfo:
    voice_id: str
    file_id: str


class Narrator(Enum):
    CONAN_O_BRIEN = NarratorInfo(
        voice_id="m5ltPV1I139V2cpXC2YE", file_id="conan_o_brien")
    SAM_ALTMAN = NarratorInfo(
        voice_id="xfaK2RM49KgNqR0nHK59", file_id="sam_altman")
    DAVID_ATTENBOROUGH = NarratorInfo(
        voice_id="pRxLP8qNw6sbBiMESYOZ", file_id="david_attenborough")
    HARVEY_SPECTER = NarratorInfo(
        voice_id="wVQNrcbcjm4WahKvqzbn", file_id="harvey_specter")



# Create a mapping of friendly names to enum members
narrator_mapping = {
    "Conan O’Brien": Narrator.CONAN_O_BRIEN,
    "Sam Altman": Narrator.SAM_ALTMAN,
    "David Attenborough": Narrator.DAVID_ATTENBOROUGH,
    "Harvey Specter": Narrator.HARVEY_SPECTER,
}
