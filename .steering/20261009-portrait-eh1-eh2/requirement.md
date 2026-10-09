# portrait-eh1-eh2

## 背景

親タスク `.steering/20261005-portrait-invitation-constraints/` は、肖像（予期しない・評価を含まない驚き）と招待の設計の制約を決めた（判断 4〜11）。判断 8 が EH1（合成の記録・参加者なし）で守る制約 E1-1〜E1-8 を導き、`.idea/20261005-motivation-fatigue-reentry-surface.md` §8.5 が EH1・EH2 の中身を書いている。

- EH1: 合成した打鍵の時間系列で、形の生成器を検査する。経路の順序で形が変わるか（`.idea` §8.5）と、形に停滞の情報が残らないか（判断 5・判断 8 E1-3）ほか。
- EH2: 自分の PC で、壁紙 API の更新・複数モニタ・仮想デスクトップ・画面共有・CPU を確かめる（`.idea` §8.5）。

研究者の指示（2026-10-09）: 「機械のみの検証などであれば実施できる状態であればすぐに行いましょう（EH1, EH2）。引継ぎなどを書いてもらえれば win, mac ごと別の機器で実行できます」。→ `.idea` §8.7-3「EH1 にいつ着手するか」はこれで決まった（今・O1/G1 の実行中に、配布物に入れずに進める）。

着手時点の状態: 形の生成器・停滞のラベルを持つ合成の記録・合否の基準は、どれもまだ無かった。IME 論文（`papers/ime-observation`）は入力層の前提の一部と方法の型（漏れの攻撃・実行コストの計器）を与えるが、EH1・EH2 そのものではない（判断 1）。

## ゴール

1. **EH1**: 合否の基準を回す前に `design.md` に固定してコミットし、`experiments/20261009-portrait-eh1/` で 1 コマンドで再現できる形で回し、結果を基準どおりに報告する。
2. **EH2**: Windows と macOS の機械の検証のスクリプトを `experiments/20261009-portrait-eh2/` に置き、Windows 版はこの機械で短く試して元の壁紙に戻す（⚠️ 背景がスポットライトで替えて戻す経路は回せず、`-DryRun` だけ。受け手の `-Quick` が最初の検証になる）。OS ごとの引き継ぎを `.steering/_handoff/` に書き、別の機器で回せるようにする。

## スコープ

### 含むもの
- EH1: 合成の記録の生成器（停滞のラベルつき）→ `gse-replay`（GSE の計算そのもの）で F 系列と `p_stuck` → 形の生成器（仮の文法 3 種 × 時間で育つか 2 種）と陽性対照 2 種 → 検査 E1-1〜E1-7 と順序の感度、E1-8 の候補の描画。U-4 の候補（不在 1 回あたり上限 1 回・揺らぎ）と「打鍵の最中」の窓の幅・更新の間隔を因子にする
- EH2: 壁紙の設定と読み戻し・呼び出しの時間・CPU とメモリ・複数モニタ（機械）と、仮想デスクトップ・画面共有（任意の手の手順）。仮の画像で回す
- OS ごとの引き継ぎ

### 含まないもの
- 製品への実装（`src-tauri/`・`src/` を変えない。配布物に入れない）
- 見た目の美しさの評価・参加者を使う EH3
- ADR・RP・`expression-channel.md` の改訂（判断 2: ADR に上げるのは EH1 の後）
- U-2・U-3・E1-8 の決定（EH1 は U-4 と E1-8 の材料を作るだけ・研究者が選ぶ）
- PR（計測の run 中なので push だけ）

## 受け入れ条件

- [ ] `design.md` の合否の基準を、EH1 の結果を出す前にコミットした（コミットの時刻で示せる）
- [ ] `experiments/20261009-portrait-eh1/run.sh` が 1 コマンドで全段を再走し、`results/` の集計 JSON が基準どおりに緑・赤・判定不能を出す
- [ ] 検査器の自己検査: 陽性対照が赤になる・壊した生成器で E1-4・E1-7 が赤になる（変異で確かめる）
- [ ] 生成した NDJSON と特徴の中間物をコミットしない（集計 JSON と少数の PNG だけ）
- [ ] EH2 の Windows 版をこの機械で短く回し、元の壁紙に戻ったことを読み戻しで確かめた → ⚠️ この機械では満たせなかった（背景が Windows スポットライトで、替えて戻す経路は戻せないため回していない・`-DryRun` だけ）。**受け手の Windows の機器の `-Quick` で満たす**（引き継ぎ §3・decisions 判断 7）
- [ ] Win・Mac の引き継ぎに、計測の run と重ねないこと・壁紙を戻すこと・CLAUDE.md の制約を書いた
- [ ] /cross-review 2 巡と対応を `decisions.md` に記録した

## 関連ドキュメント

- `.steering/20261005-portrait-invitation-constraints/decisions.md`（判断 5・8・11）・`constraints-ledger.md`
- `.idea/20261005-motivation-fatigue-reentry-surface.md` §8・§11（版管理外）
- `docs/experiment-tracking.md`・`reproducibility-discipline` Skill
- `papers/ime-observation/experiment/preregistration.md` §6.8（漏れの攻撃）・§6.10（実行コスト）

## 運用メモ
- /reimagine 適用: No
- 理由: 研究者の回答（2026-10-09）「仮の文法を数種並べる・/reimagine なし」。EH1 自体が複数の生成器を因子として比べるので、案を作り直す利点が小さい。
