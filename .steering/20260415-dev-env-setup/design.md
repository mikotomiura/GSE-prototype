# 設計

## 実装アプローチ

3 課題を独立に処理する。
1. **npm install** — 通常実行
2. **npm 脆弱性** — `npm audit fix` のみ実行（`--force` は使わず major upgrade を回避）
3. **`unused_mut` warning** — `event` の `mut` は Windows パスでのみ必要 (`event.is_repeat = true;`)。
   非 Windows ビルドで lint を黙らせるため、マッチアームに `#[cfg_attr(not(target_os = "windows"), allow(unused_mut))]` を付与する。
   サブパターン `mut event` 自体への `cfg_attr` 付与はパース不可（rustc がパターン要素への attribute を許容しない）。

## 変更対象

### 修正するファイル
- `src-tauri/src/analysis/loop_step.rs:180` — マッチアームに `cfg_attr(allow(unused_mut))` 追加
- `package-lock.json` — `npm audit fix` による依存更新
- `node_modules/` — 新規生成

### 新規作成するファイル
- `.steering/20260415-dev-env-setup/requirement.md`
- `.steering/20260415-dev-env-setup/design.md`
- `.steering/20260415-dev-env-setup/tasklist.md`
- `.steering/20260415-dev-env-setup/setup-log.md`
- `.steering/20260415-dev-env-setup/decisions.md`

## 影響範囲

- **Frontend ビルド**: `vite` / `picomatch` の patch upgrade。API 互換のため影響なしと判断。
- **Rust ビルド**: マッチアーム attribute 追加のみで、生成コードは Windows / macOS 共に変化なし。
- **Windows ビルド**: `mut event` は維持されるため `event.is_repeat = true;` の代入は引き続き有効。

## 既存パターンとの整合性

- メモリに残る `cfg_attr` パターンは無いが、`#[cfg(target_os = "...")]` ブロック分岐は
  `loop_step.rs` 内に既存例あり (185-194 行) — 同様の OS 分岐方針を踏襲。
- macOS ビルド標準コマンドは `~/.cargo/bin/cargo build --target aarch64-apple-darwin`（メモリ準拠）。

## テスト戦略

- 単体テスト: 既存テスト不変。回帰なし。
- 統合テスト: `cargo build --target aarch64-apple-darwin` が warning 0 で通ることを確認。
- 型テスト: `npx tsc --noEmit` でパスを確認。
- 脆弱性: `npm audit` で 0 件を確認。

## ロールバック計画

- npm: `git checkout package-lock.json && rm -rf node_modules && npm install`
- Rust: `git checkout src-tauri/src/analysis/loop_step.rs`
