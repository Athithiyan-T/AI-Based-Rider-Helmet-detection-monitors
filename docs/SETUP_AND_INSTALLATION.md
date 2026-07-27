# Setup and Installation Guide

Beginner-friendly, step-by-step instructions verified against this repository layout.

---

## What You Are Installing

You are installing a **Python program** that uses your **webcam** and two **AI model files** to show helmet detection and a simulated speed limit. You are **not** installing a website, database, or mobile app.

---

## Step 1: Check Required Software

### Python

1. Open PowerShell or Command Prompt.
2. Run:

```powershell
python --version
```

3. You should see **Python 3.9 or higher**.
4. **Recommended:** Python **3.10, 3.11, or 3.12** for reliable Ultralytics/PyTorch wheels.
5. If `python` is not found, install from [https://www.python.org/downloads/](https://www.python.org/downloads/) and enable **“Add Python to PATH”**.

> **Note:** Very new versions (e.g. 3.14) may lack prebuilt wheels for some ML packages. If `pip install ultralytics` fails, install Python 3.11 alongside and use that interpreter.

### pip

```powershell
python -m pip --version
```

Upgrade if needed:

```powershell
python -m pip install --upgrade pip
```

### Webcam

- Connect a working webcam.
- Close Zoom, Teams, or other apps that lock the camera.

---

## Step 2: Get the Project Files

Ensure the folder contains at minimum:

```
helmet_detection_speed_control.py
requirements.txt
models/head_detector_best.pt
models/helmet_classifier_best.pt
```

Dataset folders are **optional** for running the demo (required only for retraining or review evidence).

---

## Step 3: Virtual Environment (Strongly Recommended)

**Why?** Keeps Ultralytics/PyTorch isolated from other projects.

```powershell
cd path\to\project-folder
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks scripts:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate again.

You should see `(.venv)` in your prompt.

---

## Step 4: Install Python Dependencies

```powershell
pip install -r requirements.txt
```

### What gets installed

| Package | What it does |
|---------|----------------|
| `opencv-python` | Opens camera, draws boxes, shows window |
| `ultralytics` | Runs YOLO models; installs PyTorch and helpers |

### Expected output (example)

```text
Successfully installed opencv-python-... ultralytics-... torch-... ...
```

### First run note

Ultralytics may download small helper files on first import. Ensure internet access once.

---

## Step 5: Verify Model Files

```powershell
dir models
```

Expected:

| File | Approx. size |
|------|----------------|
| `head_detector_best.pt` | ~6 MB |
| `helmet_classifier_best.pt` | ~3 MB |

If missing, training outputs must be copied here (see `DATASET_USED_FOR_REVIEW.txt`).

---

## Step 6: Run the Application

### Option A — Windows batch file

Double-click **`RUN_DEMO.bat`**.

### Option B — Command line

```powershell
python helmet_detection_speed_control.py
```

### Success criteria

1. A window titled **Helmet Detection Speed Control** appears.
2. You see yourself on camera.
3. Boxes and speed text update.
4. Press **`q`** to quit.

---

## Environment Variables

**None required** for the stock project. Optional future variables (not implemented today):

| Variable | Would control |
|----------|----------------|
| `CAMERA_INDEX` | Which webcam (0, 1, …) |
| `MODEL_DIR` | Path to `.pt` files |
| `FULL_SPEED` / `LIMITED_SPEED` | Display values |

Today, edit constants at the top of the `.py` file instead.

---

## Third-Party Services / API Keys

| Service | Needed to run demo? |
|---------|---------------------|
| Roboflow | No (only for original dataset download/training) |
| OpenAI / cloud APIs | No |
| AWS / Azure | No |

---

## Database Installation

**Not required.**

---

## Docker Setup

**Not available** in this repository. No `Dockerfile` or `docker-compose.yml`.

To add Docker later, you would need a base image with Python, system libraries for OpenCV, and USB device passthrough for the camera—non-trivial for GUI apps.

---

## OS-Specific Notes

### Windows

- Use `helmet_detection_speed_control.py` or `RUN_DEMO.bat`.
- If the camera fails to open, try `cv2.VideoCapture(0, cv2.CAP_DSHOW)` in that script.
- Allow camera permission in **Settings → Privacy → Camera**.

### Linux

```bash
sudo apt update
sudo apt install python3-venv python3-pip
# Optional: v4l-utils for webcam debugging
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 helmet_detection_speed_control.py
```

If camera permission denied, add user to `video` group: `sudo usermod -aG video $USER` (re-login).

### macOS

```bash
brew install python@3.11
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python helmet_detection_speed_control.py
```

Grant **Camera** access when macOS prompts.

---

## Retraining Setup (Advanced)

Not automated in this package. Per `DATASET_USED_FOR_REVIEW.txt`:

1. Source: Roboflow export `PROJECT_REVIEW_DATASET_archive_2.zip` (dataset name `aryan_1`, 942 annotated images in original export).
2. Prepared folders (external to this demo tree): `bike_head_detect_dataset`, `bike_helmet_classify_dataset`.
3. Train with Ultralytics CLI, then copy `best.pt` files to `models/`.

Example commands (paths must exist on your machine):

```bash
yolo detect train data=bike_head_detect_dataset/data.yaml model=yolov8n.pt epochs=50
yolo classify train data=bike_helmet_classify_dataset model=yolov8n-cls.pt epochs=50
```

---

## Browser Extensions / Extra Tools

None required.

**Optional tools for developers:**

- VS Code or Cursor for editing
- `ffmpeg` if you add video file input later
- GPU drivers + CUDA build of PyTorch for faster inference

---

## Installation Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] `pip install -r requirements.txt` succeeded
- [ ] Both `.pt` files in `models/`
- [ ] Webcam works in another app
- [ ] `python helmet_detection_speed_control.py` opens GUI
- [ ] Press `q` closes cleanly
