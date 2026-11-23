# 背景のステージの机上の検査 —— 揺れの world の `res=sub` の赤の原因の切り分け

## 背景

揺れの world（`.steering/20261014-rhythm-stage-speed-confound-world/`）の本番で、背景のステージの検査に初めて赤が出た。L300 で緑でなかったのは両段（c100・c200）とも `res=sub` の候補だけで、`res=sec` の 12 本は両段とも緑だった。

判定の後に一次の `e13.json` から計算し直したところ（同 notes の「赤の数値の確かめ直し」）、次が分かった。

- c100 の赤は lr の攻撃者だけが運んでいる。天井で判定から外した hgb では、`res=sub` の上乗せは 12 本とも点推定 +0.014 以下だった。
- c200 で hgb でも上乗せの下限が 0.03 を超えたのは、`raw` の `sub` の 3 本だけだった。
- 赤の候補の重要度の上位には `r_absdiff`・`r_sd`（と前の窓の同じ量 `d1_`・`d2_`）が入った（記述・重要度は上乗せを分けたものではない）。

したがって赤には 2 つの読みが残る。描画が A_speed に無い手がかりを運んでいる、という読みと、A_speed の中にある手がかりのうち lr が取り出せない形のものを、描画の特徴が lr に取り出せる形で運び直している、という読みである。研究者と 2026-10-15 に決めた方向（引き継ぎ `.steering/_handoff/next-session-rhythm-stage-after-speed-confound.md` §3 の 1）は、これを 2 つの層に分けて切り分けること。

- (a) 攻撃者の能力の差: A_speed の特徴に非線形の変換を足した lr を基準にして、上乗せが残るか。
- (b) 推論の元の特徴: 赤の候補から `r_absdiff`・`r_sd` の系統を落として、上乗せが消えるか。

## ゴール

1. 設計（`design.md`）を書く。何を落とすか・基準のモデル・読み方を、切り分けの値を見る前に決める。固定の前の `/cross-review` に通し、計器とともにコミットして固定する。
2. 計器を `experiments/20261015-rhythm-stage-speed-cause-split/` に作り、c100・c200 の本番と同じ seed（20261020）で列を作り直す。前のタスクの `e13.json` の値を作り直しで再現できることを確かめてから、(a)・(b) を回す。
3. notes を書き、`/cross-review` に通す。

## スコープ

### 含むもの
- 揺れの world の c100・c200（L300）の、前のタスクの本番と同じ合成の列。
- (a) A_speed の特徴の非線形の変換を足した lr を基準にした上乗せ。c100 の hgb（天井）・c200 の hgb の値を並べて読む。
- (b) 描画の特徴から `r_absdiff`・`r_sd` の系統を落とした上乗せ。
- 作り直しの再現の検査（前のタスクの `e13.json` の A_speed と赤の候補の値）。

### 含まないもの
- L60 の λ の格子を広げる下見（引き継ぎ §3 の 2・別のタスク・研究者 2026-10-15）。
- 揺れの形を変えた world（引き継ぎ §3 の 3・この結果を見て決める・別のタスク）。
- 前のタスク・第 1 回・第 2 回・中間の world の入れ物・判定・notes を変えること（判定は書き換えない）。
- `src-tauri/`・EH3 のファイル。
- 実在の人の打鍵。キーストロークの内容・NDJSON の生ログ（合成も）を外部の LLM（Codex を含む）に送ること。

## 受け入れ条件

- [ ] `design.md` が、落とす特徴・非線形の変換・基準・読み方を、切り分けの値より前に決め、計器とともにコミットされている
- [ ] 固定の前の `/cross-review` の結果と対応が `decisions.md` にある
- [ ] 作り直しで前のタスクの `e13.json` の値（A_speed と赤の候補）が再現されたことが notes にある（再現しなければ (a)・(b) を回さずに止める）
- [ ] (a)・(b) の結果が `experiments/20261015-rhythm-stage-speed-cause-split/results/` と `notes.md` にあり、探索的と併記され、前のタスクの判定を書き換えていない
- [ ] 回す前に `gh run list` と `Get-CimInstance Win32_Process` を一次で確かめた記録がある

## 関連ドキュメント

- `.steering/20261014-rhythm-stage-speed-confound-world/`（design・decisions）
- `experiments/20261014-rhythm-stage-speed-confound-world/notes.md`（赤の数値の確かめ直し・親タスクへの材料）
- `.steering/_handoff/next-session-rhythm-stage-after-speed-confound.md`
- `docs/experiment-tracking.md`

## 運用メモ
- /reimagine 適用: No
- 理由: 切り分けの形（(a) 非線形の変換を足した lr を基準にする・(b) `r_absdiff` と `r_sd` の系統を落とす）は研究者と決めた引き継ぎ §3 で決まっている。残る細部は固定の前の `/cross-review` 2 巡で見る（研究者・2026-10-15・推奨どおり）。
