# 設計

## 実装アプローチ

**「計器は報告するだけ・判断は研究者が入れる」**を全サブ項目で貫く。
⚠️ `preregistration.md §3.6`（凍結・除外規則）は 1 文字も触らず、
**除外も判定も機械が決めない**（`validate_blocks.py` の既存規約 `README.md:614` と同じ流儀）。

### A-1 `validate_blocks.py` — 状態を報告する検査を足す

- 割付ファイル（`blocks/P0xx.json`）の**トップレベル**に `participation_status` を許す
  （`not_started` / `started_incomplete` / `completed`）＋ `status_recorded_at`。
- `check_files` の分岐を 3 つにする:

  | 状態 | 現行 | 変更後 |
  |---|---|---|
  | `file` が 1 つも無い | `[NOTE]` まだ実施していない | 変えない（`status` が `not_started` なら NOTE の文言に「未実施（実施記録で確認済み）」を添える） |
  | 一部だけ `file` がある ＋ **status 無し** | `[FAIL]` 記入漏れ | ⚠️ **変えない**（＝ 転記ミスの検出力を失わない・negative control でテスト固定） |
  | 一部だけ `file` がある ＋ `status=started_incomplete` | `[FAIL]` 記入漏れ | `[NOTE]` 未完了（第 20 版 (i)/(iii)・⚠️ 除外はしない） |

- ⚠️ `status` の値が未知の文字列なら `[FAIL]`（黙って通さない）。
- ★ `status` は `blocks[]` の要素ではなく**トップレベル**に置く
  → `assign.py` が割付を再生成したら status は消え、**従来の FAIL に戻る**（fail-closed の向き）。

### A-2 `analyze.py` — 門を収集完了で分岐させ、登録 k / 解析 m を出す

```
# :196-200 の現行（無条件 NG）
if len(conf) < n_subjects:  → [NG]

# 変更後
closed = roster.get("recruitment_closed", {}).get("closed") is True
if len(conf) < n_subjects and not closed:      → [NG]（従来どおり・§2.4-4）
if len(conf) < n_subjects and closed:          → 続行（★ 注記を errors ではなく notes へ）
```

⚠️★★★ **実装の逸脱と是正（2026-09-27・TASK-POST レビューで発覚）**: issue 002 の実装（worker）は
本設計が指定した `is True`（厳密判定）ではなく `bool(rc.get("closed"))`（素の型変換）を実装した。
これは `"closed": "false"`（文字列）等で fail-open する（Codex / security-checker / code-reviewer の
3 系統が独立に指摘・一次で再現確認）。★ TASK-POST の修正コミットで `evaluate_recruitment_closed()`
ヘルパに一本化し、本設計どおり `closed is True` の厳密判定に戻した。加えて設計時点には無かった
`date` / `decided_before_seeing_results` の必須化（closed=true のとき）も追加した
（security-checker 指摘: optional stopping の自己申告フィールドが未検証のまま通っていた）。

- 出力 JSON のトップレベルに `sample_counts` を足す:
  `{"registered_k": <config の registered_k>, "analysed_m": <n_subjects_analysed と同値>,
    "recruitment_closed": <bool>, "note": "内訳（未完了・やめた・削除の求め）は書かない（第 20 版）"}`
- ⚠️ **`registered_k < len(confirmatory)` は矛盾なので `[NG]`**（台帳と config の二重記入のずれを黙認しない）。
- ⚠️ **`m = 0` は `[NG]`**（第 20 版 (ii)(c) 逐語「完了者が 0 名になったら確証解析は行えない」）。
- ⚠️ **欠員検査（`:187-190`）は緩めない。** 名簿にいて割付が無ければ NG のまま
  （削除の求め・未実施で外した人は研究者が `confirmatory` から外す。`registered_k` が k を保つ）。
- ★ **既に実装済みで触らないもの**（着手時に一次で確認）:
  `fisher_combine` の `n<2` 非適用（`:590-594`）／`n_subjects_analysed`（`:880`）／
  `n==1` caveat（`:904-907`）／未完了者の `primary.skipped`（`:701-704`）。
  ⚠️ **ここを「作る」と思って重複実装しないこと。**

### A-3 `docs/g1-deletion-ledger.md` — O1 版を型として G1 の経路を網羅する

- 型は `docs/o1-deletion-ledger.md`（§1 経路の違い / §2 要求の受け方 / §3 A-n・B-n チェックリスト /
  §5 保管上限 / §6 実施記録（メタデータのみ・append-only）/ §7 台帳自身の検査）。
- ⚠️ **G1 固有の対象**（O1 版に無いもの）:
  `blocks/P0xx.json`（gitignore・端末にしか無い）／`results/` の集計／
  **紙の記録用紙**（`protocol.md §2.2`・⚠️ 施錠保管されている物理媒体）／
  **G1-C 回答シート（＝ 同意の正本）**／課題ページの提出物は無い（本文を保存しないため）。
