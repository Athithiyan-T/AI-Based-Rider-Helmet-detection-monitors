# Troubleshooting Guide

Copy-paste fixes for common problems when running this project.

---

## Installation Issues

### `pip install ultralytics` fails (compiler / torch errors)

**Cause:** Python version too new, or missing Visual C++ build tools on Windows.

**Fix:**

1. Install Python 3.11 from python.org.
2. Create a fresh venv with 3.11.
3. Run:

```powershell
pip install --upgrade pip
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install ultralytics opencv-python
```

---

### `ModuleNotFoundError: No module named 'cv2'`

**Cause:** OpenCV not installed in active environment.

**Fix:**

```powershell
pip install opencv-python
```

Ensure venv is activated.

---

## Model Errors

### `FileNotFoundError: Head detector model missing`

**Cause:** `models/head_detector_best.pt` (or the classifier weight) is not next to the script.

**Fix:**

1. Confirm files from the project root:

```powershell
dir models
```

2. Ensure exact names under `models/`:
   - `head_detector_best.pt`
   - `helmet_classifier_best.pt`

3. Re-clone or restore the `models/` folder if weights were deleted.

---

### Ultralytics version mismatch / strange inference output

**Cause:** Model trained with different Ultralytics major version.

**Fix:**

```powershell
pip install ultralytics==8.3.0
```

Adjust version to match training environment if known.

---

## Camera Issues

### `RuntimeError: Camera not opened`

**Cause:** Webcam busy, wrong index, driver issue, or privacy block.

**Fixes (try in order):**

1. Close all apps using the camera.
2. Unplug/replug USB webcam.
3. Windows **Settings → Privacy → Camera** → allow desktop apps.
4. On Windows, change the capture line to `cv2.VideoCapture(0, cv2.CAP_DSHOW)`.
5. Try index `1`:

```python
cap = cv2.VideoCapture(1)
```

6. Reboot machine if driver stuck.

---

### Black window or frozen frame

**Cause:** `ret` is False from `cap.read()`; USB bandwidth; exposure.

**Fix:**

- Break loop already happens on `not ret`; check cable.
- Set resolution:

```python
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

---

## Runtime / Logic Issues

### Speed always 25 km/h even with helmet

**Causes:**

- Classifier confidence below 0.50
- Helmet not visible to camera
- Class names in model do not match `helmet`, `withhelmet`, `facewithgoodhelmet`

**Fix:**

1. Look at on-screen label confidence values.
2. Lower `CLASS_CONFIDENCE` slightly (e.g. 0.45) for testing.
3. Retrain classifier with consistent class names.

---

### Speed always 60 km/h without helmet

**Cause:** Dangerous misconfiguration or history biased wrong way.

**Fix:**

1. Do **not** lower `no_helmet` vote threshold without review.
2. Check if head detector never fires and face fallback is disabled incorrectly.
3. Verify `final_decision` logic was not edited.

---

### Flickering between 60 and 25

**Cause:** Borderline confidence; single-frame noise.

**Fix:**

- Increase `DECISION_HISTORY` to 10–15.
- Strengthen rule: require 3+ helmet votes for full speed (code change).

---

## Script-Specific Issues

### `RUN_DEMO.bat` closes instantly

**Cause:** Python not on PATH or script crashed before `pause`.

**Fix:**

1. Open CMD in project folder.
2. Run `python helmet_detection_speed_control.py` manually to see error.
3. Install Python with “Add to PATH”.

---

## Performance Issues

### Very low FPS (< 5)

**Cause:** CPU inference, large frame, two YOLO calls per frame.

**Fix:**

- Reduce camera resolution.
- Use GPU PyTorch if available.
- Retrain with `yolov8n` nano models.
- Process every 2nd frame (skip-frame pattern—requires code change).

---

### High CPU / fan noise

**Expected** on CPU-only laptops during continuous inference. Use power adapter.

---

## Missing Project Components

| Item | Status |
|------|--------|
| `.env` | Not used |
| Docker | Not provided |
| Automated tests | Not provided |
| `LICENSE` | Provided (MIT) |
| Image / video-file CLI | Not implemented (webcam only) |
| `package.json` | N/A (Python only) |

---

## Getting More Help

When asking for support, include:

1. Python version (`python --version`)
2. OS version
3. Full error traceback
4. Output of `pip show ultralytics`
5. Whether `models/*.pt` exist and their file sizes
6. Photo or description of webcam setup
