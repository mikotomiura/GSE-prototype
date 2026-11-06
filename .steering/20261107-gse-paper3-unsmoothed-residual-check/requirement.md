# 論文 3 の新しい小さな試験 —— 平滑の無い記号の対照と擬似残差の検査

## 背景

論文 3（`.steering/20261107-gse-paper3-per-person-learning/`）の外枠の attack-me round 1（`attack-me/outline-paper3/round-1/verdict.md`）で、査読者が次の 2 点を求めた。研究者は判断 11 で範囲の凍結を解き、論文 3 の側で小さな新しい試験として、条件を先にコミットして回すと決めた。

1. 記号化の依存（verdict の表の J・R1 の 1・R3 の 3）: C2 の短距離の依存は、記号化の作り（30 秒窓・指数平滑・1 Hz・休止の秒も記号を出す）から来る分があるかもしれない。平滑の無い記号か、窓の重ならない記号の対照で見分ける。
2. モデル検査（R1 の 4）: 尤度以外の検査（擬似残差の自己相関など）が無く、「構造の補い」の読みが確かめられていない。

前の試験は `experiments/20261104-timeseries-tau-extend/`（以下 tau-extend）。並行の「構造の足りなさの試験」（`/Users/johnd/GSE-prototype-structure-deficit`・枝 `exp/gse-structure-deficit-test`）は別のセッションのもので、記号の順の並べ替えと量子化 3 通りを扱い、平滑の無い記号と残差の検査は入っていない。

## ゴール

`experiments/20261107-unsmoothed-residual-check/`（仮の名）に、条件と SEED を先にコミットし、合成の門を通したコードで、HP Z2 で本計算を回し、集計値だけの summary と notes を残す。結果は論文 3 の外枠の直し（C2 の限定・限界の節）に使う。

## スコープ

### 含むもの
- 記号の列 3 つ（判断 2）: 元の 26 記号（o）、平滑だけを外した記号（u・x_raw と y_raw を同じ 5×5 と連打の記号 25 に割る・1 Hz）、窓の重ならない記号（n・u を 30 秒ごとに間引く）。
- 擬似残差（判断 3）: 1 歩先の予測分布を x の帯・y の帯の周辺に畳んだ、乱数化した分位の擬似残差と、その遅れ 1〜10 の自己相関。
- 範囲（判断 4）: 論文の主の表と同じ。hmm3・ar1〜ar3、τ の 9 値、行は τ 他人と 2 段（他人）、相手は同じ構造の共通と r1。CoAuthor P15（k = 1・5・15）と CS1 C5（k = 1・5）。
- 読みの形（判断 5）: 向きと大きさの比（計算の前に条件に書く）。
- 合成の門（陽性対照と名指しの変異）、P-REPRO（o の列で tau-extend と一致）。
- 公開の kit の記号器に、平滑の前の値を出す道を足すかどうかは設計で決める（足すなら元の出力の一致を崩さない）。

### 含まないもの
- 並行の構造の試験の条件・コードの変更。
- 段 1 の候補の採否や ADR-047 の根拠に使うこと（D2・D6）。
- 書き手ごとの値・npz を人が開いて読むこと。
- 外枠・本文の書き直し（次のタスク）。
- 副のパネル（P30・9 人・全書き手）、τ 本人 CV、K 本人 CV。
- push と PR（研究者が確かめてから）。

## 受け入れ条件

- [ ] 条件（conditions.md）と SEED が、コードより前のコミットに入っている
- [ ] 設計を /reimagine で 2 案比べ、採った案と理由が decisions.md にある
- [ ] 合成の selftest で陽性対照がすべて通り、名指しの変異がすべて赤になる
- [ ] HP Z2 で本計算が済み、P-REPRO（o の列の tau-extend との一致）が通っている
- [ ] notes.md に読みの形のとおりの結果（集計値だけ）がある
- [ ] /cross-review（code-reviewer と Codex）を通した

## 関連ドキュメント

- `.steering/20261107-gse-paper3-per-person-learning/decisions.md` 判断 11
- `.steering/_handoff/next-session-gse-paper3-after-attack-me-r1.md` §3
- `experiments/20261104-timeseries-tau-extend/conditions.md`
- `papers/per-person-learning/kit/symbols/README.md`

## 運用メモ
- /reimagine 適用: Yes
- 理由: 研究者の指示（「設計は /reimagine で比べてください」）。記号の列の作り方・残差の定義・既存コードの使い回し方に複数の案がある。
