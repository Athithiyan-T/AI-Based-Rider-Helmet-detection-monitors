# Feature Documentation

Every major capability in this project, explained for developers new to computer vision.

---

## Feature 1: Live Webcam Capture

### Purpose

Feed real-time video into the detection pipeline, simulating a Raspberry Pi camera stream.

### How it works

- `cv2.VideoCapture(0)` opens the default camera.
- Each loop iteration calls `cap.read()` → boolean `ret` and `frame` (image).
- On failure to open, scripts raise `RuntimeError` (message varies by file).

### Important files

| File | Line area |
|------|-----------|
| `helmet_detection_speed_control.py` | `cap = cv2.VideoCapture(0)` |

### Dependencies

- `opencv-python`

### Business logic (simple)

Without a camera image, nothing else can run. This is the “eyes” of the system.

---

## Feature 2: Head / Helmet-Area Detection (YOLO Detect)

### Purpose

Find where the rider’s head or helmet region is in the frame so classification runs on a small, relevant image patch.

### How it works

1. Full frame passed to `head_detector` (YOLO detect model).
2. Each box has a confidence score; boxes below `HEAD_CONFIDENCE` (0.30) are ignored.
3. Remaining boxes go to cropping.

### Important files

- `models/head_detector_best.pt`
- All main `.py` scripts (inference loop)

### Dependencies

- `ultralytics` (YOLO)
- PyTorch (installed transitively)

### Business logic

“Where is the head?” must be answered before asking “is there a helmet on that head?”

---

## Feature 3: Padded Region Crop

### Purpose

Include a little context around the head box (hair, helmet brim, chin) to improve classifier accuracy.

### How it works — `crop_box(frame, box)`

1. Convert box coordinates to integers.
2. Add **18%** padding horizontally and vertically.
3. Clamp to image bounds so crops are valid.
4. Return crop image and draw coordinates.

### Important files

- `crop_box()` in each Python script

### Dependencies

- NumPy arrays via OpenCV

### Business logic

Tight crops sometimes cut off the helmet; padding reduces false “no helmet” results.

---

## Feature 4: Helmet Classification (YOLO Classify)

### Purpose

Decide whether the cropped head region shows a proper helmet.

### How it works — `classify_head(classifier, crop)`

1. Run classifier on crop.
2. Read top-1 class id and confidence.
3. Normalize class name (lowercase, alphanumeric only).
4. If name in `{helmet, withhelmet, facewithgoodhelmet}` → `"helmet"`, else `"no_helmet"`.
5. Frame counts as helmet only if class is helmet **and** confidence ≥ `CLASS_CONFIDENCE` (0.50).

### Important files

- `models/helmet_classifier_best.pt`
- `classify_head()` function

### Dataset mapping (from `DATASET_USED_FOR_REVIEW.txt`)

| Original Roboflow class | Project label |
|-------------------------|---------------|
| faceWithGoodHelmet | helmet |
| faceWithNoHelmet | no_helmet |
| faceWithBadHelmet | no_helmet |
| numberPlate, rider | ignored in training prep |

### Business logic

A good helmet allows full speed; missing or bad helmet treatment limits speed.

---

## Feature 5: Visual Overlay (Bounding Boxes and Labels)

### Purpose

Show reviewers what the AI sees—transparent debugging and demo value.

### How it works

- `cv2.rectangle` for each head or face region.
- `cv2.putText` for labels: `helmet 0.87`, `no_helmet 0.65`, `face/no_helmet`.
- Colors: green `(0,255,0)` helmet, red `(0,0,255)` no helmet (BGR).

### Important files

- Main loop in all scripts

### Dependencies

- OpenCV drawing APIs

---

## Feature 6: Face Detection Fallback (Haar Cascade)

### Purpose

If the head detector misses (profile, occlusion, distance), still detect a **face** and assume **no helmet** for safety.

### How it works

1. Only when `head_found` is false after the detection loop.
2. Convert frame to grayscale.
3. `detectMultiScale` with `scaleFactor=1.08`, `minNeighbors=6`, `minSize=(70,70)`.
4. Each face → red box, label `face/no_helmet`, sets `frame_has_no_helmet`.

### Important files

- `cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")`

### Dependencies

- OpenCV bundled Haar XML

### Business logic

Conservative: “we see a person’s face but not a confirmed helmet region” → limit speed.

---

## Feature 7: Temporal Decision Smoothing

### Purpose

Stop speed from flipping every frame when the model hesitates.

### How it works

1. Each frame appends one label to `decision_history` (`deque`, max length 7).
2. Priority per frame: any `no_helmet` evidence → append `no_helmet`; else if helmet → `helmet`; else default `no_helmet`.
3. `final_decision(history)` aggregates votes (see ARCHITECTURE.md).

### Important files

- `final_decision()`, `decision_history`

### Dependencies

- Python `collections.deque`

### Business logic

Safety system should not oscillate rapidly between 60 and 25 km/h; short noise should not instantly grant full speed.

---

## Feature 8: Simulated Speed Control

### Purpose

Represent motor driver behavior when helmet status changes.

### How it works

| `final_decision` | Status text | Speed |
|------------------|-------------|-------|
| `helmet` | Helmet Detected - Full Speed Allowed | 60 km/h |
| `no_helmet` | Helmet Not Detected - Speed Limited | 25 km/h |

Displayed on frame; **no GPIO or serial output** in this repo.

### Constants

- `FULL_SPEED = 60`
- `LIMITED_SPEED = 25`

### Business logic

Enforces policy: ride with helmet → normal speed; without → reduced speed.

---

## Feature 9: Interactive Quit

### Purpose

Clean shutdown for demos and development.

### How it works

- `cv2.waitKey(1)` reads keyboard.
- If key is `q`, break loop.
- `cap.release()` and `cv2.destroyAllWindows()`.

---

## Feature 10: Portable Model Loading

### Purpose

Resolve trained weights relative to the project folder so the demo runs after clone without machine-specific paths.

### How it works — `find_model(candidates, label)`

Tries each path in `HEAD_DETECTOR_CANDIDATES` / `HELMET_CLASSIFIER_CANDIDATES`; first existing file wins; else `FileNotFoundError` lists checked paths.

Candidates are project-relative only:

- `models/head_detector_best.pt`
- `models/helmet_classifier_best.pt`

### Important files

- `helmet_detection_speed_control.py`

---

## Feature 11: Review Dataset (Static Assets)

### Purpose

Document training data for academic/project review; support retraining.

### Location

```
dataset/separate_helmet_dataset/with_helmet/     (2061 images)
dataset/separate_helmet_dataset/without_helmet/  (1316 images)
```

### Runtime use

**Not loaded** by the demo scripts. Images are evidence and training material only.

### Source metadata

- `dataset/separate_helmet_dataset/README.txt`
- `DATASET_USED_FOR_REVIEW.txt`

---

## Feature 12: One-Click Windows Demo

### Purpose

Let non-developers run the project during external review.

### File

- `RUN_DEMO.bat` → runs `helmet_detection_speed_control.py`

---

## Dependency Summary by Feature

| Feature | opencv-python | ultralytics |
|---------|---------------|-------------|
| Webcam + UI | ✓ | |
| YOLO detect/classify | ✓ (display) | ✓ |
| Haar fallback | ✓ | |
| Speed simulation | ✓ | |

---

## Features Not Implemented

- Audio alarms
- Data logging to CSV/SQL
- Multi-rider tracking
- License plate detection (class exists in source dataset but ignored)
- Mobile app or web dashboard
- Automatic model retraining pipeline in repo
