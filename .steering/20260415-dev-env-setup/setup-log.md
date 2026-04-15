# 開発環境セットアップ作業ログ

- **日付**: 2026-04-15
- **実行環境**: macOS (Darwin 25.3.0, Apple Silicon — `aarch64-apple-darwin`)
- **対象ブランチ**: `main` (commit `0ac8cd3`)
- **担当**: Claude Code (Opus 4.6) + user

## 1. 目的

クリーンチェックアウト直後の状態から GSE-prototype をビルド可能にし、
開発に着手できる状態を整える。

## 2. 事前環境

| ツール | バージョン | 確認方法 |
|---|---|---|
| Rust | `1.93.1 (01f6ddf75 2026-02-11)` | `rustc --version` |
| Node | `v22.22.0` | `node --version` |
| npm | `10.9.4` | `npm --version` |
| cargo | `/Users/johnd/.cargo/bin/cargo` | `which cargo` |

## 3. 発見した課題と対応

### 課題 1: `node_modules/` が未インストール

**症状**:
```
$ ls node_modules/.bin/tauri
ls: node_modules/.bin/tauri: No such file or directory
$ cargo tauri --version
error: no such command: `tauri`
```

`cargo tauri` は cargo サブコマンドではなく、`@tauri-apps/cli` (npm) から
`node_modules/.bin/tauri` 経由で起動する設計。

**対応**:
```bash
npm install
# → added 72 packages, and audited 73 packages in 4s
```

**結果**: ✅ 解消。`npm run tauri dev` 起動経路が確立。

---

### 課題 2: npm high 脆弱性 × 2

**症状** (`npm audit` 出力):

| パッケージ | 影響範囲 | 種別 |
|---|---|---|
| `picomatch` 4.0.0–4.0.3 | ReDoS / Method Injection | high |
| `vite` 7.0.0–7.3.1 | Path Traversal / fs.deny bypass / WS file read | high |

**対応**:
```bash
npm audit fix
# → changed 2 packages, and audited 73 packages in 6s
# → found 0 vulnerabilities
```

破壊的変更を伴わない patch アップデート (`vite` 7.x → 7.x, `picomatch` 4.0.x → 4.0.x 以降) で解決。
`npm audit fix --force` は使っていない（major 上げのリスク回避）。

**結果**: ✅ 0 vulnerabilities。

---

### 課題 3: Rust ビルド warning — `unused_mut`

**症状** (`cargo build --target aarch64-apple-darwin`):

```
warning: variable does not need to be mutable
   --> src/analysis/loop_step.rs:180:29
    |
180 |         Some(LoopInput::Key(mut event)) => {
    |                             ----^^^^^
    |                             |
    |                             help: remove this `mut`
```

`event` は `#[cfg(target_os = "windows")]` 配下の `event.is_repeat = true;`
の代入のためだけに mutable が必要で、macOS ビルドでは `mut` が未使用扱いになる。
単に `mut` を外すと Windows ビルドが壊れる。

**試行 1 (失敗)**: パターン引数に `cfg` を切り分け
```rust
Some(LoopInput::Key(
    #[cfg(target_os = "windows")] mut event,
    #[cfg(not(target_os = "windows"))] event,
)) => {
```
→ `error: expected pattern, found '#'`
（タプルバリアント内側のサブパターンに attribute を付与できない）

**試行 2 (失敗)**: パターン要素に `cfg_attr(allow)`
```rust
Some(LoopInput::Key(
    #[cfg_attr(not(target_os = "windows"), allow(unused_mut))]
    mut event,
)) => {
```
→ 同じく `expected pattern, found '#'`

**試行 3 (成功)**: マッチアーム全体に `cfg_attr(allow(unused_mut))` を付与
```rust
#[cfg_attr(not(target_os = "windows"), allow(unused_mut))]
Some(LoopInput::Key(mut event)) => {
```

ファイル: `src-tauri/src/analysis/loop_step.rs:180`

**結果**: ✅ Windows でも `mut` を維持しつつ macOS で warning 抑制。
最終ビルド: `Finished dev profile [unoptimized] target(s) in 4.17s` (warning 0)。

## 4. 検証コマンド

```bash
# Frontend
npx tsc --noEmit                       # → exit 0 (型エラーなし)
npm audit                              # → found 0 vulnerabilities

# Backend (macOS)
cd src-tauri
cargo build --target aarch64-apple-darwin   # → Finished, warning 0
```

## 5. 残課題 / TODO

- [ ] `npm run tauri dev` での実機起動確認（Input Monitoring 権限プロンプト含む）
- [ ] Windows 環境での再ビルド検証（cfg_attr 修正の動作確認）
- [ ] CI に `cargo build --target aarch64-apple-darwin` と `npx tsc --noEmit` を組み込むか検討

## 6. 参考: 動作環境メモ

- macOS では Tauri ビルド時に `MACOSX_DEPLOYMENT_TARGET=10.15` (`build.rs`) が適用される
- Tauri CLI は npm 経由 (`npm run tauri ...`)。`cargo tauri` は使えない
- Rust のターゲット指定 `--target aarch64-apple-darwin` は Apple Silicon 必須
