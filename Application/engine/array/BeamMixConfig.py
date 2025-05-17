

from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class BeamMixConfig:
    name: str
    center_frequency: int
    processing_chain: Dict[str, int]
    mic_spacing: float
    mics_to_use: List[int]
    rows: int
    cols: int
    num_mics: int
    num_taps: int