# 研究者判断バッチ 6（判断 4）の帰結を SSOT へ反映する

> 起点: `.steering/_handoff/next-session-decision4-reflection.md`（⚠️ 一次資料ではない。当たりを付けるためだけに使う）。
> 判断の一次は `.steering/20260919-theory-ssot-promotion/decisions.md` **判断 4**（研究者の回答 10 件・2026-09-20）。
> ★ 本タスクは**反映だけ**を行う。新しい裁定はしない。⚠️ 反映の途中で規定の無い点が出たら止まって研究者に聞く。

## 背景

- 段 3（理論の SSOT 昇格）の後始末として、研究者に 10 件を聞いた（判断 4）。回答は記録済みだが、反映は未着手である。
- 反映しないと、ADR-034 が Proposed のまま（ADR-014 判断 1 / 4 が効き続ける）・事前登録に前提条件が無い・pre-SSOT の契約群が SSOT の「受容」と衝突する語を使い続ける、などの状態が残る。

## ゴール

判断 4 の #1 / #4 / #5 / #6 / #7 / #8 を、該当する一次の文書へ反映する（#2 / #3 / #9 / #10 は文書の変更なし）。

## スコープ

### 含むもの
- 2-1: ADR-034 を Accepted にする（ステータス行・状態の欄）。`docs/adr/README.md` の ADR-014 行と ADR-034 行。`docs/o1-roster-operations.md` §5。「収集完了」の古い記述の洗い出しと反映。memory の更新
- 2-2: G1 の事前登録 第 19 版（収集開始の前提条件 7 を足す）。⚠️ 版一致検査のため `analyze.py` の `PREREG_REVISION` と `config.json` の `revision` も 19 にそろえる。ADR-034「代償・残る障害」7 の状態の欄
- 2-3: 「誤受容」→「誤採用」ほかの改名（測定辞書・EVAL-NCC の契約群・`docs/theory/` 2 本）と注記の更新。glossary の扱いの判断
- 2-4: CORE-CS §5.0 の未決（ADR-033 D6 の検査を EH1 の支持に数えるか）を閉じる。Nudge の時期（と有無）を本人が統制する経路を見直し候補（未決）として登録し、`intervention-design` Skill から辿れるようにする
- 2-5: 段 3 の引き継ぎ（`next-session-theory-stage3-followups.md`）の §2 注記を反映済みへ、§3 に ADR-035 の未決 3 つを足す

### 含まないもの
- ⚠️ ADR の本文の書き換え（ステータス行・状態の欄・日付つきの注記だけ）
- ⚠️ 事前登録 `§3.1`〜`§3.6` の変更（凍結）。G1 の途中離脱者の数え方の**中身**（研究者判断・前提条件として立てるだけ）
- ⚠️ 被験者向け文書（`participant-setup-guide.md`・同意文書）の変更（ADR-034「影響を受ける文書」）。`wbs-verification-halfyear.md` は次の WBS 改訂へ回す（同）
- ⚠️ 変数名 `accepted_wrong`・過去の判断記録（各 `decisions.md` / `requirement.md` / `design.md` / `tasklist.md` / `next-task.md` / `theory-propagation-audit.md` / `_handoff/*`）・`.idea/` の改名
- 理論名（判断 4 #9 → S3 の後）・補足の検索（#10 → 差分を外部の文書に書く前）
- Nudge の統制経路そのものの設計（見直し候補として登録するだけ）

## 受け入れ条件（引き継ぎ §4 のまま）

- [ ] 1. ADR-034 のステータスが Accepted で、README の ADR-014 行と ADR-034 行が整合している。`o1-roster-operations.md` §5 が効いている状態になっている
- [ ] 2. `grep -rn "収集完了" docs/ .claude/skills/` の各ヒットについて、直したか・直さない理由を `.steering/` に記録した
- [ ] 3. 事前登録に第 19 版があり、`check_frozen_sections.py` が緑（★ 加えて `analyze.py --selftest` が緑 —— 版一致検査）
- [ ] 4. §2-3 の対象ファイルで「誤受容」が 0 件（★ 注記の中の旧名の言及を除く —— 除いた行は記録する）。変えない記録ファイルの件数は元のまま
- [ ] 5. CORE-CS §5.0 の未決が閉じ、Nudge の見直し候補が登録され、`intervention-design` Skill から辿れる
- [ ] 6. `/cross-review` の 2 巡を通した（または skip の理由を書いた）

## 関連ドキュメント

- `.steering/20260919-theory-ssot-promotion/decisions.md` 判断 4（一次）
- `docs/adr/ADR-034-g1-o1-parallel-conduct.md`・`ADR-014`・`ADR-033`・`ADR-035`・`docs/adr/README.md`
- `experiments/20260801-controlled-friction-task/preregistration.md`（第 18 版の書き方）・`check_frozen_sections.py`・`analyze.py`・`config.json`
- `.steering/20260916-gse-theory-operationalization-review/`（測定辞書・EVAL-NCC 契約群・CORE-CS 契約）
- `docs/architecture/intervention-decision-engine.md`・`.claude/skills/intervention-design/SKILL.md`

## 運用メモ

- /reimagine 適用: **No**
- 理由: 研究者が既に裁定した中身を一次の文書へ書き写す作業であり、複数案の比較が要らない（段 3 の親タスクの運用メモと同じ）
- grill: 引き継ぎファイルが範囲・受け入れ条件・変えないものを確定済みで、判断分岐は判断 4 で閉じている → 追加の質問はしない（⚠️ 反映中に規定の無い点が出たら止まって聞く）
- モデル: 反映の判断は Opus（メイン）。機械的な置換（2-3）は Sonnet のサブエージェント
