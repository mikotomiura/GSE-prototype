# CI Matrix Build 拡充: 両 OS で test + snapshot + build + tsc

## 背景

現状の `.github/workflows/ci.yml` には push/PR 時に windows-latest + macos-latest で `cargo check` のみ実行される `check` ジョブがある。`cargo build` / `cargo test` / snapshot 回帰 / Frontend tsc は **タグ push 時の build ジョブでしか走らない**。

Phase 1 実装 (Task 1/2/3) で Rust / TypeScript 両面に変更が入ったが、macOS でのみローカル検証済みで Windows での動作は未確認。`#[cfg]` 分岐漏れや Windows 固有のコンパイルエラーが main に紛れ込むリスクがある。ユーザー指摘: 「GitHub Action で行えれるでしょ」→ 正論。

## ゴール

push / PR トリガーで以下すべてが **両 OS (windows-latest + macos-latest) で常時緑** であることを保証する:

1. `cargo build --target <host-triple>` (warning 0、--target 明示で OS 分離を厳密化)
2. `cargo test --workspace`
3. `cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json` byte-equal
4. Frontend: Ubuntu で `npm ci` + `npx tsc --noEmit` + `npm run build`

tag push の build-windows / build-macos ジョブは既存のまま（変更しない）。

## スコープ

### 含むもの
- `.github/workflows/ci.yml` の `check` ジョブを拡充:
  - `cargo check` → `cargo build --target` + `cargo test --workspace` + snapshot regression に置き換え
  - `tauri-plugin-global-shortcut` の Windows ランタイム依存 (`user32.dll`) はコンパイル時にリンク解決されるため追加インストール不要
- 新規 `frontend-check` ジョブ: Ubuntu で `npm ci` + `npx tsc --noEmit` + `npm run build` を実行
- `decisions.md`: 「なぜ tag push 側は変えないか」「フルビルドを毎 push で回さない選択」の根拠
- キャッシュ (`Swatinem/rust-cache`) は既存設定を継承

### 含まないもの
- tag push の build-windows / build-macos ジョブの変更（リリースロジックに触らない）
- CI 上の `npm run tauri build` (インストーラ生成) のプッシュトリガー追加 (所要 10-15 分/回で費用増、既存の tag トリガーで十分)
- コードカバレッジ収集、Security audit (`cargo audit`) 等の別 CI 機能
- Linux ランナーでの Rust build (Tauri 本体は Linux 動作保証外、Frontend 型チェックだけ Ubuntu で回す)

## 受け入れ条件

- [ ] `.github/workflows/ci.yml` の `check` ジョブ matrix が windows-latest + macos-latest で `cargo build --target <host>` 成功
- [ ] 同ジョブで `cargo test --workspace` 全 PASS (50 テスト)
- [ ] 同ジョブで snapshot byte-equal 一致 (15 snapshots)
- [ ] 新規 `frontend-check` ジョブで `npx tsc --noEmit` エラー 0 + `npm run build` 成功
- [ ] push 時の所要時間が 10 分以内 (キャッシュウォーム後)
- [ ] 初回 push で Windows ビルドが失敗した場合、`#[cfg]` 漏れ等を fix して緑化
- [ ] 既存 tag push ジョブ (build-windows / build-macos / release) に影響なし

## 関連ドキュメント

- `.github/workflows/ci.yml` (現行設定)
- `docs/development-guidelines.md` §3 (Replay-as-Truth — snapshot regression が CI の背骨)
- `CLAUDE.md` §技術的制約 (1): `windows` crate v0.58+ のみ、`winapi` 禁止

## 運用メモ

- **/reimagine 適用: No**
- **理由**: 既存 `ci.yml` の check ジョブを拡充するのみで、新規アーキテクチャ判断なし。matrix 構成・キャッシュ戦略は既存パターンを踏襲。
- **前提**: `main` ブランチに Phase 1 Task 1/2/3 が commit 済み (`e80ea33`)
