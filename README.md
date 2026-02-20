# GSE-Next — Generative Struggle Engine

[🇯🇵 日本語](./README.ja.md) | [🇺🇸 English](./README.md)

**GSE-Next** is a real-time cognitive state estimation system for Windows. It monitors keystroke dynamics across all applications and infers whether a user is in **Flow** (productive focus), **Incubation** (thoughtful pause), or **Stuck** (frustration/blockage). When a Stuck state is detected, ambient visual feedback nudges the user toward a state change.

Built as a research prototype for the *Generative Struggle Engine* project — studying how keystroke micro-behaviors can serve as proxies for cognitive state during creative work (coding, writing, etc.).

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      Windows (Global)                   │
│   WH_KEYBOARD_LL hook      WinEvent hook (IME)          │
└────────────┬────────────────────────┬───────────────────┘
             │ InputEvent             │ IME_ACTIVE flag
             ▼                        ▼
┌────────────────────────┐   ┌────────────────────┐
│  hook.rs (Hook Thread) │   │  ime.rs (IME Thread)│
└────────────┬───────────┘   └────────────────────┘
             │ crossbeam channel
             ▼
┌──────────────────────────────────────────────────┐
│              Analysis Thread (lib.rs)            │
│                                                  │
│  ┌─────────────────┐    ┌──────────────────────┐ │
│  │  features.rs    │    │    engine.rs         │ │
│  │  FeatureExtract │───▶│  CognitiveStateEngine│ │
│  │  F1..F6 (30s)   │    │  HMM Forward Pass    │ │
│  └─────────────────┘    └──────────────────────┘ │
│                                    │              │
│  ┌─────────────────┐               │              │
│  │  logger.rs      │◀──────────────┘              │
│  │  NDJSON writer  │   feat events                │
│  └─────────────────┘                              │
└──────────────────────────────────────────────────┘
             │ Arc<Mutex<[f64;3]>>
             ▼  (polled every 500ms via Tauri IPC)
┌──────────────────────────────────────────────────┐
│            Frontend (React / TypeScript)         │
│                                                  │
│  App.tsx ──▶ Dashboard.tsx   (probability bars,  │
│          └──▶ Overlay.tsx     mist / wall UI)    │
└──────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Version |
| --- | --- | --- |
| Frontend | React + TypeScript + Vite | React 19, TS 5.8, Vite 7 |
| Backend | Rust + Tauri | Tauri 2.0 |
| Windows API | `windows` crate (Win32 + WinRT) | v0.58 |
| Async runtime | Tokio | v1 |
| IPC channels | crossbeam-channel | v0.5 |
| Logging | tracing + custom NDJSON logger | — |
| Inference | ONNX Runtime (ort) | 2.0.0-rc.0 (reserved) |

---

## Feature Extraction — F1–F6

All features are computed over a **30-second sliding window** on each keypress event.

| Feature | Name | Formula / Definition | Baseline β |
| --- | --- | --- | --- |
| **F1** | Median Flight Time | 5-event moving average of inter-key intervals (ms) | 250 ms |
| **F2** | Flight Time Variance | Variance of all FTs in window | 2000 ms² |
| **F3** | Correction Rate | (Backspace + Delete) / total keypresses | 10 % |
| **F4** | Burst Length | Avg length of typing bursts (consecutive FT < 200 ms) | 2 chars |
| **F5** | Pause Count | Number of inter-key gaps ≥ 2000 ms | 3 per 30 s |
| **F6** | Pause-After-Delete Rate | Fraction of Backspace/Delete presses followed by ≥ 2 s pause | 15 % |

**Normalization:** Each feature is normalized using the personal baseline φ function:

```
φ(x, β) = clamp((x − β) / (2β), 0.0, 1.0)
```

Baselines are calibrated for Surface Pro 8 with Japanese (IME) input patterns.

---

## Stuck Score (S_stuck)

The six normalized features are combined into a single stuck score:

```
S_stuck = 0.30·φ(F1) + 0.10·φ(F2) + 0.15·φ(F3)
        + 0.15·(1 − φ(F4)) + 0.15·φ(F5) + 0.15·φ(F6)
```

