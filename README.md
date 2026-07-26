# 🪖 AI-Powered Helmet Detection & Rider Safety Monitoring System

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![YOLO](https://img.shields.io/badge/Ultralytics-YOLOv8-00FFFF?logo=yolo&logoColor=black)
![OpenCV](https://img.shields.io/badge/OpenCV-Webcam%20Inference-5C3EE8?logo=opencv&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

A real-time computer vision demo that detects whether a rider is wearing a helmet from a **live webcam**, then **simulates vehicle speed control**: full speed when a helmet is confirmed, limited speed when it is not.

This repository is a **laptop software simulation** of an embedded safety interlock (conceptual Raspberry Pi + camera + motor). The shipped code uses a laptop webcam and on-screen speed text only — no GPIO, motor driver, or Pi Camera APIs are implemented.

---

## 📌 Overview

Two-wheeler riders without helmets face higher injury risk. This project demonstrates an automated safety idea: if the system believes the rider is **not** wearing a helmet, it **limits speed** (shown as **25 km/h**); if a helmet is detected, **full speed** is allowed (shown as **60 km/h**).

The pipeline uses **two custom YOLO models** via Ultralytics:

1. A **head/helmet-area detector** finds regions of interest in each frame.
2. A **helmet classifier** decides helmet vs no-helmet on padded crops.

When no head box is found, an OpenCV **Haar face cascade** marks faces as `face/no_helmet` (conservative bias). Decisions are smoothed over several frames before the speed overlay updates.

> **Input supported:** live webcam (`VideoCapture(0)` only). Image-file and video-file modes are not implemented.

---

## ✨ Key Features

- Live webcam inference with OpenCV display
- Two-stage YOLOv8 pipeline (detect → classify)
- Bounding boxes with class labels and confidence scores
- Haar face fallback when no head is detected
- Multi-frame decision smoothing (`deque`, length 7)
- Simulated speed overlay: **60 km/h** (helmet) / **25 km/h** (no helmet)
- One-click Windows launch via `RUN_DEMO.bat`
- Bundled trained weights under `models/` (ready to run after install)

---

## 🛠️ Tech Stack

| Technology | Role |
|------------|------|
| **Python 3.9+** | Application runtime |
| **Ultralytics YOLO** | Head detection + helmet classification |
| **OpenCV** (`opencv-python`) | Webcam capture, drawing, Haar cascades |
| **PyTorch / NumPy** | Pulled in transitively by Ultralytics |

**Not in this repository:** web frontend, REST API, database, Docker, GPIO / Raspberry Pi hardware drivers, license-plate OCR, or alert systems.

---

## 🔄 System Workflow

```
Webcam (index 0)
        │
        ▼
OpenCV frame capture (BGR)
        │
        ▼
YOLO head detector  (models/head_detector_best.pt)
        │
        ├── boxes ≥ HEAD_CONFIDENCE (0.30)
        │         │
        │         ▼
        │   Crop + 18% padding
        │         │
        │         ▼
        │   YOLO helmet classifier  (models/helmet_classifier_best.pt)
        │         │
        │         ▼
        │   helmet / no_helmet (+ confidence)
        │
        └── no head found?
                  │
                  ▼
            Haar face detector → face/no_helmet
                  │
                  ▼
        Temporal vote (deque, 7 frames)
                  │
                  ▼
        Status + Speed overlay (60 or 25 km/h)
                  │
                  ▼
        cv2.imshow  →  press Q to quit
```

**Hardware simulation mapping**

| Conceptual hardware | This project |
|---------------------|--------------|
| Raspberry Pi | Laptop running Python |
| Pi Camera | Webcam (`VideoCapture(0)`) |
| Motor driver | Speed logic in code |
| DC motor | On-screen `Speed: XX km/h` |

More detail: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## 📁 Project Structure

```
├── helmet_detection_speed_control.py   # Main entry point (webcam demo)
├── RUN_DEMO.bat                        # Windows launcher
├── requirements.txt                    # Python dependencies
├── LICENSE                             # MIT License
├── .gitignore
├── README.md
├── DATASET_USED_FOR_REVIEW.txt         # Dataset provenance / class mapping
├── models/
│   ├── head_detector_best.pt           # YOLO detection weights (~5.9 MB)
│   └── helmet_classifier_best.pt       # YOLO classification weights (~2.8 MB)
└── docs/
    ├── ARCHITECTURE.md
    ├── SETUP_AND_INSTALLATION.md
    ├── FEATURES.md
    ├── DEVELOPMENT_WORKFLOW.md
    ├── TROUBLESHOOTING.md
    └── SECURITY_AND_BEST_PRACTICES.md
```

Optional local-only folder (gitignored, not required to run the demo):

```
dataset/separate_helmet_dataset/
├── with_helmet/       # review images
└── without_helmet/
```

---

## 🧠 Model Information

| Model | Path | Role |
|-------|------|------|
| Head detector | `models/head_detector_best.pt` | YOLO **detect** — finds head / helmet-area boxes |
| Helmet classifier | `models/helmet_classifier_best.pt` | YOLO **classify** — helmet vs no-helmet on crops |

Weights are **custom-trained** (not stock COCO-only inference). Training scripts and full YOLO label trees are **not** included in this package; trained `.pt` files are shipped for inference.

**Runtime helmet labels** (normalized class names treated as helmet):

- `helmet`, `withhelmet`, `facewithgoodhelmet`

Anything else from the classifier is treated as `no_helmet`. Display labels also include `face/no_helmet` from the Haar fallback.

> No published accuracy metrics are claimed in this repository.

---

## 📊 Dataset

The live demo **does not load** dataset images at runtime. Dataset notes are for training provenance and review only.

| Item | Detail |
|------|--------|
| Source | Roboflow YOLOv8 export (`aryan_1` / `PROJECT_REVIEW_DATASET_archive_2.zip`) |
| Original classes | `numberPlate`, `faceWithNoHelmet`, `faceWithGoodHelmet`, `faceWithBadHelmet`, `rider` |
| Used for this project | Good helmet → helmet; no/bad helmet → no_helmet; plate & rider ignored |
| Local review images | Optional `dataset/separate_helmet_dataset/` (with_helmet / without_helmet) |

**The bulk image dataset is excluded from GitHub** (see `.gitignore`) to keep the clone small and focused on the runnable demo. If you have the review images locally, place them under `dataset/separate_helmet_dataset/` as documented in `DATASET_USED_FOR_REVIEW.txt`.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
cd <ACTUAL-PROJECT-FOLDER>
```

### 2. Create a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs `opencv-python` and `ultralytics` (Ultralytics installs PyTorch and related packages automatically).

### 4. Verify model weights

Confirm these files exist (included in this repository):

- `models/head_detector_best.pt`
- `models/helmet_classifier_best.pt`

No extra download step is required if you cloned the full repo with `models/`.

---

## ▶️ How to Run

### Windows (one click)

Double-click `RUN_DEMO.bat`, or from a terminal in the project folder:

```bat
RUN_DEMO.bat
```

### Cross-platform (recommended)

```bash
python helmet_detection_speed_control.py
```

On macOS/Linux you may need:

```bash
python3 helmet_detection_speed_control.py
```

**Controls:** press **`q`** in the OpenCV window to quit.

> Only **webcam** mode is supported. There is no CLI for image or video files.

---

## 🖥️ Output / Results

While running you should see an OpenCV window titled **Helmet Detection Speed Control** with:

- Green / red bounding boxes around detected heads
- Labels such as `helmet 0.87` or `no_helmet 0.62`
- Status line: `Helmet Detected - Full Speed Allowed` or `Helmet Not Detected - Speed Limited`
- Simulated speed: `Speed: 60 km/h` or `Speed: 25 km/h`
- Hint: `Q: Quit`

Frames are **not** saved to disk by default; output is live on screen only.

---

## 🔧 Configuration

Edit constants near the top of `helmet_detection_speed_control.py`:

| Constant | Default | Meaning |
|----------|---------|---------|
| `FULL_SPEED` | `60` | Displayed km/h when helmet is confirmed |
| `LIMITED_SPEED` | `25` | Displayed km/h when no helmet |
| `HEAD_CONFIDENCE` | `0.30` | Minimum head-box confidence |
| `CLASS_CONFIDENCE` | `0.50` | Minimum classifier confidence to count as helmet |
| `DECISION_HISTORY` | `7` | Frames kept for temporal voting |

Camera index is hardcoded as `0`. Change `cv2.VideoCapture(0)` if you need another device. On some Windows setups, `cv2.VideoCapture(0, cv2.CAP_DSHOW)` can help if the camera fails to open.

---

## 🩹 Troubleshooting

| Problem | What to try |
|---------|-------------|
| `ModuleNotFoundError: cv2` or `ultralytics` | Activate venv, then `pip install -r requirements.txt` |
| `FileNotFoundError` for head/helmet model | Ensure `models/*.pt` exist next to the script |
| Camera / `RuntimeError: Camera not opened` | Close other apps using the webcam; check OS camera privacy; try index `1` or `CAP_DSHOW` on Windows |
| Window opens but speed stuck at 25 | Check on-screen confidence; helmet may be below `CLASS_CONFIDENCE` or poorly visible |
| Very low FPS | Expected on CPU; reduce resolution or use a GPU build of PyTorch if available |

More detail: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

---

## 🚀 Future Improvements

These are **not** implemented today:

- Number plate recognition
- Automatic violation logging / database
- Web dashboard or REST API
- Audio / network alert system
- Cloud deployment
- Real Raspberry Pi GPIO + motor driver integration
- Image / video-file inference CLI
- Automated tests and CI


---

## 👤 Author

**Athithiyan T**

- GitHub: [`@your-username`](https://github.com/<your-username>)
- LinkedIn: [`your-profile`](https://www.linkedin.com/in/<your-profile>)

---


