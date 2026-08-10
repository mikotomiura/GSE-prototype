# G1 確証実施の前提を整える（P010 の shakedown 化・n の凍結・実施状態の記録）

## 背景

⚠️★★ **P010 は、凍結文書が「実施の前提」としている 3 点を満たさないまま走っている。**
2026-08-10 に P010 の復号・検証を行った際に判明した（`experiments/.../notes.md §10`）。

| 事前登録の要求 | 文書の記述 | ★ 実際（実測） |
|---|---|---|
| 実施条件 = Phase1 完了 ＋ 研究者承認による**凍結解除後** | 「Phase1 は GATE2 = pass / GATE3 = DataInsufficient であり、**まだ解除されていない**」 | ⚠️ P010 が 10 ブロック実施済み |
| `§2.4-2`「**確証データを 1 件も取得する前に** n を凍結し `design.n_subjects` に数値で書く」 | 手続きは `notes.md` に明記済み（P-1 後に凍結） | ⚠️ **`TO_BE_FROZEN_AFTER_PILOT` のまま**。パイロット (PILOT-mac / PILOT-win) は 4/4 実施済みで凍結の前提は整っている |
| `config.json` の `status` | `PREREGISTERED_FROZEN_NOT_EXECUTED` | ⚠️ 実施済み |

`blocks/P010.json` は `assign.assign` 由来（`confirmatory: False` を持たない）＝**コード上は確証標本**である。

### ⚠️★★ さらに: 「確証標本に誰が入るか」を決める仕組みが実質存在しない

`analyze.py` の `main()` は `bdir.glob("P*.json")` で割付ファイルを拾うが、
★ **`confirmatory` フラグを一度も見ていない**（`grep -n "confirmatory" analyze.py` で確認）。
⚠️ しかも glob `P*.json` は **`PILOT-mac.json` / `PILOT-win.json` も拾う**。

→ ★ パイロットが確証解析から外れているのは
**「dataset に NDJSON を置いていないから」であって、コードが保証しているわけではない**。
（`validate_blocks.py` は `spec.get("confirmatory") is False` を見ているのに、`analyze.py` は見ていない。）

⚠️ これは本日 2 回踏んだのと同じ型である——**文書が定めた区別をコードが持っていない**
（`notes.md §10-7` の版番号ドリフト、`§10-9` の 2 つの数え方のずれ）。

### ★ 今ならまだ間に合う

`results/` は `.gitkeep` のみで、★ **判定は一度も出していない**（`analyze.py` を走らせていない）。
`§3.10` を第 14 版で凍結できたのと同じ理由で、**結果を見る前に決めるなら研究者の自由度にならない**。
★ **順序が価値を決める。**

## ゴール

次の被験者を走らせる前に、**確証標本の定義がコードで強制され、n が凍結され、
実施状態が文書と一致している**こと。

Done は exit code で言える:

- `python3 analyze.py --selftest` → 0（roster の新ケースを含む）
- `python3 validate_blocks.py --selftest` → 0
- `bash run.sh` → GREEN
- ★ **実データ**: `analyze.py` が **P010 を確証解析に入れない**（roster が shakedown だから）
- ★ **壊して赤**: roster の P010 を confirmatory に戻すと解析対象に入る（検査が空回りしていない）
- ⚠️ roster に無い割付ファイルを **黙って無視しない**（明示的に報告する）

## 決定事項（grill で確定・`decisions.md` 参照）

1. **P010 は shakedown**（確証標本外）。`§2.8` に条項を追加する
2. **n = 3**（確証標本）。P010 は含まないので**新規 3 名**が要る
3. **SSOT は `config.json` の `sample_roster`**（★ git 管理下）。`blocks/*.json` は gitignore 対象で
   この Mac にしか無いため、この分類を託さない
4. **凍結解除は研究者承認として記録する**（Phase1 GATE3 は判定保留のまま）

## スコープ

### 含むもの

- `config.json`: `design.n_subjects: 3` の凍結 / `sample_roster` の新設 / `status` の更新 / 第 15 版へ
- `preregistration.md` 第 15 版: `§2.8` に shakedown 条項 / 実施条件の現状記録 / n 凍結の記録
  （⚠️ **この改訂は P010 取得後**であることを明記する）
- `analyze.py`: `sample_roster.confirmatory` にある被験者だけを解析する。
  ★ roster に無い割付ファイルは**明示的に報告**（silent skip を作らない）
- `notes.md`: 凍結の日付とコミットハッシュ（`§2.4-1` 手続き 3）
- `data.md` 冒頭「本実験は未実施」の訂正
- 両スクリプトの `--selftest` に回帰ケース

### 含まないもの

- ⚠️ **`src-tauri/` の変更**（配布物は無変更。`zip` 再配布不要は 20260810-detect-multi-session-block で確認済み）
- **P010 の解析そのもの**（`§3.4` の見る順序。本タスクで判定は出さない）
- **P010 のフォーム回収**（`produced_chars` 10 件 / 操作チェック 7 件）→ 別タスク
- **記録用紙と `blocks/P010.json` の `file` 列の突き合わせ** → 別タスク
- **Phase1 GATE3 の決着** → 別トラック（本タスクは「保留のまま G1 を始める」と記録するだけ）
- **被験者募集の実務**（日程調整・受付メール）

## 受け入れ条件

- [ ] `analyze.py --selftest` / `validate_blocks.py --selftest` / `run.sh` が緑
- [ ] ★ 対照つき: roster が shakedown なら P010 が解析に入らず、confirmatory に戻せば入る
- [ ] ⚠️ roster に無い割付ファイルが黙って落ちない（報告される）
- [ ] `config.json` の `design.n_subjects` が **3**、`sample_roster` が git 管理下にある
- [ ] `preregistration.md` 第 15 版に「⚠️ 本改訂は P010 取得後・いかなる解析より前」が明記される
- [ ] `notes.md` に n 凍結の**日付とコミットハッシュ**（`§2.4-1` 手続き 3）
- [ ] `config.json` の `status` と `data.md` 冒頭が実態と一致する

## 関連ドキュメント

- `experiments/20260801-controlled-friction-task/preregistration.md` §2.4 / §2.8 / §3.4 / §3.6
- `experiments/20260801-controlled-friction-task/notes.md` §10（P010 の一次記録）
- `.steering/20260810-detect-multi-session-block/`（前タスク・第 14 版）

## 運用メモ

- /reimagine 適用: **No**
- 理由: 実装は自明（roster を読んで絞る + 文書の記録）。★ 設計判断（P010 の位置づけ・n・SSOT の場所・
  凍結解除の扱い）は grill で 4 点とも確定済み。
