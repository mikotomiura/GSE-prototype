# 次セッション — AI 疲労 文献 DB: 判定の間に Claude が行うこと（B 群のサーヴェイ・判定者 2 のファイル）

> 作成: 2026-09-30（`.steering/20260930-ai-fatigue-candidates-appraisal/` の完了時）。⚠️ **このメモを一次資料にしない。** 数字は 2026-09-30 の値で、出どころを書いた。
> ★ いまは研究者（判定者 1）の判定の段。判定者 1 は、判定の前に元の DB 34 件と追加候補 225 件の AI の評価版を読む（研究者の決定・`../20260930-ai-fatigue-judge-file/decisions.md` 判断 21）。Claude は判定そのものに関わらない。

## §0 打ち込む用（★ `/clear` してから。モデルは Opus）

```
.steering/_handoff/next-session-ai-fatigue-after-appraisal.md を読んで、AI 疲労 文献 DB の次の段（研究者に確かめてから、B 群のサーヴェイか判定者 2 のファイル）を進めてください。/start-task から始めます。

⚠️ 作業は worktree（C:\wt\ai-fatigue-judge-file など）で、origin/main から新しいブランチを切って行う。main の作業ツリー（C:\GSE-prototype）には別トラックの未コミット作業がある。git add -A / git add <dir> は使わない。
⚠️ 研究者が判定中のファイル（Downloads の AI_fatigue_judge-sheet_2026-09-30_judge1.xlsx）には触らない。作り直すときは先に SHA-256 で未記入か確かめ、記入があれば止まって聞く。
⚠️ 先に git fetch → origin/main を確かめる。Codex を回す前に当日の実消費を確かめる（台帳はブランチごと・合算で上限 300,000・.codex/budget.json は git checkout -- で戻さない）。
⚠️ 外部に出る操作（著者への照会・フォーム）はしない。学術 API に研究者のメールアドレスを送らない。本文・PDF・抄録の全文はコミットしない。有料のデータベース・有料の本文は使わない。候補を AI の見立て（E1〜E3）で絞らない。
★ 完了時は code-reviewer ＋ security-checker（並列）・/cross-review 2 巡・git-workflow ルール 6（push → PR → CI 緑なら merge → main の CI 発火確認）。応答は日本語。
```

## §1 現在の状態（2026-09-30 17 時ごろ）

| 何 | 値 | 出どころ |
|---|---|---|
| 判定者 1 用のファイル | DB 34 件 ＋ 追加候補 **225 件**（AI の評価は載せない） | `.steering/20260930-ai-fatigue-judge-file/archive/judge/AI_fatigue_judge-sheet_2026-09-30_judge1.xlsx`（Downloads の写しと同じ SHA-256 `6984472e…`） |
| 追加候補の AI の評価版 | 225 件・抄録段（中心-A 2・中心-B 83・未確定 18・境界 47・背景（E2）58・背景（E4）1・除外（E1）15・除外（E3）1） | `.steering/20260930-ai-fatigue-candidates-appraisal/archive/AI_fatigue_candidates_AI_appraisal_2026-09-30_claude.xlsx`（`ed788f53…`・Downloads の写しと同じ）。案のデータは `scripts/appraisal_data.py` |
| 候補の一覧（SSOT） | `candidates.py` 225 件（2026-09-30 に 19 件を足した） | `.steering/20260930-ai-fatigue-judge-file/scripts/candidates.py`・足した理由と足さなかった記録は `.steering/20260930-ai-fatigue-candidates-appraisal/decisions.md` 判断 2・3 |
| 判定者 2 | 未定（判定者用ファイルは判定者を問わない形で作れる・`judge_xlsx.py --judge 2`） | 前タスクの判断 2 |
| 判定の順番 | 225 件を先に判定。B 群のサーヴェイで後から見つかる候補は、別のファイルと同じ形の AI の評価版で足す | `.steering/20260930-ai-fatigue-candidates-appraisal/decisions.md` 判断 1 の 3 |

## §2 やること（研究者に先に聞いて決める）

1. **どれから進めるか**（研究者に聞く）: (a) B 群のサーヴェイ（S-01 本検索〈手間が大・数週〉・S-06 警報疲れ・S-09 理論の節・S-11 語の用法）／(b) 判定者 2 が決まっていれば判定者 2 のファイル（`--judge 2`・評価版を開かない指示は『はじめに』に入っている）／(c) 判定が終わっていれば判定者 1 と 2 の突き合わせ。
2. **B 群のサーヴェイを行うなら**: 検索は `.steering/20260929-ai-fatigue-surveys/evidence/common.py` の関数で書く（抄録を空で上書きしない・repo の外・URL の柵）。検索式は design.md に固定してから回す。S-01 には「AI awareness」「AI anxiety」「STARA」と燃え尽きの組の検索ブロックを置く（S-14 の判定案 §4）。★ 新しい候補は、別の判定者用ファイルと評価版（同じ形）にする（判定中のファイルに行を足さない）。
3. **候補を足すときの規則**（本タスクの判断 2・3）: 論文が AI と書く一次研究で、人の疲労・燃え尽き・消耗・負担を扱うものはすべて足す。外すのは、文献でないもの・研究の報告でないもの・AI でないもの・人の疲労を扱わないものだけ。同じ研究の別の出版物（前刷りと雑誌の版）は記録ごとに分ける。

## §3 研究者に伝えてあること・残っている論点

- 評価版の境界（保留）47 件の多くは、規則だけで閉じない論点（AI を疲労の対策に使う介入を範囲の決定 (a) に入れるか・アラート疲労・変化の疲れ・AI に評価される側・データの由来が不明）。判定の後に、範囲の論点として研究者がまとめて決める材料になる。
- 抄録段の規則（本タスクの判断 4）: 抄録が一般の尺度・一般の構成概念を書くものは中心-B（項目文は未確認）。全文段は未実施が 116 件（無料の版あり 115・入手不明 1）。

## §4 落とし穴（2026-09-30 に実際に起きたこと）

- Python で文書を書き戻すと Windows で改行が CRLF になる（`open(..., newline="")` を使う・`file` で確かめる）。バックスラッシュを含む文字列は Edit で書き、`od -c` でバイトを確かめる（`\x` が不正なエスケープになった）。
- 検査の変異は「元と違う値」にする（元と同じ E4 を入れて空振りした）。読み直して保存し直すと末尾に空の行が増えるので、生成物との比較は末尾の空の行を除く。
- Codex の 1 回の実消費は、約 1,000 行の Python で 4 万・約 1,000 行の文書とデータで 7.8 万・約 310 行で 4.3 万（2026-09-30）。
- 題名だけの記録でも、CiNii・J-STAGE の検索の記録に DOI がある場合がある（S-08 §6 の Anti-Design は S-08 の検索の記録に DOI があった）。
