# 設計（調査と議論の進め方）

## アプローチ

1. 調査 1 ラウンド（判断 1）。サブエージェント 4 本を並列（`general-purpose`・Sonnet・入れ子禁止・締切 15 分・報告は `$CLAUDE_JOB_DIR/tmp/survey-*.md` にも書く）:
   - R1: 周辺視の持続運動と注意の捕捉・慣れ（`E-14`・ADR-026 PC-1/PC-3 の外挿の可否）
   - R2: 打鍵・身体のリズムから生成する表現の先行・リアルタイムの自己写像が状態計・回避・ゲーム化を生むか・再着手の環境の手がかり
   - T1: Windows の背景のステージ（Progman / WorkerW・Lively / Wallpaper Engine・`WDA_EXCLUDEFROMCAPTURE`・壊れやすさ）
   - T2: macOS のデスクトップ層・Tauri 2 の中で描くか別の描画か・Android のライブ壁紙
2. 断定に使う一次はメインが原本で照合する（`verify-before-claiming` ルール 1・7）。文献の `docs/references.md` への登録はメインが直列で行う（`citation-ssot`）。
3. 調査の結果を `survey-results.md` にまとめ、引き継ぎ §3 の衝突ごとに当てる。
4. 研究者に AskUserQuestion で問う（推奨と理由を添える）。最初の問いは判断 1 の続き（EH3 に入れるか後に回すか）。

## 衝突の一覧（議論で当てる・一次）

| # | 衝突 | 一次 |
|---|---|---|
| C1 | 肖6「打鍵の最中に更新しない」 | `constraints-ledger.md:33`・`.idea` §7.2-1・[P446] |
| C2 | 判断 5 の更新の規則（時計・打鍵の最中は送る）と U-4（不在の中では更新しない・判断 13） | `portrait-invitation-constraints/decisions.md` 判断 5・13 |
| C3 | 判断 5 の理由 2・T1（形に状態の情報が残らないか・E1-3）。リアルタイムの追従は凡例が無くても状態計として読まれやすい | 判断 5・15・台帳 T1 |
| C4 | `E-14`（通常時に注意を奪わないか）・ADR-026 PC-1/PC-3（代償は出す/出さないと面積で動き、強度では動かない）・`A18`（招待面の提示は離散） | `expression-channel.md:962`・`:909`・ADR-026 |
| C5 | `PS-Q8`（D21 の PC 画面内の常時リアルタイム表現を維持するか撤回するか）。この案は D21 の側に立つ具体案になりうる | `expression-channel.md:958`・ADR-017 D21 |
| C6 | 画面共有・録画での露出（PC-8・`E-13`・肖14）。ステージなら `WDA_EXCLUDEFROMCAPTURE` が使えるか | ADR-026 PC-8 |
| C7 | 招待を背景の変化で表す案: EH3 の比較との混同・窓の裏で PC-12 を満たしにくい・A18・判断 5（推定を契機にする） | 判断 4・6・16・ADR-026 PC-12 |
| C8 | ADR-025（本人に自分の量を返さない）は層 A だけ Accepted・PC 側は `E-11` で未決。打鍵の速さへの追従は「量」として読まれうる | ADR-025 D1・D2 |
| C9 | 技術: R-P8（戻せない背景では動かさない・元の壁紙を戻す）。ステージなら壁紙のファイルに触れない | `implementation-requirements.md:44` |
| C10 | 層 A（Android のライブ壁紙は持続アニメ可・iOS は不可・A-7 は OS が交絡するので第 1 版から外した ADR-022 D1） | ADR-022・`A12` |

## 変更対象

- `.steering/20261012-portrait-rhythm-motion/`（本タスクの記録）
- `docs/references.md`（新しい出典の append）
- まとめの文書（`.idea` か新しい設計の文書・研究者が決める）

## テスト戦略

実装が無いので無し。調査の検算は、断定に使う出典をメインが原本で照合すること。
