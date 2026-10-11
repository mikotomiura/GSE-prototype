# 研究者本人の G1 の書き写しで照合の確かめを試す（g1-copy-self-trial）

## 背景

ADR-039 D6 の照合の確かめは、これまで人の打鍵の記録で試していない。前の 2 回は、本文から合成した並び（`experiments/20261009-length-sequence-uniqueness/`）と、executor が同じ換算表で打った合成入力（`experiments/20261009-matching-attack-prototype/`）だった。人のローマ字の綴りの揺れ・打ち間違いと BackSpace・変換のやり直し・書き写しの途中で止まった位置は測っていない。

研究者本人が被験者になった G1 の記録（P009・P010。G1 の番号で Phase1 とは別）の書き写しのブロック（block01・block10・原文 `experiments/20260801-controlled-friction-task/materials/copy.md`）は本人の記録なので、再同意なしに試しの計算に使える（ADR-039 D8 の 2026-10-11 の注）。引き継ぎ: `.steering/_handoff/next-session-g1-copy-self-trial.md`。

## ゴール

1. 照らし合わせ: 原文から合成した長さの並びと、記録のカテゴリ列から数えた並びを比べ、ずれの量と原因（綴りの揺れ・打ち間違いと BackSpace・変換・止まった位置・区切りの挿入と欠落）を分ける。
2. 照合: 記録の連続した k 区間から、原文を候補 N 本（おとりは青空文庫 1,500 作品）の中で当てる正答率を、偶然の水準 1/N と並べる。手順を知らない長さだけの攻撃（前の L）を主にする。
3. 加工: 前の試作の L の加工を同じ記録にかける。

合否の判定ではない。結果は、同意文 v2 の第 3 層「起こりうること」1 の一文を「研究者本人の記録で試したところ」と書き直す材料と、本番の関門（2 本目の課題）の設計の材料になる（文面は研究者が決める）。

## スコープ

### 含むもの
- `experiments/20261011-g1-copy-self-trial/`（結果の前に手順と値を固定してコミット）
- notes.md・ADR-039 D6 に日付つきの注・issue #333 にコメント

### 含まないもの
- 同意文 v2 の文面の確定（材料を出すまで）
- G1 の他の参加者の記録（再同意の前は使わない）・記録の公開
- 健康状態の推定・人による違い・結び付けの測定（1 人・1 原文・4 ブロックでは測れない）
- G1 の一次の記録（data.md・notes.md §10）の P009・P010 の記述の訂正（研究者が決める）

## 受け入れ条件

- [ ] `preregistration.md`・`config.json`・`SEED` を結果の前にコミットした
- [ ] 復号した NDJSON と、記録から作った区間の並びは repo の外に置き、作業後に消した。repo に入れたのは集計だけ
- [ ] 自己検査が通り、`run.sh` で照らし合わせ・照合・表まで 1 コマンドで回る（2 回回して結果がバイト単位で同じ）
- [ ] notes.md に全セル・診断・限界・逸脱を書いた
- [ ] /cross-review 2 巡（Codex には記録を送らない）・ADR-039 D6 の注・issue #333 のコメント

## 関連ドキュメント

- `docs/adr/ADR-039-research-use-and-release.md` D6・D8
- `experiments/20261009-matching-attack-prototype/notes.md`・`experiments/20261009-length-sequence-uniqueness/`
- `.steering/20261007-research-use-and-release/consent-v2-draft.md` 第 3 層

## 運用メモ
- タスク名は引き継ぎのファイル名に合わせた（研究者は質問で異を唱えなかった）
- /reimagine 適用: No
- 理由: 前の 2 回の手順を踏襲する実測で、設計の分岐は研究者に聞いて閉じた（decisions.md 判断 1）
