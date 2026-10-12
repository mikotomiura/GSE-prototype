# 打鍵のリズムで滑らかに動く背景のステージ（調査と議論）

## 背景

研究者の提案（2026-10-12・引き継ぎ `.steering/_handoff/next-session-portrait-rhythm-motion.md` §1 の逐語の要点）:

- 壁紙の表現を、今の「遅い時間で少し変わる」静止画の更新ではなく、**打鍵のリズムでぬるぬると滑らかにリアルタイムで波打って変化する**表現にする。時計（時間）ではなく打鍵のリズムで変動させる。
- 招待も右上の図像ではなく、壁紙の背景のリアルタイムの変化で身体へ戻ることを促す形にする案（研究者はまだ決めていない）。
- **壁紙という「紙」に固執せず、背景で動くメディア表現の「ステージ」として考える**。壁紙のファイルを替えるのではなく、デスクトップの背景の層に自前の描画面を置く、という捉え方。
- この案は `.idea/20261005-motivation-fatigue-reentry-surface.md`（main のチェックアウトにだけある・git の外）に深く関係する。調査は技術とスタックも含める。

今の設計（肖6「打鍵の最中に更新しない」・判断 5 の時計による更新・U-4「不在の中では更新しない」・ADR-017 D21・ADR-026 の離散の提示・EH3 の R-P8）とぶつかる所がある（引き継ぎ §3）。

## ゴール

1. この案を EH3 に入れるか、EH3 の後（EH4 など）に回すかを、調査 1 ラウンドの結果を根拠に研究者が決められる状態にする（判断 1: 研究者は「調べてから決める」を選んだ）。
2. 引き継ぎ §3 の衝突の一つずつについて、調査の結果を当てて研究者に問い、答えを `decisions.md` に記録する。
3. 結果を `.idea` の文書か新しい設計の文書にまとめる（どちらにするかは研究者に聞く）。

## スコープ

### 含むもの
- 研究の先行（周辺視の持続運動と注意・ambient / calm / peripheral display・生体や打鍵のリズムから生成する表現・自己写像の回避や罪悪感・再着手）
- 技術とスタック（Windows の Progman / WorkerW・Wallpaper Engine / Lively の方式・画面の取り込みからの除外・マルチモニタ・スリープ・後片付け／macOS のデスクトップ層の窓／Tauri 2 の中で描くか別の描画か・CPU/GPU と電池／Android のライブ壁紙との比較）
- 文献の `docs/references.md` への登録（`citation-ssot`・メインが直列で）

### 含まないもの
- 実装・試作（試作は別のタスクで研究者の了承を得てから）
- EH3 の凍結・F-1/F-3 の決定・Windows の実機の残り
- キーストロークの内容・NDJSON の生ログを外部の LLM に送ること

## 受け入れ条件

- [ ] 調査の結果（研究・技術）が `.steering/20261012-portrait-rhythm-motion/` に記録され、断定に使う一次はメインが原本で照合している
- [ ] EH3 に入れるか後に回すかを研究者が決め、`decisions.md` に記録した
- [ ] §3 の衝突ごとの研究者の答えが `decisions.md` にある
- [ ] まとめの文書の置き場所を研究者が決め、そこに書いた

## 関連ドキュメント

- `.steering/_handoff/next-session-portrait-rhythm-motion.md`
- `C:\GSE-prototype\.idea\20261005-motivation-fatigue-reentry-surface.md` §3・§8・§11
- `.steering/20261005-portrait-invitation-constraints/decisions.md`・`constraints-ledger.md`
- `docs/adr/ADR-017`（D21）・`ADR-022`・`ADR-025`・`ADR-026`・`docs/architecture/expression-channel.md` §8（`PS-Q8`・`E-12`〜`E-14`）
- `experiments/20261011-portrait-eh3/preregistration-draft.md`・`.steering/20261011-portrait-eh3-prereg/implementation-requirements.md`

## 運用メモ
- /reimagine 適用: No
- 理由: 調査と議論のタスクで実装の設計を作らない。試作の別タスクを起こすときに改めて判断する（研究者・2026-10-12）
