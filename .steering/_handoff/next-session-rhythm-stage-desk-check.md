# 引き継ぎ: 打鍵のリズムで動く背景のステージ —— 合成の列での机上の検査

作成 2026-10-12（Windows・G-GEAR）。返答・記録は日本語で。記号（★・⚠️）を多用しない（研究者の指摘）。

**着手は EH3 の後**（`.steering/20261012-portrait-rhythm-motion/decisions.md` 判断 1）。EH3 の凍結の作業を止めて始めない。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-rhythm-stage-desk-check.md を読んで、背景のステージの机上の検査の設計を始めて。
```

## 1. ここまでの経緯（一次・読む順）

1. `.steering/20261012-portrait-rhythm-motion/requirement.md`（研究者の提案の逐語の要点）・`decisions.md` 判断 1〜9・`survey-results.md`（調査 S-RM・出典 [P468]–[P471]・[V283]–[V286]）。
2. 親の制約: `.steering/20261005-portrait-invitation-constraints/decisions.md` 判断 5・8・12〜15 と `constraints-ledger.md`（T1・T2・肖6・肖14）。
3. EH1 の型の前例: `experiments/20261010-portrait-eh1-round5/`（`data.md`・`config.json`・`scripts/gen_sessions.py`・`checks.py`・`run.sh`）と第 1〜4 回の `notes.md`。合成の打鍵の列を `gse-replay` に通して秒ごとの F 系列を取り、停滞のラベルと形の関係を検査する作り。
4. `.idea/20261005-motivation-fatigue-reentry-surface.md` §11・§12（main のチェックアウトにだけある・git の外。§12 は 2026-10-12 に研究者が追記した要約）。

## 2. 決まっていること（研究者・2026-10-12）

- 肖6・判断 5（壁紙の更新は時計・打鍵の最中は送る・U-4）は変えない。ステージは**壁紙とは別の面の候補**で、採るときにその面の規則を新しい判断として起こす（判断 3）。
- 最初の段は**合成の列での机上の検査**。試作（自分の PC で動かす）は作らない（判断 4）。
- 背景の変化での招待も候補に残す（判断 5）。検査に招待を含めるかは、設計の最初に研究者に聞く。
- `PS-Q8` は閉じない（判断 6）。

## 3. 検査で測りたいこと（案・設計で研究者と決める）

リアルタイムの写像（打鍵の F 系列 → 毎フレームの描画のパラメータ）が、次をどれだけ写すか:

1. **停滞**（EH1 と同じラベル・直近 300 s ほか）。相関だけでなく識別の検査（台帳 T1・判断 5 の理由 2）。EH1 の検査器（攻撃者・陽性対照・神託）を使い回せるかを先に確かめる。
2. **打鍵の有無**（止まった瞬間と再開の瞬間に、動きの様子が変わるか）。調査 §1.1 の推論: リズムへの追従は、動きの「開始」に近い変化を本人の打鍵に合わせて作る。
3. **速さ**（打鍵の速さを量として読めるか・ADR-025 の「自分の量」・`E-11`）。
4. **止まっている間の振る舞い**: 特徴量が据え置かれる間（`.steering/20261012-eh3-windows-device-rest/decisions.md` 判断 3）、描画をどうするか（据え置く・時間で減衰する・地へ戻る）。減衰させると「止まった時間」を写す（判断 5 の代償 3 の型）。
5. 写像の候補を複数用意して比べる（例: 生の追従・強く平滑化・順序だけを使う・揺らぎを足す）。

測らないこと: 作業中に注意を奪うか（`E-14`）は机上では測れない。机上の検査の結果を見て、試作と二重課題の器を起こすかを決める。

## 4. 守ること

- 合成の列だけを使う。実在の人の打鍵・gse-dataset のログは使わない。キーストロークの内容・NDJSON の生ログを外部の LLM（Codex を含む）に送らない。
- `reproducibility-discipline`（`experiments/<YYYYMMDD>-<name>/`・SEED・`run.sh`・`HMM_VERSION` の刻印）。
- 実装（`src-tauri/` の描画やデスクトップの層の窓）はしない。描画の試作は別タスクで研究者の了承を得てから。
- この機械は G-GEAR（self-hosted の Windows CI の runner を兼ねる）。`gse-replay` は release の build が遅いので、debug 版を絶対パスで使う（memory: G-GEAR の release は遅い）。

## 5. 技術の調査で残っていること（試作の段に回す）

- Windows: 24H2 の後の Lively のソース（`WinDesktopCore.cs` の最新）・全画面の一時停止と DPI・画面共有での映り方の実機・WebView2 が背景の窓でアニメーションを止めるか・wgpu など別の描画。
- macOS: デスクトップの層の窓の実機の振る舞い（アイコン・Spaces・全画面・Stage Manager）・`sharingType = .none` と ScreenCaptureKit。
