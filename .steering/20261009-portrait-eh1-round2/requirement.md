# portrait-eh1-round2

## 背景

肖像の EH1 第 1 回（`.steering/20261009-portrait-eh1-eh2/`・`experiments/20261009-portrait-eh1/`）は、E1-3 が両 world とも全組判定不能だった（判断 9）。v2 では材料（`p_stuck`・F の水準）が打鍵の有無を超えて停滞を当てたが（探索で +0.17〜+0.24）、既定の scheduler を通る陽性対照 PC2 は働かなかった。→ 既定の scheduler を通る形について、検査器が漏れを拾えることがまだ示されていない。

ほかに残ったもの:
- U-4 の第一候補 `recent`（60 s 以上の不在の中では更新しない）は固定の外の探索で、E1-3・E1-2 を当てていない。
- どの仮の文法も「揺らぎに強く、経路を写す」を満たさなかった（ordinal・keyed は ±50 ms で崩れ、raw は v2 で経路を写さない）。
- 計器の不具合 2 件（`run.sh` が Windows で `.exe` を補わない・`checks.py --jobs` を渡せない。第 1 回 notes 判断 W1・W2）。

研究者の決定（親の判断 9 の 3）: EH1 の第 2 回を新しい固定で回す。親の判断 8 は「形が停滞を写していないことを、参加者の前に機械で確かめる」を求める。E1-3 が判定不能のまま EH3 に進むと、未検証の形を人に見せることになる。

## ゴール

1. 第 2 回の合否の基準を、結果を出す前に `design.md` §3 に固定してコミットする（コミットの時刻で示せる）。
2. `experiments/20261009-portrait-eh1-round2/` を 1 コマンドで再現できる形で作り、スモークで全段が通ることを確かめる。
3. 本番を G-GEAR（Windows・16 コア）で回せるよう、引き継ぎを `.steering/_handoff/` に書く（本番は計測の run・self-hosted CI と重ならない時間に回す）。

## スコープ

### 含むもの
- 計器を第 1 回から写して直す: PC2 の作り直し・E1-3 の 300 s の窓・`recent` を固定の組へ・新しい文法・`run.sh` の `.exe` と `--jobs`
- 検査器の自己検査（変異）を新しい部分にも足す
- スモーク（この機械）

### 含まないもの
- 第 1 回の `experiments/20261009-portrait-eh1/` を変えること（固定した記録として残す）
- 製品への実装（`src-tauri/`・`src/` を変えない）
- EH2・EH3・ADR・U-4 の確定（第 2 回の結果の後に研究者が決める）
- 本番の結果を読んで解釈すること（本番の後のセッション）
- PR（merge の順は S-MR → 親 → `docs/portrait-eh1-eh2` → このブランチ。push だけ）

## 受け入れ条件

- [ ] `design.md` §3 の基準を、第 2 回のどの結果（スモークを含む）よりも前にコミットした
- [ ] `run.sh --smoke --world v2` と `--world v1` がこの機械で全段を通る（`.exe` の補いと `--jobs` を含む）
- [ ] 自己検査: 新しい PC2 が 300 s の窓で検査器を働かせるかはスモークで**見る**（判定は本番）。変異で E1-4・E1-7・E1-3（偽の漏れを作らない）が期待どおり
- [ ] 生成した NDJSON と `work-*/` をコミットしない
- [ ] G-GEAR 向けの引き継ぎを書いた
- [ ] /cross-review 2 巡と対応を `decisions.md` に記録した

## 関連ドキュメント

- `.steering/20261009-portrait-eh1-eh2/decisions.md` 判断 2・3・9・10・11、`design.md` §3・§8
- `experiments/20261009-portrait-eh1/notes.md`
- `.steering/20261005-portrait-invitation-constraints/decisions.md` 判断 5・8・12
- `docs/experiment-tracking.md`・`reproducibility-discipline` Skill

## 運用メモ
- /reimagine 適用: No
- 理由: 研究者の回答（2026-10-09）。設計の分岐は AskUserQuestion 8 問で閉じた。第 1 回も仮の文法を因子に並べる形で /reimagine を使わなかった（第 1 回の判断 2）。代わりに固定の前に /cross-review で基準の穴を探す。
