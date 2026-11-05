<div align="center">

# 🧠 GSE — Generative Struggle Engine

**Aims to infer a work-level cognitive state from how you type, and to offer an unscored invitation to step away before you get stuck — privacy-preserving HCI.**

GSE doesn't read your mind. It reads *keystroke dynamics* (key timing and key type only; no text is stored) — and decides
whether to offer an invitation to step away from the screen now, or to stay out of the way. The invitation never measures whether you started or finished.

> **Status:** GSE itself shows **no intervention by default**. Nudge remains in the code but is off by default
> ([ADR-040](docs/adr/ADR-040-nudge-not-in-core.md)). The full-screen Wall and Monk Mode
> were **removed in 2026-08** ([ADR-015](docs/adr/ADR-015-wall-removal.md)). The invitation to physical return
> (the PC side of Physical Anchor) runs as a glyph in the EH3 study mode and in the normal mode's week 2 (session declaration "第2週 (招待)"; not in week 1, O1 or G1). Walking promotion and its measurement are
> not pursued (2026-11-03); what follows the invitation is read from work after a candidate away gap (typing resumes, whether
> an external answer is received, window focus changes, and pointer activity) ([ADR-024](docs/adr/ADR-024-resumption-outcome-without-estimator.md)).
>
> **Direction as of 2026-10-31:** Nudge will no longer be shown as an intervention in GSE itself; the core intervention
> becomes the invitation to physical return ([ADR-040](docs/adr/ADR-040-nudge-not-in-core.md)). Nudge is now off by default;
> the invitation is wired into the normal mode's week 2 with a swappable trigger (estimator / rising / random / none, chosen in
> the researcher's `~/.gse/invitation_trigger.json`; fail-closed) and reproducible offline with `gse-replay --invitation`.

