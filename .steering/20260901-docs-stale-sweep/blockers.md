# ブロッカー記録

## ブロッカー 1: [タイトル]

- **発生日時**:
- **症状**:
- **試したこと**:
  1. ...
  2. ...
- **原因**:
- **解決方法**:
- **教訓**: 次回同じ状況に遭遇したらどうすべきか

---

## 持ち越し 1: ⚠️★★★ `functional-design.md` に O1 / G1 / 表現チャネル / プローブの機能節が無い

- **実測**: `grep -c "O1\|R3\|表現" docs/functional-design.md` → **0**
- ⚠️ **O1（継続的自然作業収集）は現在進行中の収集**（`Form_O1/` / `docs/o1-deletion-ledger.md` /
  `src-tauri/src/o1.rs`）なのに、**機能仕様の SSOT に機能としても将来拡張としても存在しない**。
- ★ 同様に **G1**（`g1.rs`）/ **表現チャネル**（ADR-017 D1 で第 1 版の追加媒体として確定）/
  **ランダム時点プローブ**（`probe_scheduler.rs`・★ 本文 L141 が「主データ源」と宣言しているのに仕様が無い）も無い。
- **なぜ本タスクでやらないか**: ★ **新設は分量が大きく、監査自身が「別タスク推奨」と判定した。**
  ⚠️ かつ機能節の新設は**是正ではなく執筆**であり、本タスクのゴール（実装との事実整合）と性質が違う。
- **次タスクの入口**（★ 監査が具体案まで出している）:
  - 機能 8 = O1: `o1.mode` / `GSE_O1_MODE=1` の 2 引き金 / 介入を出さない / 自己ラベル系を記録しない
    （★ `label_row_allowed` —— ⚠️ **`grep -rn "label_row_allowed" docs/` = 0 件**）/ 24h ローテート + 48h 猶予 / `gse_o1_*.ndjson`
  - 機能 9 = G1: マーカー + 環境変数の 2 経路 / `meta.g1_mode` / ブロック境界 / 自動提出の承認ゲート
  - 機能 10 = 非打鍵チャネル + 機能 11 = capabilities 自己記述（ADR-013）
  - 機能 7b = ランダム時点プローブ
- ⚠️ **併せて `### オプション機能` が中身ゼロの見出しとして残っている**（L376 付近）。
- ⚠️ **`### 2.x` / `### 2.x+1` がプレースホルダのまま**（機能の通し番号を振り直す時に一緒に解消する）。

## 持ち越し 2: ⚠️ コード側のコメントに残る陳腐化 3 件（★ docs ではないので本タスク対象外）

| 場所 | 逐語 | 実体 |
|---|---|---|
| `src-tauri/src/input/hook_macos.rs:670` | 「ListenOnly (Input Monitoring) → **10回失敗後** → Default (Accessibility) にフォールバック。」 | ⚠️ **同ファイル `:686` は `consecutive_failures >= 3`**。★ `:684-685` のコメントとも矛盾 |
| `src-tauri/src/analysis/metrics.rs:133` | 「`PStuckThreshold` 時の閾値。**Wall トリガ (p_stuck>0.70)** より緩め」 | ⚠️ Wall は ADR-015 D1 で削除済み |
| `src-tauri/src/logger.rs:815` / `schema_dto.rs:313` | `session_meta` を「track / task_kind / **Monk**・介入トグル」と説明 | ⚠️ `monk_mode` フィールドは ADR-015 D2 で削除済み |

- ★ **`src-tauri/src/analysis/engine.rs:52-57` の HMM 変更履歴が `0.4.0` までしか無い**
  （実体は `:58` で `0.5.0`）。⚠️ CLAUDE.md「HMM 挙動を変えたら bump → 差分を `.steering/` に記録」の記録面が欠けている。
- ⚠️ **コード変更を伴うので別ブランチ・別タスクで行うこと**（本タスクは `git status --porcelain src-tauri src` = 空を維持）。

## 持ち越し 3: `scripts/check_doc_lexicon.py` の検査対象に主要 docs が入っていない

- **実測**: `scripts/check_doc_lexicon.py:17-22` の検査対象は `docs/mitou_docs/` の 2 文書と
  `SSOT = ['docs/glossary.md', '.claude/skills/physical-anchor/SKILL.md']` **のみ**。
- ⚠️ **したがって本タスクが見つけた禁止用語（`functional-design.md:8` の「不便益に基づく」「回復」、
  `kCGEventTapOption*`）は CI でも検出されなかった。**
- ★ **是正が済んだ今なら対象を広げられる**（★ 広げる前に必ず `--self-test` と本検査を走らせること）。
  候補: `docs/functional-design.md` / `docs/architecture.md` / `docs/agent-shared.md` / `README.md` / `README.ja.md`。
- ⚠️ **これが無い限り、同じ陳腐化がまた入る**（★ 本タスクは人手の grep で 138 件見つけたが、それは再発防止ではない）。
