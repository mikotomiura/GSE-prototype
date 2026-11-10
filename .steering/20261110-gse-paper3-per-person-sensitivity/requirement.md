# 論文 3: 手順の感度を合成で確かめる試験（S15）

## 背景

論文 3 の外枠（`papers/per-person-learning/manuscript/outline.md` @ 47d9b1b2）は、構造と τ を他人で選ぶ手順の下で、CoAuthor の 15-session パネルの本人 − 共通が +4.1e-4〜+7.2e-4 にとどまり、これを本人の上積みとして読まないと書いている。CS1 では手順が共通そのもの（τ = ∞）を選ぶ。

attack-me round 2（verdict の直す順 4・R2 N2・Codex）は、この結果が「個人差が無い」のか「手順が保守的で、ある個人差を拾えない」のかを分けられないと指摘した。研究者は判断 21 で「既知の個人差を埋めた合成で確かめる（新しい試験・条件を先にコミット・補足と本文 1〜2 文）」を選んだ。

## ゴール

合成の書き手に既知の大きさの個人差（0 を含む数段）を埋め、外枠の手順をそのまま当てて、次を出す。

- 埋めた大きさごとに、手順が選ぶ構造と τ、本人 − 同じ構造の共通の中央値と良い側の割合。埋めた大きさに応じて上がるか。
- 陰性対照（埋めた差 0・乱数の種を複数）で、事前分布の最頻値と共通の違いだけでどれだけの正の残りが出るか。
- 何が出れば「拾える」と書くか（読みの形）を、結果より前に条件に書く。

結果は `experiments/20261110-per-person-sensitivity/notes.md` にまとめ、外枠の S15 と 4.3 の 1〜2 文に入れ、open items の S15 の行を消す。その後に attack-me round 3 を回す（引き継ぎ §3）。

## スコープ

### 含むもの
- 合成の形は 2 つ: CoAuthor の 15-session パネルの形と CS1 の 5 課題パネルの形（研究者の選択・2026-11-10）。記号の数は前の試験の集計値（tau-extend の tables.md の学習・評価の記号の数）だけを使う。
- 当てはめと選びのコードは前の試験（`experiments/20261104-timeseries-tau-extend/scripts/` の `hmm2.py`・`data.py`・`ml.py`）を写さずに読み込み、SHA-256 を条件に固定する。
- 条件（conditions.md）と SEED を、合成のコードより前にコミットする。
- 陽性対照・変異（selftest）、notes、外枠の S15 と 4.3 の文、open items の更新。
- attack-me round 3（Codex を加える）。

### 含まないもの
- 実データ・書き手ごとの値・npz を開かない（合成だけ）。
- 結果を段 1 の候補の採否や ADR-047 の根拠にしない（ADR-047 D2・D6）。
- push と PR（研究者が確かめてから）。
- 外枠の他の直し（round 3 の指摘への対応は別に聞く）。

## 受け入れ条件

- [ ] conditions.md と SEED が合成のコードより前のコミットにある。
- [ ] selftest（陽性対照・変異）が通ってから本計算を回した。
- [ ] notes.md に、埋めた大きさごとの選ばれた構造と τ・本人 − 共通の中央値と良い側の割合・陰性対照の分布と、条件の読みの形に当てた結論がある。
- [ ] 外枠の S15 と 4.3 に結果の 1〜2 文が入り、open items の S15 の行が消えている。
- [ ] /cross-review（Codex を含む）を通した。
- [ ] attack-me round 3 の verdict がある。

## 関連ドキュメント

- `.steering/20261107-gse-paper3-per-person-learning/decisions.md` 判断 21〜23
- `.steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-2/verdict.md`
- `experiments/20261104-timeseries-tau-extend/conditions.md`（D3 の 2 段（他人）・τ = ∞）
- `experiments/20261106-tau-mode-candidate/notes.md`（最頻値の候補）

## 運用メモ
- /reimagine 適用: Yes
- 理由: 引き継ぎ（2026-11-10）が「設計は /start-task の後に /reimagine で比べる」と定めた。埋め方（どの母数に・どの大きさの物差しで）と読みの形に複数の案があり、最良案が自明でない。