EWMA smoothing (α = 0.3) is applied before the HMM step to suppress keystroke-level jitter:

```
S_t = 0.3 · S_raw + 0.7 · S_{t−1}
```

---

## HMM Inference Engine

S_stuck [0, 1] is discretized into 11 observation bins and fed into a 3-state Hidden Markov Model.

### Transition Matrix A (literature-backed, used as fixed smoothing filter in Phase 1)

|  | → Flow | → Incubation | → Stuck |
| --- | --- | --- | --- |
| **Flow** | 0.92 | 0.07 | 0.01 |
| **Incubation** | 0.10 | 0.82 | 0.08 |
| **Stuck** | 0.05 | 0.15 | 0.80 |

Sources:
- **Flow persistence (0.92):** Csikszentmihalyi (1990). Expected duration = 1/(1−0.92) = 12.5 s.
- **Incubation persistence (0.82):** Sio & Ormerod (2009) meta-analysis. Expected duration = 5.6 s.
- **Stuck persistence (0.80):** Hall et al. (2024). Expected duration = 5.0 s.

### Emission Matrix B (3 states × 11 bins)

```
Flow:       [0.35, 0.25, 0.15, 0.10, 0.07, 0.05, 0.02, 0.01, 0.0,  0.0,  0.0 ]
Incubation: [0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.20, 0.10, 0.06, 0.01]
Stuck:      [0.0,  0.0,  0.01, 0.02, 0.05, 0.10, 0.20, 0.30, 0.20, 0.10, 0.99]
```

Bin 10 (S_stuck ≥ 0.91) is the **Backspace streak penalty bin** (≥ 5 consecutive Backspaces → forced bin 10 → P(Stuck) ≈ 1).

### Fallback Rule (Phase 1, low confidence)

If `max(P) < 0.4`, the engine falls back to a hysteresis rule:
- `S_stuck ≥ 0.50` for 5 s → STUCK
- `S_stuck < 0.30` for 3 s → FLOW
- Otherwise → INCUBATION

---

## IME Guard (Japanese Input)

Three-tier detection prevents false Stuck detections during Japanese IME composition:

1. **WinEvent hook (primary)** — monitors `EVENT_OBJECT_IME_CHANGE/SHOW/HIDE` globally via `SetWinEventHook`. Sets `IME_ACTIVE` atomic flag. Covers the romaji→hiragana phase.
2. **EnumWindows scan (secondary)** — checks for visible IME candidate windows by class name (`CandidateUI_UIElement`, `IME`, `*Candidate*`).
3. **UIAutomation (tertiary)** — last-resort check on focused element locale/class.

During IME active state: keystroke analysis is paused (`set_paused(true)`) and EWMA is reset to prevent state contamination.

---

## Visual Feedback

### Dashboard (360×480 px, always-on-top)
- Real-time probability bars for Flow / Incubation / Stuck
- Dominant state label with color coding (green / yellow / red)
- **Mist effect**: after 30 s of dominant Stuck → semi-transparent red overlay fades in

### Overlay Window (full-screen, transparent)
- **Nudge layer**: `stuck > 0.6` → red vignette appears, opacity = (stuck − 0.6) / 0.3
- **Wall layer**: after 30 s of sustained Stuck → full-screen overlay "Time to Move!" — blocked until the device is physically moved (detected via WinRT accelerometer)

---

## Session Logging

Every session is saved as NDJSON to `Documents/GSE-sessions/gse_YYYYMMDD_HHMMSS.ndjson`.

```jsonc
{"type":"meta","session_start":1771605721400}
{"type":"key","t":1771605742429,"vk":162,"press":true}
{"type":"feat","t":1771605742778,"f1":312.0,"f2":1820.0,"f3":0.08,"f4":3.2,"f5":1.0,"f6":0.0,
              "p_flow":0.82,"p_inc":0.14,"p_stuck":0.04}
```

On app exit (`quit_app` command), the logger is flushed and `behavioral_gt.py` is automatically executed for post-session labeling.

---

## File Structure