- ⚠️ **O1 版に在って G1 に無いもの**: 48 時間の猶予・端末側の最小削除幅（`.age` の自動提出が G1 では
  ブロックごとの手押しなので猶予が存在しない）。★ **流用せず「無い」と書く。**
- ★ 共用資産（ロスター・P-ID↔個人の対応表）は **O1 版 §5b を参照**する（⚠️ 3 か所目を作らない）。
- `scripts/check-g1-collection-readiness.sh` に検査 **[9] 前提条件 8** を足す。

### B `docs/person-lifecycle-ledger-template.md` — 構築仕様書

設計 `.steering/20260927-o1-receipt-ledger/t3-person-ledger-design.md` §2.2〜2.4 を
**そのまま作れる形**（列・入力規則・数式の逐語・条件付き書式）に落とす。⚠️ 実物は作らない。

### C `consent-diff-proposal.md` — 差分案（適用しない）

⚠️ **Allowed Files を提案ファイル 1 本に閉じる**ことで、被験者向け文書（契約）を
Loop が勝手に書き換える経路を構造的に無くす。★ 反映は研究者が承認してから人の手で行う。

## 変更対象

### 修正するファイル
- `experiments/20260801-controlled-friction-task/validate_blocks.py` — A-1（issue 001）
- `experiments/20260801-controlled-friction-task/protocol.md` — A-1 の記入手順（issue 001）
- `experiments/20260801-controlled-friction-task/analyze.py` — A-2（issue 002）
- `experiments/20260801-controlled-friction-task/config.json` — `sample_roster` に
  `registered_k` / `recruitment_closed` を足す（issue 002。⚠️ `revision` は触らない）
- `scripts/check-g1-collection-readiness.sh` — 検査 [9] 追加 ＋ [7] の注記更新（issue 003）
- `docs/agent-shared.md` — リンクハブに新規 2 文書の行（issue 003）
- `docs/o1-deletion-ledger.md` — G1 版への相互参照 1 行（issue 003）

### 新規作成するファイル
- `docs/g1-deletion-ledger.md` — G1 の削除保証（issue 003）
- `docs/person-lifecycle-ledger-template.md` — T3 構築仕様書（issue 004）
- `.steering/20260927-precondition8-t3-and-consent/consent-diff-proposal.md` — 差分案（issue 005）

### 削除するファイル
- なし

## 影響範囲

| 影響先 | 対処 |
|---|---|
| `config.json` にキーを足す | ⚠️ ハッシュ検査は**無い**（着手時に確認: `check-g1-collection-readiness.sh` は `revision.version` だけを見る）。`revision` を変えないので版の parity 検査は緑のまま |
| `analyze.py` の出力 JSON の形 | ★ `results/` は現在 `.gitkeep` のみ（確証データ 0 件）なので既存成果物との非互換は生じない |
| `validate_blocks.py` の判定 | ⚠️ 既存の割付（status 無し）の挙動は**完全に不変**（後方互換） |
| G1 ゲートの未達件数 | 3 件（記録票 A/B/C）→ 検査 [9] の追加で**増えない**ことが issue 003 の AC |
| 被験者向け文書 | ⚠️ **1 文字も変えない**（差分案のみ） |

## 既存パターンとの整合性

- **`--selftest` に陽性対照と陰性対照を対で置く**（`validate_blocks.py:632-951` / `analyze.py:1291-1296` /
  `check-g1-collection-readiness.sh` の `expect_red` / `expect_stays_green`）。
  ⚠️ 「検査が緑」だけを確かめず「**壊したら赤になるか**」を必ず対で書く。
- **台帳は append-only・メタデータのみ**（`docs/o1-deletion-ledger.md` §6・tombstone 規則）。
- **機械可読マーカ**（`<!-- o1-retention: set -->` の型）を G1 台帳にも置き、ゲートがアンカーを読む。
  ⚠️ **アンカーの喪失を緑にしない**（消えたら赤）。

## テスト戦略

- 単体: `validate_blocks.py --selftest` / `analyze.py --selftest`（★ 新規ケースは**対照つき**）
- 統合: `bash scripts/check-g1-collection-readiness.sh`（exit / 未達件数）
- 文書系 issue: `*-acceptance.sh`（必須節の grep ＋ ⚠️ **禁止語の不在**＝ repo に人単位ラベルが載っていないこと）
- ⚠️ E2E（実物のスプレッドシート・実フォーム）は**本タスクでは行わない**（別タスク・要研究者同席）

## ロールバック計画

- issue ごとに 1 PR。⚠️ **`config.json` の変更（issue 002）だけが唯一の「契約に触る」変更**なので、
  戻すときは `sample_roster` のキー 2 つを削るだけで元の挙動（無条件 NG）に戻る
  （★ `closed` の既定が `false` なので、**キーを消しても保護は緩まない**）。
- 文書系（003/004/005）は追加のみ。revert で完全に戻る。