[![CI / Release](https://github.com/mikotomiura/GSE-prototype/actions/workflows/ci.yml/badge.svg)](https://github.com/mikotomiura/GSE-prototype/actions/workflows/ci.yml)
![Platform](https://img.shields.io/badge/platform-Windows%2011%20·%20macOS-2563EB)
![Tauri](https://img.shields.io/badge/Tauri-2.0-24C8DB?logo=tauri&logoColor=white)
![Rust](https://img.shields.io/badge/Rust-1.77+-CE412B?logo=rust&logoColor=white)
![License](https://img.shields.io/badge/license-Research%20Prototype-8B8B8B)

[🇯🇵 日本語版 README](README.ja.md) · [📐 Design History](docs/design-history.md) · [📥 Download](https://github.com/mikotomiura/GSE-prototype/releases)

</div>

---

## Why GSE

Writers, programmers, and knowledge workers constantly move between **fluent output**, **useful pauses**,
and **unproductive loops**. GSE treats these as task-level *behavioral patterns* — never as directly
observable mental states — and protects **productive struggle** instead of interrupting it.

The trick is separating two questions:

| Question | Name | Signal |
|---|---|---|
| *Might an intervention help right now?* | **Need** | HMM `p_stuck` from keystroke features |
| *Is this a low-cost moment to interrupt?* | **Opportunity** | idle, post-burst pause, cooldown, daily cap, recent dismiss |

Only when **Need × Opportunity** both line up does GSE act — `none` / `nudge` / `defer`.
`defer` ("you're mid-struggle, don't interrupt") is a **first-class, logged decision**, not silence.

No wearables. No camera. No raw text. Just timing data the OS already exposes.

---

## How it works

```
Any app ──▶ Keyboard hook (Rust)            Win: WH_KEYBOARD_LL · Mac: CGEventTap
              │  crossbeam channel · non-blocking, content-free
              ▼
          Analysis thread · 1 Hz gate
              │  F1/F3–F6 over a 30 s window
              │   → X (Cognitive Friction) / Y (Productive Engagement)
              │   → EWMA smoothing → HMM forward step → hysteresis layer
              ▼
          Intervention policy        Need (p_stuck) × Opportunity
              │  → none / nudge / defer
              ├──▶ React UI         Dashboard + Overlay (Nudge card)
              └──▶ Session logger   NDJSON — behavioral features only, never text
```

`analysis/` is **platform-agnostic**; all OS-specific code is isolated in `input/`.
For the thread model and the full version-by-version rationale, see **[Design History](docs/design-history.md)**.

---

## Feature extraction

Five features are computed over a **30-second sliding window**, updated on every keypress.
During silence, a synthetic observation is generated each second to keep the HMM running.

| Feature | Symbol | Definition | Signal |
|---|:---:|---|---|
| Flight-time median | **F1** | Median release→press interval (ms) | speed — lower = Flow |
| Correction rate | **F3** | (Backspace + Delete) / total presses | errors — higher = Stuck |
| Burst length | **F4** | Mean run of keys with gap < 200 ms | fluency — higher = Flow |
| Pause count | **F5** | Inter-press gaps ≥ 2 s in window | deliberation |
| Pause-after-delete | **F6** | Fraction of deletes followed by a ≥ 2 s gap | post-error freeze — higher = Stuck |

Each value is normalized to `[0,1]` via a baseline-relative map `φ(x,β) = clamp((x−β)/(2β), 0, 1)`,
then projected onto two interpretable axes:

```text
X (Cognitive Friction) = 0.30·φ(F3) + 0.25·φ(F6) + 0.25·φ(F1) + 0.20·φ(F5)
Y (Productive Silence) = 0.40·φ(F4) + 0.35·(1−φ(F1)) + 0.25·(1−φ(F5))
```

`(X, Y)` is discretized into a 5×5 grid (+1 Backspace-penalty bin) and fed to a 3-state HMM
(**Flow / Incubation / Stuck**) via a one-step Forward Algorithm with a hysteresis EMA on top.
Matrices, β baselines, quantization, and the tuning history live in **[Design History](docs/design-history.md)**.

---

## Intervention

| Level | Trigger | Effect | Dismiss |
|---|---|---|---|
| **Nudge** | `action == nudge` | Small click-through side card; opacity scales with Need | auto-dismisses |
| **Physical Anchor** (invitation) | EH3 study mode (normal mode: separate task) | An invitation to step away from the screen | closes after 60 s |
| ~~**Wall**~~ | ~~full-screen block~~ | **Removed 2026-08** — see below | — |

**Suppression** (all shipping): `defer` while actively typing (IKI < 2 s), 10-min cooldown,
daily cap of 6, 20-min recent-dismiss window, and no interventions at all after 180 s idle.

**Why the Wall is gone** ([ADR-015](docs/adr/ADR-015-wall-removal.md)): a full-screen block stops
*everything* at once — the AI shortcut, asking for help, and the work itself. The behaviour worth
suppressing is narrower than that ("taking the answer as-is"), and a screen block can't aim at it.
`wall_server.rs`, the QR/phone-unlock path, Monk Mode, the Zen Timer, and early unlock were all
removed; **HIR (harmful-intervention rate) was kept** — only its target set changed.

**Physical Anchor** ([ADR-017](docs/adr/ADR-017-expression-channel-boundary.md)) is an invitation
to step away from the screen. Its PC-side invitation runs in the EH3 study mode; walking promotion and its measurement are not pursued (2026-11-03), and what follows is read from work after a candidate away gap: typing, focus changes, and pointer activity (ADR-024, ADR-023 D4, ADR-016).
**The system judges neither the start nor the completion of it**
([ADR-018](docs/adr/ADR-018-physical-anchor-without-completion.md)): there is no threshold on how
long you stay away or how you come back, and **no timer, countdown, or remaining-time display**.
GSE **does not sense physical activity at all** (no GPS, pedometer, or accelerometer).

> ⚠️ **Corrected 2026-09-01.** This paragraph used to say the completion condition was
> *"time away + return"*. ADR-018 D1 **withdrew** that condition: replacing a step target with a
> time target still creates a cell for "did not reach it", which is exactly what harms intrinsic
> motivation. The level names Lv1–Lv4 were dropped for the same reason — with the Wall gone and no
> completion condition, there is no ladder of increasing intensity left to number.

---

## 🔒 Privacy

- **No text is ever stored.** Logs contain timing, counts, and decisions — not characters.
- Keystroke content and raw NDJSON are **never** sent to any external service or LLM.
- Sessions write to `Documents/GSE-sessions/*.ndjson` locally; only ~1 KB/session of aggregate
  `--metrics --json` is ever shared (see [`gse-dataset`](https://github.com/mikotomiura/gse-dataset)).
- The NDJSON schema is machine-generated from Rust types and CI-guarded against drift.

---

## 📥 Install

Pre-built artifacts are published automatically on every version tag →
**[Releases](https://github.com/mikotomiura/GSE-prototype/releases)**.

| Platform | File | Use when |
|---|---|---|
| **Windows (portable)** | `gse-next.exe` | **Recommended** — no install, just run |
| Windows (installer) | `gse-next_X.Y.Z_x64-setup.exe` | you want a Start-menu entry |
| macOS (Apple Silicon) | `gse-next_X.Y.Z_aarch64.dmg` | — |

### Windows

This is a research build and is **not code-signed**, so Windows will warn you. That's expected.

1. Prefer the **portable `gse-next.exe`** (no installer, no UAC prompt).
2. If **SmartScreen** appears ("Windows protected your PC") → **More info** → **Run anyway**.
3. If **Smart App Control (SAC)** blocks it (no "Run anyway" button):
   **Settings → Privacy & Security → Windows Security → App & browser control →
   Smart App Control settings → Off**, then relaunch.
   > ⚠️ SAC cannot be re-enabled once turned off (a Windows limitation). If you'd rather not
   > disable it, ask the maintainer for a signed build.

### macOS

The app is ad-hoc signed (no Apple Developer ID), so Gatekeeper will block it until you clear quarantine.

```bash
# Run BEFORE first launch:
xattr -dr com.apple.quarantine /Applications/gse-next.app
codesign --force --deep --sign - /Applications/gse-next.app
```

> Do **not** use `xattr -cr` — it strips all attributes and can invalidate the signature.

Then grant **System Settings → Privacy & Security → Input Monitoring → gse-next** and restart the app
(without it, the keyboard hook can't run).

<details>
<summary>Input Monitoring still not working after granting?</summary>

1. **Re-add**: uncheck gse-next in Input Monitoring, re-check it, restart the app.
2. **Reset TCC**: `tccutil reset ListenEvent`, then re-grant and restart.
3. **Re-clear quarantine**: if you previously used `xattr -cr`, re-copy from the DMG and use
   `xattr -dr com.apple.quarantine /Applications/gse-next.app` instead.
4. **Reboot**: some TCC changes need a full restart.
</details>

---

## 🛠️ Build

| Tool | Version |
|---|---|
| Rust | 1.77+ (`rustup update stable`) |
| Node.js | 22+ |
| Tauri CLI v2 | `cargo install tauri-cli --version "^2"` |

```bash
npm install
npm run tauri dev      # development
npm run tauri build    # release → src-tauri/target/release/bundle/
```

**Verification before release/merge** — run `docs/verification-runbook.md` top-to-bottom:
automated regression (`cargo test` · `gse-replay --snapshot` · `emit_schema` · `tsc`),
macOS functional checks, Windows diffs, and the Google Form builder.

<details>
<summary><b>Researcher / debug mode (dual gate)</b></summary>

Debug features are guarded by two flags; participants run with **none** (fully blind):

| Flag | Kind | Effect |
|---|---|---|
| `VITE_GSE_DEBUG=1` | build-time (Vite) | renders debug buttons; shows week-2 model output |
| `GSE_DEBUG=1` | runtime (Rust) | enables `force_nudge` / `debug_force_probe` |

```bash
VITE_GSE_DEBUG=1 GSE_DEBUG=1 npm run tauri dev
```
See `docs/calibration-smoke-runbook.md` §1.1–1.2.
</details>

<details>
<summary><b>Release workflow (maintainers)</b></summary>

```bash
# Bump version in package.json · src-tauri/tauri.conf.json · src-tauri/Cargo.toml (keep all three in sync)
git commit -am "chore: bump version to vX.Y.Z"
git tag vX.Y.Z && git push && git push --tags
# GitHub Actions builds Windows (exe) + macOS (dmg) and publishes the Release.
```
</details>

---

## Logging & replay

Each session writes a timestamped NDJSON file; `gse-replay` re-runs the engine offline over it —
the backbone of unit, regression, GT-evaluation, and tuning workflows (one replay covers all four).

```bash
cargo run --bin gse-replay -- session.ndjson --snapshot tests/snapshots/s.json  # regression (byte-equal)
cargo run --bin gse-replay -- session.ndjson --metrics --json                    # GT metrics
```

Live Ground-Truth labeling ships today (`Ctrl/⌘ + Shift + Alt + F/I/S`), appending subjective labels
to the same log without ever touching the production HMM path.

---

## 📁 Layout

```
src/                 React / TypeScript frontend (UI + IPC only)
src-tauri/src/
  analysis/          engine.rs · features.rs · intervention.rs · loop_step.rs   (OS-agnostic)
  input/             hook_* · ime_*                                              (OS-specific)
  lib.rs · logger.rs · schema_dto.rs · redaction.rs · recording.rs
src-tauri/bin/       gse-replay (eval CLI) · emit_schema
docs/                architecture · functional-design · design-history · runbooks
```

## 📚 Docs

| File | Read when |
|---|---|
| [`docs/design-history.md`](docs/design-history.md) | the v2.1–v2.22 deep dive (hysteresis, IME, intervention, parity) |
| `docs/architecture.md` | thread model & data flow |
| `docs/functional-design.md` | intent, requirements, use cases |
| `docs/development-guidelines.md` | conventions, testing, review, dataset workflow |

<details>
<summary><b>Academic references</b></summary>

1. **Csikszentmihalyi, M.** (1990). *Flow: The Psychology of Optimal Experience*. Harper & Row.
2. **Csikszentmihalyi, M.** (1996). *Creativity*. HarperCollins.
3. **Sio, U. N., & Ormerod, T. C.** (2009). Does incubation enhance problem solving? *Psychological Bulletin, 135*(1). — Incubation self-transition (0.80) & Pause→Burst signature.
4. **Ohlsson, S.** (1992). Information-processing explanations of insight. In *Advances in the Psychology of Thinking*. — Impasse/perseveration → Stuck.
5. **Rabiner, L. R.** (1989). A tutorial on hidden Markov models. *Proceedings of the IEEE, 77*(2). — Forward Algorithm.
6. **Dhakal, V., et al.** (2018). Observations on typing from 136 million keystrokes. *CHI 2018*. — β baselines.
7. **Salthouse, T. A.** (1986). Transcription typing. *Psychological Bulletin, 99*(3). — F1/F4 design.
8. **Microsoft** (2023). *WinEvent Hooks*, MSDN. — cross-process IME detection.
</details>

---

<div align="center">
<sub>Research prototype · All rights reserved · made for protecting productive struggle</sub>
</div>
