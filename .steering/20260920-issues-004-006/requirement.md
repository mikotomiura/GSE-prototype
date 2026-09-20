# issue 004（`T1c` = 削除と挿入の遷移の形）/ 006（`T1d` = 再開）—— 未裁定 9 論点の裁定と実装

> ★ 一次資料（⚠️ 本ファイルを一次にしない）:
> `.steering/20260914-mhd-feature-offline-tiers/issues/004.md` / `006.md`（**本文の「推奨」表**）／
> 同 `decisions.md` 判断 25 #9 / #10・判断 26 ／
> `.steering/20260918-theory-critical-review/definitions-restop-t1d-t1c.md` §3 / §6.2 / §6.2b ／
> `docs/adr/ADR-030-stall-onset-and-decision-episode.md` D2 / D3 / D4 / D8 / D10 / D11 ／
> `src-tauri/src/analysis/feat_offline/`（実装）。

## 背景

タスク 2（`20260914-mhd-feature-offline-tiers`）の再開順 ④ に当たる。
① 理論レビュー / ② Loop 基盤の修正 / ③ 封筒 issue は完了済みで、
**全 acceptance の前提（`{ provenance, config, rows }` の封筒）はもう動かない**。

2026-09-20 時点の実測（baseline）:

```text
[acceptance 004] NG: 全行に revision の必須フィールドが揃っていない
[acceptance 006] NG: 全行に restart の必須フィールドが揃っていない
```

★ つまり **赤の理由は「自分の Tier が未実装」だけ**である。

⚠️ ただし着手条件（判断 26）がある: 両 issue の Background「実装フェーズで決める」節に
**未裁定の論点が 004 = 6 行 / 006 = 5 行**（`grep -c 未裁定` の実測）残っており、
**0 になるまでコードを書かない**。

## ゴール

1. **未裁定 9 論点（U1〜U4 / V1〜V5）を裁定する**（推奨を承認するか、対案に倒すか）。
   裁定は `.steering/20260920-issues-004-006/decisions.md` に記録し、
   issue 本文の「推奨（⚠️ 未裁定）」を「★ 裁定: …」へ書き換える。
   → `grep -c 未裁定` が 004 / 006 とも **0** になる。
2. `analysis/feat_offline/revision.rs` を作り、`FeatureRow.revision` の 6 フィールドを出す（issue 004）。
3. `analysis/feat_offline/restart.rs` を作り、`FeatureRow.restart` の 7 フィールドを出す（issue 006）。
4. `004-acceptance.sh` / `006-acceptance.sh` が **OK** になる。
   ★ 同時に `001-acceptance.sh` の最上位キー集合へ `revision` / `restart` を足す
   （⚠️ 忘れると 001 が赤くなる —— 判断 18 の先例）。
5. `cargo test --workspace` / ゴールデン replay / `check` / `clippy` / `fmt` が緑のまま。

## スコープ

### 含むもの
- `src-tauri/src/analysis/feat_offline/revision.rs`（新規）
- `src-tauri/src/analysis/feat_offline/restart.rs`（新規）
- `src-tauri/src/analysis/feat_offline/mod.rs`（`pub mod` ・`FeatureRow` の 2 フィールド・配線）
- `src-tauri/src/analysis/feat_offline/stall_onset.rs`（★ 006 V2 の裁定で Allowed Files に追加 —— 条件 A の辺を `pub(super)` で出す）
- `issues/004.md` / `006.md`（裁定の反映）・`006-acceptance.sh`（V3 の fixture 差し替え）・`001-acceptance.sh`（最上位キー集合）

### 含まないもの
- ⚠️★★★ `undo` / `redo` / `key.mod`（★ ADR-032 は Proposed。§Migration M4 = 同意 §3 の改訂が研究者承認待ち）
- ⚠️★★★ **E1（エピソードへの連結）そのもの**（★ V1 の裁定で `recovery` と同時に入れる別層へ送る）
- ⚠️ 転帰判定（`receipt_free_resumption` 等・ADR-024 の領域）・episode 単位の集約
- ⚠️ 新しい数値定数（★ `W` / `q` / `B` / `hole_gap_ms` は `StallOnsetConfig` から引く。値は P1 前の事前宣言）
- ⚠️ ADR 本文・事前登録 §3・被験者向け文書の書き換え

## 受け入れ条件

- [ ] `grep -c 未裁定 issues/004.md` = 0 / `issues/006.md` = 0
- [ ] `bash issues/004-acceptance.sh` → `[acceptance 004] OK`
- [ ] `bash issues/006-acceptance.sh` → `[acceptance 006] OK`
- [ ] `bash issues/001-acceptance.sh` → `[acceptance 001] OK`（★ 最上位キー集合の更新込み）
- [ ] `cargo test --workspace` 緑 ／ ゴールデン replay 緑 ／ `clippy -D warnings` / `fmt --check` 緑
- [ ] `code-reviewer` ＋ `security-checker`（並列・opus）／ `/cross-review` 2 巡（⚠️ 予算ガードで止まる場合は skip 理由を明記）

## 関連ドキュメント

- `docs/adr/ADR-030-stall-onset-and-decision-episode.md`（D2 buffer / D3 条件 A / D8 (b-2) 観測区間 / D10 Tier / D11 計器変更）
- `docs/adr/ADR-029-outcome-role-arbitration.md`（D5 censoring の分離）
- `docs/glossary.md`（★ 禁止用語 `recovery` / `回復`）
- `.steering/20260918-theory-critical-review/definitions-restop-t1d-t1c.md`

## 運用メモ

- /reimagine 適用: **No**
- 理由: 設計は一次資料（ADR-030・理論レビューの定義文書・issue 本文の推奨表）で
  既に候補が列挙されており、本タスクは「推奨を承認するか対案に倒すか」の裁定である。
  ゼロから代替案を生成する段階ではない。
