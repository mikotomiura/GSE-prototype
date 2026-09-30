# AI 疲労 文献 DB: N-05 プロトコルの次の段（判定の前に決める 2 点の反映と、研究者の確認票）

## 背景

- 前タスク `../20260930-ai-fatigue-protocol/` でプロトコルの日本語の草稿 v0.1（`protocol-ja.md`・GSRR 65 項目・確認待ち 20 項目）を作り、PR #280 で main に入った（2026-10-01 03:34 JST・MERGED を `gh pr list` で確かめた）。
- 引き継ぎ `.steering/_handoff/next-session-ai-fatigue-protocol-cont.md` §1 の順: (1) 判定の前に決めたいもの（F19・F10）→ (2) 研究者の確認 → (3) プレ査読 → (4) 英語の登録版 → (5) 登録（研究者）。
- (1) は、判定者 1 の記入が始まる前でないと判定者用ファイルを作り直せない。判定者用ファイルは archive と Downloads の写しがどちらも `48af51d3…`（未記入）であることを 2026-10-01 に確かめた。
- 2026-10-01 に AskUserQuestion で聞いた（推奨と理由を添えた・4 問とも推奨どおり。`decisions.md` 判断 1）:
  - **F19**: 案の読み方で確定し、判定者用ファイルの『判定基準』に足す。
  - **F10**: 登録前の段の判定者用ファイルに E7 を足す。
  - **範囲**: このセッションは研究者の確認票まで（プレ査読と英語の登録版は研究者の確認の後）。
  - タスク名 `ai-fatigue-protocol-cont`・/reimagine なし。

## ゴール

1. **F19・F10 の反映**: 判定者用ファイルの道具（`../20260930-ai-fatigue-judge-file/scripts/judge_xlsx.py`）の『判定基準』と除外理由の選択肢に、E4 の「尺度の原著」の読み方と E7 を足し、検査器（`check_judge_xlsx.py`）を合わせ、判定者 1 のファイルを作り直す（archive と Downloads。作り直す直前に Downloads の写しが `48af51d3…` のままかを確かめ、違えば止まって聞く）。
2. **プロトコルの草稿を v0.2 に上げる**（`../20260930-ai-fatigue-protocol/protocol-ja.md`）: [GSRR-35] の注・付録 B（判定者用ファイルの新しい版）・付録 A（年表に 1 行）・付録 F（F10・F19 を決定に）・[GSRR-7]・[GSRR-42]。
3. **研究者の確認票**（`researcher-check.md`）: 付録 F の残り 18 項目と、草稿の【案】の項目（F15）を、研究者が答えやすい形（何を決めるか・いつまでに・選択肢・草稿の案と理由・出どころ）にまとめる。★ 研究者に聞くことはユーザーに聞かない（研究者の決定待ちとして並べる）。
4. 引き継ぎを次の段（研究者の答え → プレ査読 → 英語の登録版）に差し替える。

## スコープ

### 含むもの
- 判定者用ファイル（判定者 1）の作り直し。判定者 2 のファイルは作らない（判定者 2 は未定）が、道具の上では判定者 2 の版にも同じ基準が入る。
- 検査器の変異試験（E7 を判定の語として扱う・基準の文を変える変異が赤になること）。
- 確認票に AI の 1 件ずつの判定が混ざらないことの機械検査（プロトコルと同じ規則）。

### 含まないもの
- プレ査読（attack-me）・英語の登録版・登録（OSF）: 研究者の確認の後（2026-09-30 に決めた順・判断 1）。
- 研究者の確認待ちの項目の決定（判定者 2 の人選・盲検の条件・資金・利益相反ほか）。ユーザー（判定者 1）に聞かない。
- 評価版（AI の評価の xlsx）の作り直し・元の DB の書き換え・本検索の実行。
- 有料のデータベース・有料の本文。著者への照会・フォーム・OSF など外部に出る操作。学術 API への研究者のメールアドレスの送信。本文・PDF・抄録の全文のコミット。GSE の文書（`docs/`）の書き換え。

## 受け入れ条件

- [ ] 判定者 1 のファイルの『判定基準』に E4 の尺度の原著の読み方と E7 があり、除外理由の選択肢が E1〜E7 である。`check_judge_xlsx.py` が違反 0、`--selftest` が PASS（新しい変異を含む）。評価版の検査（`check_appraisal_xlsx.py`）も違反 0 のまま。
- [ ] 作り直した判定者 1 のファイルの SHA-256 が archive と Downloads で一致し、作り直す直前の Downloads の写しが `48af51d3…` だったことを記録している。
- [ ] `protocol-ja.md` が v0.2 で、F10・F19 を決定として書き、`check_protocol_here.py` が違反 0・`--selftest` が PASS。
- [ ] `researcher-check.md` が付録 F の残り 18 項目と【案】の一覧を持ち、記録の鍵と判定の語が同じ行に無い（機械検査）。
- [ ] code-reviewer・security-checker（並列）と `/cross-review` 2 巡（Codex の当日の実消費を先に確かめる）。出荷（push → PR → CI 緑なら merge → main の CI 発火確認）。

## 関連ドキュメント

- `.steering/_handoff/next-session-ai-fatigue-protocol-cont.md`（引き継ぎ・本タスクの入口）
- `../20260930-ai-fatigue-protocol/protocol-ja.md`（草稿 v0.1）・`decisions.md`（判断 1〜19）
- `../20260928-ai-fatigue-db-appraisal/design.md`（評価プロトコル v1.0）
- `../20260928-ai-fatigue-db-appraisal/archive/input/AI_fatigue_database_with_AI_appraisal_2026-09-18.xlsx`『項目定義・採択基準』r7・r10（DB の定義）
- `../20260930-ai-fatigue-judge-file/scripts/judge_xlsx.py`・`check_judge_xlsx.py`

## 運用メモ
- /reimagine 適用: No
- 理由: 設計判断・外部の口の新設ではなく、判定の基準の 2 行と文書の追記。論点は判定者 1 と研究者が決める（判断 1）。設計の「破壊と構築」に当たるものは、研究者の確認の後のプレ査読（attack-me）で行う。
