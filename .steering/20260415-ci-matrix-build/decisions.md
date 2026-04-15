# Decisions — CI Matrix Build 拡充

## D1: push/PR では `cargo build`（フルビルド）、`cargo check` にしない

### 背景
`cargo check` は型検査のみで、リンクや一部マクロ展開を省略する。Phase 1 で `tauri-plugin-global-shortcut` を追加したが、`cargo check` では `user32.dll` リンクは発生しないため Windows での結線エラーを捕捉できない可能性がある。

### 決着
`cargo build --target ${{ matrix.target }}` に置換。`--target` 明示で OS 分離を厳密化し、`cfg(windows)` / `cfg(target_os = "macos")` が期待通り効くことを保証する。時間増は 1-2 分想定、キャッシュウォーム後は 3-4 分。

## D2: snapshot 回帰を CI に含める（Replay-as-Truth の CI 化）

### 背景
`docs/development-guidelines.md` §3 で「リプレイ CLI が回帰保護の背骨」と規定しているが、従来は手動実行のみだった。

### 決着
`cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json` を CI 必須ステップ化。両 OS で 15 snapshots の byte-equal 一致を毎 push で検証することで、HMM / features の無意識の副作用を main 到達前に検出する。

## D3: Frontend は Ubuntu で実行

### 背景
`npm ci` + `tsc --noEmit` + `vite build` は OS 非依存。macOS / Windows ランナーで回すのは時間と金の無駄。

### 決着
専用 `frontend-check` ジョブを ubuntu-latest で実行。Rust check と並列で走るため総所要時間は増えない。

## D4: matrix は `include` 形式で os + target を明示

### 背景
`matrix.os: [windows-latest, macos-latest]` だと target をジョブ内で動的解決する必要があり、`aarch64-apple-darwin` / `x86_64-pc-windows-msvc` の対応関係が暗黙になる。

### 決着
`strategy.matrix.include` で os と target を 1:1 で紐付け。`dtolnay/rust-toolchain@stable` の `targets: ${{ matrix.target }}` と合わせて明示的にホストと異なる target を要求でき、将来 macOS Intel runner に戻ったとしても正しく動く。

## D5: tag push 側の build ジョブは変更しない

### 背景
`build-windows` / `build-macos` / `release` は Tauri bundle (NSIS / DMG) + ad-hoc codesign + GitHub Release 作成を担う既存リリースパイプライン。拡充スコープを広げすぎるとレビューも検証も複雑化する。

### 決着
push 時の `check` ジョブのみ拡充、タグ push 時のリリースジョブには手を触れない。リリース経路の回帰リスクをゼロに保つ。

## D6: `fail-fast: false` を設定

### 背景
matrix のどちらかが失敗すると残り全部がキャンセルされる既定動作だと、Windows だけ落ちた時に macOS の結果が見えず原因切り分けに時間がかかる。

### 決着
`strategy.fail-fast: false` を明示。両 OS の結果を毎回見られるようにする。

## 採用しなかった代替案

- **`cargo tauri build` を push で実行**: 10-15 分/回で費用が跳ね上がる。リリース時のみに限定するのが妥当
- **Rust toolchain pin 止め (rust-toolchain.toml)**: MSRV 未定義の状態でピン止めすると更新追従が重くなる。latest stable を許容し、壊れたら pin を検討する順序
- **Linux runner で Rust ビルド**: Tauri 本体の Linux 動作は保証外、現状 Linux ユーザーを想定していない
- **`cargo audit` / `cargo deny`**: セキュリティ監査の CI 化は価値があるが本タスクのスコープ外、別タスクで