```text
GSE-Next/
├── src/                           # Frontend (React/TypeScript)
│   ├── components/
│   │   ├── Dashboard.tsx          # Main widget, probability bars, mist effect
│   │   └── Overlay.tsx            # Nudge vignette + Wall blocking overlay
│   ├── App.tsx                    # Root: state polling, wall timer, sensor events
│   ├── App.css                    # Styling, animations, color palette
│   └── main.tsx                   # React entry point
├── src-tauri/                     # Backend (Rust/Tauri 2.0)
│   ├── src/
│   │   ├── analysis/
│   │   │   ├── engine.rs          # CognitiveStateEngine — HMM, S_stuck, EWMA
│   │   │   └── features.rs        # FeatureExtractor — F1–F6, phi(), 30s window
│   │   ├── input/
│   │   │   ├── hook.rs            # WH_KEYBOARD_LL + WinEvent IME hook
│   │   │   └── ime.rs             # ImeMonitor — 3-tier IME detection
│   │   ├── lib.rs                 # Tauri setup, command handlers, thread spawning
│   │   ├── logger.rs              # NDJSON session logger (background thread)
│   │   ├── sensors.rs             # WinRT accelerometer + geolocation (60 Hz)
│   │   └── main.rs                # Binary entry point
│   ├── capabilities/default.json  # Tauri 2.0 permission declarations
│   ├── tauri.conf.json            # Window config, bundle settings
│   └── Cargo.toml                 # Rust dependencies
├── analysis/                      # Python post-processing
│   ├── behavioral_gt.py           # Behavioral ground-truth labeling (F6-based)
│   └── hmm_sensitivity.py         # HMM parameter sensitivity analysis
├── package.json
├── vite.config.ts
└── tsconfig.json
```

---

## Build & Run

### Prerequisites
- Node.js v18+
- Rust (stable)
- Windows SDK (included in Visual Studio Build Tools)

### Commands

```bash
# Install Node dependencies
npm install

# Development (hot-reload)
npm run tauri dev

# Production build
npm run tauri build
```

Output: `src-tauri/target/release/gse-next.exe`

---

## Known Issues

### Memory Exhaustion During Compilation

**Symptom:** `rustc` crashes with `memory allocation failed` or `STATUS_STACK_BUFFER_OVERRUN`.

**Cause:** `windows` crate v0.58 is extremely memory-intensive to compile.

**Fix:**
```bash
RUST_MIN_STACK=67108864 cargo build -j 1
# or for dev:
RUST_MIN_STACK=67108864 npm run tauri dev
```

Alternatively, increase the Windows page file size via:
*System Properties → Advanced → Performance Settings → Virtual Memory*

### Administrator Privileges

The global keyboard hook (`WH_KEYBOARD_LL`) requires that the app run at the same or higher integrity level as the target application. For elevated windows, run GSE-Next as Administrator.

---

## Changelog

### v2.2 — Overlay, Sensors, Session Logger

- Added `Overlay.tsx` with nudge vignette and wall layer
- Added `sensors.rs` for WinRT accelerometer-based wall unlock
- Added `logger.rs` for NDJSON session logging
- Added `analysis/` directory with `behavioral_gt.py` and `hmm_sensitivity.py`
- Post-session: `quit_app` auto-runs `behavioral_gt.py` and opens session folder

### v2.1 — IME Guard & HMM Stability

- **IME fix:** Replaced UIAutomation-only check with 3-tier WinEvent + EnumWindows + UIAutomation detection. Resolves false Stuck during Japanese conversion.
- **EWMA smoothing** (α=0.3) on S_stuck to suppress transient keystroke spikes.
- **HMM tuning:** Raised initial Flow prior 0.50→0.70; lowered Incubation prior 0.40→0.20.
- **Mutex safety:** Replaced all `unwrap()` with poisoning-aware pattern matching.

### v2.0 — Initial GSE-Next Release

- Ported from prototype v1 to Tauri 2.0
- Implemented 6-feature extraction (F1–F6) with personal baseline normalization
- HMM with literature-backed transition matrix
- Global keyboard hook + WinEvent IME detection
