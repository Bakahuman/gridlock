import os
import uuid
from abc import ABC, abstractmethod

# the detector contract. anything that returns detections in this shape
# can be swapped in (LocateAnything now, a commercial model later) without
# changing anything downstream.
#
# returns: list of dicts {label, confidence, box:{x1,y1,x2,y2}, ocr_text}


class Detector(ABC):
    @abstractmethod
    def detect(self, image_bytes, prompts):
        ...


# placeholder used for wiring and demos before the GPU model is ready.
# produces deterministic fake boxes so the full pipeline runs on any machine.
class MockDetector(Detector):
    def detect(self, image_bytes, prompts):
        return [
            {
                "label": "car",
                "confidence": 0.93,
                "box": {"x1": 120, "y1": 200, "x2": 360, "y2": 380},
                "ocr_text": None,
            },
            {
                "label": "license_plate",
                "confidence": 0.88,
                "box": {"x1": 220, "y1": 350, "x2": 300, "y2": 375},
                "ocr_text": "KA01AB1234",
            },
            {
                "label": "motorcycle_rider",
                "confidence": 0.9,
                "box": {"x1": 480, "y1": 220, "x2": 600, "y2": 420},
                "ocr_text": None,
            },
        ]


# real detector. Dev B fills in the LocateAnything call. all model-specific
# code stays inside this class only.
class LocateAnythingDetector(Detector):
    def __init__(self, model_path=None, device="cuda"):
        self.model_path = model_path or os.environ.get("LA_MODEL", "nvidia/LocateAnything-3B")
        self.device = device
        self.model = None
        self._load()

    def _load(self):
        # TODO Dev B: load LocateAnything-3B onto the 3060 here.
        # keep imports local so the backend never needs torch installed.
        pass

    def detect(self, image_bytes, prompts):
        # TODO Dev B: run inference for each prompt, return boxes in the
        # contract shape above. until then, raise so it's obvious it's a stub.
        raise NotImplementedError("LocateAnything detect() not implemented yet")


def get_detector():
    backend = os.environ.get("DETECTOR", "mock").lower()
    if backend == "locateanything":
        return LocateAnythingDetector()
    return MockDetector()
