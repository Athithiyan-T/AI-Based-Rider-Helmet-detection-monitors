from collections import deque
from pathlib import Path

import cv2
from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parent

HEAD_DETECTOR_CANDIDATES = [
    BASE_DIR / "models" / "head_detector_best.pt",
]

HELMET_CLASSIFIER_CANDIDATES = [
    BASE_DIR / "models" / "helmet_classifier_best.pt",
]

FULL_SPEED = 60
LIMITED_SPEED = 25
HEAD_CONFIDENCE = 0.30
CLASS_CONFIDENCE = 0.50
DECISION_HISTORY = 7


def find_model(candidates: list[Path], label: str) -> Path:
    for path in candidates:
        if path.exists():
            return path

    searched = "\n".join(str(path) for path in candidates)
    raise FileNotFoundError(f"{label} missing. Checked paths:\n{searched}")


def normalize_name(name: str) -> str:
    return "".join(ch for ch in name.lower() if ch.isalnum())


def crop_box(frame, box):
    height, width = frame.shape[:2]
    x1, y1, x2, y2 = map(int, box)

    box_width = x2 - x1
    box_height = y2 - y1
    pad_x = int(box_width * 0.18)
    pad_y = int(box_height * 0.18)

    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(width, x2 + pad_x)
    y2 = min(height, y2 + pad_y)

    return frame[y1:y2, x1:x2], (x1, y1, x2, y2)


def classify_head(classifier: YOLO, crop):
    result = classifier(crop, verbose=False)[0]
    class_id = int(result.probs.top1)
    confidence = float(result.probs.top1conf)
    class_name = normalize_name(classifier.names[class_id])

    if class_name in {"helmet", "withhelmet", "facewithgoodhelmet"}:
        return "helmet", confidence

    return "no_helmet", confidence


def final_decision(history: deque[str]) -> str:
    if not history:
        return "no_helmet"

    no_helmet_votes = history.count("no_helmet")
    helmet_votes = history.count("helmet")

    if no_helmet_votes >= 2:
        return "no_helmet"
    if helmet_votes > no_helmet_votes:
        return "helmet"
    return "no_helmet"


HEAD_DETECTOR_MODEL = find_model(HEAD_DETECTOR_CANDIDATES, "Head detector model")
HELMET_CLASSIFIER_MODEL = find_model(
    HELMET_CLASSIFIER_CANDIDATES,
    "Helmet classifier model",
)

head_detector = YOLO(HEAD_DETECTOR_MODEL)
helmet_classifier = YOLO(HELMET_CLASSIFIER_MODEL)

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def open_camera(max_index: int = 5):
    """Try to open a camera using several backends and indices.

    Returns an open `cv2.VideoCapture` or None if none could be opened.
    """
    backends = []
    # Prefer DirectShow / MSMF on Windows where available
    if hasattr(cv2, "CAP_DSHOW"):
        backends.append(cv2.CAP_DSHOW)
    if hasattr(cv2, "CAP_MSMF"):
        backends.append(cv2.CAP_MSMF)
    # Fallback to any available backend
    backends.append(cv2.CAP_ANY)

    for backend in backends:
        for idx in range(0, max_index + 1):
            try:
                cap = cv2.VideoCapture(idx, backend)
            except Exception:
                # Some OpenCV builds expect a single-argument constructor
                try:
                    cap = cv2.VideoCapture(idx)
                except Exception:
                    cap = None

            if cap is None:
                continue

            if cap.isOpened():
                print(f"Opened camera index={idx} backend={backend}")
                return cap

            # cleanup and continue
            try:
                cap.release()
            except Exception:
                pass

    return None


cap = open_camera()
if cap is None or not cap.isOpened():
    raise RuntimeError(
        "Camera not opened. Check that a webcam is connected, no other app is using it, and try different camera indices."
    )

decision_history = deque(maxlen=DECISION_HISTORY)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    head_results = head_detector(frame, verbose=False)[0]
    frame_has_helmet = False
    frame_has_no_helmet = False
    head_found = False

    for box in head_results.boxes:
        head_confidence = float(box.conf[0])
        if head_confidence < HEAD_CONFIDENCE:
            continue

        crop, (x1, y1, x2, y2) = crop_box(frame, box.xyxy[0])
        if crop.size == 0:
            continue

        head_found = True
        class_name, class_confidence = classify_head(helmet_classifier, crop)

        if class_name == "helmet" and class_confidence >= CLASS_CONFIDENCE:
            frame_has_helmet = True
            color = (0, 255, 0)
            label = f"helmet {class_confidence:.2f}"
        else:
            frame_has_no_helmet = True
            color = (0, 0, 255)
            label = f"no_helmet {class_confidence:.2f}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            frame,
            label,
            (x1, max(25, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2,
        )

    if not head_found:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.08,
            minNeighbors=6,
            minSize=(70, 70),
        )
        for (x, y, w, h) in faces:
            frame_has_no_helmet = True
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(
                frame,
                "face/no_helmet",
                (x, max(25, y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2,
            )

    if frame_has_no_helmet:
        decision_history.append("no_helmet")
    elif frame_has_helmet:
        decision_history.append("helmet")
    else:
        decision_history.append("no_helmet")

    decision = final_decision(decision_history)

    if decision == "helmet":
        status = "Helmet Detected - Full Speed Allowed"
        speed = FULL_SPEED
        status_color = (0, 255, 0)
    else:
        status = "Helmet Not Detected - Speed Limited"
        speed = LIMITED_SPEED
        status_color = (0, 0, 255)

    cv2.putText(
        frame,
        status,
        (25, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        status_color,
        2,
    )
    cv2.putText(
        frame,
        f"Speed: {speed} km/h",
        (25, 95),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        status_color,
        2,
    )
    cv2.putText(
        frame,
        "Q: Quit",
        (25, 135),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
    )

    cv2.imshow("Helmet Detection Speed Control", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
