# 引き継ぎ: 相対のタイミングの写像は停滞と速さを写すか（机上の検査・G-GEAR）

作成 2026-10-15（Mac）。返答・記録・AskUserQuestion の引数は日本語で。記号（★・⚠️）を多用しない。AskUserQuestion には推奨と理由を添える。

## 0. 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-tangibility-relative-timing-desk-check.md を読んで、/start-task で机上の検査のタスクを立て、§3 の問いの立て方を研究者と決めるところから始めて。
```

## 1. 背景（2026-10-15 に決まったこと）

- タスク `.steering/20261015-tangibility-design/`（ブランチ `docs/tangibility-design`）の判断 14・17。
- 案 D（手触りの写像）は、打ち方の**全体の速さを割り引いた相対のタイミング**（打鍵の間隔の比など）を形に写す。速さそのものは写さない。根拠は調査 S-TG（`docs/literature/20261015-tangibility-agency-trace-replay.md`）: 自分の運動は時間をおいても見分けられうる（[P489]）。手がかりが時間の構造で、ピアニストはテンポを除いても自分の演奏を見分けた、という報告（[P491]–[P493]）は道具の要約か検索の要約しか無く、カードでは否決した（#10）。[P493]（手拍子）は「全体のテンポが重要」と逆向き。本文を読むまで仮説の材料にとどめる。
- これは仮説で、(a) 本人が自分の打ち方と分かるか（人の段でしか測れない）と (b) 停滞と速さを写さないか、の 2 つが未検証。このタスクは (b) を合成の列で測る。

## 2. 使えるもの（G-GEAR）

- 背景のステージの机上の検査の計器と合成の world: 第 1 回 `experiments/20261012-rhythm-stage-desk-check/`・第 2 回 `experiments/20261013-rhythm-stage-round2/`・第 3 回 `experiments/20261014-rhythm-stage-graded-world/`（ブランチ `docs/rhythm-stage-desk-check` → `docs/rhythm-stage-round2` → `docs/rhythm-stage-graded-world` に積み重なっている。2026-10-14 の時点で push 済み・PR なし。マージの順は研究者が決める）。
- 第 3 回の notes の「親タスクへの材料」: 中間の world（t = 0.25〜0.75）では、速さの要約（A_speed）が L300 の停滞をほぼ完全に見分けた（AUC 0.995〜0.998）。
- その後の 2 段（2026-10-15 に origin で確かめた）: ブランチ `docs/rhythm-stage-speed-confound` の揺れの world（`experiments/20261014-rhythm-stage-speed-confound-world/notes.md`）と原因の切り分け（`experiments/20261015-rhythm-stage-speed-cause-split/notes.md`。notes の 134 行: `raw`・`jitter`・`smooth-hold` の `sub` の上乗せは描画の `r_absdiff`・`r_sd` の系統が運んでいた（c100 の `lr`・`lrbin` と c200 の `lrbin`。c200 の `lr` は除く）。135 行: `rank` の 3 本は `R2` を落としてもほとんど下がらず表の外）、ブランチ `docs/rhythm-stage-speed-shape` の揺れの形を分けた world（grill 済み・引き継ぎ `next-session-rhythm-stage-speed-shape-world.md`）。

## 3. 決めること（研究者）

0. **最初に重なりを確かめる**: §2 のその後の 2 段の notes を読み、相対のタイミングに近い写像が既に測られていないか（`rank` は描画の候補の名前で、相対のタイミングの写像に当たるかは推測。notes の定義で確かめる）、天井の前提が変わっていないかを確かめてから問いを立てる。

1. **問いの立て方**: 「相対のタイミングの写像が A_speed を超えて停滞を写すか」と立てると、第 3 回と同じ天井に当たる。「相対のタイミングの写像そのものが停滞をどれだけ識別するか（比べる基準は速さの写像）」に立て直す案がある（判断 17 の注意）。
2. **相対のタイミングの定義**: 隣り合う打鍵の間隔の比・窓の中の間隔を中央値で割ったもの・順位など。長い休止（停滞そのもの）を比に含めるか、上限で切るか。
3. **world**: v4（停滞を訂正にだけ置く）では作りの上で答えが決まってしまう（第 1 回 notes）。打鍵の時刻に停滞が出る world（v2・中間の world）を使うか。
4. 合格の定義と、固定の前の `/cross-review`。

## 4. 守ること

- 合成の列だけを使う。NDJSON（合成も）・キーストロークの内容を外部の LLM（Codex を含む）に送らない。
- 第 1〜3 回の入れ物と判定を書き換えない。`src-tauri/`・EH3 のファイルに触れない。
- `git add -A` を使わない。計測の run の最中は PR を出さない（push だけ）。
