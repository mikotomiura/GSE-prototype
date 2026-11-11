# 論文 3 の attack-me round 3 への対応の計算 3 つ

## 背景

論文 3（打鍵の系列モデルの個人の学習）の外枠への attack-me round 3 は major だった（`.steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-3/verdict.md`）。研究者は判断 24（同 `decisions.md`）で次を選んだ。

- T1（Take-home の「at most about 1e-3 … not read as a per-person gain」と感度の合成の食い違い）: 文で直したうえで、最頻値の分解（a = 本人(τ) − 最頻値、b = 最頻値 − 共通）を感度の合成の陽性と陰性対照に当て、分解が埋めた個人差を見分けるかを確かめる。
- R1（事前分布の最頻値）: 実データでも最頻値を比べの相手に加え、主の表（Table 2）を作り直す。置き方は「列と候補の両方」（2026-11-11 に研究者が AskUserQuestion で選んだ）。
- T5（CS1 の感度が 1 種）: CS1 の種を足す（用量の各段 2 種・陰性対照 5 種）。
- 機械: 実データは職場の PC（HP Z2）、合成は Mac。

## ゴール

1. 計算 1（Mac）: 感度の合成の CoAuthor の複製に分解を当てた結果と、条件に先に書いた読み（Take-home の「読まない」を残す・弱める・やめる）の当て。
2. 計算 2（Mac）: CS1 の 6 複製を足し、D7 の読みを 2 種・5 種で当て直した結果。
3. 計算 3（HP Z2）: 最頻値を列と候補に置いた主の表の集計値。Mac では条件とコードと合成の門までを作り、職場の PC への引き継ぎを書く。
4. 結果がそろったら verdict.md の「直す順」で外枠を直し、round 4 を回すかを研究者に問う。

## スコープ

### 含むもの
- 3 つの計算の条件（コードより前にコミット）・コード・合成の門（selftest・変異）・Mac での本計算・notes。
- 結果に依らない外枠の直し（T8・T9・T10・言い回し・Aalbers と Saeb）と、文献の調べ（T4）・意図の資料の更新は、計算の間に進めてよい。

### 含まないもの
- 実データ・書き手ごとの値・npz をメインの文脈で開くこと（集計値だけ）。
- 外部の LLM（Codex を含む）に打鍵の内容・NDJSON・書き手ごとの値を送ること。
- 結果を段 1 の候補の採否や ADR-047 の根拠にすること。
- push と PR（研究者が確かめてから）。

## 受け入れ条件

- [ ] 各計算の conditions.md と SEED が、その計算のコードより前のコミットにある。
- [ ] 合成の門（selftest・変異）が通り、本計算の来歴（run_id・code_hash・版）が残る。
- [ ] 計算 1・2 の notes に、条件の読みの形の当てと、外れた所が書かれている。
- [ ] 計算 3 のコードが合成の門を通り、職場の PC への引き継ぎがある（実データの本計算は職場の PC）。
- [ ] code-reviewer と /cross-review（Codex 込み・書き手ごとの値は送らない）を通す。

## 関連ドキュメント

- `.steering/_handoff/next-session-gse-paper3-round3-computations.md`
- `experiments/20261110-per-person-sensitivity/`（感度の合成）
- `experiments/20261106-tau-mode-candidate/`（最頻値の試験・分解の定義と形 1〜5）
- `experiments/20261104-timeseries-tau-extend/`（当てはめと選び）
- `papers/per-person-learning/manuscript/outline.md`

## 運用メモ
- /reimagine 適用: No
- 理由: 計算の方針は判断 24 と研究者の選択（最頻値は列と候補の両方）で決まっていて、残るのは既存の試験の作りへの追記。設計の分岐は条件に書いて読みの形を先に固定する。
