# 設計判断

## D1: `unused_mut` warning の抑制方法

**判断**: マッチアーム本体に `#[cfg_attr(not(target_os = "windows"), allow(unused_mut))]` を付与する。

**選択肢**:
1. `mut` を外す → Windows ビルドで `event.is_repeat = true;` がエラー。却下。
2. パターン要素への `cfg(target_os = ...)` 分岐 → rustc はパターン内サブ要素への attribute を許容せずパース失敗。却下。
3. パターン要素への `cfg_attr(allow(unused_mut))` → 同じくパース失敗。却下。
4. **マッチアーム本体への `cfg_attr(allow(unused_mut))`** → 採用。最小変更で OS 別の lint 抑制を実現。
5. 関数全体に `#[allow(unused_mut)]` → 範囲が広すぎて他の意図しない `mut` 抑制リスク。却下。

**理由**:
- Windows パスで `mut` は意味があり、削除不可
- パターンサブ要素への attribute はサポート外（rustc 言語仕様）
- アーム本体への attribute は局所的かつ条件付きで、副作用最小

**影響**: なし（生成コード不変）。

## レビュー結果（2026-04-15）

### code-reviewer
- HIGH/MED 指摘なし。
- LOW: `Some(LoopInput::Key(event))` でバインドして Windows ブロック内で `let mut event = event;` する代替案あり。現状の差分が小さく可読性も許容範囲のため現行維持で OK。
- 同 match 内で他に `mut` バインディングを持つアームは無く、波及リスクなし。

### security-checker
- HIGH/MED 指摘なし。`npm audit` は 0 vulnerabilities。
- vite 7.3.2 / picomatch 4.0.4 に既知 CVE なし。
- loop_step.rs の変更は lint 抑制属性のみで、キーストロークデータ取り扱いに影響なし（vk_code/timestamp/is_press のみ記録、変更前後で不変）。
- LOW: CI に `npm audit --production` を定期化推奨。
