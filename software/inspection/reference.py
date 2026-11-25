"""Independent file-image challenge for the known high-confidence false OK."""

import hashlib
from pathlib import Path


REFERENCE_SHA256 = "872b8cd6257a14ad28b7636756152a4b6ceb29a50f0f54936aab3682077783f0"
REFERENCE_PATH = Path(__file__).resolve().parents[2] / "configs/reference/IMG_7.jpg"


def inspect_reference(classifier):
    import cv2
    import numpy as np
    from vision.yolo.station import square_cover

    data = REFERENCE_PATH.read_bytes()
    if hashlib.sha256(data).hexdigest() != REFERENCE_SHA256:
        raise ValueError("Restore the original IMG_7 reference photo before automatic inspection.")
    frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Cannot read the IMG_7 reference photo.")
    label, confidence = classifier.predict(square_cover(frame, classifier.size))
    return {"book": "IMG_7", "truth": "NG", "label": label, "confidence": confidence}
