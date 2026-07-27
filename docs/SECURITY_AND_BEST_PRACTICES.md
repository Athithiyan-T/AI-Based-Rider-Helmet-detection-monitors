# Security and Best Practices

Assessment of this repository from a security, quality, and performance perspective (verified against current files).

---

## Security Risks

| Risk | Severity | Details |
|------|----------|---------|
| **No authentication** | Low (for local demo) | Anyone at the machine can run the script; not a network service. |
| **Camera access** | Medium (privacy) | Application reads live video; could be extended to record without user knowledge if code is modified maliciously. |
| **Arbitrary path loading** | Low | `find_model()` loads first existing `.pt` from a short project-relative list—if an attacker could place a malicious file on a searched path, PyTorch pickle risks apply. **Only load models from trusted sources.** |
| **Pickle in `.pt` weights** | Medium | PyTorch weights are pickled objects; never load `.pt` files from untrusted third parties. |
| **No input validation on camera** | Low | Only local device index; no network attack surface in stock code. |
| **No HTTPS / API** | N/A | No transport security needed for offline app. |

### Hardcoded secrets scan

**Result:** No API keys, passwords, or tokens found in source files.  
**No `.env` files** present.

---

## Safety-Critical Logic (Product Risk)

This is a **simulation**, not certified safety equipment.

| Topic | Risk | Recommendation |
|-------|------|----------------|
| False “helmet” → 60 km/h | Physical harm if wired to real motor | Add hardware watchdog; require sustained helmet detection > N seconds before full power |
| Face fallback → no helmet | May limit speed when head detector fails but person wears helmet | Acceptable for safety bias; tune for production |
| Default `no_helmet` when empty history path | Good safe default | Keep in production |
| Display-only speed | Users may think motor is actually controlled | Label UI “SIMULATION” in production builds |

---

## Best Practice Notes (Current Repo)

| Topic | Status / recommendation |
|-------|-------------------------|
| **Single entry script** | Done — `helmet_detection_speed_control.py` only |
| **Portable model paths** | Done — `BASE_DIR / "models" / ...` only |
| **LICENSE** | Done — MIT (`LICENSE`) |
| **Unpinned dependencies** | Optional: pin `ultralytics` / `opencv-python` versions for reproducibility |
| **No logging** | Add structured logs if deploying beyond a demo |
| **No tests** | Add pytest for `final_decision` and `normalize_name` |
| **Dataset in git** | Bulk `dataset/` is gitignored; keep optional locally |

---

## Performance Improvements

1. **Single YOLO pipeline** — Explore one multi-class detector instead of detect + classify twice per head.
2. **Frame skipping** — Run detector every 2–3 frames; reuse boxes between frames.
3. **Resize input** — Downscale frame to 640px width before inference.
4. **GPU** — Install CUDA-enabled PyTorch on supported laptops.
5. **Export formats** — On Pi, convert to ONNX or TFLite for faster inference.
6. **Batch crops** — If multiple heads, batch classify in one forward pass.

---

## Optimization Opportunities

| Area | Current | Suggested |
|------|---------|-----------|
| Model size | ~9 MB total weights | Already small; good for Pi |
| Padding | Fixed 18% | Tune from validation set |
| History length | 7 frames | Tune vs latency requirement |
| Haar fallback | Runs every frame without heads | Could throttle to every N frames |
| `verbose=False` | Good for speed | Keep in production |

---

## Dependency Hygiene

```text
# Recommended requirements.txt pattern (example — verify versions before use):
opencv-python>=4.8.0,<5.0.0
ultralytics>=8.2.0,<9.0.0
```

Run periodic:

```powershell
pip audit
```

(When supported by pip version.)

---

## Data Governance

- Dataset derived from **Roboflow export** (`aryan_1` / `PROJECT_REVIEW_DATASET_archive_2.zip`).
- **3,377 images** may contain identifiable faces—handle per GDPR/local privacy rules if deployed publicly.
- Do not redistribute dataset without checking Roboflow/dataset license.

---

## Deployment Best Practices (Raspberry Pi)

1. Run as non-root user; GPIO group only as needed.
2. Read-only filesystem option for kiosk mode.
3. Sign or checksum model files at deploy time.
4. Physical e-stop independent of software.
5. OTA update mechanism with rollback for model updates.

---

## Suggested Improvements Summary (Priority)

| Priority | Item |
|----------|------|
| P1 | Pin dependencies for reproducibility |
| P2 | Add config file (YAML/env) for thresholds |
| P2 | Add minimal pytest suite |
| P3 | GPIO abstraction for real hardware |
| P3 | Structured logging |

---

## What This Project Does Well

- Clear safety bias toward **limited speed** when uncertain
- Small, reviewable codebase suitable for academic demonstration
- Sensible two-stage vision pipeline for helmet tasks
- Temporal smoothing reduces UI flicker
- Includes models and dataset evidence for reproducibility
- Windows batch launcher for non-technical reviewers
