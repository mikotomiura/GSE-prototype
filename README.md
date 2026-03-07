# GSE-Next — Generative Struggle Engine (Prototype v2)

> **Real-time cognitive state estimation from keystroke dynamics on Windows 11**
> Classifies the writer's mental state into **Flow / Incubation / Stuck** using a hand-tuned Hidden Markov Model, without any cloud dependency or user-facing interruption.

[🇯🇵 日本語版 README はこちら](README.ja.md)

---

## Table of Contents

1. [Motivation](#motivation)
2. [Cognitive State Model](#cognitive-state-model)
3. [Architecture Overview](#architecture-overview)
4. [Folder Structure](#folder-structure)
5. [Feature Extraction (F1, F3–F6)](#feature-extraction-f1-f3f6)
6. [HMM Engine](#hmm-engine)
7. [Hysteresis & Stability Fixes (v2.1)](#hysteresis--stability-fixes-v21)
8. [IME Detection and Context-Aware Baseline (v2.2)](#ime-detection-and-context-aware-baseline-v22)
9. [IME Mode Detection: Robust Multi-Layer Architecture (v2.3)](#ime-mode-detection-robust-multi-layer-architecture-v23)
10. [1Hz Timer-Driven Inference & Synthetic Friction (v2.4)](#1hz-timer-driven-inference--synthetic-friction-v24)
11. [Intervention UI: Nudge & Wall (v2.5)](#intervention-ui-nudge--wall-v25)
12. [Session Start Screen & Engine Reset (v2.6)](#session-start-screen--engine-reset-v26)
13. [Frontend–Backend Initial State Sync (v2.7)](#frontendbackend-initial-state-sync-v27)
14. [Security & Reliability Hardening (v2.8)](#security--reliability-hardening-v28)
15. [Centralized State Management & Phone Connection Badge (v2.9)](#centralized-state-management--phone-connection-badge-v29)
16. [EWMA Drift Prevention & Lv2 Timer Stability (v2.10)](#ewma-drift-prevention--lv2-timer-stability-v210)
17. [Analysis Engine Parity & Silence Detection (v2.11)](#analysis-engine-parity--silence-detection-v211)
18. [Hook-Level Repeat Event Forwarding (v2.12)](#hook-level-repeat-event-forwarding-v212)
19. [Logging & Analysis](#logging--analysis)
20. [Build Instructions](#build-instructions)
21. [Academic References](#academic-references)

---

## Motivation

Writers, programmers, and knowledge workers alternate between states of **flow** (effortless, high-output), **incubation** (deliberate pause, sub-conscious processing), and **stuck** (cognitive block, unproductive looping). Real-time awareness of these states could enable adaptive tools—ambient music, nudges, or UI dimming—to scaffold metacognition without disrupting the task itself.

Existing approaches require wearables, cameras, or explicit self-report. This prototype uses only **keystroke timing** (already available from the OS), making it deployable on any Windows device without additional hardware.

---

## Cognitive State Model

The three states are grounded in established cognitive science literature:

| State | Definition | Behavioral Signature |
|---|---|---|
| **Flow** | Effortless, intrinsically motivated task engagement (Csikszentmihalyi, 1990) | Short inter-key intervals, low correction rate, long continuous bursts |
| **Incubation** | Deliberate pause enabling sub-conscious problem restructuring (Sio & Ormerod, 2009) | **High $P(\text{Burst} \mid \text{Pause})$**: Extended silence (≥2 s) followed by rapid output burst |
| **Stuck** | Perseverative failure to escape an impasse (Ohlsson, 1992) | **High $P(\text{Pause} \mid \text{Delete})$**: Perseverative delete-pause loops with near-zero character gain |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Windows 11 (Surface Pro 8)                  │
│                                                                      │
│  ┌─────────────┐   WH_KEYBOARD_LL    ┌──────────────────────────┐  │
│  │  Any App    │ ─────────────────── │   Hook Thread (Rust)     │  │
│  │ (foreground)│                     │  SetWindowsHookExW       │  │
│  └─────────────┘                     │  WinEvent IME monitor    │  │
│                                      └──────────┬───────────────┘  │
│                                                 │ crossbeam channel │
│                                      ┌──────────▼───────────────┐  │
│                                      │  Analysis Thread (Rust)  │  │
│                                      │  ── 1 Hz Timer Gate ──   │  │
│                                      │  FeatureExtractor        │  │
│                                      │    F1 flight-time median │  │
│                                      │    F3 correction rate    │  │
│                                      │    F4 burst length       │  │
│                                      │    F5 pause count        │  │
│                                      │    F6 pause-after-del.   │  │
│                                      │                          │  │
│                                      │  CognitiveStateEngine    │  │
│                                      │    Latent Axes (X, Y)    │  │
│                                      │    EWMA smoothing        │  │
│                                      │    HMM Forward Step      │  │
│                                      │    Hysteresis EMA layer  │  │
│                                      └──────────┬───────────────┘  │
│                                                 │ Tauri IPC         │
│                                      ┌──────────▼───────────────┐  │
│                                      │   React/TS Frontend      │  │
│                                      │   Dashboard + Overlay    │  │
│                                      │   Lv1 Nudge (red mist)   │  │
│                                      │   Lv2 Wall  (full block) │  │
│                                      └──────────┬───────────────┘  │
│                                                 │ unlock            │
│                                      ┌──────────┴───────────────┐  │
│                                      │  Wall Server (tiny_http) │  │
│                                      │  QR code → smartphone    │  │
│                                      └──────────────────────────┘  │
│                                                 │                   │
│                                      ┌──────────▼───────────────┐  │
│                                      │   SessionLogger (Rust)   │  │
│                                      │   NDJSON → Documents/    │  │
│                                      │   GSE-sessions/          │  │
│                                      └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Thread Model

```
Main Thread (Tauri event loop)
    │
    ├─ Hook Thread            ← WH_KEYBOARD_LL message loop + WinEvent IME callbacks
    │       │ crossbeam::channel (bounded 64, non-blocking send)
    │       │ bounded(1) wake channel → IME Polling Thread
    ├─ Analysis Thread        ← recv_timeout(1 s) → 1 Hz timer gate; HMM update ≤ 1×/sec
    │       │ Arc<Mutex<CognitiveStateEngine>> (Tauri managed state)
    │       │ Synthetic Friction: silence ≥ 8 s → ramps F6/F3 toward Stuck
    ├─ IME Monitor Thread     ← polls is_candidate_window_open() every 100 ms (composition pause)
    ├─ IME Polling Thread     ← recv_timeout(100 ms) wake; ImmGetOpenStatus + VK_DBE_* fallback
    │
    ├─ Logger Thread          ← bounded channel(512) → NDJSON file (BufWriter)
    └─ Wall Server Thread     ← tiny_http; QR code served to smartphone for Wall unlock
```

---

## Folder Structure

```
GSE-Next/
├── analysis/
│   ├── behavioral_gt.py       # Post-session behavioral GT labeling
│   └── hmm_sensitivity.py     # Parameter sensitivity analysis
│
├── src/                       # React / TypeScript frontend
│   ├── components/
│   │   ├── Dashboard.tsx      # State probability bars, session stopwatch, keyboard status, Monk Mode, hook warning
│   │   └── Overlay.tsx        # Nudge (red mist) + Wall (full-screen block) + typing warning + phone connection badge
│   ├── App.tsx                # Centralized state polling + intervention state machine (Lv1 → Lv2 escalation)
│   └── main.tsx
│
├── src-tauri/                 # Rust / Tauri 2.0 backend
│   ├── capabilities/
│   │   └── default.json       # Tauri 2.0 capability declarations
│   ├── src/
│   │   ├── analysis/
│   │   │   ├── engine.rs      # HMM + hysteresis layer (display_probs EMA)
│   │   │   ├── features.rs    # F1, F3–F6 extraction + silence synthesis
│   │   │   └── mod.rs
│   │   ├── input/
│   │   │   ├── hook.rs        # WH_KEYBOARD_LL hook + WinEvent IME detection
│   │   │   ├── ime.rs         # ImeMonitor (EnumWindows + UIAutomation fallback)
│   │   │   └── mod.rs
│   │   ├── lib.rs             # Tauri setup, thread orchestration, IPC commands
│   │   ├── logger.rs          # Async NDJSON session logger
│   │   ├── main.rs
│   │   └── wall_server.rs     # HTTP server + QR code; smartphone-based Wall unlock
│   ├── Cargo.toml
│   └── tauri.conf.json
│
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

---

## Feature Extraction (F1, F3–F6)

All features are computed over a **30-second sliding window** of raw keystroke events, updated on every key press. Non-typing keys are filtered at the keyboard hook (before entering the bounded channel). Auto-repeat events (key held down) are forwarded through the channel with an `is_repeat` flag: F1 (flight time) and F4 (burst length) ignore repeats to preserve typing rhythm accuracy, while F3 (correction rate), F5, and F6 include them so that long-press deletions (e.g., holding Backspace) are correctly reflected in Stuck detection. During silence (no input), a synthetic observation is generated every 1 second via `make_silence_observation()` to keep the HMM running.

| Feature | Symbol | Definition | Cognitive Signal |
|---|---|---|---|
| Flight Time Median | **F1** | Median of key-release → key-press intervals (ms) within 30-second window | Typing speed — lower = Flow |
| Correction Rate | **F3** | (Backspace + Delete presses) / total presses | Error frequency — higher = Stuck |
| Burst Length | **F4** | Mean length of consecutive keystroke runs (inter-key gap < 200 ms) | Output fluency — higher = Flow |
| Pause Count | **F5** | Count of inter-press gaps ≥ 2 000 ms within window | Deliberation frequency |
| Pause-after-Delete Rate | **F6** | Fraction of Backspace/Delete presses followed by a ≥ 2 s gap | Post-error freeze — higher = Stuck |

F2 (Flight Time Variance) was removed in v2.11 — it was unused by the HMM latent axis computation and added unnecessary noise.

### Normalization: φ(x, β)

Each raw feature value is mapped to [0, 1] using a baseline-relative linear normalization:

```
φ(x, β) = clamp( (x − β) / (κ · β), 0.0, 1.0 )     κ = 2.0
```

where β is a fixed reference value representing the expected population median.
Values below β return 0.0; values at 3β return 1.0.
This form is analogous to a one-sided z-score with an implicit σ = κ·β.

---

## HMM Engine

### Semantic Latent Axes: Cognitive Friction × Productive Silence

The five normalized features are projected onto two interpretable semantic latent axes before discretization:

```text
X (Cognitive Friction)   = 0.30·φ(F3) + 0.25·φ(F6) + 0.25·φ(F1) + 0.20·φ(F5)
Y (Productive Silence)   = 0.40·φ(F4) + 0.35·(1 − φ(F1)) + 0.25·(1 − φ(F5))
```

**Cognitive Friction ($X$)**: Quantifies the depth of "hesitation" or struggle, heavily weighting the Stuck index $P(\text{Pause} \mid \text{Delete})$ (represented by F6).

**Productive Silence ($Y$)**: Indicates how much a silence leads to a productive burst. This separates valuable DMN-activated incubation from mere cognitive stalling.

Both axes are smoothed with an Exponential Weighted Moving Average (α = 0.30) to suppress single-keystroke noise:
```
ewma_t = 0.30 · raw_t + 0.70 · ewma_{t−1}
```

### Observation Bins

(X, Y) ∈ [0,1]² is discretized into a 5×5 grid (25 bins) plus one penalty bin (obs = 25, triggered by ≥ 14 consecutive Backspace presses):

```
Cognitive Friction X →  0(low)   1      2      3      4(high)
Productive Silence Y ↓
4 (high)     [Flow]  [Flow]  [   ]  [   ]  [    ]
3            [Flow]  [Flow]  [   ]  [   ]  [    ]
2            [    ]  [    ]  [ ? ]  [Stk]  [Stk ]
1            [Inc ]  [Inc ]  [Inc]  [Stk]  [Stk ]
0 (low)      [Inc ]  [Inc ]  [ ? ]  [Stk]  [Stk ]
```

### HMM Forward Step

At each update, the belief vector **π** = [p_Flow, p_Inc, p_Stuck] is propagated by a single Forward Algorithm step:

```
π'_j = ( Σ_i  π_i · A[i,j] ) · B[j, obs]    for j ∈ {0, 1, 2}
π'   ← π' / Σ_j π'_j                         (normalize to sum = 1)
```

- **A** = 3×3 transition matrix (rows = from, cols = to)
- **B** = 3×26 emission matrix (state × observation bin); minimum value = 0.01 (static floor baked into the table, prevents probability absorption)

### Transition Matrix A

| From \ To | Flow | Incubation | Stuck |
|---|---|---|---|
| **Flow** | 0.75 | 0.17 | 0.08 |
| **Incubation** | 0.12 | 0.80 | 0.08 |
| **Stuck** | 0.06 | 0.18 | 0.76 |

Flow self-transition 0.75 → mean dwell ≈ 4 s (reduced from 0.80 to mitigate "Flow gravity" — the tendency to stay in Flow even when friction rises).
Incubation 0.80 → consistent with Sio & Ormerod (2009): incubation typically lasts seconds to minutes.
Stuck 0.76 → consistent with high perseveration tendency (Ohlsson, 1992).

---

## Hysteresis & Stability Fixes (v2.1)

Three pathological behaviors were identified from session log analysis and corrected:

---

### Fix ①: Cold-Start Hysteresis (Stuck → Flow window-reset spike)

**Theoretical Note: O(1) Alternative to HSMM**
Standard HMMs cannot model state duration distributions explicitly (they assume geometric decay). While a Hidden Semi-Markov Model (HSMM) is theoretically optimal for modeling the distinct, non-geometric durations of Incubation and Stuck, it introduces $O(T^2)$ computational complexity and requires massive data to estimate duration parameters (overfitting in $n=1$ environments). The EMA hysteresis layer introduced below acts as an $O(1)$ computational hack to enforce minimum state dwell times without the overhead of an HSMM, making it ideal for edge inference.

**Problem:** At t = 255.2 s a 30-second window advanced past heavy backspacing activity. The deleted events exited the window; fresh-window features looked like Flow. Result: `p_stuck = 0.994 → p_flow = 0.48` in one HMM step (< 1 ms).

**Root cause:** `get_current_state()` returned the raw HMM belief, which is a point estimate with no temporal inertia.

**Fix:** A secondary probability vector `display_probs` is maintained alongside the raw HMM belief. It tracks the raw belief via a slow EMA:

```
display_t = α · raw_t + (1 − α) · display_{t−1}

α = 0.40  (normal updates → time-constant τ ≈ 2.5 updates ≈ 2.5 s)
α = 0.60  (backspace-penalty bin during active typing → rapid Stuck onset)
α = 0.50  (backspace-penalty bin during silence → moderate Stuck onset)
```

`get_current_state()` returns `display_probs`. A genuine state change now requires approximately 2.5 seconds of sustained evidence to register in the UI and log.

Simulation of the window-reset scenario (α = 0.40, raw p\_stuck ≈ 0 after reset):

| Tick | raw p_flow | display p_stuck |
|---|---|---|
| 0 (before reset) | 0.01 | **0.994** |
| 1 (reset, flow signal) | 0.48 | 0.596 |
| 2 | 0.52 | 0.358 |
| 3 | 0.54 | 0.215 |
| 4 | 0.56 | 0.129 |

The Stuck display probability decays gracefully over ~2.5 seconds rather than collapsing instantly.

---

### Fix ②: Probability Discrete Clustering (step-wise ceilings)

**Problem:** With dynamic emission floor ε = 0.05 added to every bin at runtime, the HMM converged to fixed-point probabilities:
- `p_flow` clustering at 0.9734 (39.1% of frames)
- `p_inc` clustering at 0.9381
- `p_stuck` clustering at 0.9944

These clusters arise because for observation bins dominated by one state, the ratio of emission probabilities determines a unique fixed point. With ε = 0.05 the penalty-bin ratio is only 0.99/0.05 ≈ 20×, blunting the Backspace-streak Stuck signal significantly.

**Fix:** Dynamic additive floor removed. Emission values of exactly 0.00 are replaced with a static **0.01** baked into the emission table. The penalty-bin ratio improves to 0.99/0.01 ≈ 99×, sharply increasing Stuck sensitivity to repeated Backspace bursts. Maximum attainable probability per state now saturates near 0.88–0.90, leaving meaningful mass for competing states.

---

### Fix ③: Inc → Stuck Silence Transition (50 s no-input stays Inc)

**Problem:** Long silences (≥ 50 s) were classified as Incubation because `make_silence_observation()` only populated F5 (pause count). The maximum X (Friction) achievable from F5 alone is:

```
X_max(F5 only) = 0.20 · φ(F5) = 0.20 · 1.0 = 0.20   → x_bin = 1 (Incubation)
```

The Stuck-dominant bins require x_bin ≥ 3 (X ≥ 0.60), which was unreachable without F3 or F6.

**Cognitive rationale:** Prolonged output silence is not semantically equivalent to deliberate incubation. When a writer stares at a screen without typing for over 30 seconds, the behavioral interpretation shifts from "thinking" toward "blocked." Synthesizing friction during extreme silence reflects this cognitive transition.

**Fix:** `make_silence_observation()` now generates synthetic friction values with early onset and guaranteed floor values:

```rust
// F6: onset at 8 s, floor 0.15 at ≥10 s, reaches 0.50 at ~33 s
F6_synthetic = if silence ≥ 10s { max(clamp((s−8)/50, 0, 0.50), 0.15) }
              else              { clamp((s−8)/50, 0, 0.50) }

// F3: onset at 15 s, floor 0.20 at ≥10 s, reaches 0.40 at ~47 s
F3_synthetic = if silence ≥ 10s { max(clamp((s−15)/80, 0, 0.40), 0.20) }
              else              { clamp((s−15)/80, 0, 0.40) }
```

Resulting X trajectory (with F5 saturated at φ = 1.0, typical F1):

| Silence | F3_syn | F6_syn | X (Friction) | x_bin | Region |
|---|---|---|---|---|---|
| 8 s | 0.00 | 0.00 | ≈ 0.20 | 1 | Incubation |
| 10 s | 0.20 | 0.15 | ≈ 0.34 | 1 | Incubation |
| 20 s | 0.20 | 0.24 | ≈ 0.38 | 1 | Boundary |
| 33 s | 0.23 | 0.50 | ≈ 0.64 | 3 | **Stuck** |

The early onset (8 s for F6, 15 s for F3) and guaranteed floor values at ≥10 s ensure that the HMM begins transitioning toward Stuck significantly earlier than the original thresholds (20 s / 30 s). Combined with the EWMA and hysteresis layers, the Stuck label is confirmed after ~15 s of sustained silence.

---

## IME Detection and Context-Aware Baseline (v2.2)

Japanese IME input introduces two distinct challenges for keystroke analysis:

1. **Candidate selection phase** (space → kanji list visible): navigation keystrokes (arrow, Enter) should not pollute feature vectors
2. **Input mode context** (あ mode vs A mode): flight-time norms differ significantly between Japanese writing and ASCII coding

### Candidate Window Suppression

When the kanji candidate list is visible, analysis is paused and the display state is held at Flow. Two detection layers are used:

| Layer | Method | Notes |
|---|---|---|
| **Primary** | `EnumWindows` scan for "CandidateUI" / "IME" window classes | Direct cross-process window scan, no hooks required |
| **Secondary** | UIAutomation `GetFocusedElement` | Fallback when focused element is the IME candidate panel |

Global TSF hooks (`ITfThreadMgr`) are not used — they are blocked by UIPI across process boundaries.

**MSCTFIME UI is explicitly excluded:** This class belongs to the TSF language bar (the A/あ indicator on the taskbar), which is always visible when Japanese IME is loaded. Including it would cause a permanent false positive.

### IME Mode Detection via VK\_DBE\_\* Keys (v2.2)

**Why `VK_PROCESSKEY` does not work:** `WH_KEYBOARD_LL` fires before the IME engine processes input. Keys typed during composition therefore arrive as their raw codes (`VK_A`, `VK_I`, etc.), not as `VK_PROCESSKEY` (0xE5). This is by design — the low-level hook is below the IME layer.

**What does work:** Windows delivers IME mode-switch keys — `VK_DBE_ALPHANUMERIC` (0xF0), `VK_DBE_HIRAGANA` (0xF2), `VK_DBE_KATAKANA` (0xF1), etc. — to `WH_KEYBOARD_LL` before IME processing, because these are hardware-level input mode toggles. **Empirical confirmation:** `VK_DBE_ALPHANUMERIC` (vk = 240) was observed 14 times in session log `gse_20260222_074741.ndjson`, proving that mode-switch keys reach the hook reliably.

The hook thread maintains `IME_OPEN: AtomicBool`:

| VK Code | Value | Effect on `IME_OPEN` |
|---|---|---|
| `VK_DBE_ALPHANUMERIC` (0xF0) | Switch to alphanumeric (A) | → `false` |
| `VK_DBE_SBCSCHAR` (0xF3) | Single-byte mode | → `false` |
| `VK_DBE_HIRAGANA` (0xF2) | Hiragana mode (あ) | → `true` |
| `VK_DBE_KATAKANA` (0xF1) | Katakana mode (カ) | → `true` |
| `VK_DBE_DBCSCHAR` (0xF4) | Double-byte mode | → `true` |
| `VK_KANJI` (0x19) | Half/full-width toggle | → flip |

**Limitation:** The initial state is assumed `false` (alphanumeric). The flag becomes accurate after the first mode-switch key is pressed.

### Context-Specific Baseline β (Dual Baseline)

The `φ(x, β)` normalization function uses different reference values depending on the current IME mode, correcting a systematic bias:

| Context | `IME_OPEN` | β\_F1 (ms) | β\_F3 | β\_F4 | β\_F5 | β\_F6 |
| --- | --- | --- | --- | --- | --- | --- |
| **β\_coding** (A mode) | `false` | 150 | 0.06 | 5.0 | 2.0 | 0.08 |
| **β\_writing** (あ/カ mode) | `true` | 100 | 0.10 | 2.5 | 1.0 | 0.12 |

**Why this matters:** A coder at 150 ms flight time appears as Flow against β\_coding but would incorrectly appear as Stuck if evaluated against the slower β\_writing baseline (and vice versa). Context switching eliminates this systematic misclassification.

IME mode changes are logged as a new record type:

```jsonc
// IME mode switch: user pressed VK_DBE_HIRAGANA (→ Japanese writing mode)
{"type":"ime_state","t":1740000001234,"on":true}

// IME mode switch: user pressed VK_DBE_ALPHANUMERIC (→ alphanumeric/coding mode)
{"type":"ime_state","t":1740000005678,"on":false}
```

---

## IME Mode Detection: Robust Multi-Layer Architecture (v2.3)

Version 2.2 described the initial VK\_DBE\_\* based IME mode detection. Empirical testing on a Surface Pro 8 Type Cover revealed three additional failure modes that required a complete rework of the detection pipeline.

### Bugs Found and Fixed

**Bug 1 — Same-millisecond flapping** (log `gse_20260225_142614.ndjson`):
The analysis thread emitted `ImeState` entries at the exact same millisecond as the triggering keystroke, producing `on:true` + `on:false` pairs with identical timestamps. Root cause: the analysis thread computed IME state synchronously from the keystroke event timestamp.

**Bug 2 — Zero detections via `ImmGetContext`** (log `gse_20260225_153634.ndjson`):
A pure polling approach using `ImmGetContext(foreground_hwnd)` returned NULL for all cross-process windows on Windows 10/11. The system silently produced zero `ime_state` entries.

**Bug 3 — Surface Type Cover keyboard asymmetry** (log `gse_20260225_162114.ndjson`):
On this specific keyboard, `VK_DBE_HIRAGANA` (0xF2) fires **only as key-UP** and `VK_DBE_ALPHANUMERIC` (0xF0) fires **only as key-DOWN**, always paired within the same millisecond. The `is_press`-only handler in v2.2 missed the hiragana key entirely.

**Bug 4 — Initial state never emitted**:
With `last_state: bool = false` and `IME_OPEN` initialized to `false`, pressing `VK_DBE_ALPHANUMERIC` set `IME_OPEN = false` (no change), making `false != false` evaluate to `false` — no emission.

### v2.3 Architecture: Three Detection Layers

```
Layer 1 (Primary): ImmGetOpenStatus polling
  └─ Works when ImmGetContext returns non-NULL (rare: own-process windows only)

Layer 2 (Fallback): VK_DBE_* atomic tracking via IME_STATE_DIRTY flag
  ├─ hook_callback sets IME_OPEN + IME_STATE_DIRTY on both key-DOWN and key-UP
  └─ Covers Surface Type Cover asymmetry (VK_DBE_HIRAGANA key-UP only)

Layer 3 (Inference): WinEvent EVENT_OBJECT_IME_CHANGE/SHOW
  └─ Composition can ONLY start in Japanese mode → infer IME_OPEN=true cross-process
```

### Anti-Flapping Guarantee

`LogEntry::ImeState` is emitted **exclusively** from the IME Polling Thread, never from the keyboard hook or analysis thread. The flow is:

```
hook_callback (key-DOWN or key-UP)
    │  atomic store: IME_OPEN = new_state
    │  atomic store: IME_STATE_DIRTY = true
    └─ try_send(()) on bounded(1) wake channel (non-blocking, drops if full)

IME Polling Thread
    │  recv_timeout(100ms)   ← wakes within 1ms of keypress signal
    │  sleep(5ms)            ← allows IME engine to settle
    │  read IME_STATE_DIRTY  ← check if state changed
    │  emit LogEntry::ImeState { timestamp: SystemTime::now(), on }
    └─ timestamp is always ≥5ms after the triggering keystroke
```

### Key Atomics (`hook.rs`)

| Atomic | Writer | Reader | Purpose |
|---|---|---|---|
| `IME_OPEN` | hook (VK_DBE_* ↑↓, WinEvent), polling thread | analysis thread | Current IME mode |
| `IME_STATE_DIRTY` | hook (VK_DBE_* ↑↓, WinEvent composition start) | polling thread (`.swap(false)`) | Triggers log emission |
| `IME_ACTIVE` | WinEvent hook (composition start/end) | ImeMonitor (100ms poll) | Candidate window pause |

### `Option<bool>` Initial State

The polling thread tracks `last_state: Option<bool> = None` (not `bool = false`). The comparison:

```rust
if last_state.map_or(true, |prev| prev != current) { emit(); last_state = Some(current); }
```

ensures the **first detection always emits** regardless of whether the initial state is `false` or `true`.

### Production Verification

Log `gse_20260225_172338.ndjson` confirms the fix:

| Observation | Result |
|---|---|
| `ime_state` entries detected | **9** (vs. 0 in v2.2) |
| Same-timestamp flapping | **None** |
| Minimum key → ime\_state lag | **5 ms** (VK\_DBE\_* path) |
| WinEvent composition inference lag | **~23–38 ms** |
| Alternating on/false pattern | **Correct** |

---

## 1Hz Timer-Driven Inference & Synthetic Friction (v2.4)

### Decoupling from Keystroke Events

In the initial implementation, the HMM was updated synchronously on every keystroke. This caused the EMA hysteresis layer (τ ≈ 4 seconds) to behave inconsistently: during fast typing (10+ keys/sec), the α = 0.25 update accumulated far more than once per second, while during silence the system received no updates at all.

**Fix:** The analysis thread now enforces an **independent 1 Hz timer gate** using `Instant`-based absolute time scheduling. A `next_engine_update` timestamp advances by exactly 1 second after each HMM step. The `recv_timeout` duration is dynamically computed as the remaining time until the next scheduled update:

- **Keystroke arrives:** Event is buffered and features are extracted. The HMM step executes only when `Instant::now() >= next_engine_update`.
- **Timeout (no input):** A synthetic silence observation is generated via `make_silence_observation()` and fed to the HMM.
- **Clock drift protection:** If `next_engine_update` falls behind `now` (e.g. after a system sleep), it is reset to `now + 1s` to prevent burst catch-up.

This decoupling ensures exactly **one HMM forward step per second**, making the EMA time constant τ = 1/α ≈ 4 updates = **4 seconds** mathematically precise regardless of typing speed.

### Synthetic Friction

When the 1 Hz timer fires during extended silence, `make_silence_observation()` generates **synthetic friction** — artificial F3 (correction rate) and F6 (pause-after-delete rate) values that ramp up linearly with silence duration. This mechanism ensures that prolonged inactivity (≥ 50 s) transitions the HMM from Incubation to Stuck, reflecting the cognitive shift from deliberate pause to unproductive stalling. See **Fix ③** in the Hysteresis section above for the detailed derivation and trajectory table.

---

## Intervention UI: Nudge & Wall (v2.5)

When the HMM detects a Stuck state, the system provides graduated intervention through Tauri's transparent multi-window overlay system.

### Two-Level Intervention

| Level | Name | Trigger | Visual Effect | User Interaction |
| --- | --- | --- | --- | --- |
| **Lv1** | Nudge | p\_stuck > 0.60 | Red vignette (mist) around screen edges | Click-through (transparent to input) |
| **Lv2** | Wall | p\_stuck > 0.70 for 30 s (**bypassed when Monk Mode is ON**) | Full-screen blocking overlay with message; red warning banner on any keyboard input | Blocks all input until unlocked |

### Nudge (Lv1): Ambient Friction Cue

The Nudge layer renders a semi-transparent red vignette overlay whose opacity scales linearly with the Stuck probability:

```text
opacity = clamp((p_stuck − 0.60) / 0.30, 0.0, 1.0)
```

The overlay window is set to **click-through** mode via Tauri's `setIgnoreCursorEvents(true)`, allowing the user to continue working while receiving a peripheral visual cue that they may be stuck.

### Wall (Lv2): Forced Break

If p\_stuck accumulates above 0.70 for a total of 30 seconds (cumulative, not consecutive — partial recovery below 0.50 causes 2× speed decay; the 0.50–0.70 range freezes the timer), the system escalates to a Wall — a full-screen blocking overlay that requires **physical movement** to dismiss. The overlay displays:

> *"Time to Move! Please stand up and walk around to unlock."*

The Wall is unlocked **exclusively by the smartphone timer**. When the Wall activates, `start_wall_server` launches a local HTTP server (`tiny_http`) and generates a QR code. The user scans the QR code, which opens a 2-minute countdown page on their phone. When the timer reaches 0:00, the phone automatically POSTs to `/unlock`, the server emits `"sensor-accelerometer"` with `"move"` payload, and the Wall dismisses. There is no early-exit button and no PC-side fallback timer — the 2-minute wait is intentional. If the user does not want the Wall to engage at all, they can enable **Monk Mode** from the Dashboard beforehand. Any keyboard input detected while the Wall is active triggers a **warning banner** on the overlay. This approach requires no HTTPS — the unlock signal travels over the local network from phone to PC.

### Monk Mode (Wall Suppression Toggle)

The Dashboard provides a **Monk Mode** toggle that disables automatic Wall activation. When Monk Mode is **ON**, the LV2 Wall timer is bypassed — the system continues estimating cognitive state and showing Nudge overlays, but the full-screen Wall intervention is suppressed. Toggling the button emits a `monk-mode-changed` boolean event (Tauri frontend broadcast) which both windows receive and use to sync their `isMonkMode` state. The LV2 timer condition becomes `p_stuck > 0.70 && !isMonkMode`. This allows users to enter a focused, uninterrupted deep work session without risk of forced breaks.

### Dashboard Session Indicators

The Dashboard panel shows two live indicators alongside the state bars:

| Indicator | Source | Display |
| --- | --- | --- |
| **Session** | `Date.now()` on mount | Stopwatch (`M:SS` or `H:MM:SS`) |
| **Keyboard** | `get_keyboard_idle_ms()` (reads `LAST_KEY_MS` atomic) | `Active` if idle < 3 s, else `Idle Xs` |

The `get_keyboard_idle_ms` Tauri command returns `now_ms − LAST_KEY_MS`, where `LAST_KEY_MS` is the `AtomicU64` updated on every keystroke in `hook_callback`. This is used for dashboard display only — Wall unlock is driven by the phone timer, not PC-side idle detection.

### Design Rationale

This graduated intervention is grounded in the insight that cognitive blocks often persist because the writer lacks awareness of being stuck (metacognitive failure). The Nudge provides gentle awareness without disruption; the Wall enforces a physical context switch, which research suggests facilitates problem restructuring (Sio & Ormerod, 2009).

---

## Session Start Screen & Engine Reset (v2.6)

### Problem

Previous versions started keystroke detection and HMM inference immediately on app launch. This caused two issues:

1. **Dirty warm-up data**: Keystrokes during app startup fed the HMM before a meaningful session began
2. **Misleading initial display**: The hardcoded `useState` initial value (`stuck: 0.8`) showed "Stuck: 80%" before any real inference had occurred

### Solution: Explicit Session Boundary

A **Start Screen** is shown on app launch. Detection does not begin until the user clicks "開始する" (Start). On click, `invoke("start_session")` calls the Rust backend which:

1. **Resets `CognitiveStateEngine`**: returns all HMM state to Flow-biased initial priors `[0.80, 0.15, 0.05]` (most users start sessions in a fluent state), clearing `display_probs`, `axes_ewma`, and `backspace_streak`
2. **Flushes `FeatureExtractor`**: an `Arc<AtomicBool>` signal is set; the analysis thread clears all keystroke buffers and drains any queued key events
3. **Logs session boundary**: `LogEntry::SessionStart { timestamp }` is written to the NDJSON log

The React session timer starts from the click moment (not from app launch).

### Benefits

| Before (v2.5) | After (v2.6) |
|---|---|
| Detection starts immediately on launch | Detection starts on explicit user action |
| Session timer starts at app launch | Session timer starts when user clicks "Start" |
| HMM may be dirty from pre-session keystrokes | HMM always starts clean from initial priors |
| No session boundary in log | `session_start` marker in NDJSON log |

---

## Frontend–Backend Initial State Sync (v2.7)

### Background

After the parameter tuning that updated the backend's initial priors from `[0.5, 0.3, 0.2]` to `[0.80, 0.15, 0.05]`, the React `useState` initial value remained at `{flow: 0.5, incubation: 0.3, stuck: 0.2}`. This caused a visible probability jump (flicker) immediately after the first `get_cognitive_state` poll returned data aligned with the new priors.

### Resolution

The `cognitiveState` initial value in `App.tsx` is synchronized with the backend's `initial_probs`:

```tsx
const [cognitiveState, setCognitiveState] = useState<CognitiveStateRaw>({
  flow: 0.80,
  incubation: 0.15,
  stuck: 0.05,
});
```

The UI now displays consistent values from launch to the first data poll (~500 ms), eliminating the cold-start flicker.

---

## Security & Reliability Hardening (v2.8)

Six independent bugs and reliability gaps were identified and resolved, aligned with the macOS reference implementation.

---

### Fix ①: F1 30-Second Window (Feature Consistency Bug)

**Problem:** `F1` (flight-time median) was computed from the full accumulated `flight_times` buffer (up to 600 events, ~10 min of history), while `F2`–`F6` were computed from a 30-second sliding window. This inconsistency caused F1 to respond far more slowly to recent typing rhythm changes than the other features, systematically biasing the HMM observation toward past behaviour.

**Fix:** `F1` is now computed from the same 30-second `window_fts` vector used for the other features, ensuring all features reflect the same temporal scope.

---

### Fix ②: Pre-Session Event Drain (`SessionActive` gate)

**Problem:** The analysis thread processed keystrokes from app launch, before the user clicked "開始する". Keystrokes typed while navigating the start screen (e.g. alt-tab, window focus) entered the feature buffer and subtly biased the initial HMM prior.

**Fix:** A `SessionActive(Arc<AtomicBool>)` flag is introduced, initialized to `false`. The analysis thread drains (discards) all incoming key events via `try_recv()` until `start_session` sets the flag to `true`. The bounded channel (cap = 64) is also kept from overflowing during the pre-session phase.

---

### Fix ③: Backspace Streak — Atomic Decoupling & Penalty Race Fix

**Problem:** `backspace_streak` was stored as `Arc<Mutex<u32>>`. Every keystroke (including at 10+ keys/sec) acquired and released the mutex twice (once in `register_keystroke`, once in `update()`), adding unnecessary lock overhead. A secondary race condition also existed: if BS×8 set the streak to the penalty threshold and the next non-BS key immediately reset it to 0 before `update()` ran, the penalty was silently dropped.

**Fix:** Changed to `Arc<AtomicU32>`. A new `has_pending_penalty: Arc<AtomicBool>` flag is set by `register_keystroke` when the streak reaches the penalty threshold and is consumed (via `swap(false, AcqRel)`) by `update()` — surviving any streak reset in between. `is_paused` was similarly converted from `Arc<Mutex<bool>>` to `Arc<AtomicBool>`. All three atomics eliminate mutex overhead on the hot path.

---

### Fix ④: Channel-Based Logger Shutdown

**Problem:** `quit_app` used `thread::sleep(400 ms)` to give the logger thread time to flush and close the NDJSON file before proceeding to Python post-processing. This was a race: under load the flush could take longer than 400 ms, corrupting the session file.

**Fix:** `SessionLogger::start()` now returns a `Receiver<()>` (`shutdown_rx`) in addition to the `Sender<LogEntry>`. When `LogEntry::End` is processed and the file is flushed, the logger thread sends `()` on this channel. `quit_app` waits on `shutdown_rx.recv_timeout(2000 ms)` — a correct, bounded synchronization instead of a blind sleep.

---

### Fix ⑤: WallServer Cleanup on Quit

**Problem:** `quit_app` did not stop the WallServer. On app exit the HTTP server thread kept running and the dynamically-added Windows Firewall rule (`GSE-WallServer-<port>`) was left in place.

**Fix:** Added `WallServerState::stop()` which signals the server thread and calls `netsh` to remove the firewall rule. `quit_app` now calls `wall.stop()` as its first action.

---

### Fix ⑥: CSP & Hook Status API

**Content Security Policy:** `tauri.conf.json` `csp` was `null` (no restrictions). Changed to `"default-src 'self'; style-src 'self' 'unsafe-inline'"`, restricting all resource loads to same-origin and limiting inline styles.

**`get_hook_status` command:** Added for macOS API compatibility. The macOS version requires an explicit system permission prompt before the keyboard hook can be installed; this command exposes that status to the frontend. On Windows no prompt is needed, so the command unconditionally returns `true`.

---

## Centralized State Management & Phone Connection Badge (v2.9)

### Unified Polling & Timer in App.tsx

Previously, `App.tsx` used three independent `useEffect` hooks: one for cognitive state polling (500 ms), one for keyboard idle + hook status polling (1000 ms), and one for the Lv2 Wall cumulative timer (triggered by React render). This caused two problems:

1. **Redundant polling**: `get_hook_status` was polled every second despite being a static value (always `true` on Windows; set once at permission grant on macOS).
2. **Timer drift**: The Lv2 cumulative timer relied on `useEffect` dependency triggers, making its elapsed-time calculation dependent on React's rendering interval rather than wall-clock time.

**Fix:** The three hooks are consolidated into a single architecture:

- **`hookActive`** (`boolean | null`, initial `null`) is fetched **once on mount** — not polled:

```tsx
useEffect(() => {
  invoke<boolean>("get_hook_status")
    .then((active) => setHookActive(active))
    .catch(() => setHookActive(true)); // optimistic fallback
}, []);
```

- **A single 500 ms `setInterval`** fetches `get_cognitive_state` and `get_keyboard_idle_ms` via `Promise.all`, then computes the Lv2 timer in the same block using `Date.now()`-based elapsed time:

```tsx
const [state, idle] = await Promise.all([
  invoke<CognitiveStateRaw>("get_cognitive_state"),
  invoke<number>("get_keyboard_idle_ms"),
]);
// Lv2 timer computed here with Date.now() — no render-dependency drift
```

`Dashboard.tsx` no longer contains any `invoke()` calls or `setInterval` polling — it is a pure presentational component receiving all data via props.

### Permission Warning Banner (Dashboard)

When `hookActive === false`, a rich permission banner (class `permission-banner`) is displayed at the top of the Dashboard with step-by-step instructions for granting Input Monitoring access via System Settings. On Windows, `get_hook_status` always returns `true`, so this banner is never shown. The code exists for codebase unification with the macOS version.

### Wall Unlock Screen (Overlay)

The Wall overlay (displayed when `isWallActive` is true) provides a user-friendly unlock flow ported from the macOS version:

- **QR container** (`qr-container`): wraps the QR code image with a camera hint ("Open camera app and point at QR code") and the server URL
- **Network troubleshooting hint** (`wall-network-hint`): reminds the user to ensure PC and phone are on the same Wi-Fi
- **Phone connection badge**: when the smartphone connects to the Wall Server, a "Phone connected — Zen Timer running" badge appears
- **Typing warning**: if the user attempts to type during the Wall, a warning banner is shown for 2.5 seconds

---

## EWMA Drift Prevention & Lv2 Timer Stability (v2.10)

### Silence-Specific HMM Update (`update_silence`)

During keyboard inactivity (silence ticks), the standard `update()` method (α=0.30) would feed extreme idle-period features into the EWMA smoother too aggressively, causing rapid drift toward high-Friction values.

**Fix:** A dedicated `update_silence()` method in `engine.rs` performs HMM transition and emission updates with a **reduced EWMA learning rate** (α=0.15 normal, α=0.25 for deep silence ≥15 s). This allows the EWMA to respond to sustained silence without the aggressive drift of the normal α=0.30:

```rust
pub fn update_silence(&self, features: &Features, ime_open: bool, silence_secs: f64) {
    let alpha = if silence_secs >= 15.0 { 0.25 } else { 0.15 };
    // EWMA update with reduced α — responds to silence without aggressive drift
    ewma.0 = alpha * raw_x + (1.0 - alpha) * ewma.0;
    ewma.1 = alpha * raw_y + (1.0 - alpha) * ewma.1;
    // HMM forward step uses updated EWMA position
    // ...
}
```

### Ref Mirror Pattern for Lv2 Timer

Previously, `isWallActive` and `isMonkMode` were included in the unified polling `useEffect`'s dependency array. This caused the `setInterval` to be torn down and recreated whenever these values changed, introducing timing gaps in the Lv2 cumulative timer.

**Fix:** State values are mirrored into refs, and the interval reads from refs instead:

```tsx
const isWallActiveRef = useRef(isWallActive);
const isMonkModeRef = useRef(isMonkMode);
useEffect(() => { isWallActiveRef.current = isWallActive; }, [isWallActive]);
useEffect(() => { isMonkModeRef.current = isMonkMode; }, [isMonkMode]);

// Dependency array: only [isStarted, windowLabel] — no teardown on Wall/Monk toggle
```

This ensures the 500 ms interval runs continuously without interruption, and `Date.now()`-based elapsed calculations remain accurate across Wall activation and Monk Mode toggles.

---

## Analysis Engine Parity & Silence Detection (v2.11)

Sixteen fixes from the macOS reference implementation were evaluated for applicability to the Windows version. All platform-independent analysis engine improvements were ported, achieving feature parity between both platforms.

---

### Fix ①: F2 Removal (Dead Feature)

F2 (Flight Time Variance) was not used in either the Cognitive Friction (X) or Productive Silence (Y) axis computations. It was removed from the `Features` struct, `FeatureExtractor::calculate_features()`, `make_silence_observation()`, `LogEntry::Feat`, and the logger format string. This eliminates unnecessary computation and log bloat.

---

### Fix ②: Key Repeat & Non-Typing Key Filtering (Hook + Feature Extractor)

**Problem:** Key repeat events (holding a key down) inflated flight time calculations with artificial zero-interval entries. Non-typing keys (arrow keys, function keys, IME mode keys) introduced noise unrelated to typing rhythm. All raw key events consumed bounded channel capacity (64 slots) regardless of analytical relevance.

**Fix:** Two-layer filtering ensures clean typing data reaches the HMM:

1. **Hook-level gate** (`hook_callback`): `is_typing_key()` filters non-typing keys *before* they enter the crossbeam channel. `PRESSED_KEYS: Mutex<HashSet<u32>>` detects auto-repeat events and tags them with `is_repeat: true` in the `InputEvent` struct (v2.12). Repeat events are forwarded to the analysis thread so that long-press deletions (e.g., holding Backspace) contribute to F3/F5/F6 and trigger the Backspace streak penalty. `LAST_KEY_MS` (idle detection) and `POLL_WAKE_TX` (IME polling wake) remain unconditional for all keys.
2. **Feature extractor** (`calculate_features()`): F1 (flight time) and F4 (burst length) skip events where `is_repeat == true`, preserving typing rhythm accuracy. F3, F5, and F6 include repeat events to accurately reflect deletion volume.

`is_typing_key()` covers A–Z, 0–9, Numpad keys (0x60–0x6F), OEM symbol keys, Backspace, Enter, Space, Tab, and Delete.

---

### Fix ③: BS Penalty Threshold 8 → 14 (IME Compatibility)

**Problem:** Japanese IME composition routinely generates 8–12 consecutive Backspace presses during normal editing (e.g. deleting a mis-converted word). The threshold of 8 triggered false Stuck penalties during ordinary Japanese writing.

**Fix:** The Backspace streak penalty threshold was raised from 8 to 14. Additionally, the penalty is now guarded by IME mode: when `ime_open == true`, the penalty is suppressed entirely, since Backspace during IME composition is a normal editing operation, not an indicator of cognitive struggle.

---

### Fix ④: β\_writing Recalibration

**Problem:** The β\_writing baseline values (F1=220, F3=0.08, F4=2.0, F5=4.0) were set before empirical IME typing data was available. F1=220 ms was far too high (IME typing typically produces ~100 ms flight times due to rapid romaji input), and F5=4.0 was too lenient (allowing 4 pauses before registering any friction).

**Fix:** Recalibrated to F1=100, F3=0.10, F4=2.5, F5=1.0 based on observed Japanese writing sessions. These values correctly position normal IME typing in the Flow region while remaining sensitive to genuine hesitation.

---

### Fix ⑤: Independent 1Hz Gate Architecture

**Problem:** The original `recv_timeout(1000ms)` approach drifted by the processing time of each iteration (feature extraction + HMM update), accumulating ~50–100 ms error per minute.

**Fix:** Replaced with `Instant`-based absolute time scheduling. A `next_engine_update` timestamp advances by exactly 1 second after each HMM step. The `recv_timeout` duration is dynamically computed as `next_engine_update - now`. If the scheduled time falls behind (e.g. after system sleep), it resets to `now + 1s` to prevent burst catch-up. See the updated v2.4 section for details.

---

### Fix ⑥: Ongoing Silence F5 Augmentation

**Problem:** `calculate_features()` only counts completed pauses within the 30-second window. During an ongoing 12-second silence, only past pauses are counted — the current silence is invisible to F5 until the user resumes typing.

**Fix:** After `calculate_features()` returns, if `silence_secs >= 2.0` and the buffer contains real data (`f1 > 0`), the current silence duration is added to F5: `features.f5_pause_count += silence_secs / 2.0`. This ensures the HMM observes ongoing silence in real time.

---

### Fix ⑦: Silence-Break Protection (3-Keystroke Gate)

**Problem:** A single accidental keypress after a long silence (e.g. bumping the keyboard) would reset the silence timer, causing the HMM to immediately receive a normal `update()` with α=0.30 — snapping the EWMA back toward Flow and erasing the accumulated silence signal.

**Fix:** After ≥10 seconds of silence, the analysis thread requires 3 consecutive key presses before treating input as genuine resumed typing. Until 3 presses are reached, the silence timer continues running and `update_silence()` is used instead of `update()`.

---

### Fix ⑧: `force_flow_state()` Removal

**Problem:** When the IME candidate window was detected, `force_flow_state()` was called to hold the display at Flow. This method destructively overwrote `display_probs`, `axes_ewma`, and HMM beliefs — completely erasing the engine's accumulated cognitive state. After the candidate window closed, the engine had to rebuild state from scratch.

**Fix:** `force_flow_state()` was removed entirely. The IME monitor thread now only calls `engine.set_paused(active)`, which suspends HMM updates without destroying state. When the candidate window closes, inference resumes from the preserved state.

---

### Fix ⑨: Session Start Race Condition

**Problem:** `start_session()` set `session_active = true` before `engine.reset()` completed. The analysis thread could observe the active flag and run an HMM update with stale pre-reset state.

**Fix:** Reordered to `engine.reset()` → `reset_signal.store(true)` → `session_active.store(true)`. The reset signal is also consumed via `swap(false, AcqRel)` instead of separate `load` + `store` to prevent TOCTOU races.

---

### Fix ⑩: `register_keystroke` Cross-Platform Decoupling

**Problem:** `CognitiveStateEngine::register_keystroke()` contained `if vk_code == 0x08` — a Windows-specific virtual key code (`VK_BACK`). On macOS the Delete key is `0x33` (`kVK_Delete`), making the Backspace streak logic non-functional on that platform.

**Fix:** Changed `register_keystroke(vk_code: u32)` → `register_keystroke(is_backspace: bool)`. The OS-specific key code check is now performed at the call site in `lib.rs` (`event.vk_code == 0x08`), keeping the engine fully platform-agnostic. No mathematical or model behavior is changed.

---

## Hook-Level Repeat Event Forwarding (v2.12)

### Problem

The v2.11 hook-level gate discarded auto-repeat events (key held down) entirely, preventing them from reaching the analysis thread. This caused a critical gap in Stuck detection: **holding Backspace to bulk-delete text** — a strong signal of cognitive struggle — was invisible to the engine. The Backspace streak counter (`register_keystroke`) never incremented beyond 1 for a long-press, so the ≥14 consecutive BS penalty never fired.

### Fix

`InputEvent` now carries an `is_repeat: bool` field. The hook's `PRESSED_KEYS` set still detects auto-repeat, but instead of discarding the event, it tags it with `is_repeat: true` and sends it through the channel.

**Feature-level handling:**

| Feature | Repeat events | Rationale |
|---|---|---|
| **F1** (Flight Time) | Ignored (`continue`) | Repeats inject artificial zero-interval entries that distort typing rhythm |
| **F3** (Correction Rate) | Included | Each repeated BS/Del is a real deletion — omitting them understates correction rate |
| **F4** (Burst Length) | Ignored (`continue`) | Repeats inflate burst length without representing intentional sequential keystrokes |
| **F5** (Pause Count) | Included | During a long-press, the user is active — gaps between repeats correctly shrink F5 |
| **F6** (Del-Pause Rate) | Included | Repeated BS fills the gap after the initial press, so F6 only fires when the user truly stops |

**Analysis thread handling:**

- `register_keystroke()`: Repeat events are counted. Holding Backspace now increments the streak counter and fires the ≥14 BS penalty.
- Silence-break protection (`presses_since_silence`): Repeat events are excluded — automatic key repetition does not constitute intentional typing resumption after silence.

---

## Logging & Analysis

Every session produces a timestamped NDJSON file:

```
%USERPROFILE%\Documents\GSE-sessions\gse_YYYYMMDD_HHMMSS.ndjson
```

Record types:

```jsonc
// Session metadata (written at file creation)
{"type":"meta","session_start":1740000000000}

// User clicked "開始する" — explicit session boundary marker (v2.6)
{"type":"session_start","t":1740000000500}

// Raw keystroke event
{"type":"key","t":1740000001234,"vk":65,"press":true}

// Feature snapshot + HMM state probabilities + diagnostics (1 Hz)
{"type":"feat","t":1740000001235,
 "f1":145.20,"f3":0.0800,"f4":6.50,"f5":1.0,"f6":0.0000,
 "p_flow":0.7123,"p_inc":0.2100,"p_stuck":0.0777,
 "raw_x":0.1234,"raw_y":0.7890,"ewma_x":0.1100,"ewma_y":0.8012,"obs":4,"alpha":0.30}

{"type":"meta","session_end":1740000060000}
```

### Post-session Ground-Truth Labeling

```bash
python analysis/behavioral_gt.py gse_YYYYMMDD_HHMMSS.ndjson
```

Labels are assigned per 30-second sliding window (1-second step):

| Label | Behavioral Rule |
|---|---|
| **FLOW** | median(FT) < 200 ms AND correction\_rate < 0.15 AND not STUCK/INC |
| **INCUBATION** | Pause(≥ 2 s) → Burst(≥ 5 chars at FT < 200 ms) → diff\_chars ≥ 3 within 30 s |
| **STUCK** | ≥ 3× (Burst(≤ 3 chars) → Delete(≥ 1) → Pause(≥ 2 s)) in 60 s AND diff\_chars ≤ 0 |
| **UNKNOWN** | No condition met, or multiple labels conflict |

---

## Build Instructions

### Prerequisites

| Tool | Version |
|---|---|
| Rust | 1.77+ (`rustup update stable`) |
| Node.js | 20+ |
| Tauri CLI v2 | `cargo install tauri-cli --version "^2"` |

### Development

```bash
cd GSE-Next
npm install
npm run tauri dev
```

### Release Build

```bash
npm run tauri build
# Installer: src-tauri/target/release/bundle/
```

### Post-session Analysis

```bash
python analysis/behavioral_gt.py "%USERPROFILE%\Documents\GSE-sessions\gse_YYYYMMDD_HHMMSS.ndjson"
```

---

## Academic References

1. **Csikszentmihalyi, M.** (1990). *Flow: The Psychology of Optimal Experience*. Harper & Row.
   — Foundation for the Flow cognitive state definition and its behavioral correlates.

2. **Csikszentmihalyi, M.** (1996). *Creativity: Flow and the Psychology of Discovery and Invention*. HarperCollins.
   — Extends flow theory to creative and generative writing tasks.

3. **Sio, U. N., & Ormerod, T. C.** (2009). Does incubation enhance problem solving? A meta-analytic review. *Psychological Bulletin, 135*(1), 94–120.
   — Empirical basis for the Incubation state self-transition probability (0.80) and the Pause→Burst behavioral signature.

4. **Ohlsson, S.** (1992). Information-processing explanations of insight and related phenomena. In M. T. Keane & K. J. Gilhooly (Eds.), *Advances in the Psychology of Thinking* (pp. 1–44). Harvester Wheatsheaf.
   — Impasse and perseveration theory underlying the Stuck state model and its high self-transition probability.

5. **Rabiner, L. R.** (1989). A tutorial on hidden Markov models and selected applications in speech recognition. *Proceedings of the IEEE, 77*(2), 257–286.
   — HMM Forward Algorithm formulation used in `CognitiveStateEngine::update()`.

6. **Dhakal, V., Feit, A. M., Kristensson, P. O., & Oulasvirta, A.** (2018). Observations on typing from 136 million keystrokes. *Proceedings of CHI 2018*.
   — Population baseline values for flight time and correction rate used in the φ normalization reference values (β).

7. **Salthouse, T. A.** (1986). Perceptual, cognitive, and motoric aspects of transcription typing. *Psychological Bulletin, 99*(3), 303–319.
   — Flight-time decomposition and anticipatory processing in skilled typing; informs F1 and F4 feature design.

8. **Microsoft Corporation.** (2023). *WinEvent Hooks*. Windows Developer Documentation (MSDN).
   — `SetWinEventHook`, `EVENT_OBJECT_IME_CHANGE/SHOW/HIDE` constants, and `WINEVENT_OUTOFCONTEXT` flag; used for cross-process IME detection without DLL injection.

---

## License

Research prototype. All rights reserved.

---

*Last updated: 2026-03-07*
