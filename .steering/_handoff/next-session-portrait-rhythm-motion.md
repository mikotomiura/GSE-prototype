# 引き継ぎ: 打鍵のリズムで滑らかに動く壁紙（肖像）の調査と議論

作成 2026-10-12（Windows・G-GEAR）。返答・記録は日本語で。記号（★・⚠️）を多用しない（研究者の指摘）。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-portrait-rhythm-motion.md を読んで、打鍵のリズムで滑らかに動く壁紙の調査と議論を始めて。
```

## 1. 研究者の提案（2026-10-12・逐語の要点）

- 壁紙の表現を、今の「遅い時間で少し変わる」静止画の更新ではなく、**打鍵のリズムでぬるぬると滑らかにリアルタイムで波打って変化する**表現にする。時計（時間）ではなく打鍵のリズムで変動させる。
- 招待も右上の図像ではなく、壁紙の背景のリアルタイムの変化で身体へ戻ることを促す形にする案（Claude の見立ては下の §3。研究者はまだ決めていない）。
- この案は `.idea/20261005-motivation-fatigue-reentry-surface.md`（main のチェックアウト `C:\GSE-prototype\.idea\` にだけある・git の外）に深く関係する。次のセッションから具体的な調査と議論を行う。**調査は技術とスタックも含める**（研究者が了承）。

## 2. 今の設計（一次・読む順）

1. `.idea/20261005-motivation-fatigue-reentry-surface.md` §1〜3（核・面の分担: 壁紙は「再着手の面」・作業中の立ち上がりは画面端の小面）、§8.1〜8.4（具体案 v0）、§11（肖像と招待の設計制約）。⚠️ 長い文書なので 1 節だけで代表させない（`verify-before-claiming` ルール 7）。
2. `.steering/20261005-portrait-invitation-constraints/decisions.md` 判断 4〜7・判断 12〜13 と `constraints-ledger.md`（肖6「打鍵の最中に更新しない」・T1・T2）。
3. `docs/adr/ADR-017`（D21: PC 画面内の表現は常時リアルタイム）・`docs/architecture/expression-channel.md` §8 の `PS-Q8`（D21 を維持するか撤回するか・未決）と `E-14`（通常時に注意を奪わないことをどう確かめるか・未決）・`E-12`・`E-13`。
4. `docs/adr/ADR-022`（層 A の媒体: Android のライブ壁紙は持続アニメーションが可・iOS は不可）・`ADR-025`（本人に自分の量を返さない）・`ADR-026`（PC の招待面: PC-1〜PC-12・`A18` の離散の提示）。
5. EH3: `experiments/20261011-portrait-eh3/preregistration-draft.md`（凍結前）・`.steering/20261011-portrait-eh3-prereg/implementation-requirements.md`（R-P8: 戻せない背景＝動く壁紙などでは動かさない）。

## 3. Claude の見立て（2026-10-12・研究者に伝えた・決定ではない）

- 打鍵のリズム（F 系列）を材料にすることは判断 5 の材料の規則に反しない（判断 5 が禁じるのは推定 `p_stuck`・X/Y を材料・契機に使うこと）。⚠️ 2026-10-12 の会話で Claude は一度「判断 5 に反する」と言い過ぎ、訂正した。
- ぶつかるのは:
  - 肖6「打鍵の最中に更新しない」と、v0 の面の分担（壁紙は再着手の面）。
  - 判断 5 の理由 2・E1-3（形に状態の情報が残らないか）。リズムへのリアルタイムの追従は、凡例が無くても状態計として読まれやすい。壁紙は画面の取り込みから外せないので、画面共有でも見える（PC-8・E-13）。
  - `E-14`（常に動くものが視野にあると注意を奪う）・`PS-Q8`（D21 の維持か撤回か）。
  - 技術: Windows の壁紙の API は静止画だけ。動かすには、デスクトップの裏に自前の窓を差し込む非公式の手（Progman / WorkerW）が要り、R-P8 が「戻せない背景」として避けている種類に近い。
- 招待を壁紙で表す案は、EH3 の比較（壁紙の条件 空・地模様・肖像を日ごとに替える・招待はどの条件でも同じ形）と混ざる・作業中の壁紙は窓の裏で PC-12 を満たしにくい・`A18`（離散の提示）・停滞の推定を壁紙の契機にする（判断 5）、とぶつかる。身体へ戻る表現は、スマホ側（層 A・Android のライブ壁紙）の方が合う可能性がある。
- 提案: EH3 はこのまま凍結へ進め、この案は EH3 の後の候補（EH4 など）として調査と議論から始める。EH3 に入れるかは研究者が決める。

## 4. このセッションでやること

1. `/start-task` で `.steering/[YYYYMMDD]-portrait-rhythm-motion/` を作る（実装ではなく調査と議論。`requirement.md` に研究者の提案の逐語を置く）。
2. 調査（サブエージェントで並列。`subagent-delegation` の契約: model の明示・範囲と禁止・締切。文献の append はメインで直列＝`/literature-review` Step 2）:
   - 研究: 打鍵や身体のリズムから生成する表現（generative art・ambient display・calm technology・peripheral display）の先行、周辺視の持続運動と注意の捕捉（`E-14`・ADR-026 PC-1/PC-3 の [P341] [P343] [P346]）、自分の状態の写像が回避や罪悪感を生むか（S-PI のカード）、リアルタイムの自己写像と再着手。
   - 技術とスタック:
     - Windows: Progman / WorkerW に窓を差し込む方法の安定性（Windows 11 の版ごと）、Wallpaper Engine / Lively Wallpaper の方式、DirectComposition / Direct3D / WebView2、マルチモニタ・DPI、スリープとロック、終了・異常終了での後片付け、元の壁紙へ戻す保証（R-P8）、画面の取り込みから外せるか（`WDA_EXCLUDEFROMCAPTURE` がデスクトップ層の窓に効くか）。
     - macOS: デスクトップ層の窓（`kCGDesktopWindowLevel`）・Spaces・複数ディスプレイ・Stage Manager。
     - Tauri 2 の中で描くか（WebView のアニメーション・Canvas/WebGL）、別の描画（wgpu など）か。CPU/GPU と電池の予算。打鍵のフックのスレッドとの境界（`hook-constraints`: コールバックは Atomic と channel だけ）、`analysis/` に OS API を入れない（`architecture-rules`）。
     - Android のライブ壁紙（層 A・ADR-022）との比較。
   - 一次は原本で照合し、`citation-ssot`（`[Pn]`/`[Vn]`）で登録する。有料の本文は使わない。
3. 議論: 調査の結果を、§3 の衝突の一つずつに当てて、研究者に AskUserQuestion で問う（推奨と理由を添える）。既決（肖6・判断 5・D21・ADR-026）を変えるなら、どの記録を改めるか（新しい ADR か判断か）も問う。
4. 結果を `.idea` の文書か新しい設計の文書にまとめる（どちらにするかは研究者に聞く）。

## 5. 守ること

- キーストロークの内容・NDJSON の生ログを外部の LLM（Codex を含む）に送らない。打鍵のリズムを試しに描くなら、合成の列か集計だけを使う。
- 実装はしない（調査と議論のタスク）。試作を作るなら別のタスクで、研究者の了承を得てから。
- この機械は G-GEAR（Windows のデスクトップ・self-hosted の Windows CI の runner を兼ねる）。Surface（Modern Standby）とはスリープの経路が違う。
- 範囲外: EH3 の凍結・F-1/F-3・Windows の実機の残り（`.steering/20261012-eh3-windows-device-rest/tasklist.md`）。

## 6. 今日の状態（2026-10-12）

- PR #357（試作の段 `trigger=proto`・0.50/10 秒）・#359（招待の実機の記録・空の日に壁紙を書き直さない）は main に merge 済み。
- 招待の実機で見つかった「間を置いて 1 キーだけ押した後の静止が契機になる」は、本番の値と一緒に決める（`.steering/20261012-eh3-windows-device-rest/decisions.md` 判断 3）。リズムで描く表現を考えるときにも、打鍵が止まっている間に特徴量が据え置かれることは関係する。
