# GSE (Generative Struggle Engine) Prototype

A Windows-based prototype that monitors keyboard input to detect user cognitive states (FLOW, INCUBATION, STUCK) and provides visual feedback through screen overlay effects.

## Prerequisites

- Windows 10/11 (64-bit)
- Rust 1.70 or later
- Visual Studio Build Tools with C++ development tools

## Building

```bash
cargo build --release
```

## Running

**Note**: Administrator privileges are required for the global keyboard hook.

```bash
cargo run --release
```

## Project Structure

```
src/
├── main.rs                # Entry point
├── input/
│   ├── mod.rs
│   └── keyboard.rs        # Global keyboard hook implementation
├── inference/
│   ├── mod.rs
│   └── rules.rs           # State classification logic
└── ui/
    ├── mod.rs
    └── overlay.rs         # Screen overlay rendering
```

## Development Phases

See [CLAUDE.md](CLAUDE.md) for detailed development guide.

- Phase 0: Project initialization ✅
- Phase 1: Global keyboard hook
- Phase 2: Rule-based state inference
- Phase 3: HMM integration (optional)
- Phase 4: Overlay UI
- Phase 5: TSF integration (optional)

## License

MIT
