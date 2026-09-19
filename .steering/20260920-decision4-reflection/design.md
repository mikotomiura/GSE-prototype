# 設計

## 実装アプローチ

引き継ぎ §2 の順（2-1 → 2-5）に、各反映先を**一次で開いてから**直す。ADR 本文は書き換えず、先例の形（ステータス行・状態の欄・README の行）で状態だけを動かす。

### 2-1 ADR-034 の Accepted（先例に合わせる）
- ステータス行: 先例 ADR-029 `- **ステータス**: ★★★ **Accepted**（2026-09-13・研究者判断）` に合わせ、括弧に判断の一次（段 3 判断 4 #1）を入れる。旧ステータスの文言（「Accepted になるまで ADR-014 判断 1 / 4 が効き続ける」）は消さずに「Proposed 時の注記」として残す。
- 本文（D1 の律速 3・Consequences 5・Migration 1）は書き換えない。Consequences 5 の状態の欄に日付つきで「✅ 2026-09-20 に Accepted」を足す（先例: Consequences 6 を 2026-09-19 に閉じた書き方）。
- README: ADR-034 行のステータス列 → Accepted。ADR-014 行の「上書きする予定」→「上書きした」、時期の列の「G1 の収集完了後」を合わせる（先例: ADR-016 行の「上書きが ADR-029 D3 で入った」）。ADR-014 本文には注記を入れない。
- 「収集完了」の各ヒットは直す / 直さない（ADR 本文）の理由を `decisions.md` に表で残す。

### 2-2 事前登録 第 19 版
- 第 18 版の書き方（何を決めたか / 前提条件 / 変えていないもの）に揃え、先頭に置く。
- ⚠️ 版一致検査（`analyze.py` selftest 0: `config.json` ↔ `PREREG_REVISION` ↔ 文書の見出し）が赤にならないよう、`PREREG_REVISION = 19`・`config.json` の `revision.version = 19`・`date`・`v19_changes` を足す（先例: 第 18 版のコミット `1fcca96` が同じ 3 点を動かしている）。
- `check_frozen_sections.py` と `analyze.py --selftest` を実行して緑を確かめる。

### 2-3 改名（Sonnet のサブエージェント）
- 置換規則は 3 つ（「誤受容」→「誤採用」／測定辞書の「受容率（★ AI の提案を採った割合」→「採用率」／「正しい提案の受容」→「正しい提案の採用」）。SSOT の「受容」「受容率」「受容性」は巻き込まない。
- 前後の件数を `rename-counts-before.txt` / `rename-counts-after.txt` に残す。
- 注記（測定辞書 `:20`・分析契約 `:13`）と `docs/theory/` 2 本の冒頭の改訂一覧はメインが直す（旧名への言及はここに残る）。
- glossary: 判断して `decisions.md` に残す。

### 2-4 CORE-CS §5.0 と Nudge の見直し候補
- §5.0 `:98` の「未決」→ 研究者判断（数える）と理由 2 点・証拠の種類・検査が未存在であることを書く。
- Nudge: `docs/architecture/intervention-decision-engine.md` に「見直し候補（未決）」の節を足し、`intervention-design` Skill の冒頭の注記から 1 行で参照する。

### 2-5 引き継ぎの整理
- 段 3 の引き継ぎ §2 注記を「反映済み」へ、§3 に ADR-035 の未決 3 つ。

## 変更対象

### 修正するファイル
- `docs/adr/ADR-034-g1-o1-parallel-conduct.md` — ステータス行・Consequences 5 / 7 の状態の欄
- `docs/adr/README.md` — ADR-014 行・ADR-034 行（＋ ADR-032 行の注記を要否判断）
- `docs/o1-roster-operations.md` — §5 冒頭の注記
- `docs/glossary.md` — O1 の実験名の行（収集完了）・「誤採用」の扱い
- `docs/architecture/workspace-behavior-observation.md` — `:393` / `:456`
- `experiments/20260801-controlled-friction-task/preregistration.md` / `config.json` / `analyze.py`（定数 1 行）
- `.steering/20260916-gse-theory-operationalization-review/` の測定辞書・EVAL-NCC 契約 3 本・被覆行列・CORE-CS 契約
- `docs/theory/generative-relinquishment-theory.md` / `theory-architecture-and-roadmap.md`
- `docs/architecture/intervention-decision-engine.md` / `.claude/skills/intervention-design/SKILL.md`
- `.steering/_handoff/next-session-theory-stage3-followups.md`
- memory `project_g1_build_distribution_boundary.md`

