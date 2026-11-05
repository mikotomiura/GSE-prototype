# gse-public-data-fit-item2（公開データの当てはめ 項目 2・KLiCKe）

## 背景

- 3 本の並行（`_handoff/next-session-gse-three-parallel-tracks.md`）の T2。個別の引き継ぎは `_handoff/next-session-gse-public-data-fit-item2.md`。
- 項目 1 と案 A（CoAuthor）では、推定の 30 秒の上がりは「AI を求めた手前」にも「本人の停滞の手前」にも立たなかった。招待の契機の候補として「止まりの初期」（休止が本人の θ の一定割合に届いた時点）が挙がった。
- その値を 3〜5 名に合わせすぎないため、公開データ（KLiCKe [V264]・AI なしの英語の作文・約 5,000 本）で母集団の分布と誤発火の基準を見る。

## ゴール

- 主: 止まりの初期（0.5θ・0.75θ・時計は最後の文字からと停滞の時計の両方）の発火の頻度（1 時間あたり）と停滞に至る割合を、今の契機（`p_stuck ≥ 0.60` が 30 秒）と並べて出す。
- 副: 案 A の追試（離しの実時刻あり・AI なし）。
- 結果と研究者が決める材料を `experiments/20261101-klicke-early-stall-trigger/notes.md` と `decisions.md` に書き、合流（three-parallel-tracks §4）に渡す。

## スコープ

### 含むもの
- KLiCKe の取得（SHA-256 照合）・変換・replay・解析・集計値だけの記録

### 含まないもの
- 契機の値の決定（合流で研究者が決める）・コードの変更（`src-tauri/` は触らない）
- Kaggle [V265]（KLiCKe 由来）・本文・人口統計のファイル
- 照合論文のトラックの成果物の書き換え

## 受け入れ条件

- [ ] 条件（`conditions.md`）を計算の前にコミットした
- [ ] zip の SHA-256 が照合論文の値と一致した
- [ ] θ と onset の Python 再現が replay と全件一致した
- [ ] 主・副の結果と言える範囲を notes.md に書いた
- [ ] code-reviewer と /cross-review を並列で回し、指摘を反映した
- [ ] `[skip ci]` で main へ入れ、`_handoff/README.md` の行を完了にした

## 関連ドキュメント

- `experiments/20261101-coauthor-pre-stall-signal/`（案 A）・`docs/adr/` の ADR-030・`src-tauri/src/analysis/invitation.rs`

## 運用メモ
- /reimagine 適用: No
- 理由: コードの設計判断を伴わない探索の解析。解析の条件は研究者が AskUserQuestion で決め、計算の前にコミットする
