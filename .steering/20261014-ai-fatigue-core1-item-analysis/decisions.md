# 重要な判断

## 判断 1: 範囲（2026-10-14・ユーザー）

- 新しい文献の探索はしない。S-AF2 で見つかっている尺度の項目の文言をデータとして、内容分析だけを行う（ユーザー「具体的なデータからの分析を実施するだけかと思った」）。
- 人の回答データは使えない（[P486] は合計点だけ）ので、ここでの「データ」は項目の文言。
- ユーザーの判断が要る箇所は AskUserQuestion で聞く（判定者の列を空けて渡す形にしない）。
- 却下: 範囲を AI 系の尺度全般に広げて題名検索で補う（Claude の当初の案。C の本体を先取りし、依頼の範囲を超える）。

## 判断 2: コードブックの区分（2026-10-15・AskUserQuestion）

- 第 1 段は、M4 の 4 型（`MOT` 動機・関心の低下／`AVO` 回避／`FUT` 無益感・無力感／`IRR` 苛立ち）に `OTH` を足す（推奨どおり）。理由: 提案書 v2 §6.1 の M4 にそのまま対応し、C に渡しやすい。却下: 3 値（直接／境界／問わない）、有無だけ。
- 第 2 段は、項目に合わせた 5 区分（`TASK`・`AI_USE`・`AI_VERIFY`・`AI_PRIV`・`SOCIAL`）にする（推奨どおり）。却下: 引き継ぎの案の 4 区分（プライバシーと人との関わりが「その他」に埋もれる）。
- 判定は文言だけで行い、著者の因子名は別の列に置く。食い違いは結果として数える（推奨どおり）。却下: 因子名に従う。

## 判断 3: 境界の 7 項目の確定（2026-10-15・AskUserQuestion）

すべて Claude の予備判定どおりに確定した（`coder` = `claude-prelim+user`）。
- Lau 7 discouraged → `IRR`（副 `MOT`）／Lau 10 ignore new AI features → `AVO`（副 `MOT`）
- ZEF "too tired to do other things" → `OTH`（副 `MOT`。因子名との食い違いとして数える）
- Zhao & Liu の "tired of constantly evaluating ..." 2 項目 → `OTH`（副 `MOT`）
- ZEF "want to be alone" → `AVO`（副 `MOT`）／"need time by yourself" → `AVO`（副 `OTH`）
- 理由: `MOT` は、関心・する気・積極性の低下を文言がそのまま言う項目に限る（保守的に数える）。第 2 候補は列に残し、緩い数え方の集計に使う。

## 判断 4: 一次の入手（2026-10-15）

- [P362] の出版版の Table 1 は画像（ScienceDirect）。前刷りの p.18 と項目の文言が同じことを、メインが目で照合した。前置きの文だけが違う。
- ZEF は ScienceDirect の本文（Chrome）で Table 2・Table 3 を読んだ。CC BY 4.0。
- Zhao & Liu は Europe PMC の全文 XML（PMC13501034・CC BY 4.0）の Table 2 から取った。
- [P488] は全文 XML に AI 疲労の項目が無い（補足資料も無い。データは著者に求めれば出るとする）。出典は Kim et al. 2023（SSRN・AI 不安の論文）→ 項目未入手とした。

## 判断 5: 出典の採番（2026-10-17）

- Zhao & Liu 2026 を `docs/references.md` に [P514] として登録した（書誌は Crossref で照合）。
- 理由: 核 2 のブランチ（`docs/ai-fatigue-core2-discriminant`）が [P498]–[P513] を使っている。番号は恒久なので、核 2 の後の番号を取る。
- main へ入れる順は、`docs/ai-fatigue-motivation-claims` → 核 2 → 核 1。核 1 を取り込むときは、`references.md` の末尾の衝突を [P513] の後に [P514] を置いて解く。