## 影響範囲

- 文書のみ（`analyze.py` は版の定数 1 行だけ）。配布物・被験者向け文書・Rust / TS は変えない。

## 既存パターンとの整合性

- ADR の状態変更: ADR-029（ステータス行）・ADR-016 行（README で上書きを示す）・ADR-034 Consequences 6（状態の欄を日付つきで閉じる）
- 事前登録の改訂: 第 18 版（前提条件の追加・変えていないもの・機械検査）
- 改名: 段 3 判断 1 #1（「非支配的協調」→「関係的自律を支える協調」の反映の仕方）

## テスト戦略

- `python experiments/20260801-controlled-friction-task/check_frozen_sections.py`（凍結節）
- `python experiments/20260801-controlled-friction-task/analyze.py --selftest`（版一致検査を含む）
- `grep` の前後件数（改名）
- `python scripts/check_citations.py`（引用に触れたら「違反なし」まで）・`python scripts/check_doc_lexicon.py`

## 検査の記録（★ 2026-09-20 に実行した実出力）

| 検査 | 結果 |
|---|---|
| `python experiments/20260801-controlled-friction-task/check_frozen_sections.py` | `[OK] 凍結節は第 1 版（6013104）と一致: §3.1(全体), §3.2(全体), §3.4(全体), §3.5(append-only), §3.6(append-only)`（rc=0） |
| `python experiments/20260801-controlled-friction-task/analyze.py --selftest` | `[OK] analyze.py selftest 緑 (…)`（rc=0・★ 版一致検査 = 文書 第 19 版 / `config.json` 19 / `PREREG_REVISION` 19） |
| `PYTHONUTF8=1 bash run.sh`（G1 実験ディレクトリ） | `[GREEN] 実施前チェック 全項目通過`（rc=0）。⚠️ `PYTHONUTF8` なしでは `[FAIL] config.json が JSON として壊れている` ほか 2 件 —— ★ HEAD の `config.json` でも同じ（cp932 の既存問題・decisions 観察 1） |
| `PYTHONUTF8=1 python scripts/check_citations.py` | `=== 違反なし ===` |
| `PYTHONUTF8=1 python scripts/check_doc_lexicon.py` | `=== 違反なし ===` |
| 改名の残存検査（下のコマンド） | `OK: 注記以外の残存 0`。★ 陰性対照: 「誤受容」を含む行を注入したファイルでは検出する（rc=0）。⚠️ **ファイルが無いと `grep` が rc=2 でも `grep -v` の後ろで rc=1（＝残存なし）に化ける** → 存在確認を先に置いた |
| 改名の diff の突き合わせ | `git diff -U0` の 33 行ペアを置換規則 3 つで写して一致（不一致 0） |
| schema parity check（`/finish-task` Step 3） | ⚠️ drift（`activity_label` が gse-dataset 側に無い）。★ 本タスクは schema に触れていない（`git diff 046f6c2..HEAD -- src-tauri/src/schema_dto.rs src-tauri/schema/current.json` = 0 ファイル）。★ 既知の保留（`.steering/20260913-esm-audit-criterion-gate/decisions.md` 判断 3「同期は本ブランチのマージ後」—— いま同期すると dataset が main より先に進む） |

```bash
# ★ 改名の残存検査（契約・理論の 7 本で、旧名が注記以外に残っていないか）
F=".steering/20260916-gse-theory-operationalization-review/measurement-dictionary.md
.steering/20260916-gse-theory-operationalization-review/eval-ncc-analysis-contract.md
.steering/20260916-gse-theory-operationalization-review/eval-ncc-dag.md
.steering/20260916-gse-theory-operationalization-review/gr-h4-h9-h11-h12-falsification-table.md
.steering/20260916-gse-theory-operationalization-review/core-proposition-coverage-matrix.md
docs/theory/generative-relinquishment-theory.md
docs/theory/theory-architecture-and-roadmap.md"
for f in $F; do [ -f "$f" ] || { echo "MISSING: $f"; exit 2; }; done   # ⚠️ 無いと黙って緑になる
if grep -n "誤受容" $F | grep -v '旧名「誤受容」\|「誤受容」→'; then echo "RESIDUAL"; else echo "OK: 注記以外の残存 0"; fi
```

## ロールバック計画

- 反映単位ごとにコミットを分ける（2-1〜2-5）。問題があれば該当コミットを revert する。
